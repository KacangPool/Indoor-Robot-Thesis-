"""Shared algorithms/import boundaries and copied-tool bundle; no robot access."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

import numpy as np
import box_depth_viewer
import person_detection_filter
import record_detection_test
import ros_message_sample
import build_robot_tool_bundle
from fahad_core import camera_metrics, depth, detections, recording, message_samples

ROOT = Path(__file__).resolve().parent


class ModularTests(unittest.TestCase):
    def test_entry_points_reexport_same_algorithms_not_copies(self):
        for entry, module, names in [
            (box_depth_viewer, depth, ['depth_metres','patch_stats','pair_problem']),
            (person_detection_filter, detections, ['select_person_boxes','filtered_message']),
            (record_detection_test, detections, ['boxes_list','finite_number']),
            (record_detection_test, recording, ['header_dict','frame_key','ImageCache','write_json','append_json','free_megabytes']),
            (ros_message_sample, message_samples, ['message_lines','image_samples','scan_summary','payload_lines']),
        ]:
            for name in names:self.assertIs(getattr(entry,name),getattr(module,name))

    def test_core_base_import_does_not_import_ros_numpy_or_start_threads(self):
        code="import sys,threading;sys.path.insert(0,sys.argv[1]);import fahad_core;assert 'numpy' not in sys.modules;assert 'rospy' not in sys.modules;assert len(threading.enumerate())==1"
        subprocess.run([sys.executable,'-I','-c',code,str(ROOT)],check=True,capture_output=True)

    def test_camera_rgb_statistics_preserve_thresholds(self):
        image=np.array([[[0,0,0],[255,255,255]]],dtype=np.uint8)
        stats=camera_metrics.rgb_statistics(image)
        self.assertAlmostEqual(stats['mean'],127.5);self.assertEqual(stats['dark'],50);self.assertEqual(stats['bright'],50)

    def test_diagnostic_depth_legacy_fallback_stays_separate_from_strict_viewer(self):
        image=np.array([[1000,0]],dtype=np.uint16)
        self.assertEqual(camera_metrics.depth_statistics(image,'mono16')['median'],1)
        self.assertEqual(camera_metrics.depth_statistics(image,'mono16')['valid'],50)
        with self.assertRaises(ValueError):depth.depth_metres(image,'mono16')
        self.assertTrue(np.isnan(camera_metrics.depth_statistics(np.zeros((2,2)),'32FC1')['median']))

    def test_camera_info_invalid_matrix_and_metadata(self):
        obj=mock.Mock(K=[0]*8);self.assertIsNone(camera_metrics.camera_info_summary(obj))
        obj.K=[1,0,3,0,5,6,0,0,1];obj.width=640;obj.height=480;obj.header.frame_id='optical';obj.distortion_model='plumb_bob'
        self.assertEqual(camera_metrics.camera_info_summary(obj)['cx'],3)

    def test_shared_robot_modules_have_python36_grammar(self):
        for path in (ROOT/'fahad_core').glob('*.py'):
            ast.parse(path.read_text(encoding='utf8'),feature_version=(3,6))

    def test_bundle_contains_all_shared_dependencies_and_no_results_vendor_or_tests(self):
        with tempfile.TemporaryDirectory() as folder:
            archive=Path(folder)/'tools.zip';manifest=build_robot_tool_bundle.build(archive)
            with zipfile.ZipFile(archive) as bundle:
                names=set(bundle.namelist());self.assertIn('fahad_core/__init__.py',names)
                self.assertIn('fahad_core/camera_metrics.py',names)
                self.assertIn('robot_inventory.py',names)
                self.assertIn('fahad_core/inventory.py',names)
                self.assertIn('fahad_core/fusion.py',names)
                self.assertIn('fahad_core/fusion_geometry.py',names)
                self.assertIn('fusion_prototype.py',names)
                self.assertIn('fusion_demo_template.html',names)
                self.assertEqual(names,set(manifest['files'])|{'tool_bundle_manifest.json'})
                for name,digest in manifest['files'].items():self.assertEqual(hashlib.sha256(bundle.read(name)).hexdigest(),digest)
                bundle.extractall(Path(folder)/'isolated')  # our own fixed-name bundle, not an untrusted ZIP
            code="import sys;sys.path.insert(0,sys.argv[1]);import box_depth_viewer,record_detection_test,person_detection_filter,ros_message_sample;assert 'rospy' not in sys.modules"
            subprocess.run([sys.executable,'-I','-c',code,str(Path(folder)/'isolated')],check=True,capture_output=True)
            before=archive.read_bytes()
            with self.assertRaises(FileExistsError):build_robot_tool_bundle.build(archive)
            self.assertEqual(archive.read_bytes(),before)

    def test_optional_detector_import_does_not_load_weights_or_read_images(self):
        folder=ROOT.parent/'Testing other Models'/'DetectorTest'
        code="import sys;sys.path.insert(0,sys.argv[1]);import test_detector,detector_model;assert 'torch' not in sys.modules;assert 'torchvision' not in sys.modules;assert 'PIL' not in sys.modules"
        subprocess.run([sys.executable,'-I','-c',code,str(folder)],check=True,capture_output=True)

    def test_optional_detector_accepts_injected_model_and_preserves_annotation(self):
        path=ROOT.parent/'Testing other Models'/'DetectorTest'/'detector_model.py'
        spec=importlib.util.spec_from_file_location('optional_detector_for_test',path)
        detector=importlib.util.module_from_spec(spec);spec.loader.exec_module(detector)
        weights=mock.Mock();weights.transforms.return_value=lambda image:'tensor'
        model=mock.Mock(return_value=[{'result':1}]);torch=mock.Mock();torch.inference_mode.return_value.__enter__=mock.Mock();torch.inference_mode.return_value.__exit__=mock.Mock(return_value=False)
        self.assertEqual(detector.predict_image('image',model,weights,torch),{'result':1});model.assert_called_once_with(['tensor'])
        image=mock.Mock();draw=mock.Mock();output=[]
        prediction={'boxes':[np.array([1,2,3,4]),np.array([5,6,7,8])],'labels':[1,1],'scores':[.49,.5]}
        result,count=detector.annotate_prediction(image,prediction,['background','person'],emit=output.append,draw_factory=lambda value:draw)
        self.assertIs(result,image.copy.return_value);self.assertEqual(count,1);self.assertEqual(output,['person: 0.50'])


if __name__=='__main__':unittest.main()
