"""Proportional speed and live-scan diagnostics; fake callbacks/clock only."""
import json
import threading
import unittest
from unittest import mock
import manual_drive as drive
import server
from test_dashboard import Holder, Clock
import test_session_drive as session_tests


class SpeedTests(unittest.TestCase):
    def test_observed_beams_preserve_invalid_gaps_and_limits(self):
        message=LidarTests().message
        result=server.scan_summary(message([1,float('inf'),2,float('nan'),0.01]))
        self.assertEqual(len(result['observed_rays']),2)
        self.assertEqual([ray[1] for ray in result['observed_rays']],[1,2])
        self.assertAlmostEqual(result['observed_rays'][1][0]-result['observed_rays'][0][0],2*result['ray_width_rad'])
        self.assertLessEqual(len(server.scan_summary(message([1.]*10000))['observed_rays']),720)
    def test_session_joystick_is_proportional_and_bounded(self):
        for power in (-1,-.8,-.5,-.2,0,.12,.25,.5,.8,1):
            for turn in (-1,-.5,0,.5,1):
                v,w=drive.requested_twist('joystick',power,turn,joystick_speed=drive.JOYSTICK_SPEED)
                self.assertLessEqual(abs(v),.30);self.assertLessEqual(abs(w),abs(v)+1e-12)
                self.assertAlmostEqual(v,.30*drive.axis(power))
                if v==0:self.assertEqual(w,0)
    def test_small_medium_full_deflections_increase_without_minimum_boost(self):
        values=[drive.requested_twist('joystick',x,0,joystick_speed=.30)[0] for x in (0,.1,.2,.45,.75,1)]
        self.assertEqual(values[:2],[0,0]);self.assertLess(values[2],.03);self.assertLess(values[3],values[4]);self.assertEqual(values[-1],.30)
    def test_buttons_and_legacy_joystick_keep_previous_speed(self):
        for action in drive.ACTIONS:
            v,w=drive.requested_twist(action,joystick_speed=.30);self.assertEqual(abs(v),.03)
        self.assertEqual(drive.requested_twist('joystick',1,0),(.03,0))
    def test_real_session_worker_maps_joystick_ceiling_and_release_to_zero(self):
        fixture=session_tests.ControlTests();fixture.setUp();fixture.command('joystick',1,throttle=1,steering=0);fixture.control.tick()
        self.assertEqual(fixture.sent[-1][1:],(.30,0));fixture.command('neutral',1);fixture.control.tick();self.assertEqual(fixture.sent[-1][1:],(0,0))
        state=fixture.control.snapshot();self.assertEqual(state['joystick_speed_request_m_s'],.30);self.assertEqual(state['button_speed_request_m_s'],.03)
    def test_feedback_headroom_accepts_observed_overshoot_not_excess_speed(self):
        self.assertEqual(drive.JOYSTICK_SPEED,.30);self.assertEqual(drive.REPORTED_SPEED_LIMIT,.32)
        for speed,expected in ((.30,True),(-.30,True),(-.102,True),(.32,True),(-.32,True),(.321,False),(-.321,False)):
            clock=Clock();feedback=drive.ManualFeedback(clock,drive.REPORTED_SPEED_LIMIT,drive.REPORTED_YAW_LIMIT);feedback.graph(None)
            for i in range(3):clock.value+=.01;feedback.observe(drive.crawl.BASE,1000+i,1000+i,(speed,0,.08))
            self.assertEqual(feedback.problem(True) is None,expected)
    def test_session_turn_envelope_and_lateral_guard(self):
        for velocity,expected in (((.30,0,.30),True),((-.30,0,-.35),True),((.30,0,.351),False),((.30,.041,0),False)):
            clock=Clock();feedback=drive.ManualFeedback(clock,drive.REPORTED_SPEED_LIMIT,drive.REPORTED_YAW_LIMIT);feedback.graph(None)
            for i in range(3):clock.value+=.01;feedback.observe(drive.crawl.BASE,1000+i,1000+i,velocity)
            self.assertEqual(feedback.problem(True) is None,expected)


class LidarTests(unittest.TestCase):
    def setUp(self):
        self.clock=Clock();self.app=server.Dashboard(ros=True,clock=self.clock)
        self.reader=server.RosReader.__new__(server.RosReader);self.reader.dashboard=self.app
    def connection(self,count):
        self.app.scan_connections=count;self.app.scan_connection_time=self.clock()
    def message(self,ranges=None,**changes):
        message=Holder(range_min=.1,range_max=10.,angle_min=0.,angle_increment=.01,
                       ranges=[1.,2.,3.] if ranges is None else ranges,
                       header=Holder(frame_id='laser',stamp=Holder(to_sec=lambda:12.5)),
                       _connection_header={'callerid':'/lsn10'})
        message.__dict__.update(changes);return message
    def scan(self):return self.app.status()['scan']
    def test_waiting_is_not_claimed_connected(self):
        self.assertEqual(self.scan()['state'],'waiting');self.assertIsNone(self.scan()['publisher_connections']);self.assertFalse(self.scan()['available'])
    def test_no_connection_vs_connected_without_messages(self):
        self.connection(0);self.assertEqual(self.scan()['state'],'no_publisher')
        self.connection(1);self.assertEqual(self.scan()['state'],'waiting_messages');self.assertFalse(self.scan()['available'])
    def test_valid_callback_shows_source_frame_and_real_geometry(self):
        self.connection(1);self.reader.scan_callback(self.message());state=self.scan()
        self.assertEqual(state['state'],'live');self.assertTrue(state['available']);self.assertEqual(state['publisher'],'/lsn10');self.assertEqual(state['frame'],'laser');self.assertEqual(state['stamp'],12.5);self.assertEqual(state['minimum_m'],1.)
        json.dumps(state,allow_nan=False)
    def test_intensity_aligned_with_only_valid_sample_indices(self):
        state=server.scan_summary(self.message([1,float('inf'),2],intensities=[10,999,40]))
        self.assertEqual(state['point_intensities'],[10,40]);self.assertEqual(state['intensity_state'],'available')
        self.assertEqual((state['intensity_min'],state['intensity_max']),(10,40))
    def test_missing_mismatched_and_nonfinite_intensities_do_not_invent_values(self):
        for values in ([],[12],[float('nan')]*3):
            state=server.scan_summary(self.message(intensities=values))
            self.assertEqual(state['intensity_state'],'unavailable');self.assertEqual(state['point_intensities'],[None]*3)
            json.dumps(state,allow_nan=False)
    def test_mixed_and_constant_intensities_are_raw_not_object_labels(self):
        state=server.scan_summary(self.message(intensities=[0,0,0]))
        self.assertEqual(state['intensity_state'],'available');self.assertEqual(state['intensity_min'],state['intensity_max'])
        state=server.scan_summary(self.message(intensities=[float('inf'),7,float('nan')]))
        self.assertEqual(state['point_intensities'],[None,7,None]);json.dumps(state,allow_nan=False)
    def test_decimated_intensities_remain_aligned_and_bounded(self):
        state=server.scan_summary(self.message([1.]*1000,intensities=list(range(1000))))
        self.assertLessEqual(len(state['point_intensities']),240)
        self.assertEqual(len(state['point_intensities']),len(state['points']))
        self.assertEqual(state['point_intensities'][:3],[0,5,10])
    def test_raw_arrival_rate_not_confused_with_decimated_preview(self):
        self.connection(1)
        for unused in range(12):self.clock.value+=.1;self.reader.scan_callback(self.message())
        state=self.scan();self.assertAlmostEqual(state['arrival_rate_hz'],10);self.assertEqual(state['messages_received'],12);self.assertEqual(state['last_message_age_s'],0)
    def test_stale_data_unavailable_and_old_rate_expires(self):
        self.connection(1);self.reader.scan_callback(self.message());self.clock.value+=2.1
        state=self.scan();self.assertEqual(state['state'],'stale');self.assertFalse(state['available']);self.assertIsNone(state['arrival_rate_hz'])
    def test_connection_loss_hides_even_recent_points(self):
        self.connection(1);self.reader.scan_callback(self.message());self.connection(0)
        self.assertEqual(self.scan()['state'],'no_publisher');self.assertFalse(self.scan()['available'])
    def test_multiple_sources_not_displayed_as_one_valid_lidar(self):
        self.reader.scan_callback(self.message());self.connection(2)
        self.assertEqual(self.scan()['state'],'multiple_publishers');self.assertFalse(self.scan()['available'])
    def test_no_valid_returns_still_reports_live_messages(self):
        self.connection(1);self.reader.scan_callback(self.message([float('inf'),float('nan'),.01,100]))
        state=self.scan();self.assertEqual(state['state'],'no_valid_returns');self.assertTrue(state['available']);self.assertIsNone(state['minimum_m']);self.assertEqual(state['points'],[])
        json.dumps(state,allow_nan=False)
    def test_invalid_scan_invalidates_previous_geometry_and_recovers(self):
        self.connection(1);self.reader.scan_callback(self.message());self.clock.value+=.21
        self.reader.scan_callback(self.message(angle_increment=0));state=self.scan();self.assertEqual(state['state'],'invalid');self.assertFalse(state['available']);self.assertTrue(state['error']);self.assertNotIn('points',state)
        self.clock.value+=.21;self.reader.scan_callback(self.message());self.assertEqual(self.scan()['state'],'live');self.assertIsNone(self.scan()['error'])
    def test_arrival_history_and_drawn_points_remain_bounded(self):
        for unused in range(1000):self.clock.value+=.01;self.reader.scan_callback(self.message())
        self.assertLessEqual(len(self.app.scan_arrivals),80);self.assertLessEqual(len(self.scan()['points']),240)
    def test_sparse_valid_returns_not_lost_by_raw_index_decimation(self):
        values=[float('inf')]*10000;values[1]=2.
        state=server.scan_summary(self.message(values));self.assertEqual(state['valid_samples'],1);self.assertEqual(len(state['points']),1)
    def test_invalid_sensor_stamp_not_serialized_as_nan(self):
        message=self.message();message.header.stamp.to_sec=lambda:float('nan');state=server.scan_summary(message)
        self.assertIsNone(state['stamp']);json.dumps(state,allow_nan=False)
    def test_reader_checks_local_connection_without_master_or_driver_launch(self):
        self.reader.rospy=mock.Mock();self.reader.rospy.is_shutdown.side_effect=[False,True]
        self.reader.scan_subscriber=mock.Mock();self.reader.scan_subscriber.get_num_connections.return_value=1
        self.reader.pending={};self.reader.lock=threading.Lock();self.reader.fps=1000
        self.reader.encode_loop();self.assertEqual(self.scan()['publisher_connections'],1);self.assertEqual(self.scan()['state'],'waiting_messages')


if __name__=='__main__':unittest.main()
