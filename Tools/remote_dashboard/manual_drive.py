"""Repeatable supervised car-like holds. No ROS imports until explicit --drive.

An application lease/zero attempts are not an independent controller watchdog.
Python 2.7 / 3.6 syntax. Nonzero output requires fresh held-input heartbeats.
"""
from __future__ import print_function
import threading
import uuid
import math
import collections

import crawl_test as crawl
from control import monotonic_clock

SPEED = 0.03
JOYSTICK_SPEED = 0.30  # session joystick ceiling only; buttons stay at crawl speed
REPORTED_SPEED_LIMIT = 0.32  # provisional feedback headroom; not a command limit
REPORTED_YAW_LIMIT = 0.35  # .30 m/s * 1/m curvature plus provisional headroom
MAX_HOLD = 2.0
LEASE = 0.35
CAMERA_AGE = 0.75
PERIOD = 0.1
STOP_SECONDS = 2.0
MAX_CURVATURE = 1.0  # requested inverse metres; not a measured steering limit
DEADZONE = 0.12
ACTIONS = ('forward', 'forward_left', 'forward_right',
           'reverse', 'reverse_left', 'reverse_right')


def axis(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('Numeric joystick axis required')
    if math.isnan(value) or math.isinf(value) or not -1 <= value <= 1:
        raise ValueError('Joystick axis must be finite and within -1..1')
    if abs(value) <= DEADZONE:
        return 0.0
    return math.copysign((abs(value) - DEADZONE) / (1.0 - DEADZONE), value)


def requested_twist(action, throttle=None, steering=None, joystick_speed=SPEED):
    """ROS +X forward, +yaw left. Steering +1 means front wheels right.

    Curvature couples yaw to signed speed: no sideways or in-place spin.
    Reverse with the same wheel-steering direction reverses yaw sign.
    """
    if action == 'joystick':
        power, turn = axis(throttle), axis(steering)
    elif action in ACTIONS or action == 'neutral':
        if throttle is not None or steering is not None:
            raise ValueError('Axes are valid only for joystick commands')
        power = -1.0 if action.startswith('reverse') else 0.0 if action == 'neutral' else 1.0
        turn = -1.0 if action.endswith('_left') else 1.0 if action.endswith('_right') else 0.0
    else:
        raise ValueError('Unsupported car-like action')
    speed = (joystick_speed if action == 'joystick' else SPEED) * power
    yaw = -speed * MAX_CURVATURE * turn
    return speed, yaw


class ManualFeedback(crawl.Feedback):
    """Retain real-source/time/graph checks; allow bounded signed travel."""
    def __init__(self, clock=None, speed_limit=0.12, yaw_limit=0.15):
        # Historical crawl adapters retain their previous envelope. Only the
        # explicit live-session adapter selects the enlarged session envelope.
        crawl.Feedback.__init__(self, clock)
        self.speed_limit, self.yaw_limit = speed_limit, yaw_limit

    def stopped_since(self, since):
        with self.lock:
            if self.bad:
                return False
            # Strictly later: a sample at the release timestamp may still be
            # the stationary observation immediately before its first command.
            values = [v for t, v in self.samples if t > since and self.clock() - t <= crawl.ODOM_AGE]
            return len(values) >= 3 and all(crawl.stationary(v) for v in values[-3:])

    def problem(self, moving=False):
        if not moving:
            return crawl.Feedback.problem(self, moving=False)
        with self.lock:
            now = self.clock()
            if self.graph_time is None or now - self.graph_time > crawl.GRAPH_AGE:
                return 'ROS graph check is stale/unavailable'
            if self.graph_error:
                return self.graph_error
            if self.bad:
                return self.bad
            recent = [v for t, v in self.samples if now - t <= crawl.ODOM_AGE]
            if len(recent) < 3:
                return 'Need at least three recent physical odometry samples'
            x, y, yaw = recent[-1]
            if abs(x) > self.speed_limit or abs(y) > 0.04 or abs(yaw) > self.yaw_limit:
                return 'Unexpected reported speed (vx=%.3f m/s, vy=%.3f m/s, yaw=%.3f rad/s); stop' % (x, y, yaw)
            return None


class ManualForward(object):
    """One owner, renewable idle session; each release retires its generation.

Only tick() publishes. HTTP handlers change intent, never drive a pulse directly.
No automatic resume/rearm after release, cap, faults or reconnect. New explicit
browser Enable is allowed after zero cleanup and fresh stationary feedback.
"""
    def __init__(self, health, emit, stopped_since, clock=None, steering_enabled=False):
        self.clock = clock or monotonic_clock()
        self.health, self.emit, self.stopped_since = health, emit, stopped_since
        self.lock = threading.RLock()
        self.owner = self.generation = None
        self.sequence = 0
        self.stage, self.action, self.reason = 'disabled', 'neutral', 'Start disabled'
        self.contact = self.hold_at = self.last_positive = None
        self.stop_at = self.last_zero = None
        self.last_tick = self.clock()
        self.zero_failures = 0
        self.steering_enabled = steering_enabled
        self.target = (0.0, 0.0)
        self.disable_count = 0
        self.disable_events = collections.deque(maxlen=20)

    def _stop(self, reason):
        if self.stage in ('stopping', 'disabled') and self.owner is None and self.stop_at is not None:
            return  # Preserve the first stop/fault reason until a fresh Enable.
        if self.owner is not None:
            self.disable_count += 1
            self.disable_events.append({'id': self.disable_count, 'clock_s': self.clock(),
                                        'reason': reason, 'stage': self.stage,
                                        'requested_linear_m_s': self.target[0],
                                        'requested_yaw_rad_s': self.target[1]})
        moving = self.stage == 'holding'
        self.owner = self.generation = None
        self.sequence = 0
        self.action, self.reason = 'neutral', reason
        self.target = (0.0, 0.0)
        if moving:
            self.stage = 'stopping'
            self.stop_at, self.last_zero = self.clock(), None
            self.zero_failures = 0
        elif self.stage != 'stopping':
            self.stage = 'disabled'
        # Repeated Stop cannot postpone the existing cleanup deadline.

    def _expire(self):
        now = self.clock()
        if self.stage in ('armed', 'holding') and now - self.contact >= LEASE:
            self._stop('Browser heartbeat expired; enable again deliberately')
        elif self.stage == 'holding' and now - self.hold_at >= MAX_HOLD:
            self._stop('Two-second hold limit reached; release, then enable again')

    def _problem(self):
        if self.stage != 'disabled':
            return 'Stop/cleanup in progress' if self.stage == 'stopping' else 'Already enabled'
        if self.zero_failures:
            return 'Zero publication failed; inspect controller/process before further driving'
        issue = self.health(False)
        if issue:
            return issue
        if self.stop_at is not None and not self.stopped_since(self.stop_at):
            return 'Waiting for fresh near-zero odometry after stop requests'
        return None

    def arm(self, owner):
        with self.lock:
            self._expire()
            if not isinstance(owner, str) or len(owner) != 32 or any(c not in '0123456789abcdef' for c in owner):
                raise ValueError('Invalid browser owner')
            issue = self._problem()
            if issue:
                raise ValueError(issue)
            self.owner, self.generation = owner, uuid.uuid4().hex
            self.stage, self.action = 'armed', 'neutral'
            self.sequence, self.contact = 0, self.clock()
            self.hold_at = self.last_positive = None
            self.reason = 'Enabled: hold a direction or drag the joystick; release requests stop' if self.steering_enabled else 'Enabled: hold Forward; release requests stop'
            return self.generation

    def command(self, owner, generation, sequence, action, throttle=None, steering=None):
        with self.lock:
            self._expire()
            if self.stage not in ('armed', 'holding') or owner != self.owner or generation != self.generation:
                raise ValueError('Disabled, expired or wrong browser generation')
            if type(sequence) is not int or not self.sequence < sequence <= 2147483647:
                raise ValueError('Old or invalid sequence')
            if not self.steering_enabled and (action not in ('neutral', 'forward') or throttle is not None or steering is not None):
                raise ValueError('This profile supports forward only')
            target = requested_twist(action, throttle, steering)
            self.sequence, self.contact = sequence, self.clock()
            if self.stage == 'holding' and self.target[0] * target[0] < 0:
                self._stop('Forward/reverse change: stop first, release and enable again')
            elif target[0] == 0 and self.stage == 'holding':
                self._stop('Released; stop requested')
            elif target[0] != 0 and self.stage == 'armed':
                issue = self.health(False)
                if issue:
                    self._stop(issue)
                    raise ValueError(issue)
                self.stage, self.action, self.hold_at = 'holding', action, self.clock()
                self.target = target
                self.reason = 'Car-like hold requested; maximum two seconds'
            elif self.stage == 'holding':
                self.action, self.target = action, target
            elif self.stage == 'armed':
                self.action, self.target = 'neutral', (0.0, 0.0)
            return self.snapshot()

    def stop(self, reason='Stopped by operator'):
        with self.lock:
            self._stop(reason)

    def snapshot(self):
        with self.lock:
            self._expire()
            issue = self._problem() if self.stage == 'disabled' else None
            return {'armed': self.stage in ('armed', 'holding'), 'owner': self.owner,
                    'action': self.action, 'stage': self.stage, 'reason': self.reason,
                    'motor_output': True, 'timeout_ms': int(LEASE * 1000),
                    'allowed_actions': list(ACTIONS) + ['joystick'] if self.steering_enabled else ['forward'], 'max_hold_s': MAX_HOLD,
                    'speed_request_m_s': SPEED, 'ready': self.stage == 'disabled' and not issue,
                    'requested_linear_m_s': self.target[0], 'requested_yaw_rad_s': self.target[1],
                    'max_curvature_m_inv': MAX_CURVATURE, 'joystick_deadzone': DEADZONE,
                    'readiness': issue, 'zero_failures': self.zero_failures,
                    'stop_feedback': None if self.stop_at is None else bool(self.stopped_since(self.stop_at)),
                    'last_disable': dict(self.disable_events[-1]) if self.disable_events else None,
                    'disable_events': list(self.disable_events)}

    def tick(self):
        with self.lock:
            now = self.clock()
            self._expire()
            if self.stage in ('armed', 'holding'):
                if now - self.last_tick > 0.25:
                    self._stop('Drive-worker scheduling gap; no catch-up or auto-resume')
                else:
                    issue = self.health(self.stage == 'holding')
                    if issue:
                        self._stop(issue)
            self.last_tick = now
            if self.stage == 'holding' and (self.last_positive is None or now - self.last_positive >= PERIOD - 1e-9):
                # Guard again immediately before enqueue; emit must be nonblocking.
                self._expire()
                issue = self.health(True)
                self._expire()
                if self.clock() - now > 0.25:
                    self._stop('Drive health check delayed; no late positive request')
                if self.stage == 'holding' and not issue:
                    try:
                        if self.steering_enabled:
                            self.emit(*self.target)
                        else:
                            self.emit(self.target[0])
                        self.last_positive = self.clock()
                    except Exception:
                        self._stop('Positive publication failed; zero requests attempted')
                elif issue:
                    self._stop(issue)
            if self.stage == 'stopping':
                if self.last_zero is None or now - self.last_zero >= PERIOD - 1e-9 or now - self.stop_at >= STOP_SECONDS:
                    try:
                        if self.steering_enabled:
                            self.emit(0.0, 0.0)
                        else:
                            self.emit(0.0)
                    except Exception:
                        self.zero_failures += 1
                    self.last_zero = self.clock()
                if self.clock() - self.stop_at >= STOP_SECONDS:
                    self.stage = 'disabled'
                    if self.zero_failures:
                        self.reason += '; zero publication errors: %d; stopping not guaranteed' % self.zero_failures


class ManualAckermann(ManualForward):
    def __init__(self, health, emit, stopped_since, clock=None):
        ManualForward.__init__(self, health, emit, stopped_since, clock, steering_enabled=True)


class ManualSession(ManualAckermann):
    """Enable once; normal release keeps an idle session, never a held intent.

    No fixed hold-duration cap. Stop/fault/lease loss still retires the session.
    A separate monotonically increasing motion ID retires each released hold,
    preventing delayed commands or inputs held during braking from resuming it.
    """
    BRAKE_MIN = 0.15
    BRAKE_TIMEOUT = 2.0

    def __init__(self, health, emit, stopped_since, clock=None):
        ManualAckermann.__init__(self, health, emit, stopped_since, clock)
        self.active_motion = None
        self.retired_motion = 0
        self.brake_at = None

    def arm(self, owner):
        with self.lock:
            token = ManualAckermann.arm(self, owner)
            self.active_motion, self.retired_motion, self.brake_at = None, 0, None
            self.reason = 'Session enabled; hold to drive, release to stop'
            return token

    def _stop(self, reason):
        if self.stage == 'braking':
            # Full Stop/fault during normal braking still gets the zero tail.
            self.stage = 'holding'
        self.active_motion = None
        ManualAckermann._stop(self, reason)

    def _expire(self):
        if self.stage in ('armed', 'holding', 'braking') and self.clock() - self.contact >= LEASE:
            self._stop('Browser heartbeat expired; session disabled')

    def _brake(self, reason, motion):
        self.retired_motion = max(self.retired_motion, motion, self.active_motion or 0)
        self.active_motion = None
        self.action, self.target = 'neutral', (0.0, 0.0)
        if self.stage != 'braking':
            self.stage, self.brake_at, self.last_zero = 'braking', self.clock(), None
        self.reason = reason

    def command(self, owner, generation, sequence, action, throttle=None, steering=None, motion=None):
        with self.lock:
            self._expire()
            if self.stage not in ('armed', 'holding', 'braking') or owner != self.owner or generation != self.generation:
                raise ValueError('Disabled, expired or wrong browser generation')
            if type(sequence) is not int or not self.sequence < sequence <= 2147483647:
                raise ValueError('Old or invalid sequence')
            if type(motion) is not int or not 0 <= motion <= 2147483647:
                raise ValueError('Valid motion ID required')
            target = requested_twist(action, throttle, steering, joystick_speed=JOYSTICK_SPEED)
            if action != 'neutral' and motion <= self.retired_motion:
                raise ValueError('Released motion cannot resume; use a fresh press')
            if self.stage == 'holding' and motion < self.active_motion:
                raise ValueError('Old motion cannot replace current hold')
            self.sequence, self.contact = sequence, self.clock()
            if action == 'neutral':
                if self.stage in ('holding', 'braking'):
                    self._brake('Released; checking stationary feedback', motion)
                else:
                    self.retired_motion = max(self.retired_motion, motion)
                    self.reason = 'Session enabled; ready for another hold'
            elif self.stage == 'braking':
                # Never queue a press made before stopping/feedback completes.
                self.retired_motion = max(self.retired_motion, motion)
                self.reason = 'Still stopping; release and press again when ready'
            elif self.stage == 'holding':
                if motion != self.active_motion or self.target[0] * target[0] < 0 or target[0] == 0:
                    self._brake('Stop before changing travel direction; release and press again', motion)
                else:
                    self.action, self.target = action, target
            elif target[0] != 0:
                issue = self.health(False)
                if issue:
                    self._stop(issue)
                    raise ValueError(issue)
                self.stage, self.action, self.target = 'holding', action, target
                self.active_motion, self.hold_at, self.last_positive = motion, self.clock(), None
                self.reason = 'Driving while held; release requests stop'
            # A centred initial joystick sample reserves no motion/output and
            # does not retire the ID: the user can then drag away from centre.
            return self.snapshot()

    def snapshot(self):
        with self.lock:
            result = ManualAckermann.snapshot(self)
            result.update({'session_persistent': True, 'max_hold_s': None,
                           'joystick_speed_request_m_s': JOYSTICK_SPEED,
                           'button_speed_request_m_s': SPEED,
                           'max_speed_request_m_s': JOYSTICK_SPEED,
                           'reported_speed_fault_limit_m_s': REPORTED_SPEED_LIMIT,
                           'reported_yaw_fault_limit_rad_s': REPORTED_YAW_LIMIT,
                           'armed': self.stage in ('armed', 'holding', 'braking'),
                           'motion_ready': self.stage == 'armed',
                           'active_motion': self.active_motion,
                           'retired_motion': self.retired_motion,
                           'sequence': self.sequence})
            return result

    def tick(self):
        with self.lock:
            if self.stage != 'braking':
                return ManualAckermann.tick(self)
            now = self.clock()
            self._expire()
            if self.stage == 'braking':
                issue = self.health(True)
                if now - self.last_tick > 0.25 or self.clock() - now > 0.25:
                    self._stop('Drive-worker scheduling gap while stopping; session disabled')
                elif issue:
                    self._stop(issue)
            self.last_tick = self.clock()
            if self.stage == 'braking':
                if self.last_zero is None or now - self.last_zero >= PERIOD - 1e-9:
                    try:
                        self.emit(0.0, 0.0)
                    except Exception:
                        self._stop('Zero publication failed; session disabled')
                        self.zero_failures += 1
                    self.last_zero = self.clock()
                if self.stage == 'braking':
                    elapsed = self.clock() - self.brake_at
                    if elapsed >= self.BRAKE_MIN and self.stopped_since(self.brake_at):
                        issue = self.health(False)
                        self._expire()
                        if self.stage == 'braking' and not issue and self.clock() - self.last_tick <= 0.25:
                            self.stage = 'armed'
                            self.reason = 'Session enabled; ready for another hold'
                        elif issue:
                            self._stop(issue)
                    elif elapsed >= self.BRAKE_TIMEOUT:
                        self._stop('Stationary feedback did not arrive; session disabled')
            if self.stage == 'stopping':
                ManualAckermann.tick(self)


class RosManualDrive(object):
    """Explicit opt-in adapter; leaves drivers/firmware/boot configuration alone."""
    def __init__(self, dashboard, rospy):
        import rosgraph
        from geometry_msgs.msg import Twist
        if rospy.get_param('/use_sim_time', False):
            raise ValueError('Physical manual drive refuses simulated ROS time')
        self.app, self.rospy = dashboard, rospy
        self.clock = dashboard.clock
        self.halt, self.monitor_halt = threading.Event(), threading.Event()
        self.feedback = ManualFeedback(self.clock, REPORTED_SPEED_LIMIT, REPORTED_YAW_LIMIT)
        self.publisher = self.monitor = self.worker = None
        self.failed = False
        try:
            self.monitor = crawl.RosFeedback(rospy, rosgraph, self.feedback, self.monitor_halt)
            self.publisher = rospy.Publisher(crawl.COMMAND, Twist, queue_size=1,
                                             latch=False, tcp_nodelay=True)
            def health(moving):
                if self.failed:
                    return 'Drive worker failed; operator process inspection required'
                if dashboard.closed.is_set() or rospy.is_shutdown():
                    return 'Dashboard/ROS closing'
                issue = self.feedback.problem(moving=moving)
                if issue:
                    return issue
                if moving and hasattr(self, 'control'):
                    with self.feedback.lock:
                        if self.feedback.samples:
                            reported = self.feedback.samples[-1][1][0]
                            expected = self.control.target[0]
                            if abs(reported) > 0.02 and expected * reported < 0:
                                return 'Reported travel direction disagrees with request; stop'
                if self.publisher.get_num_connections() != 1:
                    return 'Expected unique isolated controller connection unavailable'
                with dashboard.lock:
                    image = dashboard.frames.get('rgb')
                    if not image or self.clock() - image['received'] >= CAMERA_AGE:
                        return 'Need recent colour-camera messages'
                return None
            def emit(speed, yaw=0.0):
                message = Twist()
                message.linear.x = speed
                message.angular.z = yaw  # no lateral motion; no yaw at zero speed
                self.publisher.publish(message)
            self.control = ManualSession(health, emit, self.feedback.stopped_since, self.clock)
            self.worker = threading.Thread(target=self.run)
            self.worker.daemon = True
            self.worker.start()
        except Exception:
            self.close()
            raise

    def run(self):
        try:
            while not self.halt.is_set():
                self.control.tick()
                self.halt.wait(0.02)
        except Exception:
            # Do not silently leave a failed worker armed; best-effort zero tail.
            self.failed = True
            self.control.stop('Drive worker exception; physical stopping not guaranteed')
            until = self.clock() + STOP_SECONDS
            while self.clock() < until:
                try:
                    self.control.tick()
                except Exception:
                    pass
                threading.Event().wait(0.1)

    def close(self):
        if hasattr(self, 'control'):
            self.control.stop('Dashboard closing')
            until = self.clock() + STOP_SECONDS + 0.5
            while self.worker and self.worker.is_alive() and self.clock() < until:
                if self.control.snapshot()['stage'] != 'stopping':
                    break
                threading.Event().wait(0.02)
        self.halt.set()
        if self.worker:
            self.worker.join(1.0)
            if self.worker.is_alive():
                print('Drive worker cleanup incomplete; physical stopping NOT verified.')
        if self.publisher:
            self.publisher.unregister()
        self.monitor_halt.set()
        if self.monitor:
            self.monitor.subscriber.unregister()
