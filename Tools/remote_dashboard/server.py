#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Local robot dashboard: default ROS subscriptions and motor-free rehearsal.

Python 2.7 / 3.6+ syntax. Explicit --ros --drive opts in to a separate guarded
car-like publisher adapter; default stays motor-free. No shell/service/vendor/
boot changes. Loopback + SSH only.
"""
from __future__ import print_function

import argparse
import collections
import hmac
import json
import math
import os
import signal
import sys
import threading
import uuid
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn
    from urllib.parse import urlsplit, parse_qs
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn
    from urlparse import urlsplit, parse_qs

from control import RehearsalControl, monotonic_clock


from settings import ASSETS, TOPICS
from sensor_models import finite, planar_pose, occupancy_summary, scan_summary
from sensor_state import Dashboard
from ros_reader import RosReader


class LocalServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, app, handler=None):
        self.app = app
        self.slots = threading.BoundedSemaphore(8)
        HTTPServer.__init__(self, address, handler or Handler)

    def process_request(self, request, address):
        if not self.slots.acquire(False):
            self.shutdown_request(request)
            return
        try:
            ThreadingMixIn.process_request(self, request, address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            ThreadingMixIn.process_request_thread(self, request, address)
        finally:
            self.slots.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'FahadDashboard/0.1'
    sys_version = ''

    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.connection.settimeout(3.0)

    def log_message(self, fmt, *args):
        # Never log headers, session tokens or URL queries.
        if args and str(args[1] if len(args) > 1 else '').startswith('5'):
            print('Dashboard request failed', file=sys.stderr)

    def respond(self, code, body, mime='application/json; charset=utf-8'):
        if not isinstance(body, bytes):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self' blob:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def json(self, code, value):
        self.respond(code, json.dumps(value, allow_nan=False))

    def valid_host(self):
        port = self.server.server_address[1]
        return self.headers.get('Host') in ('127.0.0.1:%d' % port, 'localhost:%d' % port)

    def do_GET(self):
        if not self.valid_host():
            self.json(403, {'error': 'Use the loopback address or SSH tunnel'})
            return
        path = urlsplit(self.path).path
        if path in ASSETS:
            filename, mime = ASSETS[path]
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', filename), 'rb') as handle:
                self.respond(200, handle.read(), mime)
        elif path == '/api/bootstrap':
            self.json(200, {'key': self.server.app.key, 'boot_id': self.server.app.boot_id})
        elif path == '/api/status':
            self.json(200, self.server.app.status())
        elif path == '/api/map':
            revision = parse_qs(urlsplit(self.path).query).get('revision', [None])[0]
            self.json(200, self.server.app.map_status(revision))
        elif path in ('/api/frame/rgb', '/api/frame/yolo'):
            data = self.server.app.frame(path.rsplit('/', 1)[1])
            if data is None:
                self.json(503, {'error': 'No recent camera message; old frames are hidden'})
            else:
                self.respond(200, data, 'image/jpeg')
        else:
            self.json(404, {'error': 'Not found'})

    def do_POST(self):
        app = self.server.app
        if not self.valid_host():
            self.json(403, {'error': 'Invalid Host'})
            return
        expected_origins = ('http://127.0.0.1:%d' % self.server.server_address[1],
                            'http://localhost:%d' % self.server.server_address[1])
        if self.headers.get('Origin') not in expected_origins:
            self.json(403, {'error': 'Same-origin request required'})
            return
        key = self.headers.get('X-Dashboard-Key', '')
        if not hmac.compare_digest(key.encode('utf-8'), app.key.encode('utf-8')):
            self.json(403, {'error': 'Reload this local dashboard'})
            return
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self.json(415, {'error': 'JSON required'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096 or self.headers.get('Transfer-Encoding'):
                raise ValueError('Invalid request size')
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            if not isinstance(data, dict):
                raise ValueError('JSON object required')
            path = urlsplit(self.path).path
            self.operation(path, data)
        except (ValueError, TypeError, OverflowError):
            # Auth/origin checks above still fail closed without this payload.
            # An authenticated malformed/rejected command must not be labelled
            # a network timeout if a backend fault explains its rejection.
            self.json(400, {'error': 'Invalid, expired or conflicting control request',
                            'control': app.control.snapshot()})

    def operation(self, path, data):
        """Default server remains motor-free; specialised servers opt in separately."""
        app = self.server.app
        if path.startswith('/api/drive/'):
            if app.drive is None:
                return self.json(404, {'error': 'Live drive mode is not enabled'})
            if path == '/api/drive/stop':
                # Automatic browser cleanup is scoped to the owner's generation.
                # Empty body remains an explicit global operator/Hub Stop.
                with app.control.lock:
                    if 'owner' not in data or (data['owner'] == app.control.owner and
                            (data.get('generation') is None or data['generation'] == app.control.generation)):
                        app.control.stop()
                return self.json(200, app.control.snapshot())
            if path == '/api/drive/arm':
                generation = app.control.arm(str(data.get('owner', '')))
                return self.json(200, {'generation': generation})
            if path == '/api/drive/command':
                return self.json(200, app.control.command(data.get('owner'), data.get('generation'),
                                                         data.get('sequence'), data.get('action'),
                                                         **{k: data[k] for k in ('throttle', 'steering', 'motion') if k in data}))
            return self.json(404, {'error': 'Unknown drive operation'})
        if app.drive is not None:
            return self.json(404, {'error': 'Rehearsal operations are unavailable in live mode'})
        if path == '/api/rehearsal/stop':
            app.control.stop()
            self.json(200, app.control.snapshot())
        elif path == '/api/rehearsal/arm':
            generation = app.control.arm(str(data.get('owner', '')))
            self.json(200, {'generation': generation})
        elif path == '/api/rehearsal/command':
            self.json(200, app.control.command(data.get('owner'), data.get('generation'),
                                             data.get('sequence'), data.get('action')))
        else:
            self.json(404, {'error': 'No such operation; motor output is not implemented'})


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Local-only ROS viewer; default motor-free. --ros --drive enables supervised slow car-like controls.')
    parser.add_argument('--ros', action='store_true', help='Read existing camera/scan topics; starts no drivers.')
    parser.add_argument('--drive', action='store_true', help='Explicit live motor capability; page Enable then hold arrows or joystick. No terminal countdown.')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--fps', type=float, default=3.0, help='JPEG refresh cap per source (1-5), not detector FPS.')
    args = parser.parse_args(argv)
    if args.drive and not args.ros:
        parser.error('--drive requires --ros and the existing isolated base; preview is motor-free')
    if not 1024 <= args.port <= 65535:
        parser.error('--port must be 1024..65535')
    if not finite(args.fps) or not 1 <= args.fps <= 5:
        parser.error('--fps must be finite and 1..5')
    return args


def main(argv=None):
    args = parse_args(argv)
    app = Dashboard(ros=args.ros)
    reader = None
    server = None
    try:
        if args.ros:
            reader = RosReader(app, args.fps)
        server = LocalServer(('127.0.0.1', args.port), app)
        if args.drive:
            from manual_drive import RosManualDrive
            app.drive = RosManualDrive(app, reader.rospy)
            app.control = app.drive.control
            app.mode = 'ros_manual_ackermann'
    except Exception as error:
        app.closed.set()
        if app.drive:
            app.drive.close()
        if server:
            server.server_close()
        if reader:
            reader.close()
        print('Cannot start dashboard: %s' % error, file=sys.stderr)
        print('Use the existing ROS Python environment; do not upgrade ROS/Python. Nothing was launched or moved.', file=sys.stderr)
        return 2
    server.timeout = 0.1
    def request_stop(signum, frame):
        app.closed.set()
    for name in ('SIGINT', 'SIGTERM', 'SIGHUP'):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), request_stop)
    print('Fahad dashboard: http://127.0.0.1:%d/' % args.port)
    if args.drive:
        print('Mode: %s | LIVE MOTOR CAPABILITY | page Enable + arrows/joystick; release requests stop.' % app.mode)
        print('Buttons |speed| 0.03 m/s; joystick proportional up to 0.30 m/s; curvature <= 1/m.')
        print('Enable once, drive while held; no fixed hold cap. Speeds are requests, not measurements.')
        print('Release requests zero; fresh press after stationary feedback. Stop/fault disables session.')
        print('Direct observation + clear floor + reachable physical power-off required. No verified hardware watchdog.')
    else:
        print('Mode: %s | MOTOR OUTPUT DISCONNECTED | loopback only; use an SSH tunnel remotely.' % app.mode)
    try:
        while not app.closed.is_set():
            server.handle_request()
            app.control.snapshot()
    finally:
        app.closed.set()
        app.control.stop('Dashboard closed')
        if app.drive:
            app.drive.close()
        server.server_close()
        if reader:
            reader.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
