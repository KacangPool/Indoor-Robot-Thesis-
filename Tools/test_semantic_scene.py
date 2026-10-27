"""Synthetic semantics only; no real detections, ROS, robot or file persistence."""
from copy import deepcopy
import unittest
from types import SimpleNamespace as N
from fahad_core.observations import camera_observations, source_age
from fahad_core.semantic_scene import semantic_snapshot
from fusion_fixtures import semantic_demo_snapshots


def message():
    return N(image_header=N(seq=1, stamp=N(secs=10,nsecs=0), frame_id='camera_rgb_optical_frame'),
             bounding_boxes=[N(Class='tvmonitor',id=62,probability=.8,xmin=10,xmax=50,ymin=10,ymax=50)])


class CameraObservationsTests(unittest.TestCase):
    def test_unmatched_detection_kept_with_exact_source_and_no_position(self):
        result=camera_observations(message())
        self.assertEqual(result['image_key'],[10,0,1,'camera_rgb_optical_frame'])
        record=result['records'][0]
        self.assertEqual(record['class'],'tvmonitor');self.assertIsNone(record['position'])
        self.assertEqual(record['height'],'unknown');self.assertEqual(record['clearance'],'unknown')
    def test_empty_message_bounded_and_invalid_rejected(self):
        msg=message();msg.bounding_boxes=[];self.assertEqual(camera_observations(msg)['records'],[])
        for field,value in [('probability',float('nan')),('probability',1.1),('xmin',55),('Class','bad\nlabel')]:
            msg=message();setattr(msg.bounding_boxes[0],field,value)
            with self.assertRaises(ValueError):camera_observations(msg)
        msg=message();msg.bounding_boxes*=101
        with self.assertRaises(ValueError):camera_observations(msg)
    def test_source_clock_age_has_no_host_time_assumption(self):
        obs=camera_observations(message());self.assertAlmostEqual(source_age(obs,10.1),.1)
        for now in (9,12,float('inf')):
            with self.assertRaises(ValueError):source_age(obs,now)


class SemanticSceneTests(unittest.TestCase):
    def setUp(self):self.snapshot=semantic_demo_snapshots()[0]['snapshot']
    def test_monitor_kept_above_plane_without_labelling_table_rays(self):
        before=deepcopy(self.snapshot);scene=semantic_snapshot(self.snapshot)
        self.assertEqual(self.snapshot,before)
        monitor,table=scene['observations']
        self.assertEqual(monitor['status'],'camera_only')
        self.assertEqual(monitor['sample_height_relation'],'above_scan_plane')
        self.assertGreater(monitor['camera_surface']['laser_xyz_m'][2],.15)
        self.assertEqual(monitor['support_relation'],'unknown');self.assertEqual(monitor['clearance'],'unknown')
        self.assertEqual(table['status'],'depth_supported')
        self.assertEqual([r['class'] for r in scene['labelled_laser_rays']],['diningtable'])
        self.assertEqual(scene['labelled_laser_rays'][0]['indices'],list(range(5)))
        self.assertEqual(scene['labelled_laser_rays'][0]['scan_header'],self.snapshot['scan']['header'])
        self.assertTrue(scene['labelled_laser_rays'][0]['synthetic'])
        monitor_map=[r for r in scene['camera_depth_map_observations'] if r['class']=='tvmonitor'][0]
        self.assertEqual(monitor_map['evidence'],'camera_depth_only');self.assertTrue(monitor_map['synthetic'])
    def test_unknown_depth_is_not_floating_or_discarded(self):
        scene=semantic_snapshot(semantic_demo_snapshots()[1]['snapshot'])
        record=scene['observations'][0]
        self.assertEqual(record['class'],'tvmonitor');self.assertIsNone(record['camera_surface'])
        self.assertEqual(record['sample_height_relation'],'unknown')
        self.assertEqual(len(scene['observations']),2)
    def test_blocked_calibration_keeps_labels_but_no_positions(self):
        self.snapshot['calibration_status']='unvalidated';scene=semantic_snapshot(self.snapshot)
        self.assertEqual(len(scene['observations']),2)
        self.assertFalse(scene['labelled_laser_rays']);self.assertFalse(scene['camera_depth_map_observations'])
        self.assertTrue(all(o['camera_surface'] is None for o in scene['observations']))
    def test_missing_map_tf_never_invents_a_position(self):
        del self.snapshot['laser_to_map'];scene=semantic_snapshot(self.snapshot)
        self.assertTrue(scene['observations'][0]['camera_surface']);self.assertFalse(scene['camera_depth_map_observations'])
    def test_camera_depth_survives_no_valid_laser_returns(self):
        self.snapshot['scan']['ranges']=[None]*5;scene=semantic_snapshot(self.snapshot)
        self.assertEqual(scene['observations'][0]['status'],'camera_only')
        self.assertTrue(scene['observations'][0]['camera_surface'])
        self.assertFalse(scene['labelled_laser_rays'])
        self.assertTrue(all(p['evidence']=='camera_depth_only' for p in scene['camera_depth_map_observations']))
    def test_map_transform_must_match_camera_time_too(self):
        self.snapshot['image']['header']['nsecs']=80000000
        self.snapshot['detections']['image_header']['nsecs']=80000000
        for box in self.snapshot['detections']['boxes']:box['object_depth']['image_header']['nsecs']=80000000
        self.snapshot['reference_stamp']=10.1
        scene=semantic_snapshot(self.snapshot)
        self.assertEqual(scene['fusion']['gate'],'ready');self.assertFalse(scene['camera_depth_map_observations'])


if __name__=='__main__':unittest.main()
