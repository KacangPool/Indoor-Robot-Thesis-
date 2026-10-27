import copy
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

import home_lab
from home_lab_scenes import virtual_scene, demo_session, session_for
from fahad_core.experiment import canonical, decode, digest, evaluate_session, save_run, verify_run, MAX_BYTES
from fahad_core.semantic_memory import object_layer
from fahad_core.capture import CaptureBudget, TOPICS
from fahad_core.simulation import bicycle_step, obstacles, route_exercise
import prepare_simulation
import record_fusion_session

ROOT = Path(__file__).parent


class HomeLabTests(unittest.TestCase):
    def test_virtual_height_background_and_depth_use_real_existing_core(self):
        supported = home_lab.evaluate_request({'scene': {}})
        self.assertEqual(supported['scene']['observations'][0]['status'], 'depth_supported')
        raised = home_lab.evaluate_request({'scene': {'height': .3}})
        self.assertEqual(raised['scene']['observations'][0]['status'], 'camera_only')
        self.assertEqual(raised['scene']['observations'][0]['sample_height_relation'], 'above_scan_plane')
        self.assertFalse(raised['scene']['labelled_laser_rays'])
        background = home_lab.evaluate_request({'scene': {'background': 3.2}})
        self.assertEqual(background['scene']['observations'][0]['reason'], 'object_depth_disagrees_with_laser')
        no_depth = home_lab.evaluate_request({'scene': {'depth': False}})
        self.assertEqual(no_depth['scene']['observations'][0]['status'], 'candidate_only')
        self.assertIsNone(no_depth['layer']['observations'][0]['position_m'])

    def test_all_ten_existing_scenarios_are_retained(self):
        for index in range(10):
            result = home_lab.evaluate_request({'case': index})
            self.assertFalse(result['motor_output'])
            self.assertEqual(result['session']['mode'], 'synthetic')

    def test_bad_requests_are_not_configuration_or_commands(self):
        for request in ({'shell': 'x'}, {'case': True}, {'case': -1}, {'case': 10},
                        {'scene': {'distance': float('nan')}}, {'scene': {'depth': 1}},
                        {'scene': {'height': .5}}, {'scene': {'host': 'remote'}}):
            with self.assertRaises((ValueError, TypeError)):
                home_lab.evaluate_request(request)

    def test_headers_stay_matched_and_static_groups_are_not_identities(self):
        session = demo_session()
        results = evaluate_session(session)
        self.assertTrue(all(s['fusion']['gate'] == 'ready' for s in results))
        layer = object_layer(session, results)
        self.assertEqual(len(layer['observations']), 3)
        self.assertEqual(len(layer['static_provisional_groups']), 1)
        self.assertTrue(layer['static_provisional_groups'][0]['provisional_group_not_identity'])
        self.assertTrue(all(s['historical_not_live'] for s in layer['observations']))

    def test_dynamic_people_do_not_become_permanent_static_groups(self):
        session = demo_session()
        for snapshot in session['snapshots']:
            snapshot['detections']['boxes'][0]['class'] = 'person'
        layer = object_layer(session, evaluate_session(session))
        self.assertEqual(len(layer['observations']), 3)
        self.assertEqual(layer['static_provisional_groups'], [])

    def test_duplicates_deduplicate_but_conflicting_source_is_rejected(self):
        session = demo_session()
        session['snapshots'] = [session['snapshots'][0], copy.deepcopy(session['snapshots'][0])]
        self.assertEqual(len(object_layer(session, evaluate_session(session))['observations']), 1)
        session['snapshots'][1]['detections']['boxes'][0]['score'] = .8
        with self.assertRaises(ValueError):
            object_layer(session, evaluate_session(session))

    def test_mixed_or_malformed_sessions_rejected(self):
        for mutate in (lambda s: s.update(schema_version=True), lambda s: s.update(map_id='../private'),
                       lambda s: s.update(snapshots=[]), lambda s: s['snapshots'][0].update(mode='recorded'),
                       lambda s: s['snapshots'][0].update(calibration_id='other')):
            session = demo_session()
            mutate(session)
            with self.assertRaises(ValueError):
                evaluate_session(session)

    def test_strict_json_and_size_limits(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b' '* (MAX_BYTES+1)):
            with self.assertRaises(ValueError):
                decode(raw)
        with self.assertRaises(ValueError):
            home_lab.evaluate_request({'session_json': '{"schema_version":1,"schema_version":2}'})
        self.assertEqual(home_lab.evaluate_request({'session_json': canonical(demo_session()).decode('utf8')})['session']['kind'], 'fusion_session')

    def test_save_load_hashes_new_directory_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'new'
            session = demo_session()
            save_run(target, session)
            self.assertEqual(verify_run(target), session)
            with self.assertRaises(FileExistsError):
                save_run(target, session)
            path = target/'semantic_layer.json'
            path.write_bytes(b'{}')
            with self.assertRaises(ValueError):
                verify_run(target)

    def test_manifest_cannot_choose_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'new'
            save_run(target, demo_session())
            path = target/'manifest.json'
            value = json.loads(path.read_text())
            value['files']['../outside'] = 'x'
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                verify_run(target)

    def test_replay_preserves_original_time_and_unknown_positions(self):
        session = session_for([virtual_scene({'calibrated': False})])
        result = home_lab.evaluate_request({'session': session})
        self.assertEqual(result['scene']['fusion']['reason'], 'calibration_not_validated')
        self.assertIsNone(result['layer']['observations'][0]['position_m'])
        self.assertEqual(result['time_basis'], 'recorded_reference_not_current_time')

    def test_local_http_smoke_and_pure_origin_guards(self):
        import http.client
        server = home_lab.make_server(0)
        worker = threading.Thread(target=server.serve_forever)
        worker.start()
        try:
            connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
            connection.request('GET', '/api/cases')
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertEqual(len(json.loads(response.read())), 10)
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            worker.join(3)
        fake = types.SimpleNamespace(server=types.SimpleNamespace(server_port=8878), headers={'Host': '127.0.0.1:8878'})
        self.assertTrue(home_lab.Handler.trusted(fake))
        fake.headers['Origin'] = 'https://outside.invalid'
        self.assertFalse(home_lab.Handler.trusted(fake))

    def test_imports_start_no_services_or_ros(self):
        code = "import sys,threading;sys.path.insert(0,sys.argv[1]);import home_lab,record_fusion_session,prepare_simulation;assert 'rospy' not in sys.modules;assert 'rosbag' not in sys.modules;assert 'numpy' not in sys.modules;assert len(threading.enumerate())==1"
        subprocess.run([sys.executable, '-I', '-c', code, str(ROOT)], check=True, capture_output=True)

    def test_workbench_inline_script_syntax_and_no_raw_html_labels(self):
        import shutil
        node = shutil.which('node')
        if node is None:
            self.skipTest('Existing Node runtime unavailable; nothing installed')
        source = (ROOT/'home_lab.html').read_text(encoding='utf8')
        script = source.split('<script>', 1)[1].split('</script>', 1)[0]
        subprocess.run([node, '--check'], input=script, text=True, check=True, capture_output=True)
        self.assertNotIn('innerHTML', script)
        for forbidden in ('/api/drive', 'cmd_vel', 'WebSocket'):
            self.assertNotIn(forbidden, script)

    def test_session_aggregate_work_budget(self):
        session = demo_session()
        template = session['snapshots'][0]
        template['scan']['ranges'] = [None]*7200
        session['snapshots'] = [copy.deepcopy(template) for _ in range(3)]
        with self.assertRaises(ValueError):
            evaluate_session(session)


class CaptureTests(unittest.TestCase):
    def test_allowlist_never_contains_command_topics(self):
        self.assertEqual(len(TOPICS), 10)
        self.assertFalse(any('cmd_vel' in topic or 'goal' in topic for topic, _ in TOPICS))
        budget = CaptureBudget(0)
        with self.assertRaises(ValueError):
            budget.accept('/cmd_vel', 20, 1)

    def test_budget_limits_time_bytes_count_and_clock(self):
        budget = CaptureBudget(0, max_bytes=1024, max_messages=1)
        self.assertTrue(budget.accept('/scan', 100, 0))
        self.assertFalse(budget.accept('/scan', 100, .1))
        self.assertEqual(budget.reason, 'message_or_byte_limit')
        self.assertTrue(CaptureBudget(0, seconds=1).expired(1))
        regressed = CaptureBudget(1)
        self.assertTrue(regressed.expired(0))
        self.assertEqual(regressed.reason, 'capture_clock_regressed')
        for size in (0, -1, True, 8*1024*1024+1):
            with self.assertRaises(ValueError):
                CaptureBudget(0).accept('/scan', size, 0)

    def test_default_capture_plan_imports_no_ros(self):
        with mock.patch('sys.stdout', new=io.StringIO()) as output:
            self.assertEqual(record_fusion_session.main([]), 0)
            self.assertIn('OFFLINE PLAN ONLY', output.getvalue())
        self.assertNotIn('rospy', sys.modules)
        with mock.patch.object(record_fusion_session, 'record', side_effect=RuntimeError('PRIVATE-RAW-DETAIL')), \
             mock.patch('sys.stdout', new=io.StringIO()) as output:
            self.assertEqual(record_fusion_session.main(['--record', '--output', 'unused-test-path']), 1)
            self.assertIn('RuntimeError', output.getvalue())
            self.assertNotIn('PRIVATE-RAW-DETAIL', output.getvalue())

    def test_adapter_fake_ros_records_fixed_topics_and_partial_failure(self):
        class Message:
            def serialize(self, stream):
                stream.write(b'FAKE')
        class Bag:
            fail = False
            def __init__(self, path, mode):
                self.stream = open(path, 'wb')
            def write(self, topic, message, **kwargs):
                if self.fail:
                    raise OSError('fake')
                self.stream.write(b'FAKE')
            def close(self):
                self.stream.close()
        fake = types.SimpleNamespace(init_node=lambda *a, **k: None, get_param=lambda *a: False,
                                     is_shutdown=lambda: False, Time=types.SimpleNamespace(now=lambda: 10))
        def subscribe(topic, msg_type, callback, **kwargs):
            callback(Message(), kwargs['callback_args'])
            return types.SimpleNamespace(unregister=lambda: None)
        fake.Subscriber = subscribe
        modules = {'rospy': fake, 'rosbag': types.SimpleNamespace(Bag=Bag)}
        for name, values in [('sensor_msgs.msg', ('Image', 'CameraInfo', 'LaserScan')),
                             ('darknet_ros_msgs.msg', ('BoundingBoxes',)),
                             ('tf2_msgs.msg', ('TFMessage',)), ('nav_msgs.msg', ('Odometry',))]:
            modules[name] = types.SimpleNamespace(**{value: Message for value in values})
        for fail in (False, True):
            Bag.fail = fail
            tick = iter(i*.1 for i in range(100))
            with tempfile.TemporaryDirectory() as folder, mock.patch.dict(sys.modules, modules), \
                 mock.patch.object(record_fusion_session, 'wall_time', side_effect=lambda: next(tick)), \
                 mock.patch.object(record_fusion_session, 'free_megabytes', return_value=4096), \
                 mock.patch.object(record_fusion_session.time, 'sleep'):
                target = Path(folder)/'raw'
                result = record_fusion_session.record(str(target), seconds=2, max_mib=1)
                self.assertTrue((target/'capture_manifest.json').exists())
                self.assertFalse(result['calibration_validated'])
                self.assertEqual(result['messages'], 0 if fail else 10)
                self.assertEqual(len(result['missing_topics']), 10 if fail else 0)


class SimulationTests(unittest.TestCase):
    def test_bicycle_forward_reverse_turn_and_bounds(self):
        self.assertEqual(bicycle_step([0, 0, 0], 0, .3), [0, 0, 0])
        self.assertGreater(bicycle_step([0, 0, 0], .1, 0)[0], 0)
        self.assertLess(bicycle_step([0, 0, 0], -.1, 0)[0], 0)
        self.assertGreater(bicycle_step([0, 0, 0], .1, .2)[2], 0)
        for values in ((.2, 0), (.1, .5), (float('nan'), 0)):
            with self.assertRaises(ValueError):
                bicycle_step([0, 0, 0], *values)

    def test_known_route_completes_only_in_ideal_model(self):
        result = route_exercise()
        self.assertTrue(result['metrics']['reached'])
        self.assertFalse(result['hardware_output'])
        self.assertLess(result['metrics']['final_error_m'], .12)
        self.assertTrue(all(abs(v['sim_steering_rad']) <= .45 for v in result['trace']))
        with self.assertRaises(ValueError):
            route_exercise([])

    def test_seeded_worlds_and_xml_joint_sensor_namespace_contract(self):
        self.assertEqual(obstacles(7), obstacles(7))
        self.assertNotEqual(obstacles(7), obstacles(8))
        root = ET.fromstring(prepare_simulation.world_xml('test', obstacles(7)))
        self.assertEqual(root.attrib['version'], '1.9')
        self.assertTrue(root.findall('.//sensor[@type="gpu_lidar"]'))
        self.assertTrue(root.findall('.//sensor[@type="rgbd_camera"]'))
        driver = root.find('.//plugin[@name="gz::sim::systems::AckermannSteering"]')
        self.assertEqual(driver.findtext('topic'), '/home_lab_sim/cmd_vel')
        self.assertEqual(len(root.findall('.//model[@name="home_lab_toy_car"]/joint')), 6)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'sim'
            self.assertTrue(prepare_simulation.prepare(target)['reached'])
            self.assertEqual(len(list(target.glob('*.sdf'))), 3)
            self.assertFalse(json.loads((target/'simulation_manifest.json').read_text())['gazebo_executed'])
            with self.assertRaises(FileExistsError):
                prepare_simulation.prepare(target)


if __name__ == '__main__':
    unittest.main()
