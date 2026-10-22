"""Offline prototype checks. No ROS, motors, Internet or external packages."""
from __future__ import print_function
import ast
import json
import os
import threading
import unittest
try:
    import http.client as http_client
except ImportError:
    import httplib as http_client

import control
import server


class Clock(object):
    def __init__(self): self.value = 100.0
    def __call__(self): return self.value


class Holder(object):
    def __init__(self, **values): self.__dict__.update(values)


OWNER = 'a' * 32


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.control = control.RehearsalControl(self.clock)

    def test_disabled_on_start(self):
        state = self.control.snapshot()
        self.assertFalse(state['armed'])
        self.assertFalse(state['motor_output'])
        self.assertEqual(state['action'], 'neutral')

    def test_deliberate_arm_then_intent(self):
        generation = self.control.arm(OWNER)
        state = self.control.command(OWNER, generation, 1, 'forward_left')
        self.assertEqual(state['action'], 'forward_left')
        self.assertFalse(state['motor_output'])

    def test_no_heartbeat_expires_exact_boundary(self):
        self.control.arm(OWNER)
        self.clock.value += 0.5
        self.assertFalse(self.control.snapshot()['armed'])

    def test_late_command_cannot_restore_enable(self):
        generation = self.control.arm(OWNER)
        self.clock.value += 0.6
        with self.assertRaises(ValueError): self.control.command(OWNER, generation, 9, 'forward')
        self.assertFalse(self.control.snapshot()['armed'])

    def test_stop_invalidates_inflight_generation(self):
        old = self.control.arm(OWNER)
        self.control.stop()
        fresh = self.control.arm(OWNER)
        self.assertNotEqual(old, fresh)
        with self.assertRaises(ValueError): self.control.command(OWNER, old, 99, 'forward')
        self.assertEqual(self.control.snapshot()['action'], 'neutral')

    def test_single_owner_and_no_rearm_while_active(self):
        self.control.arm(OWNER)
        for owner in [OWNER, 'b' * 32]:
            with self.assertRaises(ValueError): self.control.arm(owner)

    def test_other_browser_cannot_command(self):
        generation = self.control.arm(OWNER)
        with self.assertRaises(ValueError): self.control.command('b'*32, generation, 1, 'forward')

    def test_sequences_and_types(self):
        generation = self.control.arm(OWNER)
        self.control.command(OWNER, generation, 3, 'neutral')
        for sequence in [2, 3, True, 4.5, '5', 2147483648]:
            with self.assertRaises(ValueError): self.control.command(OWNER, generation, sequence, 'forward')

    def test_no_sideways_or_spin_commands(self):
        generation = self.control.arm(OWNER)
        for action in ['left', 'right', 'spin', 'sideways', 'shell']:
            with self.assertRaises(ValueError): self.control.command(OWNER, generation, 1, action)

    def test_heartbeat_cannot_extend_maximum_arm_period(self):
        generation = self.control.arm(OWNER)
        for sequence in range(1, 150):
            self.clock.value = 100.0 + sequence * 0.2
            self.control.command(OWNER, generation, sequence, 'neutral')
        self.clock.value = 130.0
        self.assertFalse(self.control.snapshot()['armed'])

    def test_reconnect_does_not_arm(self):
        generation = self.control.arm(OWNER)
        self.control.command(OWNER, generation, 1, 'reverse')
        self.clock.value += 1
        self.control.snapshot()
        self.clock.value += 10
        self.assertFalse(self.control.snapshot()['armed'])

    def test_invalid_owner(self):
        for owner in ['', 'x'*32, None, 'a'*33]:
            with self.assertRaises(ValueError): self.control.arm(owner)


class DataTests(unittest.TestCase):
    def setUp(self): self.clock = Clock(); self.app = server.Dashboard(clock=self.clock)

    def test_preview_is_explicit_not_fake_live(self):
        state = self.app.status()
        self.assertEqual(state['mode'], 'preview')
        self.assertFalse(state['motor_output'])
        self.assertFalse(state['scan']['available'])
        self.assertFalse(state['cameras']['rgb']['available'])

    def test_stale_images_not_served(self):
        self.app.set_frame('rgb', b'jpeg', self.clock(), 'optical', 10.0, 5)
        self.assertEqual(self.app.frame('rgb'), b'jpeg')
        self.clock.value += 2
        self.assertIsNone(self.app.frame('rgb'))
        self.assertFalse(self.app.status()['cameras']['rgb']['available'])

    def test_only_latest_image_retained(self):
        for sequence in range(100):
            self.app.set_frame('rgb', b'jpeg', self.clock(), 'frame', 1.0, sequence)
        self.assertEqual(len(self.app.frames), 1)
        self.assertEqual(self.app.status()['cameras']['rgb']['sequence'], 99)

    def scan(self, values):
        return Holder(range_min=0.1, range_max=10.0, angle_min=0.0, angle_increment=0.1,
                      header=Holder(frame_id='laser'), ranges=values)

    def test_scan_finite_in_physical_message_limits(self):
        result = server.scan_summary(self.scan([float('nan'), float('inf'), -1, 0.05, 1.0, 20]))
        self.assertEqual(result['samples'], 6)
        self.assertEqual(result['valid_samples'], 1)
        self.assertEqual(result['minimum_m'], 1.0)
        self.assertEqual(result['frame'], 'laser')

    def test_scan_empty_no_invented_distance(self):
        self.assertIsNone(server.scan_summary(self.scan([]))['minimum_m'])

    def test_scan_is_bounded(self):
        result = server.scan_summary(self.scan([1.0]*10000))
        self.assertLessEqual(len(result['points']), 240)

    def test_scan_invalid_geometry_rejected(self):
        for field, value in [('angle_increment',0),('range_max',float('inf')),('range_min',-1)]:
            scan = self.scan([1.0]); setattr(scan,field,value)
            with self.assertRaises(ValueError): server.scan_summary(scan)

    def test_scan_stale(self):
        self.app.scan = server.scan_summary(self.scan([1.0]))
        self.app.scan_time = self.clock()
        self.assertTrue(self.app.status()['scan']['available'])
        self.clock.value += 2
        self.assertFalse(self.app.status()['scan']['available'])

    def test_no_ros_publish_shell_or_dynamic_topic_endpoint(self):
        with open(server.__file__.replace('.pyc','.py'), 'r') as handle: tree = ast.parse(handle.read())
        forbidden = {'Publisher','Popen','system','execv','execve','call','check_call'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, forbidden)

    def test_cli_cannot_select_live_motors_or_lan_bind(self):
        for argv in [['--live'], ['--host','0.0.0.0'], ['--fps','nan'],['--fps','30'],['--port','22']]:
            with self.assertRaises(SystemExit): server.parse_args(argv)


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.app = server.Dashboard()
        self.server = server.LocalServer(('127.0.0.1',0),self.app)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(2)

    def fetch(self, path, body=None, changes=None, method=None):
        connection = http_client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        headers = {'Host':'127.0.0.1:%d'%self.port}
        if body is not None:
            headers.update({'Origin':'http://127.0.0.1:%d'%self.port,
                            'Content-Type':'application/json', 'X-Dashboard-Key':self.app.key})
            body = json.dumps(body)
        headers.update(changes or {})
        connection.request(method or ('POST' if body is not None else 'GET'),path,body,headers)
        response = connection.getresponse()
        code, payload, result_headers = response.status, response.read(), dict(response.getheaders())
        connection.close()
        return code,payload,result_headers

    def test_static_and_no_external_assets(self):
        for path in ['/','/style.css','/app.js']:
            code,body,headers = self.fetch(path)
            self.assertEqual(code,200)
            self.assertEqual(headers['Cache-Control'],'no-store')
            self.assertIn('frame-ancestors',headers['Content-Security-Policy'])
            self.assertNotIn(b'https://',body)

    def test_status_and_bootstrap(self):
        code,body,_ = self.fetch('/api/status')
        self.assertEqual(code,200)
        self.assertFalse(json.loads(body.decode('utf8'))['motor_output'])
        code,body,_ = self.fetch('/api/bootstrap')
        self.assertEqual(json.loads(body.decode('utf8'))['key'], self.app.key)

    def test_foreign_host_and_dns_rebinding_denied(self):
        self.assertEqual(self.fetch('/api/status',changes={'Host':'attacker.example'})[0],403)

    def test_mutations_need_origin_and_key(self):
        for headers in [{'Origin':'https://attacker.example'}, {'X-Dashboard-Key':'bad'}, {'Origin':''}]:
            self.assertEqual(self.fetch('/api/rehearsal/arm',{'owner':OWNER},headers)[0],403)
        self.assertFalse(self.app.control.snapshot()['armed'])

    def test_get_cannot_arm(self):
        self.assertEqual(self.fetch('/api/rehearsal/arm')[0],404)
        self.assertFalse(self.app.control.snapshot()['armed'])

    def test_missing_camera_is_not_a_replayed_image(self):
        self.assertEqual(self.fetch('/api/frame/rgb')[0],503)

    def test_no_file_traversal_or_motor_endpoint(self):
        for path in ['/../server.py','/control.py','/api/cmd_vel','/api/launch','/api/shutdown']:
            self.assertEqual(self.fetch(path)[0],404)
            self.assertEqual(self.fetch(path,{})[0],404)

    def test_full_rehearsal_and_stop(self):
        code,body,_ = self.fetch('/api/rehearsal/arm',{'owner':OWNER})
        self.assertEqual(code,200)
        generation = json.loads(body.decode('utf8'))['generation']
        command = {'owner':OWNER,'generation':generation,'sequence':1,'action':'forward'}
        self.assertEqual(self.fetch('/api/rehearsal/command',command)[0],200)
        self.assertEqual(self.app.control.snapshot()['action'],'forward')
        self.assertEqual(self.fetch('/api/rehearsal/stop',{})[0],200)
        command['sequence'] = 2
        self.assertEqual(self.fetch('/api/rehearsal/command',command)[0],400)
        self.assertFalse(self.app.control.snapshot()['armed'])

    def test_request_size_and_content_type(self):
        self.assertEqual(self.fetch('/api/rehearsal/arm',{'owner':'a'*5000})[0],400)
        self.assertEqual(self.fetch('/api/rehearsal/arm',{}, {'Content-Type':'text/plain'})[0],415)


if __name__ == '__main__': unittest.main()
