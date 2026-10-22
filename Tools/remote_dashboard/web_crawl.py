#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""One supervised web-forward trial per launch, not general teleoperation.

Default OFFLINE. --check is subscription-only. --live additionally requires the
existing isolated driver, fresh real feedback, interactive terminal confirmation
and an expiring browser prepare/hold. No vendor/service/boot changes. Py2.7/3.6.
"""
from __future__ import print_function
import argparse
import os
import signal
import sys
import threading
import uuid

import crawl_test as crawl
import server
from control import monotonic_clock

PERMIT_SECONDS = 60.0
PREPARE_SECONDS = 5.0
LEASE_SECONDS = 0.35
CAMERA_AGE = 0.75


class WebGate(object):
    """One-use intent, no ROS. Worker alone executes the fixed pulse routine."""
    def __init__(self, readiness, emit, clock=None):
        self.clock = clock or monotonic_clock()
        self.readiness, self.emit = readiness, emit
        self.lock = threading.RLock()
        self.deadline = self.clock() + PERMIT_SECONDS
        self.state, self.reason = 'available', 'Terminal permit: one supervised forward trial'
        self.owner = self.token = None
        self.sequence = 0
        self.prepared_at = self.contact = None
        self.cancelled = threading.Event()
        self.pending = threading.Event()
        self.started = None
        self.stop_feedback = None

    def _expire(self):
        now = self.clock()
        if self.state in ('available', 'prepared', 'queued') and now >= self.deadline:
            self.stop('Terminal permit expired; restart deliberately')
        elif self.state in ('prepared', 'queued', 'running'):
            if now - self.contact >= LEASE_SECONDS:
                self.stop('Browser heartbeat expired')
            elif self.state == 'prepared' and now - self.prepared_at >= PREPARE_SECONDS:
                self.stop('Prepared action expired')
            elif self.state == 'queued' and now - self.started >= crawl.PULSE_SECONDS:
                self.stop('Worker start delayed; no replay')

    def prepare(self, owner):
        with self.lock:
            self._expire()
            if self.state != 'available':
                raise ValueError('Only one browser attempt per terminal launch')
            if not isinstance(owner, str) or len(owner) != 32 or any(c not in '0123456789abcdef' for c in owner):
                raise ValueError('Invalid owner')
            issue = self.readiness(False)
            if issue:
                raise ValueError(issue)
            self.state, self.owner, self.token = 'prepared', owner, uuid.uuid4().hex
            self.contact = self.prepared_at = self.clock()
            self.reason = 'Prepared: hold Forward within five seconds'
            return self.token

    def command(self, owner, token, sequence, action):
        with self.lock:
            self._expire()
            if self.state not in ('prepared', 'queued', 'running') or self.cancelled.is_set():
                raise ValueError('Inactive action')
            if owner != self.owner or token != self.token:
                raise ValueError('Wrong browser or retired token')
            if type(sequence) is not int or not self.sequence < sequence <= 2147483647:
                raise ValueError('Old or invalid sequence')
            if action not in ('heartbeat', 'forward'):
                raise ValueError('Only fixed forward is implemented')
            if action == 'forward':
                if self.state != 'prepared':
                    raise ValueError('No replay')
                issue = self.readiness(False)
                if issue:
                    self.stop(issue)
                    raise ValueError(issue)
                self.state, self.started = 'queued', self.clock()
                self.reason = 'One forward request queued'
                self.pending.set()
            self.sequence, self.contact = sequence, self.clock()
            return self.snapshot()

    def stop(self, reason='Stopped by operator'):
        with self.lock:
            self.cancelled.set()
            self.state, self.reason = 'spent', reason
            self.token = None
            # Stop also burns an unused permit: a delayed prepare cannot arm it.

    def snapshot(self):
        with self.lock:
            self._expire()
            issue = self.readiness(False) if self.state == 'available' else None
            return {'state': self.state, 'reason': self.reason, 'owner': self.owner,
                    'ready': self.state == 'available' and not issue,
                    'readiness': issue, 'stop_feedback': self.stop_feedback,
                    'speed_request_m_s': crawl.SPEED, 'max_request_s': crawl.PULSE_SECONDS}

    def health(self):
        with self.lock:
            self._expire()
            if self.cancelled.is_set():
                return self.reason
            if self.started is not None and self.clock() - self.started >= crawl.PULSE_SECONDS:
                return 'Original browser-action deadline reached'
            return self.readiness(True)

    def guarded_emit(self, speed):
        with self.lock:
            if speed != 0:
                issue = self.health()
                if issue:
                    raise ValueError(issue)
                if self.started is None or self.clock() - self.started >= crawl.PULSE_SECONDS:
                    raise ValueError('Original browser-action deadline reached')
            self.emit(speed)

    def run_once(self, wait, stopped_since):
        """No movement unless queued; no catch-up after a delayed worker."""
        with self.lock:
            self._expire()
            if self.state != 'queued' or self.cancelled.is_set():
                return False
            self.state = 'running'
        reason = 'Worker failed; physical stop may be needed'
        stop_at = None
        try:
            reason, stop_at = crawl.pulse(self.guarded_emit, self.health, self.clock,
                                          wait, self.cancelled.is_set)
        finally:
            with self.lock:
                self.stop_feedback = bool(stop_at is not None and stopped_since(stop_at))
                self.stop(reason)
                print('WEB TRIAL FINISHED: %s' % reason)
                print('Fresh near-zero feedback after zero requests: %s' % self.stop_feedback)
                print('Not a firmware watchdog/fault-stop test. No automatic retry.')
        return True


class WebDashboard(server.Dashboard):
    def __init__(self):
        server.Dashboard.__init__(self, ros=True)
        self.mode = 'web_crawl_one_shot'
        self.gate = None

    def status(self):
        state = server.Dashboard.status(self)
        state['motor_output'] = True  # capability, not proof of physical movement
        state['crawl'] = self.gate.snapshot() if self.gate else None
        return state


class WebHandler(server.Handler):
    def do_GET(self):
        if not self.valid_host():
            return self.json(403, {'error': 'Use the laptop loopback SSH tunnel'})
        path = server.urlsplit(self.path).path
        assets = {'/': ('web_crawl.html', 'text/html; charset=utf-8'),
                  '/web_crawl.js': ('web_crawl.js', 'application/javascript; charset=utf-8')}
        if path in assets:
            name, mime = assets[path]
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', name), 'rb') as handle:
                return self.respond(200, handle.read(), mime)
        return server.Handler.do_GET(self)

    def operation(self, path, data):
        gate = self.server.app.gate
        if path == '/api/crawl/stop':
            gate.stop()
            return self.json(200, gate.snapshot())
        if path == '/api/crawl/prepare':
            return self.json(200, {'token': gate.prepare(str(data.get('owner', '')))})
        if path == '/api/crawl/command':
            return self.json(200, gate.command(data.get('owner'), data.get('token'),
                                              data.get('sequence'), data.get('action')))
        return self.json(404, {'error': 'Only the one-shot crawl operations exist in this mode'})


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Supervised one-shot browser crawl. Default OFFLINE.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='Existing subscription-only readiness check; no server/publisher.')
    group.add_argument('--live', action='store_true', help='Interactive terminal permit for ONE browser hold.')
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.check:
        return crawl.main(['--check'])
    if not args.live:
        print('OFFLINE ONLY. No ROS, server, publisher or movement.')
        print('One supervised forward request: 0.03 m/s, at most 0.4 s; best-effort zeros.')
        print('--check reads readiness; --live requires interactive terminal + browser confirmation.')
        return 0
    app = WebDashboard()
    reader = monitor = publisher = http = worker = None
    feedback = crawl.Feedback(app.clock)
    try:
        import rospy
        import rosgraph
        from geometry_msgs.msg import Twist
        # Bind before enabling anything: fail if the old viewer still owns 8765.
        http = server.LocalServer(('127.0.0.1', 8765), app, WebHandler)
        reader = server.RosReader(app, 3.0)
        if rospy.get_param('/use_sim_time', False):
            raise ValueError('Refusing physical test with simulated time')
        monitor = crawl.RosFeedback(rospy, rosgraph, feedback, app.closed)
        def signal_stop(signum, frame):
            app.closed.set()
        for name in ('SIGINT', 'SIGTERM', 'SIGHUP'):
            if hasattr(signal, name):
                signal.signal(getattr(signal, name), signal_stop)
        def readiness(moving):
            if app.closed.is_set() or rospy.is_shutdown():
                return 'Dashboard closing or ROS stopped'
            issue = feedback.problem(moving=moving)
            if issue:
                return issue
            with app.lock:
                image = app.frames.get('rgb')
                if not image or app.clock() - image['received'] >= CAMERA_AGE:
                    return 'Need a recent colour-camera message'
            if publisher is not None and publisher.get_num_connections() != 1:
                return 'Isolated controller connection is not unique'
            return None
        deadline = app.clock() + 10.0
        while not app.closed.is_set() and app.clock() < deadline and readiness(False):
            app.closed.wait(0.05)
        if readiness(False):
            raise ValueError(readiness(False))
        print('This permits ONE browser trial in the next 60 seconds, not immediate movement.')
        if not crawl.confirm(app.closed, app.clock):
            print('Cancelled: no Publisher created.')
            return 0
        if readiness(False):
            raise ValueError(readiness(False))
        publisher = rospy.Publisher(crawl.COMMAND, Twist, queue_size=1, latch=False, tcp_nodelay=True)
        deadline = app.clock() + 3.0
        while not app.closed.is_set() and publisher.get_num_connections() != 1 and app.clock() < deadline:
            app.closed.wait(0.02)
        if readiness(False):
            raise ValueError(readiness(False))
        def emit(speed):
            message = Twist()
            message.linear.x = speed
            publisher.publish(message)
        app.gate = WebGate(readiness, emit, app.clock)
        def run_worker():
            while not app.closed.is_set() and not app.gate.pending.wait(0.02):
                app.gate.snapshot()
            if not app.closed.is_set():
                try:
                    app.gate.run_once(threading.Event().wait, feedback.stopped_since)
                except Exception as error:
                    print('WEB WORKER ERROR: %s. Use physical power-off if abnormal.' % error, file=sys.stderr)
        worker = threading.Thread(target=run_worker)
        worker.daemon = True
        worker.start()
        http.timeout = 0.1
        print('ONE-SHOT WEB MODE: http://127.0.0.1:8765/ | refresh laptop page')
        print('Prepare, then HOLD Forward. Release/Stop requests cancellation. No reverse/steering.')
        print('Direct line of sight + reachable main power required; camera is not validated driving feedback.')
        while not app.closed.is_set():
            http.handle_request()
            app.gate.snapshot()
        return 0
    except Exception as error:
        print('WEB MODE REFUSED/FAILED: %s' % error, file=sys.stderr)
        return 2
    finally:
        app.closed.set()
        if app.gate:
            app.gate.stop('Server closing')
        # Join pulse cleanup before unregistering its publisher or closing ROS.
        if worker:
            worker.join(4.0)
            if worker.is_alive():
                print('Worker cleanup did not finish; physical stopping NOT verified.', file=sys.stderr)
        if publisher:
            publisher.unregister()
        if monitor:
            monitor.subscriber.unregister()
        if reader:
            reader.close()
        if http:
            http.server_close()


if __name__ == '__main__':
    sys.exit(main())
