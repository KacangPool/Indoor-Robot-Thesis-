"""Synthetic/offline regression cases. No live sensors, model or motor calls."""
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fahad_core.fusion import fuse_snapshot, settings
from fahad_core.fusion_geometry import (camera_model, header_stamp, inside, number,
                                        project, rigid_transform, scan_clusters, transform_point)
from fusion_fixtures import demo_snapshots
import fusion_prototype


class FusionTests(unittest.TestCase):
    def setUp(self):
        self.cases = demo_snapshots()
        self.scene = deepcopy(self.cases[0]['snapshot'])

    def record(self, scene=None):
        return fuse_snapshot(scene or self.scene)['observations'][0]

    def test_eight_documented_scenarios_and_input_immutable(self):
        expected = ['depth_supported', 'camera_only', 'camera_only', 'candidate_only',
                    'ambiguous', 'unavailable', 'depth_supported', 'unavailable']
        before = deepcopy(self.cases)
        for case, status in zip(self.cases, expected):
            self.assertEqual(self.record(case['snapshot'])['status'], status)
        self.assertEqual(self.cases, before)

    def test_only_supported_timed_case_makes_map_marker(self):
        result = fuse_snapshot(self.scene)
        self.assertEqual(len(result['map_markers']), 1)
        marker = result['map_markers'][0]
        self.assertEqual(marker['frame'], 'map')
        self.assertTrue(marker['synthetic'])
        self.assertEqual(marker['stamp'], 10)
        self.assertAlmostEqual(marker['expires_at'], 10.5)
        self.assertNotIn('occupancy', result)

    def test_raised_same_bearing_object_gets_no_fake_range(self):
        result = fuse_snapshot(self.cases[1]['snapshot'])
        self.assertEqual(result['observations'][0]['reason'], 'no_projected_cluster')
        self.assertIsNone(result['observations'][0]['laser_point_m'])
        self.assertEqual(result['map_markers'], [])

    def test_background_in_rectangle_rejected_by_independent_depth(self):
        result = fuse_snapshot(self.cases[2]['snapshot'])
        self.assertGreater(len(result['projected_points']), 0)
        self.assertEqual(result['observations'][0]['reason'], 'object_depth_disagrees_with_laser')
        self.assertFalse(result['map_markers'])

    def test_projection_alone_never_becomes_supported_or_mapped(self):
        result = fuse_snapshot(self.cases[3]['snapshot'])
        self.assertEqual(len(result['observations'][0]['candidates']), 1)
        self.assertEqual(result['observations'][0]['status'], 'candidate_only')
        self.assertFalse(result['map_markers'])

    def test_shared_cluster_ambiguous_for_both_boxes(self):
        result = fuse_snapshot(self.cases[4]['snapshot'])
        self.assertTrue(all(o['status'] == 'ambiguous' for o in result['observations']))
        self.assertFalse(result['map_markers'])

    def test_two_separate_in_box_clusters_are_ambiguous(self):
        self.scene['scan'].update(angle_min=-0.06, ranges=[1.6,1.6,1.6,None,1.65,1.65,1.65])
        self.assertEqual(self.record()['reason'], 'multiple_clusters')

    def test_invalid_return_splits_cluster_and_range_boundary_is_valid(self):
        scan = deepcopy(self.scene['scan'])
        scan.update(range_min=1.6, ranges=[1.6, 1.6, None, 1.6, float('nan'), -1, 11])
        groups = scan_clusters(scan)
        self.assertEqual([len(g) for g in groups], [2,1])
        self.assertEqual(groups[0][0]['laser_xyz_m'][2], 0)

    def test_full_rigid_projection_uses_height_and_rotation(self):
        tf = rigid_transform(self.scene['laser_to_camera'], 'laser', 'camera_rgb_optical_frame', 10, .05)
        point = transform_point([1.6, 0, 0], tf)
        self.assertEqual(point, [0.0, -.02, 1.57])
        cam = camera_model(self.scene['camera'], self.scene['image'])
        self.assertAlmostEqual(project(point, cam)[1], 240-10/1.57)
        self.assertIsNone(project([0,0,-1], cam))

    def test_transform_reversed_wrong_frame_scale_reflection_rejected(self):
        for change in [{'source_frame':'base_link'}, {'target_frame':'laser'},
                       {'rotation':[[2,0,0],[0,1,0],[0,0,1]]},
                       {'rotation':[[1,0,0],[0,1,0],[0,0,-1]]}]:
            s=deepcopy(self.scene);s['laser_to_camera'].update(change)
            with self.assertRaises(ValueError):fuse_snapshot(s)

    def test_exact_yolo_source_image_key_not_output_timestamp(self):
        for change in [{'seq':2}, {'nsecs':1}, {'frame_id':'camera_link'}]:
            s=deepcopy(self.scene);s['detections']['image_header'].update(change)
            self.assertEqual(fuse_snapshot(s)['reason'], 'detection_source_image_mismatch')

    def test_stale_future_and_whole_scan_acquisition_window(self):
        s=deepcopy(self.scene);s['reference_stamp']=11
        self.assertEqual(fuse_snapshot(s)['reason'], 'stale_or_future_measurements')
        s=deepcopy(self.scene);s['reference_stamp']=9
        self.assertEqual(fuse_snapshot(s)['reason'], 'stale_or_future_measurements')
        s=deepcopy(self.scene);s['scan']['time_increment']=.03;s['reference_stamp']=10.13
        self.assertEqual(fuse_snapshot(s)['reason'], 'acquisition_times_not_aligned')
        s['scan']['time_increment']=.1
        self.assertEqual(fuse_snapshot(s)['reason'], 'scan_duration_unsupported')

    def test_moving_and_unvalidated_real_recording_blocked(self):
        self.scene['stationary']=False
        self.assertEqual(fuse_snapshot(self.scene)['reason'], 'moving_or_unknown_motion_not_supported')
        self.scene['stationary']=True;self.scene['mode']='recorded'
        self.assertEqual(fuse_snapshot(self.scene)['reason'], 'calibration_not_validated')

    def test_raw_image_missing_model_and_invalid_focal_rejected(self):
        for field, value in [('rectified',False)]:
            s=deepcopy(self.scene);s['image'][field]=value
            with self.assertRaises(ValueError):fuse_snapshot(s)
        for patch_model in [{'fx':0},{'fy':float('nan')},{'frame_id':'wrong'},{'width':320}]:
            s=deepcopy(self.scene);s['camera'].update(patch_model)
            with self.assertRaises(ValueError):fuse_snapshot(s)

    def test_low_score_and_full_image_bounding_box(self):
        self.scene['detections']['boxes'][0]['score']=.2
        self.assertEqual(self.record()['status'], 'filtered')
        self.scene['detections']['boxes'][0].update(score=.9,xmin=0,ymin=0,xmax=640,ymax=480)
        self.assertEqual(self.record()['status'], 'depth_supported')

    def test_empty_physical_returns_not_described_as_ready(self):
        self.scene['scan']['ranges']=[None,0,-1,11,float('nan')]
        result=fuse_snapshot(self.scene)
        self.assertEqual(result['gate'],'blocked')
        self.assertEqual(result['reason'],'no_valid_laser_returns')
        self.assertEqual(result['map_markers'],[])

    def test_unverified_invalid_mixed_or_mismatched_depth_stays_candidate(self):
        for patch_depth in [{'region_verified':False}, {'registered_to_rgb':False},
                            {'values':[[0]*3 for _ in range(3)]}, {'values':[[1000,2000,1000]]*3},
                            {'encoding':'8UC1'}, {'u':10}, {'values':[[1570.5]*3]*3}]:
            s=deepcopy(self.scene);s['detections']['boxes'][0]['object_depth'].update(patch_depth)
            self.assertEqual(self.record(s)['status'], 'candidate_only')
        s=deepcopy(self.scene);s['detections']['boxes'][0]['object_depth']['image_header']['seq']=2
        self.assertEqual(self.record(s)['status'], 'candidate_only')

    def test_float_depth_metres_not_radial_range(self):
        patch_depth=self.scene['detections']['boxes'][0]['object_depth']
        patch_depth.update(encoding='32FC1',values=[[1.57]*3 for _ in range(3)])
        self.assertEqual(self.record()['status'], 'depth_supported')

    def test_map_missing_wrong_or_untimed_never_falls_back_to_origin(self):
        for map_tf in [None, {'source_frame':'wrong'}, {'stamp':9}, {'static':True}]:
            s=deepcopy(self.scene)
            if map_tf is None:del s['laser_to_map']
            else:s['laser_to_map'].update(map_tf)
            result=fuse_snapshot(s)
            self.assertEqual(result['observations'][0]['status'],'depth_supported')
            self.assertIsNone(result['observations'][0]['map_point_m'])
            self.assertEqual(result['map_markers'],[])

    def test_representative_is_a_real_ray_not_invented_centroid(self):
        result=fuse_snapshot(self.scene)
        point=result['observations'][0]['laser_point_m']
        self.assertIn(point,[p['laser_xyz_m'] for p in result['projected_points']])

    def test_invalid_contract_limits_and_thresholds(self):
        for value in [True,float('nan'),float('inf'),'1']:
            with self.assertRaises(ValueError):number(value)
        for overrides in [{'unknown':1},{'min_score':2},{'cluster_gap_m':0},{'min_points':2.5}]:
            with self.assertRaises(ValueError):settings(overrides)
        s=deepcopy(self.scene);s['scan']['ranges']=[1]*7201
        with self.assertRaises(ValueError):fuse_snapshot(s)
        for patch_box in [{'score':float('nan')},{'xmin':400},{'class':''}]:
            s=deepcopy(self.scene);s['detections']['boxes'][0].update(patch_box)
            with self.assertRaises(ValueError):fuse_snapshot(s)

    def test_wrong_container_types_fail_explicitly(self):
        for value in [None, [], 'snapshot']:
            with self.assertRaises(ValueError):fuse_snapshot(value)
        for field in ['image','scan','detections','laser_to_camera','camera']:
            s=deepcopy(self.scene);s[field]=[]
            with self.assertRaises(ValueError):fuse_snapshot(s)
        s=deepcopy(self.scene);s['detections']['boxes']=[None]
        with self.assertRaises(ValueError):fuse_snapshot(s)

    def test_bad_header_and_depth_container_never_fabricate_support(self):
        for bad in [None,{'seq':True,'secs':10,'nsecs':0,'frame_id':'laser'},
                    {'seq':1,'secs':10,'nsecs':1000000000,'frame_id':'laser'}]:
            with self.assertRaises(ValueError):header_stamp(bad)
        self.scene['detections']['boxes'][0]['object_depth']='not a patch'
        self.assertEqual(self.record()['status'],'candidate_only')

    def test_imports_have_no_process_file_or_model_startup(self):
        with patch('subprocess.Popen',side_effect=AssertionError('must not start')):
            spec=importlib.util.spec_from_file_location('fusion_import_test',fusion_prototype.__file__)
            spec.loader.exec_module(importlib.util.module_from_spec(spec))

    def test_cli_refuses_overwrite_and_escapes_html_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'out'
            self.assertEqual(fusion_prototype.main(['--demo','--output',str(out)]),0)
            before=(out/'report.json').read_bytes()
            with self.assertRaises(SystemExit):fusion_prototype.main(['--demo','--output',str(out)])
            self.assertEqual((out/'report.json').read_bytes(),before)
            s=deepcopy(self.scene);s.update(mode='recorded',calibration_status='validated')
            s['detections']['boxes'][0]['class']='</script><script>bad</script>'
            source=Path(directory)/'input.json';source.write_text(json.dumps(s),encoding='utf8')
            self.assertEqual(fusion_prototype.main(['--input',str(source),'--output',str(Path(directory)/'safe')]),0)
            html=(Path(directory)/'safe/index.html').read_text(encoding='utf8')
            self.assertNotIn('</script><script>bad',html)
            self.assertIn('\\u003c/script>',html)


if __name__ == '__main__':
    unittest.main()
