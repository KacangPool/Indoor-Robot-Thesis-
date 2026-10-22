"""Read-only occupancy view: fake ROS objects and laptop loopback only."""
import json
import unittest
from unittest import mock
import server
from test_dashboard import Holder, Clock
import test_dashboard as base


def message(width=2,height=2,data=None,**changes):
    result=Holder(info=Holder(width=width,height=height,resolution=.05,
                  origin=Holder(position=Holder(x=1,y=2,z=0),orientation=Holder(x=0,y=0,z=0,w=1))),
                  header=Holder(frame_id='map'),data=[0,-1,100,25] if data is None else data,
                  _connection_header={'callerid':'/slam'})
    result.__dict__.update(changes)
    return result


class MapTests(unittest.TestCase):
    def setUp(self):
        self.clock=Clock();self.app=server.Dashboard(ros=True,clock=self.clock)
    def connected(self):
        self.app.map_grid=server.occupancy_summary(message());self.app.map_revision=1
        self.app.map_received=self.clock();self.app.map_connections=1;self.app.map_connection_time=self.clock()
    def test_preserves_row_order_unknown_occupancy_origin_and_frame(self):
        grid=server.occupancy_summary(message());self.assertEqual(grid['cells'],[0,-1,100,25])
        self.assertEqual(grid['origin'],{'x':1,'y':2,'yaw':0});self.assertEqual(grid['frame'],'map')
        self.assertEqual(grid['resolution'],.05);self.assertEqual(grid['stride'],1)
    def test_rejects_invalid_dimensions_lengths_limits_and_resolution(self):
        for w,h,data in [(0,2,[]),(1001,1000,[]),(2,2,[0])]:
            with self.assertRaises(ValueError):server.occupancy_summary(message(w,h,data))
        for value in [0,-1,float('inf'),float('nan')]:
            msg=message();msg.info.resolution=value
            with self.assertRaises(ValueError):server.occupancy_summary(msg)
    def test_rejects_invalid_cells_and_does_not_wrap_large_values(self):
        for value in [-2,101,1.5,True,256]:
            with self.assertRaises(ValueError):server.occupancy_summary(message(data=[value,0,0,0]))
    def test_rejects_nonplanar_or_invalid_pose_and_empty_frame(self):
        for xyz in [(0,0,0,0),(.707,0,0,.707),(0,0,float('nan'),1)]:
            msg=message();msg.info.origin.orientation=Holder(x=xyz[0],y=xyz[1],z=xyz[2],w=xyz[3])
            with self.assertRaises(ValueError):server.occupancy_summary(msg)
        msg=message();msg.header.frame_id=''
        with self.assertRaises(ValueError):server.occupancy_summary(msg)
    def test_conservative_coarse_cells_preserve_obstacles_and_unknown(self):
        data=[0]*512;data[0]=-1;data[2]=-1;data[3]=100
        grid=server.occupancy_summary(message(512,1,data));self.assertLessEqual(len(grid['cells']),65536)
        self.assertEqual(grid['stride'],2);self.assertEqual(grid['cells'][0],-1)
        self.assertEqual(grid['cells'][1],100)  # occupied wins; padding/unknown never hides an obstacle
        self.assertEqual(grid['cells'][2],-1)  # incomplete padded row cannot become free
    def test_unavailable_preview_and_no_publisher_never_fabricate_map(self):
        self.assertFalse(self.app.map_status()['available']);self.connected()
        self.app.mode='preview';self.assertEqual(self.app.map_status()['state'],'preview')
        self.assertNotIn('cells',self.app.map_status());self.app.mode='ros_read_only'
        self.app.map_connections=0;self.assertFalse(self.app.map_status()['available'])
    def test_multiple_stale_connection_and_invalid_map_are_hidden(self):
        self.connected();self.app.map_connections=2;self.assertEqual(self.app.map_status()['state'],'multiple_publishers')
        self.app.map_connections=1;self.clock.value+=2.1;self.assertFalse(self.app.map_status()['available'])
        self.app.map_connection_time=self.clock();self.app.map_error='Bad map';self.assertEqual(self.app.map_status()['state'],'invalid')
    def test_static_snapshot_age_not_false_live_and_unchanged_cells_omitted(self):
        self.connected();self.clock.value+=30;self.app.map_connection_time=self.clock()
        state=self.app.map_status(1);self.assertTrue(state['available']);self.assertEqual(state['age_s'],30)
        self.assertNotIn('cells',state);self.assertIn('cells',self.app.map_status(0));json.dumps(state,allow_nan=False)
    def test_overlay_requires_fresh_update_and_map_availability(self):
        self.connected();self.app.map_overlay={'robot':{'x':0,'y':0,'yaw':0}};self.app.map_overlay_time=self.clock()
        self.assertIn('robot',self.app.map_status()['overlay']);self.clock.value+=.76
        self.assertEqual(self.app.map_status()['overlay'],{})
        self.app.map_overlay_time=self.clock();self.app.map_connections=0;self.assertEqual(self.app.map_status()['overlay'],{})
    def test_worker_invalidates_bad_map_and_missing_tf_does_not_invent_pose(self):
        reader=server.RosReader.__new__(server.RosReader);reader.dashboard=self.app
        reader.lock=__import__('threading').Lock();reader.pending_map=(message(),self.clock())
        reader.map_subscriber=mock.Mock();reader.map_subscriber.get_num_connections.return_value=1
        reader.tf_buffer=None;reader.rospy=mock.Mock();reader.rospy.is_shutdown.return_value=False
        with mock.patch.object(self.app.closed,'wait',side_effect=lambda timeout:self.app.closed.set()):reader.map_loop()
        self.assertTrue(self.app.map_status()['available']);self.assertEqual(self.app.map_status()['overlay'],{})
        self.app.closed.clear();reader.pending_map=(message(data=[999]*4),self.clock())
        with mock.patch.object(self.app.closed,'wait',side_effect=lambda timeout:self.app.closed.set()):reader.map_loop()
        self.assertIsNone(self.app.map_grid);self.assertEqual(self.app.map_status()['state'],'invalid')
    def test_worker_uses_actual_frame_transform_and_hides_stale_pose(self):
        self.connected();reader=server.RosReader.__new__(server.RosReader);reader.dashboard=self.app
        reader.lock=__import__('threading').Lock();reader.pending_map=None
        reader.map_subscriber=mock.Mock();reader.map_subscriber.get_num_connections.return_value=1
        reader.rospy=mock.Mock();reader.rospy.is_shutdown.return_value=False;reader.rospy.Time.now.return_value.to_sec.return_value=100
        transform=Holder(header=Holder(stamp=Holder(to_sec=lambda:99.8)),transform=Holder(translation=Holder(x=2,y=3,z=0),rotation=Holder(x=0,y=0,z=0,w=1)))
        reader.tf_buffer=mock.Mock();reader.tf_buffer.lookup_transform.return_value=transform
        self.app.scan={'stamp':99.9,'frame':'laser','points':[[1,0]]};self.app.scan_time=self.clock();self.app.scan_connections=1
        with mock.patch.object(self.app.closed,'wait',side_effect=lambda timeout:self.app.closed.set()):reader.map_loop()
        self.assertEqual(self.app.map_overlay['robot'],{'x':2,'y':3,'yaw':0});self.assertEqual(self.app.map_overlay['scan'],[[3,3]])
        self.assertEqual(self.app.map_overlay['scan_ranges_m'],[1])
        args=reader.tf_buffer.lookup_transform.call_args_list[0].args;self.assertEqual(args[:2],('map','base_footprint'))
        self.app.closed.clear();transform.header.stamp.to_sec=lambda:90;self.app.scan['stamp']=90
        with mock.patch.object(self.app.closed,'wait',side_effect=lambda timeout:self.app.closed.set()):reader.map_loop()
        self.assertEqual(self.app.map_overlay,{})
    def test_http_read_only_map_route_is_host_guarded_and_does_not_arm(self):
        fixture=base.HttpTests();fixture.setUp()
        try:
            fixture.app.mode='ros_read_only';fixture.app.map_grid=server.occupancy_summary(message())
            fixture.app.map_revision=7;fixture.app.map_received=fixture.app.clock()
            fixture.app.map_connections=1;fixture.app.map_connection_time=fixture.app.clock()
            code,body,_=fixture.fetch('/api/map');self.assertEqual(code,200);self.assertIn('cells',json.loads(body))
            code,body,_=fixture.fetch('/api/map?revision=7');self.assertNotIn('cells',json.loads(body))
            self.assertFalse(fixture.app.control.snapshot()['armed'])
            self.assertEqual(fixture.fetch('/api/map',changes={'Host':'evil.example'})[0],403)
        finally:fixture.tearDown()


if __name__=='__main__':unittest.main()
