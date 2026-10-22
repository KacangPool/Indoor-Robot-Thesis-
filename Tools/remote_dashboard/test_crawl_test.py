"""Offline tests only: fake time/ROS, no network, serial port or motor output."""
import contextlib
import io
import os
import sys
import types
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

import crawl_test as crawl


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def wait(self, seconds):
        self.now += seconds


def graph():
    return [[[crawl.ODOM, [crawl.BASE]]], [[crawl.COMMAND, [crawl.BASE]]], []]


class Guards(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.app = crawl.Feedback(self.clock)
        self.app.graph(None)
        self.stamp = 1000.0

    def sample(self, velocity=(0, 0, 0), caller=crawl.BASE):
        self.clock.wait(0.01)
        self.stamp += 0.01
        self.app.observe(caller, self.stamp, self.stamp, velocity)

    def ready(self):
        for unused in range(3):
            self.sample()

    def test_expected_graph(self):
        self.assertIsNone(crawl.graph_problem(graph(), '/test'))

    def test_self_publisher_allowed(self):
        state = graph()
        state[0].append([crawl.COMMAND, ['/test']])
        self.assertIsNone(crawl.graph_problem(state, '/test'))

    def test_missing_or_extra_subscriber(self):
        for names in ([], ['/other'], [crawl.BASE, '/other']):
            state = graph()
            state[1][0][1] = names
            self.assertIsNotNone(crawl.graph_problem(state, '/test'))

    def test_other_test_publisher(self):
        state = graph()
        state[0].append([crawl.COMMAND, ['/other']])
        self.assertIsNotNone(crawl.graph_problem(state, '/test'))

    def test_ordinary_velocity_publisher(self):
        state = graph()
        state[0].append(['/cmd_vel', ['/teleop']])
        self.assertIsNotNone(crawl.graph_problem(state, '/test'))

    def test_other_base_velocity_subscription(self):
        state = graph()
        state[1].append(['/other/cmd_vel', [crawl.BASE]])
        self.assertIsNotNone(crawl.graph_problem(state, '/test'))

    def test_odom_source_must_be_unique(self):
        for names in ([], ['/other'], [crawl.BASE, '/other']):
            state = graph()
            state[0][0][1] = names
            self.assertIsNotNone(crawl.graph_problem(state, '/test'))

    def test_three_stationary_samples_needed(self):
        self.sample()
        self.sample()
        self.assertIsNotNone(self.app.problem())
        self.sample()
        self.assertIsNone(self.app.problem())

    def test_stale_odom(self):
        self.ready()
        self.clock.wait(0.51)
        self.app.graph(None)
        self.assertIsNotNone(self.app.problem())

    def test_stale_or_failed_graph(self):
        self.ready()
        self.clock.wait(0.76)
        self.assertIsNotNone(self.app.problem())
        self.app.graph('Graph unavailable')
        self.assertEqual(self.app.problem(), 'Graph unavailable')

    def test_wrong_caller_clears_readiness(self):
        self.ready()
        self.sample(caller='/different_base')
        self.assertIsNotNone(self.app.problem())
        self.assertEqual(len(self.app.samples), 0)

    def test_bad_timestamp(self):
        for stamp, now in ((0, 1000), (998, 1000), (1002, 1000),
                           (float('nan'), 1000), (1000, float('inf'))):
            self.app.observe(crawl.BASE, stamp, now, (0, 0, 0))
            self.assertIsNotNone(self.app.bad)

    def test_timestamp_replay(self):
        self.ready()
        self.app.observe(crawl.BASE, self.stamp, self.stamp, (0, 0, 0))
        self.assertIsNotNone(self.app.problem())

    def test_nonfinite_or_malformed_velocity(self):
        for value in ((float('nan'), 0, 0), (0, float('inf'), 0),
                      ('bad', 0, 0), (0, 0), None):
            self.ready()
            self.sample(velocity=value)
            self.assertIsNotNone(self.app.problem())

    def test_no_arm_when_moving(self):
        self.ready()
        self.sample((0.03, 0, 0))
        self.assertIsNotNone(self.app.problem())
        self.assertIsNone(self.app.problem(moving=True))

    def test_unexpected_motion(self):
        for velocity in ((-0.03, 0, 0), (0.11, 0, 0), (0, 0.05, 0), (0, 0, 0.16)):
            self.ready()
            self.sample(velocity)
            self.assertIsNotNone(self.app.problem(moving=True))

    def test_stop_needs_fresh_post_stop_samples(self):
        self.ready()
        since = self.clock() + 0.001
        self.assertFalse(self.app.stopped_since(since))
        self.ready()
        self.assertTrue(self.app.stopped_since(since))
        self.clock.wait(0.51)
        self.assertFalse(self.app.stopped_since(since))


class Pulse(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.sent = []

    def emit(self, speed):
        self.sent.append((self.clock(), speed))

    def run_pulse(self, health=lambda: None, wait=None, cancelled=lambda: False, emit=None):
        return crawl.pulse(emit or self.emit, health, self.clock,
                           wait or self.clock.wait, cancelled)

    def assert_zero_tail(self):
        zeros = [(t, v) for t, v in self.sent if v == 0]
        self.assertGreaterEqual(len(zeros), 20)
        self.assertGreaterEqual(zeros[-1][0] - zeros[0][0], crawl.STOP_SECONDS)
        first = self.sent.index(zeros[0])
        self.assertTrue(all(v == 0 for t, v in self.sent[first:]))

    def test_fixed_one_shot_then_zeros(self):
        reason, unused = self.run_pulse()
        self.assertEqual(reason, 'Pulse request finished')
        nonzero = [(t, v) for t, v in self.sent if v]
        self.assertGreater(len(nonzero), 0)
        self.assertTrue(all(v == 0.03 and t < 0.4 for t, v in nonzero))
        self.assertLessEqual(len(nonzero), 4)
        self.assert_zero_tail()

    def test_failed_initial_health_only_zeros(self):
        self.run_pulse(health=lambda: 'Not ready')
        self.assertTrue(all(v == 0 for t, v in self.sent))
        self.assert_zero_tail()

    def test_cancelled_only_zeros(self):
        self.run_pulse(cancelled=lambda: True)
        self.assertTrue(all(v == 0 for t, v in self.sent))
        self.assert_zero_tail()

    def test_mid_pulse_cancellation(self):
        self.run_pulse(cancelled=lambda: self.clock() >= 0.08)
        self.assertEqual(len([v for t, v in self.sent if v]), 1)
        self.assert_zero_tail()

    def test_health_exception_still_attempts_stop(self):
        def health():
            raise RuntimeError('Mock failure')
        with self.assertRaises(RuntimeError):
            self.run_pulse(health=health)
        self.assert_zero_tail()

    def test_publish_exception_still_attempts_stop(self):
        def emit(speed):
            self.emit(speed)
            if speed:
                raise RuntimeError('Mock transport failure')
        with self.assertRaises(RuntimeError):
            self.run_pulse(emit=emit)
        self.assert_zero_tail()

    def test_scheduler_gap_no_catchup(self):
        def wait(delay):
            self.clock.wait(0.3 if delay == 0.02 else delay)
        reason, unused = self.run_pulse(wait=wait)
        self.assertIn('scheduling gap', reason)
        self.assertEqual(len([v for t, v in self.sent if v]), 1)
        self.assert_zero_tail()

    def test_slow_first_health_sends_no_nonzero(self):
        def health():
            self.clock.wait(0.3)
        self.run_pulse(health=health)
        self.assertTrue(all(v == 0 for t, v in self.sent))
        self.assert_zero_tail()

    def test_zero_failures_not_reported_success(self):
        def emit(speed):
            self.emit(speed)
            if not speed:
                raise RuntimeError('Mock link lost')
        reason, unused = self.run_pulse(emit=emit)
        self.assertIn('zero-command publication errors', reason)
        self.assert_zero_tail()


class EntryPoints(unittest.TestCase):
    def test_live_confirmation_refuses_noninteractive_input(self):
        with mock.patch.object(crawl.sys, 'stdin') as stdin, \
                mock.patch.object(crawl.select, 'select') as select_input, \
                contextlib.redirect_stderr(io.StringIO()):
            stdin.isatty.return_value = False
            self.assertFalse(crawl.confirm(mock.Mock(), Clock()))
            select_input.assert_not_called()

    def test_live_confirmation_requires_exact_word(self):
        for answer in ('CRAWL\n', 'yes\n', 'crawl\n', '\n'):
            with mock.patch.object(crawl.sys, 'stdin') as stdin, \
                    mock.patch.object(crawl.select, 'select', return_value=([True], [], [])), \
                    contextlib.redirect_stdout(io.StringIO()):
                stdin.isatty.return_value = True
                stdin.readline.return_value = answer
                closed = mock.Mock()
                closed.is_set.return_value = False
                self.assertEqual(crawl.confirm(closed, Clock()), answer == 'CRAWL\n')

    def test_offline_default_without_ros_import(self):
        # No rospy installed on this development computer.
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(crawl.main([]), 0)
        self.assertIn('OFFLINE PLAN ONLY', output.getvalue())

    def test_cli_does_not_allow_tuning_or_two_modes(self):
        for args in (['--speed', '1'], ['--duration', '10'], ['--topic', '/cmd_vel'],
                     ['--live', '--check']):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                crawl.parse_args(args)

    def test_launch_isolated_no_includes(self):
        root = ET.parse(os.path.join(os.path.dirname(__file__), 'base_crawl_check.launch')).getroot()
        self.assertEqual(root.tag, 'launch')
        self.assertEqual(len(list(root)), 1)
        node = root.find('node')
        self.assertEqual(node.get('name'), crawl.BASE.lstrip('/'))
        self.assertEqual(node.get('type'), 'wheeltec_robot_node')
        self.assertEqual(node.get('respawn'), 'false')
        self.assertEqual(node.find('remap').attrib, {'from': 'cmd_vel', 'to': crawl.COMMAND})

    def exercise_main(self, args, confirmed=True, ready=True, simulated=False):
        clock = Clock()
        shared = {}
        rospy = types.ModuleType('rospy')
        rosgraph = types.ModuleType('rosgraph')
        geometry = types.ModuleType('geometry_msgs')
        messages = types.ModuleType('geometry_msgs.msg')
        class Vector:
            x = y = z = 0.0
        class Twist:
            def __init__(self):
                self.linear, self.angular = Vector(), Vector()
        messages.Twist = Twist
        rospy.init_node = mock.Mock()
        rospy.get_param = mock.Mock(return_value=simulated)
        rospy.is_shutdown = lambda: False
        rospy.signal_shutdown = mock.Mock()
        publisher = mock.Mock()
        publisher.get_num_connections.return_value = 1
        rospy.Publisher = mock.Mock(return_value=publisher)

        def feedback():
            app = shared.get('app')
            if app and ready:
                app.graph(None)
                stamp = 1000 + clock()
                app.observe(crawl.BASE, stamp, stamp, (0, 0, 0))

        class Event:
            flag = False
            def is_set(self):
                return self.flag
            def set(self):
                self.flag = True
            def wait(self, delay):
                clock.wait(delay)
                feedback()

        def reader(unused_ros, unused_graph, app, closed):
            shared['app'] = app
            for unused in range(3):
                clock.wait(0.01)
                feedback()
            return types.SimpleNamespace(subscriber=mock.Mock())

        modules = {'rospy': rospy, 'rosgraph': rosgraph, 'geometry_msgs': geometry,
                   'geometry_msgs.msg': messages}
        with mock.patch.dict(sys.modules, modules), \
                mock.patch.object(crawl, 'monotonic_clock', return_value=clock), \
                mock.patch.object(crawl, 'RosFeedback', side_effect=reader), \
                mock.patch.object(crawl, 'confirm', return_value=confirmed), \
                mock.patch.object(crawl.threading, 'Event', Event), \
                mock.patch.object(crawl.signal, 'signal'), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            result = crawl.main(args)
        return result, rospy, publisher

    def test_check_never_creates_publisher(self):
        result, rospy, unused = self.exercise_main(['--check'])
        self.assertEqual(result, 0)
        rospy.Publisher.assert_not_called()

    def test_failed_readiness_never_creates_publisher(self):
        result, rospy, unused = self.exercise_main(['--live'], ready=False)
        self.assertEqual(result, 2)
        rospy.Publisher.assert_not_called()

    def test_declined_confirmation_never_creates_publisher(self):
        result, rospy, unused = self.exercise_main(['--live'], confirmed=False)
        self.assertEqual(result, 0)
        rospy.Publisher.assert_not_called()

    def test_simulated_time_refused(self):
        result, rospy, unused = self.exercise_main(['--live'], simulated=True)
        self.assertEqual(result, 2)
        rospy.Publisher.assert_not_called()

    def test_live_fake_ros_only_fixed_forward_then_zero(self):
        result, rospy, publisher = self.exercise_main(['--live'])
        self.assertEqual(result, 0)
        rospy.Publisher.assert_called_once_with(crawl.COMMAND, mock.ANY, queue_size=1,
                                               latch=False, tcp_nodelay=True)
        values = [call.args[0] for call in publisher.publish.call_args_list]
        self.assertTrue(any(value.linear.x == 0.03 for value in values))
        self.assertEqual(values[-1].linear.x, 0)
        for value in values:
            self.assertIn(value.linear.x, (0, 0.03))
            self.assertEqual((value.linear.y, value.linear.z, value.angular.x,
                              value.angular.y, value.angular.z), (0, 0, 0, 0, 0))
        publisher.unregister.assert_called_once()


if __name__ == '__main__':
    unittest.main()
