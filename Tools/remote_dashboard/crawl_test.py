#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Separate one-shot crawl test, NOT a dashboard motor endpoint.

Default: offline plan only. --check: ROS subscriptions/graph only, no Publisher.
--live: explicit typed confirmation, expected isolated driver and fresh physical
odometry required. Best-effort zeros cannot guarantee a physical stop on failure.
Python 2.7 / 3.6+ syntax; reuse the already deployed monotonic clock helper.
"""
from __future__ import print_function
import argparse
import collections
import math
import select
import signal
import sys
import threading

from control import monotonic_clock

BASE = '/fahad_base_crawl_check'
COMMAND = '/fahad/crawl_test/cmd_vel'
ODOM = '/odom'
SPEED = 0.03
PULSE_SECONDS = 0.4
STOP_SECONDS = 2.0
PERIOD = 0.1
ODOM_AGE = 0.5
GRAPH_AGE = 0.75


def finite(value):
    try:
        return not math.isnan(value) and not math.isinf(value)
    except (TypeError, ValueError, OverflowError):
        return False


def graph_problem(state, self_name):
    publishers, subscribers, unused_services = state
    pubs, subs = dict(publishers), dict(subscribers)
    if set(subs.get(COMMAND, [])) != set([BASE]):
        return 'Expected isolated base subscriber is absent or not unique'
    if any(name != self_name for name in pubs.get(COMMAND, [])):
        return 'Another publisher owns the test command topic'
    if pubs.get('/cmd_vel', []):
        return 'Another ordinary movement-command publisher exists'
    if any(BASE in names and topic != COMMAND and 'cmd_vel' in topic
           for topic, names in subscribers):
        return 'Base also subscribes to another velocity-command topic'
    if set(pubs.get(ODOM, [])) != set([BASE]):
        return 'Odometry must come only from the isolated base driver'
    return None


def stationary(velocity):
    return abs(velocity[0]) <= 0.02 and abs(velocity[1]) <= 0.02 and abs(velocity[2]) <= 0.05


class Feedback(object):
    def __init__(self, clock=None):
        self.clock = clock or monotonic_clock()
        self.lock = threading.RLock()
        self.samples = collections.deque(maxlen=12)
        self.last_stamp = None
        self.bad = 'Waiting for physical odometry'
        self.graph_time = None
        self.graph_error = 'Waiting for ROS graph'

    def graph(self, error):
        with self.lock:
            self.graph_error = error
            self.graph_time = self.clock()

    def observe(self, caller, stamp, ros_now, velocity):
        with self.lock:
            if (caller != BASE or not finite(stamp) or not finite(ros_now)
                    or stamp <= 0 or abs(ros_now - stamp) > 1.0):
                self.bad = 'Wrong/stale/invalid odometry source or timestamp'
                self.samples.clear()
                return
            if self.last_stamp is not None and stamp <= self.last_stamp:
                self.bad = 'Odometry timestamp did not advance'
                self.samples.clear()
                return
            if not isinstance(velocity, (tuple, list)) or len(velocity) != 3 or not all(finite(x) for x in velocity):
                self.bad = 'Non-finite odometry'
                self.samples.clear()
                return
            self.last_stamp = stamp
            self.samples.append((self.clock(), tuple(velocity)))
            self.bad = None

    def problem(self, moving=False):
        with self.lock:
            now = self.clock()
            if self.graph_time is None or now - self.graph_time > GRAPH_AGE:
                return 'ROS graph check is stale/unavailable'
            if self.graph_error:
                return self.graph_error
            if self.bad:
                return self.bad
            recent = [sample for sample in self.samples if now - sample[0] <= ODOM_AGE]
            if len(recent) < 3:
                return 'Need at least three recent physical odometry samples'
            if not moving and not all(stationary(value) for unused, value in recent[-3:]):
                return 'Robot does not report stationary; do not arm'
            if moving:
                x, y, yaw = recent[-1][1]
                if x < -0.02 or x > 0.10 or abs(y) > 0.04 or abs(yaw) > 0.15:
                    return 'Unexpected reported speed/direction; stop'
            return None

    def stopped_since(self, since):
        with self.lock:
            if self.bad:
                return False
            values = [v for t, v in self.samples
                      if t >= since and self.clock() - t <= ODOM_AGE]
            return len(values) >= 3 and all(stationary(v) for v in values[-3:])


def pulse(emit, health, clock, wait, cancelled):
    """One bounded request phase then repeated zeros. No retries or speed ramp.

    emit(vx) must be nonblocking. No graph/network queries run on this thread.
    Scheduling and lower-controller behavior prevent a hard real-time guarantee.
    """
    started = clock()
    last = None
    reason = 'Pulse request finished'
    try:
        while clock() - started < PULSE_SECONDS:
            if cancelled():
                reason = 'Interrupted'
                break
            issue = health()
            if issue:
                reason = issue
                break
            now = clock()
            if now - (last if last is not None else started) > 0.25:
                reason = 'Publisher scheduling gap; no further nonzero request'
                break
            if last is None or now - last >= PERIOD:
                # Recheck elapsed before each nonzero request; never catch up.
                if clock() - started >= PULSE_SECONDS:
                    break
                last = clock()
                emit(SPEED)
            wait(0.02)
    finally:
        # Always attempt zeros, even if health/emit throws. This is not a hardware
        # watchdog and cannot run after SIGKILL, host failure or lost drive link.
        stop_at = clock()
        zero_failures = 0
        while True:
            try:
                emit(0.0)
            except Exception:
                zero_failures += 1
            if clock() - stop_at >= STOP_SECONDS:
                break
            wait(PERIOD)
    if zero_failures:
        reason += '; %d zero-command publication errors' % zero_failures
    return reason, stop_at


class RosFeedback(object):
    def __init__(self, rospy, rosgraph, app, closed):
        from nav_msgs.msg import Odometry
        self.rospy, self.app, self.closed = rospy, app, closed
        self.master = rosgraph.Master(rospy.get_name())
        self.subscriber = rospy.Subscriber(ODOM, Odometry, self.callback, queue_size=1, tcp_nodelay=True)
        self.thread = threading.Thread(target=self.monitor)
        self.thread.daemon = True
        self.thread.start()

    def monitor(self):
        while not self.closed.is_set():
            try:
                error = graph_problem(self.master.getSystemState(), self.rospy.get_name())
                self.app.graph(error)
            except Exception:
                self.app.graph('Cannot inspect current ROS graph')
            self.closed.wait(0.2)

    def callback(self, message):
        try:
            caller = getattr(message, '_connection_header', {}).get('callerid')
            twist = message.twist.twist
            self.app.observe(caller, message.header.stamp.to_sec(), self.rospy.Time.now().to_sec(),
                             (twist.linear.x, twist.linear.y, twist.angular.z))
        except Exception:
            with self.app.lock:
                self.app.bad = 'Cannot decode physical odometry'
                self.app.samples.clear()


def confirm(closed, clock):
    if not sys.stdin.isatty():
        print('Live mode requires a foreground interactive terminal.', file=sys.stderr)
        return False
    print('LIVE TEST: robot on clear level floor, people clear of wheels/steering,')
    print('normal main-power cutoff confirmed and immediately reachable; no lifting.')
    print('Command: forward %.2f m/s for at most %.1f s, then repeated zeros.' % (SPEED, PULSE_SECONDS))
    print('Actual speed/stop are NOT guaranteed. Use physical power-off if abnormal.')
    print('Do not close camera/tunnel to stop; Ctrl+C here requests software stop.')
    print('Type CRAWL within 30 seconds ONLY when these conditions are met:')
    sys.stdout.flush()
    end = clock() + 30.0
    while not closed.is_set() and clock() < end:
        if select.select([sys.stdin], [], [], 0.1)[0]:
            return sys.stdin.readline().strip() == 'CRAWL'
    return False


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='One-shot isolated crawl check; default OFFLINE, no ROS or movement.')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Read ROS graph/odometry only; no motor publisher.')
    mode.add_argument('--live', action='store_true', help='Explicitly enable one gated crawl request; physical cutoff required.')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if not args.check and not args.live:
        print('OFFLINE PLAN ONLY: no ROS imports, connections or movement.')
        print('Fixed request: %.2f m/s forward, %.1f s maximum; zero steering/lateral.' % (SPEED, PULSE_SECONDS))
        print('Nominal %.1f cm ONLY if speed tracking is correct; not a distance guarantee.' % (100 * SPEED * PULSE_SECONDS))
        print('Use --check for read-only readiness. --live requires typed confirmation.')
        return 0
    try:
        import rospy
        import rosgraph
        from geometry_msgs.msg import Twist
    except ImportError as error:
        print('ROS unavailable: %s. Source existing robot workspace; do not upgrade.' % error, file=sys.stderr)
        return 2
    clock = monotonic_clock()
    closed = threading.Event()
    app = Feedback(clock)
    # Initialization may wait if no master; no Publisher exists at this point.
    rospy.init_node('fahad_crawl_test', anonymous=True, disable_signals=True)
    if rospy.get_param('/use_sim_time', False):
        print('Refusing physical test with /use_sim_time enabled.', file=sys.stderr)
        return 2
    def stop_signal(signum, frame):
        closed.set()
    for name in ('SIGINT', 'SIGTERM', 'SIGHUP'):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), stop_signal)
    reader = RosFeedback(rospy, rosgraph, app, closed)
    publisher = None
    try:
        deadline = clock() + 10.0
        while not closed.is_set() and clock() < deadline and app.problem():
            closed.wait(0.05)
        issue = app.problem()
        if closed.is_set() or issue:
            print('NOT READY: %s. No movement command sent.' % (issue or 'Interrupted'))
            return 2
        print('READINESS: expected isolated driver + recent stationary odometry observed.')
        if args.check:
            print('CHECK ONLY: no Publisher created and no movement command sent.')
            return 0
        if not confirm(closed, clock):
            print('Cancelled. No Publisher created and no movement command sent.')
            return 0
        issue = app.problem()
        if issue or closed.is_set():
            print('NOT READY after confirmation: %s. No movement command sent.' % (issue or 'Interrupted'))
            return 2
        publisher = rospy.Publisher(COMMAND, Twist, queue_size=1, latch=False, tcp_nodelay=True)
        deadline = clock() + 3.0
        while not closed.is_set() and publisher.get_num_connections() != 1 and clock() < deadline:
            closed.wait(0.02)
        if closed.is_set() or publisher.get_num_connections() != 1 or app.problem():
            print('Controller connection/readiness not established. No movement command sent.')
            return 2
        def emit(speed):
            message = Twist()  # all steering/lateral/other fields remain zero
            message.linear.x = speed
            publisher.publish(message)
        def health():
            if rospy.is_shutdown() or publisher.get_num_connections() != 1:
                return 'Controller connection lost'
            return app.problem(moving=True)
        print('Requesting ONE pulse. Physical power-off remains the fallback.')
        cleanup_wait = threading.Event()  # do not skip zero attempts when closed is set
        reason, stop_at = pulse(emit, health, clock, cleanup_wait.wait, closed.is_set)
        print('Zero-command attempts finished: %s' % reason)
        if app.stopped_since(stop_at):
            print('Recent feedback reports near-zero speed AFTER stop requests.')
            print('This does NOT verify independent firmware timeout or fault stopping.')
        else:
            print('STOP NOT VERIFIED BY FEEDBACK. Use the physical power-off if needed; do not repeat.')
        return 0 if reason == 'Pulse request finished' and app.stopped_since(stop_at) else 2
    except Exception as error:
        print('Test failed: %s. Stopping is NOT guaranteed; use physical power-off if needed.' % error, file=sys.stderr)
        return 2
    finally:
        closed.set()
        if publisher is not None:
            publisher.unregister()
        reader.subscriber.unregister()
        rospy.signal_shutdown('Crawl check finished')


if __name__ == '__main__':
    sys.exit(main())
