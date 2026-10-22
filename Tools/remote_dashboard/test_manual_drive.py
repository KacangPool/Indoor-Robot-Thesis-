"""Fake clock/ROS and loopback only; no physical robot access or output."""
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
import manual_drive as drive

OWNER = 'a' * 32


class Clock:
    def __init__(self): self.value = 100.0
    def __call__(self): return self.value
    def wait(self, seconds): self.value += seconds


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.issue = None
        self.stopped = True
        self.sent = []
        self.control = drive.ManualForward(lambda moving: self.issue, self.emit,
                                           lambda since: self.stopped, self.clock)

    def emit(self, value): self.sent.append((self.clock(), value))
    def arm(self): return self.control.arm(OWNER)
    def command(self, token, sequence=1, action='forward', owner=OWNER):
        return self.control.command(owner, token, sequence, action)
    def finish_stop(self):
        for unused in range(105):
            self.clock.wait(.02); self.control.tick()

    def test_starts_disabled_no_output(self):
        self.control.tick()
        self.assertFalse(self.control.snapshot()['armed'])
        self.assertEqual(self.sent, [])

    def test_arm_and_idle_heartbeat_publish_nothing(self):
        token = self.arm()
        self.command(token, action='neutral'); self.control.tick()
        self.assertEqual(self.sent, [])

    def test_slow_forward_only_on_worker_tick(self):
        token = self.arm(); self.command(token)
        self.assertEqual(self.sent, [])
        self.control.tick()
        self.assertEqual([v for t,v in self.sent], [.03])

    def test_invalid_owner(self):
        for owner in (None, '', 'x'*32, 'a'*33):
            with self.assertRaises(ValueError): self.control.arm(owner)

    def test_wrong_owner_generation_and_sequence(self):
        token = self.arm()
        for owner,value,seq in [('b'*32, token,1),(OWNER,'wrong',1),(OWNER,token,True),
                               (OWNER,token,0),(OWNER,token,1.1),(OWNER,token,2147483648)]:
            with self.assertRaises(ValueError): self.command(value,seq,'forward',owner)
        self.command(token,3,'neutral')
        for seq in (2,3):
            with self.assertRaises(ValueError): self.command(token,seq)

    def test_other_browser_cannot_arm(self):
        self.arm()
        for owner in (OWNER,'b'*32):
            with self.assertRaises(ValueError): self.control.arm(owner)

    def test_no_reverse_steering_or_arbitrary_actions(self):
        token = self.arm()
        for action in ('reverse','forward_left','forward_right','spin','shell',None,{}):
            with self.assertRaises(ValueError): self.command(token,action=action)
        self.assertEqual(self.sent, [])

    def test_stale_lease_before_start_cannot_resume(self):
        token = self.arm(); self.clock.wait(.36)
        with self.assertRaises(ValueError): self.command(token)
        self.control.tick()
        self.assertEqual(self.sent, [])

    def test_idle_has_no_terminal_countdown(self):
        token = self.arm()
        for seq in range(1,1301):
            self.clock.wait(.05)
            self.command(token,seq,'neutral'); self.control.tick()
        self.assertTrue(self.control.snapshot()['armed'])
        self.assertEqual(self.sent, [])

    def test_release_stops_and_retires_old_token(self):
        token = self.arm(); self.command(token); self.control.tick()
        self.control.stop('Released'); self.control.tick()
        self.assertEqual(self.sent[-1][1],0)
        with self.assertRaises(ValueError): self.command(token,2)
        with self.assertRaises(ValueError): self.arm()

    def test_normal_reenable_without_process_restart(self):
        first = self.arm(); self.command(first); self.control.tick()
        self.control.stop(); self.finish_stop()
        second = self.arm()
        self.assertNotEqual(first,second)
        with self.assertRaises(ValueError): self.command(first,999)
        self.command(second); self.control.tick()
        self.assertEqual([v for t,v in self.sent if v], [.03,.03])

    def test_reenable_requires_post_stop_feedback(self):
        token = self.arm(); self.command(token); self.control.tick()
        self.control.stop(); self.stopped = False; self.finish_stop()
        self.assertFalse(self.control.snapshot()['ready'])
        with self.assertRaises(ValueError): self.arm()
        self.stopped = True
        self.assertTrue(self.control.snapshot()['ready'])

    def test_no_rearm_after_feedback_loss(self):
        token = self.arm(); self.command(token); self.control.tick()
        self.issue = 'Odometry stale'; self.control.tick()
        self.finish_stop()
        with self.assertRaises(ValueError): self.arm()
        self.assertEqual(self.sent[-1][1],0)

    def test_neutral_after_forward_retires_generation(self):
        token = self.arm(); self.command(token); self.control.tick()
        self.command(token,2,'neutral'); self.control.tick()
        self.assertEqual(self.sent[-1][1],0)
        with self.assertRaises(ValueError): self.command(token,3)

    def test_two_second_hold_cannot_be_extended_by_heartbeats(self):
        token = self.arm(); self.command(token); self.control.tick()
        for seq in range(2,41):
            self.clock.wait(.05); self.command(token,seq); self.control.tick()
        self.clock.wait(.06); self.control.tick()
        self.assertFalse(self.control.snapshot()['armed'])
        self.assertTrue(all(t < 102.0 for t,v in self.sent if v))
        self.assertEqual(self.sent[-1][1],0)
        with self.assertRaises(ValueError): self.command(token,99)

    def test_missing_browser_heartbeat_sends_zeros(self):
        token = self.arm(); self.command(token); self.control.tick()
        for unused in range(20): self.clock.wait(.02); self.control.tick()
        self.assertFalse(self.control.snapshot()['armed'])
        self.assertEqual(self.sent[-1][1],0)
        with self.assertRaises(ValueError): self.command(token,2)

    def test_worker_gap_never_catches_up(self):
        token = self.arm(); self.command(token); self.control.tick()
        self.clock.wait(.3); self.command(token,2); self.control.tick()
        self.assertEqual(len([v for t,v in self.sent if v]),1)
        self.assertIn('scheduling gap', self.control.reason)
        self.assertEqual(self.sent[-1][1],0)

    def test_slow_health_cannot_send_late_positive(self):
        token = self.arm(); self.command(token)
        def health(moving): self.clock.wait(.3)
        self.control.health = health
        self.control.tick()
        self.assertTrue(all(v == 0 for t,v in self.sent))

    def test_readiness_rechecked_before_hold(self):
        token = self.arm(); self.issue = 'Wrong graph'
        with self.assertRaises(ValueError): self.command(token)
        self.assertEqual(self.sent, [])

    def test_stale_camera_graph_ros_or_odom_stops(self):
        for issue in ('Camera stale','Graph stale','Competing publisher','ROS closing','Wrong direction'):
            self.setUp(); token = self.arm(); self.command(token); self.control.tick()
            self.issue = issue; self.clock.wait(.02); self.control.tick()
            self.assertEqual(self.sent[-1][1],0)
            self.assertFalse(self.control.snapshot()['armed'])

    def test_zero_cleanup_repeated_for_two_seconds(self):
        token = self.arm(); self.command(token); self.control.tick(); self.control.stop()
        self.finish_stop()
        self.assertGreaterEqual(len([v for t,v in self.sent if v == 0]),19)
        self.assertEqual(self.control.stage,'disabled')

    def test_stop_before_any_positive_has_no_motion(self):
        token = self.arm(); self.command(token); self.control.stop(); self.control.tick()
        self.assertTrue(all(v == 0 for t,v in self.sent))

    def test_repeated_stop_does_not_postpone_cleanup(self):
        token = self.arm(); self.command(token); self.control.tick(); self.control.stop()
        started = self.control.stop_at
        for unused in range(110):
            self.clock.wait(.02); self.control.stop(); self.control.tick()
        self.assertEqual(self.control.stop_at,started)
        self.assertEqual(self.control.stage,'disabled')

    def test_positive_publish_exception_attempts_zero(self):
        def emit(value):
            self.emit(value)
            if value: raise RuntimeError('Fake transport failure')
        self.control.emit = emit
        token = self.arm(); self.command(token); self.control.tick()
        self.assertEqual([v for t,v in self.sent], [.03,0])
        self.assertEqual(self.control.stage,'stopping')

    def test_zero_publication_failure_blocks_reenable(self):
        token = self.arm(); self.command(token); self.control.tick()
        def emit(value):
            self.emit(value)
            if value == 0: raise RuntimeError('Fake zero failure')
        self.control.emit = emit
        self.control.stop(); self.finish_stop()
        self.assertGreater(self.control.zero_failures,0)
        with self.assertRaises(ValueError): self.arm()

    def test_status_only_changes_expired_intent_never_publishes(self):
        token = self.arm(); self.command(token); self.clock.wait(.36)
        self.control.snapshot()
        self.assertEqual(self.sent, [])


class IntegrationTests(unittest.TestCase):
    def test_cli_explicit_opt_in_only(self):
        self.assertFalse(server.parse_args([]).drive)
        self.assertFalse(server.parse_args(['--ros']).drive)
        self.assertTrue(server.parse_args(['--ros','--drive']).drive)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): server.parse_args(['--drive'])

    def test_dashboard_status_releases_image_lock_before_control(self):
        app = server.Dashboard()
        class Control:
            def snapshot(inner):
                self.assertFalse(app.lock._is_owned())
                return {'armed':False}
        app.control = Control()
        self.assertFalse(app.status()['control']['armed'])

    def test_python36_runtime_syntax(self):
        for name in ('manual_drive.py','server.py'):
            with open(os.path.join(os.path.dirname(__file__),name),encoding='utf8') as handle:
                ast.parse(handle.read(),feature_version=(3,6))

    def adapter(self, simulated=False):
        app = server.Dashboard(ros=True)
        app.set_frame('rgb', b'jpeg', app.clock(), 'optical',1,1)
        rospy = types.ModuleType('rospy')
        rospy.get_param = lambda name,default: simulated
        rospy.is_shutdown = lambda: False
        publisher = mock.Mock(); publisher.get_num_connections.return_value = 1
        rospy.Publisher = mock.Mock(return_value=publisher)
        messages = types.ModuleType('geometry_msgs.msg')
        class Vector:
            x = y = z = 0.0
        class Twist:
            def __init__(self): self.linear,self.angular = Vector(),Vector()
        messages.Twist = Twist
        feedback = mock.Mock(); feedback.problem.return_value = None; feedback.stopped_since.return_value = True
        feedback.lock = threading.RLock(); feedback.samples = []
        modules = {'rosgraph':types.ModuleType('rosgraph'),'geometry_msgs':types.ModuleType('geometry_msgs'),'geometry_msgs.msg':messages}
        with mock.patch.dict(sys.modules,modules), \
                mock.patch.object(drive.crawl,'RosFeedback') as monitor, \
                mock.patch.object(drive,'ManualFeedback',return_value=feedback), \
                mock.patch.object(drive.threading,'Thread') as thread:
            thread.return_value.is_alive.return_value = False
            adapter = drive.RosManualDrive(app,rospy)
        return app,rospy,publisher,adapter,feedback,monitor,thread

    def test_adapter_start_creates_no_motion(self):
        app,ros,pub,adapter,feedback,monitor,thread = self.adapter()
        pub.publish.assert_not_called()
        self.assertIsNone(adapter.control.health(False))
        adapter.close(); pub.unregister.assert_called_once()

    def test_adapter_only_fixed_forward_and_zeros(self):
        app,ros,pub,adapter,feedback,monitor,thread = self.adapter()
        token = adapter.control.arm(OWNER); adapter.control.command(OWNER,token,1,'forward',motion=1); adapter.control.tick()
        adapter.control.stop(); adapter.control.tick()
        values = [call.args[0] for call in pub.publish.call_args_list]
        self.assertEqual([m.linear.x for m in values],[.03,0])
        for message in values:
            self.assertEqual((message.linear.y,message.linear.z,message.angular.x,message.angular.y,message.angular.z),(0,0,0,0,0))
        adapter.close()

    def test_adapter_checks_camera_controller_feedback_and_worker(self):
        app,ros,pub,adapter,feedback,monitor,thread = self.adapter()
        app.frames.clear(); self.assertIn('camera',adapter.control.health(False))
        app.set_frame('rgb',b'jpeg',app.clock(),'optical',1,1)
        pub.get_num_connections.return_value = 2; self.assertIn('unique',adapter.control.health(False))
        pub.get_num_connections.return_value = 1
        feedback.problem.return_value = 'Stale odometry'; self.assertEqual(adapter.control.health(False),'Stale odometry')
        feedback.problem.return_value = None
        adapter.failed = True; self.assertIn('worker failed',adapter.control.health(False))
        adapter.close()

    def test_simulated_time_refused_before_publisher(self):
        with self.assertRaises(ValueError): self.adapter(simulated=True)


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.sent = []
        self.app = server.Dashboard(ros=True)
        self.app.drive = object()
        self.app.mode = 'ros_manual_forward'
        self.app.control = drive.ManualForward(lambda moving:None,self.sent.append,lambda since:True)
        self.http = server.LocalServer(('127.0.0.1',0),self.app)
        self.thread = threading.Thread(target=self.http.serve_forever,daemon=True); self.thread.start()
    def tearDown(self):
        self.http.shutdown(); self.http.server_close(); self.thread.join(2)
    def fetch(self,path,body=None,extra=None):
        port = self.http.server_address[1]
        connection = http.client.HTTPConnection('127.0.0.1',port,timeout=3)
        headers = {'Host':'127.0.0.1:%d'%port}
        if body is not None: headers.update({'Origin':'http://127.0.0.1:%d'%port,'Content-Type':'application/json','X-Dashboard-Key':self.app.key})
        headers.update(extra or {})
        connection.request('POST' if body is not None else 'GET',path,json.dumps(body) if body is not None else None,headers)
        response=connection.getresponse(); result=response.status,response.read(); connection.close(); return result
    def test_live_mode_is_explicit_in_status(self):
        status=json.loads(self.fetch('/api/status')[1]); self.assertTrue(status['motor_output']); self.assertEqual(status['mode'],'ros_manual_forward')
        self.assertFalse(status['control']['armed'])
    def test_get_rehearsal_and_arbitrary_endpoints_cannot_drive(self):
        self.assertEqual(self.fetch('/api/drive/arm')[0],404)
        for path in ('/api/rehearsal/arm','/api/cmd_vel','/api/launch','/api/drive/reverse'):
            self.assertEqual(self.fetch(path,{})[0],404)
        self.assertEqual(self.sent,[])
    def test_origin_host_and_key_enforced(self):
        for extra in ({'Origin':'http://evil.example'},{'Origin':''},{'Host':'evil.example'},{'X-Dashboard-Key':'wrong'}):
            self.assertEqual(self.fetch('/api/drive/arm',{'owner':OWNER},extra)[0],403)
        self.assertFalse(self.app.control.snapshot()['armed'])
    def test_arm_command_stop_keeps_publication_in_worker(self):
        code,body=self.fetch('/api/drive/arm',{'owner':OWNER}); self.assertEqual(code,200)
        token=json.loads(body)['generation']; command={'owner':OWNER,'generation':token,'sequence':1,'action':'forward'}
        self.assertEqual(self.fetch('/api/drive/command',command)[0],200); self.assertEqual(self.sent,[])
        self.app.control.tick(); self.assertEqual(self.sent,[.03])
        self.assertEqual(self.fetch('/api/drive/stop',{})[0],200); self.app.control.tick(); self.assertEqual(self.sent[-1],0)
        command['sequence']=2; self.assertEqual(self.fetch('/api/drive/command',command)[0],400)


class ServerLifecycleTests(unittest.TestCase):
    def exercise(self, enabled=True, failure=None):
        app = server.Dashboard(ros=True)
        output = []
        controller = drive.ManualForward(lambda moving:None,output.append,lambda since:True)
        adapter = types.SimpleNamespace(control=controller,close=mock.Mock())
        http = mock.Mock()
        http.handle_request.side_effect = app.closed.set
        args = ['--ros','--drive'] if enabled else ['--ros']
        with mock.patch.object(server,'Dashboard',return_value=app), \
                mock.patch.object(server,'RosReader') as reader, \
                mock.patch.object(server,'LocalServer',return_value=http), \
                mock.patch.object(drive,'RosManualDrive',side_effect=failure,return_value=adapter) as create, \
                mock.patch.object(server.signal,'signal'), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = server.main(args)
        return result,app,adapter,http,reader,create,output

    def test_default_ros_main_never_constructs_drive(self):
        result,app,adapter,http,reader,create,output = self.exercise(enabled=False)
        self.assertEqual(result,0); create.assert_not_called()
        self.assertFalse(app.status()['motor_output']); self.assertEqual(output,[])

    def test_explicit_drive_main_stays_disabled_and_cleans_up(self):
        result,app,adapter,http,reader,create,output = self.exercise()
        self.assertEqual(result,0); create.assert_called_once()
        self.assertEqual(app.mode,'ros_manual_ackermann'); self.assertFalse(app.control.snapshot()['armed'])
        self.assertEqual(output,[]); adapter.close.assert_called_once(); http.server_close.assert_called_once()
        reader.return_value.close.assert_called_once()

    def test_failed_drive_initialisation_closes_http_and_reader(self):
        result,app,adapter,http,reader,create,output = self.exercise(failure=ValueError('Fake invalid ROS environment'))
        self.assertEqual(result,2); self.assertTrue(app.closed.is_set())
        self.assertIsNone(app.drive); self.assertEqual(output,[])
        http.server_close.assert_called_once(); reader.return_value.close.assert_called_once()


if __name__ == '__main__': unittest.main()
