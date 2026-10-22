"""Offline web gate, fake lifecycle and loopback HTTP checks; never real ROS."""
import ast
import contextlib
import io
import json
import os
import sys
import threading
import types
import unittest
from unittest import mock
import http.client

import server
import web_crawl as web

OWNER = 'a' * 32


class Clock:
    def __init__(self): self.now = 100.0
    def __call__(self): return self.now
    def wait(self, seconds): self.now += seconds


class GateTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.issue = None
        self.sent = []
        self.gate = web.WebGate(lambda moving: self.issue,
                               lambda value: self.sent.append((self.clock(), value)), self.clock)

    def prepare(self): return self.gate.prepare(OWNER)
    def command(self, token, seq=1, action='forward', owner=OWNER):
        return self.gate.command(owner, token, seq, action)

    def test_no_motor_on_prepare_or_heartbeat(self):
        token = self.prepare()
        self.command(token, action='heartbeat')
        self.assertEqual(self.sent, [])
        self.assertFalse(self.gate.run_once(self.clock.wait, lambda since: False))

    def test_one_owner_and_only_one_prepare(self):
        self.prepare()
        for owner in (OWNER, 'b' * 32):
            with self.assertRaises(ValueError): self.gate.prepare(owner)

    def test_invalid_owner_or_missing_readiness(self):
        for owner in ('', None, 'x'*32, 'a'*33):
            with self.assertRaises(ValueError): self.gate.prepare(owner)
        self.issue = 'Stale odometry'
        with self.assertRaises(ValueError): self.prepare()
        self.assertFalse(self.gate.snapshot()['ready'])

    def test_wrong_owner_token_and_sequence(self):
        token = self.prepare()
        for owner, value, seq in [('b'*32, token, 1), (OWNER, 'bad', 1),
                                  (OWNER, token, True), (OWNER, token, 0),
                                  (OWNER, token, 1.1), (OWNER, token, 2147483648)]:
            with self.assertRaises(ValueError): self.command(value, seq, 'heartbeat', owner)
        self.command(token, 2, 'heartbeat')
        for seq in (1, 2):
            with self.assertRaises(ValueError): self.command(token, seq)

    def test_no_reverse_steering_or_tuning(self):
        token = self.prepare()
        for action in ('reverse', 'forward_left', 'forward_right', 'left', 'shell', None, {}):
            with self.assertRaises(ValueError): self.command(token, action=action)
        self.assertEqual(self.sent, [])

    def test_stop_retires_token_and_delayed_prepare(self):
        token = self.prepare()
        self.gate.stop()
        with self.assertRaises(ValueError): self.command(token)
        with self.assertRaises(ValueError): self.prepare()
        other = web.WebGate(lambda moving: None, self.sent.append, self.clock)
        other.stop()
        with self.assertRaises(ValueError): other.prepare(OWNER)

    def test_expired_heartbeat_cannot_restore(self):
        token = self.prepare()
        self.clock.wait(web.LEASE_SECONDS + .001)
        with self.assertRaises(ValueError): self.command(token, action='heartbeat')
        self.assertEqual(self.gate.snapshot()['state'], 'spent')

    def test_prepare_hard_expiry_despite_heartbeats(self):
        token = self.prepare()
        for seq in range(1, 25):
            self.clock.wait(.2)
            self.command(token, seq, 'heartbeat')
        self.clock.wait(.21)
        with self.assertRaises(ValueError): self.command(token, 25)
        self.assertEqual(self.sent, [])

    def test_terminal_permit_expiry_before_prepare_and_after_prepare(self):
        self.clock.wait(60.0)
        with self.assertRaises(ValueError): self.prepare()
        self.setUp()
        self.clock.wait(59.9)
        token = self.prepare()
        self.clock.wait(.11)
        with self.assertRaises(ValueError): self.command(token)

    def test_readiness_rechecked_at_start(self):
        token = self.prepare()
        self.issue = 'Camera stale'
        with self.assertRaises(ValueError): self.command(token)
        self.assertEqual(self.gate.snapshot()['state'], 'spent')

    def test_duplicate_start_cannot_queue_second_pulse(self):
        token = self.prepare()
        self.command(token)
        with self.assertRaises(ValueError): self.command(token, 2)
        self.assertEqual(self.sent, [])

    def test_stop_before_worker_prevents_nonzero(self):
        token = self.prepare()
        self.command(token)
        self.gate.stop()
        self.assertFalse(self.gate.run_once(self.clock.wait, lambda since: True))
        self.assertEqual(self.sent, [])

    def test_delayed_worker_does_not_replay(self):
        token = self.prepare()
        self.command(token)
        self.clock.wait(.5)
        self.assertFalse(self.gate.run_once(self.clock.wait, lambda since: True))
        self.assertEqual(self.sent, [])

    def run_trial(self, wait=None, stopped=True):
        token = self.prepare()
        self.command(token)
        sequence = [1]
        def progress(seconds):
            self.clock.wait(seconds)
            if self.gate.state in ('queued', 'running') and not self.gate.cancelled.is_set():
                sequence[0] += 1
                self.command(token, sequence[0], 'heartbeat')
        with contextlib.redirect_stdout(io.StringIO()):
            self.gate.run_once(wait or progress, lambda since: stopped)

    def assert_zeros(self):
        self.assertGreaterEqual(len([v for t, v in self.sent if v == 0]), 20)
        self.assertEqual(self.sent[-1][1], 0)

    def test_fixed_pulse_and_repeated_zeros_one_use(self):
        self.run_trial()
        self.assertTrue(any(v == .03 for t, v in self.sent))
        self.assertTrue(all(v in (0, .03) for t, v in self.sent))
        first = self.sent[0][0]
        self.assertTrue(all(t-first < .4 for t, v in self.sent if v))
        self.assert_zeros()
        self.assertTrue(self.gate.snapshot()['stop_feedback'])
        with self.assertRaises(ValueError): self.prepare()
        count = len(self.sent)
        self.assertFalse(self.gate.run_once(self.clock.wait, lambda since: True))
        self.assertEqual(len(self.sent), count)

    def test_lost_browser_heartbeat_aborts_and_zeros(self):
        self.run_trial(wait=self.clock.wait)
        self.assert_zeros()
        self.assertIn('heartbeat', self.gate.reason)

    def test_release_aborts_and_zeros(self):
        def wait(seconds):
            self.clock.wait(seconds)
            if self.clock() >= 100.04: self.gate.stop('Released')
        self.run_trial(wait=wait)
        self.assert_zeros()
        self.assertTrue(all(t < 100.05 for t, v in self.sent if v))

    def test_odom_graph_camera_failure_aborts(self):
        for issue in ('Stale odometry', 'Competing publisher', 'Camera stale'):
            self.setUp()
            def wait(seconds):
                self.clock.wait(seconds)
                self.issue = issue
            self.run_trial(wait=wait)
            self.assert_zeros()
            self.assertEqual(self.gate.reason, issue)

    def test_scheduling_gap_no_catchup(self):
        def wait(seconds): self.clock.wait(.3 if seconds == .02 else seconds)
        self.run_trial(wait=wait)
        self.assertEqual(len([v for t, v in self.sent if v]), 1)
        self.assert_zeros()

    def test_delayed_start_cannot_extend_original_deadline(self):
        token = self.prepare()
        self.command(token)
        self.clock.wait(.25)
        self.command(token, 2, 'heartbeat')
        def wait(seconds):
            self.clock.wait(seconds)
        with contextlib.redirect_stdout(io.StringIO()):
            self.gate.run_once(wait, lambda since: False)
        self.assertTrue(all(t < 100.4 for t, v in self.sent if v))
        self.assert_zeros()

    def test_publish_exception_still_zeros_and_spends(self):
        def emit(value):
            self.sent.append((self.clock(), value))
            if value: raise RuntimeError('Fake transport failure')
        self.gate.emit = emit
        with self.assertRaises(RuntimeError): self.run_trial()
        self.assert_zeros()
        self.assertEqual(self.gate.state, 'spent')
        self.assertFalse(self.gate.stop_feedback)

    def test_stop_is_serialized_with_positive_publication(self):
        token = self.prepare()
        self.command(token)
        self.gate.stop()
        with self.assertRaises(ValueError): self.gate.guarded_emit(.03)
        self.gate.guarded_emit(0)
        self.assertEqual([v for t, v in self.sent], [0])

    def test_missing_stop_feedback_not_claimed_verified(self):
        self.run_trial(stopped=False)
        self.assertFalse(self.gate.snapshot()['stop_feedback'])


class EntryTests(unittest.TestCase):
    def test_default_is_offline(self):
        with mock.patch.dict(sys.modules, {'rospy': None}), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(web.main([]), 0)
        self.assertIn('OFFLINE ONLY', output.getvalue())

    def test_check_delegates_subscription_only(self):
        with mock.patch.object(web.crawl, 'main', return_value=0) as check:
            self.assertEqual(web.main(['--check']), 0)
        check.assert_called_once_with(['--check'])

    def test_no_tuning_flags(self):
        for args in (['--speed','1'], ['--duration','4'], ['--topic','/cmd_vel'],
                     ['--port','80'], ['--live','--check'], ['--host','0.0.0.0']):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): web.parse_args(args)

    def test_python36_grammar(self):
        for name in ('web_crawl.py', 'server.py'):
            with open(os.path.join(os.path.dirname(__file__), name), encoding='utf-8') as file:
                ast.parse(file.read(), feature_version=(3,6))

    def exercise(self, confirm=True, simulated=False, ready=True):
        app = web.WebDashboard()
        app.set_frame('rgb', b'jpeg', app.clock(), 'optical', 100, 1)
        ros = types.ModuleType('rospy')
        ros.get_param = mock.Mock(return_value=simulated)
        ros.is_shutdown = lambda: False
        pub = mock.Mock()
        pub.get_num_connections.return_value = 1
        ros.Publisher = mock.Mock(return_value=pub)
        messages = types.ModuleType('geometry_msgs.msg')
        messages.Twist = mock.Mock
        feedback = mock.Mock()
        feedback.problem.return_value = None if ready else 'Not ready'
        http = mock.Mock()
        http.handle_request.side_effect = app.closed.set
        # Refusal case skips wait loop, without sleeping or fake network access.
        if not ready: app.closed.set()
        modules = {'rospy':ros, 'rosgraph':types.ModuleType('rosgraph'),
                   'geometry_msgs':types.ModuleType('geometry_msgs'), 'geometry_msgs.msg':messages}
        with mock.patch.dict(sys.modules, modules), \
                mock.patch.object(web, 'WebDashboard', return_value=app), \
                mock.patch.object(web.server, 'LocalServer', return_value=http), \
                mock.patch.object(web.server, 'RosReader') as reader, \
                mock.patch.object(web.crawl, 'Feedback', return_value=feedback), \
                mock.patch.object(web.crawl, 'RosFeedback') as monitor, \
                mock.patch.object(web.crawl, 'confirm', return_value=confirm), \
                mock.patch.object(web.signal, 'signal'), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = web.main(['--live'])
        return result, ros, pub, http, reader, monitor

    def test_declined_terminal_confirmation_no_publisher(self):
        result, ros, pub, http, reader, monitor = self.exercise(confirm=False)
        self.assertEqual(result, 0)
        ros.Publisher.assert_not_called()
        http.server_close.assert_called_once()

    def test_simulated_time_no_publisher(self):
        result, ros, pub, http, reader, monitor = self.exercise(simulated=True)
        self.assertEqual(result, 2)
        ros.Publisher.assert_not_called()

    def test_unready_no_publisher(self):
        result, ros, pub, http, reader, monitor = self.exercise(ready=False)
        self.assertEqual(result, 2)
        ros.Publisher.assert_not_called()

    def test_confirmed_startup_without_browser_never_publishes(self):
        result, ros, pub, http, reader, monitor = self.exercise()
        self.assertEqual(result, 0)
        ros.Publisher.assert_called_once_with(web.crawl.COMMAND, mock.ANY,
                                             queue_size=1, latch=False, tcp_nodelay=True)
        pub.publish.assert_not_called()
        pub.unregister.assert_called_once()
        reader.return_value.close.assert_called_once()


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.app = web.WebDashboard()
        self.sent = []
        self.app.gate = web.WebGate(lambda moving: None, self.sent.append)
        self.http = server.LocalServer(('127.0.0.1', 0), self.app, web.WebHandler)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.http.shutdown(); self.http.server_close(); self.thread.join(2)

    def fetch(self, path, body=None, headers=None):
        port = self.http.server_address[1]
        connection = http.client.HTTPConnection('127.0.0.1', port, timeout=3)
        extra = {'Host':'127.0.0.1:%d'%port}
        if body is not None:
            extra.update({'Origin':'http://127.0.0.1:%d'%port, 'Content-Type':'application/json',
                          'X-Dashboard-Key':self.http.app.key})
        extra.update(headers or {})
        connection.request('POST' if body is not None else 'GET', path,
                           json.dumps(body) if body is not None else None, extra)
        response = connection.getresponse()
        result = response.status, response.read()
        connection.close()
        return result

    def test_live_page_assets_and_status(self):
        for path in ('/', '/style.css', '/web_crawl.js'):
            code, body = self.fetch(path)
            self.assertEqual(code, 200)
            self.assertNotIn(b'https://', body)
        code, body = self.fetch('/api/status')
        data = json.loads(body)
        self.assertTrue(data['motor_output'])
        self.assertEqual(data['mode'], 'web_crawl_one_shot')
        self.assertIn('crawl', data)

    def test_same_origin_host_key_content_guards(self):
        for headers, expected in (({'Origin':'https://evil.example'},403),
                                   ({'Origin':''},403), ({'Host':'evil.example'},403),
                                   ({'X-Dashboard-Key':'wrong'},403),
                                   ({'Content-Type':'text/plain'},415)):
            self.assertEqual(self.fetch('/api/crawl/prepare', {'owner':OWNER}, headers)[0], expected)
        self.assertEqual(self.app.gate.state, 'available')
        self.assertEqual(self.sent, [])

    def test_get_and_unrelated_operations_cannot_move(self):
        for path in ('/api/crawl/prepare', '/api/crawl/command'):
            self.assertEqual(self.fetch(path)[0], 404)
        for path in ('/api/rehearsal/arm', '/api/cmd_vel', '/api/launch', '/api/shutdown'):
            self.assertEqual(self.fetch(path,{})[0], 404)
        self.assertEqual(self.sent, [])

    def test_http_prepare_start_stop_no_worker_no_movement(self):
        code, body = self.fetch('/api/crawl/prepare', {'owner':OWNER})
        self.assertEqual(code, 200)
        token = json.loads(body)['token']
        request = {'owner':OWNER, 'token':token, 'sequence':1, 'action':'forward'}
        self.assertEqual(self.fetch('/api/crawl/command', request)[0],200)
        request['sequence'] = 2
        self.assertEqual(self.fetch('/api/crawl/command', request)[0],400)
        self.assertEqual(self.fetch('/api/crawl/stop',{})[0],200)
        request['sequence'] = 3
        self.assertEqual(self.fetch('/api/crawl/command', request)[0],400)
        self.assertEqual(self.sent, [])

    def test_original_default_server_has_no_crawl_routes(self):
        original = self.app
        self.http.app = server.Dashboard()
        self.http.RequestHandlerClass = server.Handler
        self.assertFalse(json.loads(self.fetch('/api/status')[1])['motor_output'])
        self.assertEqual(self.fetch('/api/crawl/prepare',{'owner':OWNER})[0],404)
        self.assertEqual(self.fetch('/api/crawl/command',{})[0],404)
        self.http.app = original


if __name__ == '__main__': unittest.main()
