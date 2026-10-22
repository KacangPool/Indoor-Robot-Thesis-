#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Personal robot-side hub helper. Python 2.7/3.6; no motion publisher.

Fixed services only; reuse registrations, do not kill unrelated processes.
No root, shell endpoint, Wi-Fi/boot change or automatic movement/arming.
"""
from __future__ import print_function
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import time
import uuid
try:
    import xmlrpc.client as xmlrpc
    import http.client as httplib
    from urllib.request import Request, urlopen
    from urllib.parse import urlsplit
except ImportError:
    import xmlrpclib as xmlrpc
    import httplib
    from urllib2 import Request, urlopen
    from urlparse import urlsplit

VERSION = '0.13'
BASE = '/fahad_base_crawl_check'
COMMAND = '/fahad/crawl_test/cmd_vel'
RUNTIME_FILES = ('server.py', 'manual_drive.py', 'control.py', 'crawl_test.py',
                 'base_crawl_check.launch', 'dist/index.html', 'dist/app.js',
                 'dist/joystick.js', 'dist/controls.css', 'dist/style.css')
RUNTIME_FILES += ('settings.py', 'sensor_models.py', 'sensor_state.py',
                  'ros_reader.py', 'dist/sensor_view.js')


class TimeoutTransport(xmlrpc.Transport):
    def make_connection(self, host):
        return httplib.HTTPConnection(host, timeout=2)


def graph_snapshot():
    uri = os.environ.get('ROS_MASTER_URI', 'http://localhost:11311')
    parts = urlsplit(uri)
    if parts.scheme != 'http' or parts.hostname not in ('localhost', '127.0.0.1'):
        raise RuntimeError('Hub requires the established robot-local ROS master; settings were not changed')
    try:
        master = xmlrpc.ServerProxy(uri, transport=TimeoutTransport())
        code, unused, state = master.getSystemState('/fahad_hub_probe')
        if code != 1:
            raise RuntimeError('Master refused graph request')
        publishers, subscribers, services = [dict(items) for items in state]
        nodes = sorted(set(n for items in state for topic, names in items for n in names))
        return {'reachable': True, 'publishers': publishers, 'subscribers': subscribers, 'nodes': nodes}
    except Exception:
        return {'reachable': False, 'publishers': {}, 'subscribers': {}, 'nodes': [],
                'error': 'ROS master unavailable or graph request timed out'}


def http_json(path, data=None, key=None):
    headers = {}
    encoded = None
    if data is not None:
        encoded = json.dumps(data).encode('utf8')
        headers = {'Content-Type': 'application/json', 'Origin': 'http://127.0.0.1:8765',
                   'X-Dashboard-Key': key or ''}
    response = urlopen(Request('http://127.0.0.1:8765' + path, encoded, headers), timeout=2)
    try:
        raw = response.read(262145)
        if len(raw) > 262144:
            raise RuntimeError('Dashboard response too large')
        return json.loads(raw.decode('utf8'))
    finally:
        response.close()


def dashboard_snapshot():
    try:
        result = http_json('/api/status')
        if not isinstance(result, dict) or 'control' not in result or 'boot_id' not in result:
            return None
        return result
    except Exception:
        return None


def stop_drive():
    # Only a stop request, never arm/drive/neutral heartbeat. Key stays in RAM.
    bootstrap = http_json('/api/bootstrap')
    return http_json('/api/drive/stop', {}, bootstrap['key'])


def process_info(pid):
    try:
        if os.stat('/proc/%d' % pid).st_uid != os.geteuid():
            return None
        with open('/proc/%d/cmdline' % pid, 'rb') as handle:
            argv = [x.decode('utf8', 'replace') for x in handle.read().split(b'\0') if x]
        with open('/proc/%d/stat' % pid) as handle:
            fields = handle.read().rsplit(')', 1)[1].split()
        if fields[0] == 'Z':
            return None
        return {'pid': pid, 'argv': argv, 'start': fields[19], 'group': int(fields[2])}
    except (IOError, OSError, ValueError, IndexError):
        return None


def processes():
    return [p for p in (process_info(int(n)) for n in os.listdir('/proc') if n.isdigit()) if p]


def digest(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def bundle_id(files):
    raw = json.dumps({'version': VERSION, 'files': files}, sort_keys=True, separators=(',', ':')).encode('utf8')
    return hashlib.sha256(raw).hexdigest()


def atomic_replace(source, destination):
    # Python 2 on the robot uses POSIX rename; Python 3 also permits portable
    # Windows fixture tests without unlinking an existing destination first.
    getattr(os, 'replace', os.rename)(source, destination)


class Manager(object):
    def __init__(self, fahad=None, graph=None, dashboard=None, proc=None):
        self.fahad = os.path.abspath(fahad or os.path.expanduser('~/fahad'))
        if os.path.realpath(self.fahad) != self.fahad:
            raise RuntimeError('Personal workspace is a symlink; refusing automatic writes')
        self.root = os.path.join(self.fahad, 'robot_hub')
        self.runtime = os.path.join(self.fahad, 'remote_dashboard_web_trial')
        self.graph = graph or graph_snapshot
        self.dashboard = dashboard or dashboard_snapshot
        self.proc = proc or processes

    def safe(self, path):
        path = os.path.abspath(path)
        if not path.startswith(self.fahad + os.sep) or os.path.realpath(path) != path:
            raise RuntimeError('Path is outside personal workspace or uses symlinks')
        return path

    def directory(self, path):
        path = self.safe(path)
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def read_state(self):
        path = self.safe(os.path.join(self.root, 'services.json'))
        try:
            with open(path) as handle:
                return json.load(handle)
        except IOError:
            return {}

    def write_json(self, path, data):
        path = self.safe(path)
        self.directory(os.path.dirname(path))
        temporary = path + '.tmp-' + uuid.uuid4().hex
        with open(temporary, 'w') as handle:
            json.dump(data, handle, sort_keys=True)
        os.chmod(temporary, 0o600)
        atomic_replace(temporary, path)

    def status(self):
        graph = self.graph()
        pubs, subs, nodes = graph['publishers'], graph['subscribers'], set(graph['nodes'])
        dashboard = self.dashboard()
        running = self.proc()
        def has_token(names):
            return any(any(os.path.basename(a) in names for a in p['argv']) for p in running)
        camera_ready = bool(pubs.get('/camera/rgb/image_raw') and pubs.get('/darknet_ros/detection_image'))
        camera_partial = bool('/camera/driver' in nodes or '/darknet_ros' in nodes or has_token(('darknet_ros', 'yolo_v3.launch')))
        lidar_pubs = pubs.get('/scan', [])
        lidar_partial = has_token(('lsn10', 'rplidarNode', 'lslidar_m10_driver_node', 'wheeltec_lidar.launch'))
        base_ready = (set(pubs.get('/odom', [])) == set([BASE]) and
                      set(subs.get(COMMAND, [])) == set([BASE]) and not pubs.get('/cmd_vel') and
                      not any(BASE in names and topic != COMMAND and 'cmd_vel' in topic for topic, names in subs.items()) and
                      not any(not n.startswith('/fahad_dashboard_reader_') for n in pubs.get(COMMAND, [])))
        base_partial = bool(BASE in nodes or pubs.get('/odom') or subs.get(COMMAND) or
                            pubs.get('/cmd_vel') or has_token(('wheeltec_robot_node', 'base_crawl_check.launch')))
        services = {
            'camera': 'ready' if camera_ready else 'partial' if camera_partial else 'stopped',
            'lidar': 'ready' if len(lidar_pubs) == 1 else 'conflict' if len(lidar_pubs) > 1 else 'partial' if lidar_partial else 'stopped',
            'base': 'ready' if base_ready else 'conflict' if base_partial else 'stopped',
            'dashboard': 'ready' if dashboard else 'partial' if self.dashboard_processes(running) else 'stopped'}
        owned = self.read_state()
        for name, record in owned.items():
            current = next((p for p in running if p['pid'] == record.get('pid')), None)
            record['alive'] = bool(current and current['start'] == record.get('start') and current['argv'] == record.get('argv'))
        try:
            with open(self.safe(os.path.join(self.runtime, 'hub_manifest.json'))) as handle:
                installed = json.load(handle).get('bundle_id')
        except (IOError, ValueError):
            installed = None
        return {'agent_version': VERSION, 'services': services, 'graph': graph, 'dashboard': dashboard,
                'owned': owned, 'runtime_ok': self.runtime_matches(),
                'installed_bundle': installed,
                'device_lidar': os.path.exists('/dev/wheeltec_lidar')}

    def dashboard_processes(self, running=None):
        script = os.path.join(self.runtime, 'server.py')
        return [p for p in (self.proc() if running is None else running)
                if script in p['argv'] and p['argv'] and os.path.basename(p['argv'][0]).startswith('python')]

    def runtime_matches(self):
        try:
            with open(self.safe(os.path.join(self.runtime, 'hub_manifest.json'))) as handle:
                manifest = json.load(handle)
            return (manifest['version'] == VERSION and manifest.get('bundle_id') == bundle_id(manifest['files']) and set(manifest['files']) == set(RUNTIME_FILES) and
                    all(digest(self.safe(os.path.join(self.runtime, name))) == manifest['files'][name] for name in RUNTIME_FILES))
        except (IOError, KeyError, ValueError):
            return False

    def start(self, name):
        if name not in ('camera', 'lidar', 'base', 'dashboard'):
            raise RuntimeError('Unknown service')
        status = self.status()
        if status['services'][name] == 'ready':
            return {'action': 'reused', 'service': name}
        if status['services'][name] != 'stopped':
            raise RuntimeError('%s is partial/conflicting; no duplicate was started' % name)
        if status['owned'].get(name, {}).get('alive'):
            return {'action': 'starting', 'service': name}
        if name != 'camera' and not status['graph']['reachable']:
            raise RuntimeError('Start/check camera and ROS master first')
        if name == 'lidar' and not status['device_lidar']:
            raise RuntimeError('/dev/wheeltec_lidar missing; device rules were not changed')
        if name in ('base', 'dashboard') and not status['runtime_ok']:
            raise RuntimeError('Runtime not fully installed/verified; install update first')
        if name == 'dashboard' and status['services']['base'] != 'ready':
            raise RuntimeError('Expected isolated base is not ready; driving server not started')
        commands = {'camera': ['roslaunch', 'darknet_ros', 'yolo_v3.launch'],
                    'lidar': ['roslaunch', 'turn_on_wheeltec_robot', 'wheeltec_lidar.launch'],
                    'base': ['roslaunch', os.path.join(self.runtime, 'base_crawl_check.launch')],
                    'dashboard': ['python', '-u', os.path.join(self.runtime, 'server.py'), '--ros', '--drive']}
        logs = self.directory(os.path.join(self.root, 'logs'))
        with open(os.path.join(logs, name + '.log'), 'ab') as output, open(os.devnull, 'rb') as input_file:
            child = subprocess.Popen(commands[name], stdin=input_file, stdout=output, stderr=subprocess.STDOUT,
                                     close_fds=True, preexec_fn=os.setsid)
        info = process_info(child.pid)
        if not info:
            raise RuntimeError('%s exited immediately; inspect its hub log' % name)
        record = self.read_state()
        record[name] = info
        self.write_json(os.path.join(self.root, 'services.json'), record)
        return {'action': 'started', 'service': name, 'pid': child.pid}

    def logs(self, name):
        if name not in ('camera', 'lidar', 'base', 'dashboard'):
            raise RuntimeError('Unknown service')
        path = self.safe(os.path.join(self.root, 'logs', name + '.log'))
        try:
            with open(path, 'rb') as handle:
                handle.seek(0, os.SEEK_END)
                size = handle.tell()
                handle.seek(max(0, size - 12000))
                text = handle.read().decode('utf8', 'replace')
            return {'text': text}
        except IOError:
            return {'text': 'No hub-owned log: service may be reused from an external terminal.'}

    def prepare_update(self):
        candidates = self.dashboard_processes()
        dashboard = self.dashboard()
        if len(candidates) > 1:
            raise RuntimeError('Multiple personal dashboard processes; refusing automatic replacement')
        if candidates:
            control = (dashboard or {}).get('control', {})
            if not dashboard:
                raise RuntimeError('Existing dashboard does not respond; inspect it before replacing')
            if dashboard.get('motor_output'):
                if control.get('armed') or control.get('stage') not in ('disabled',) or control.get('zero_failures'):
                    raise RuntimeError('Release controls and click dashboard Stop first; active/faulted session was not restarted')
                if not control.get('ready'):
                    raise RuntimeError('Need fresh stationary/readiness feedback before replacing the live dashboard')
                stop_drive()
            candidate = candidates[0]
            current = process_info(candidate['pid'])
            if not current or current['start'] != candidate['start'] or current['argv'] != candidate['argv']:
                raise RuntimeError('Dashboard process identity changed; not terminated')
            os.kill(current['pid'], signal.SIGTERM)
            deadline = time.time() + 8
            while self.dashboard_processes() and time.time() < deadline:
                time.sleep(.1)
            if self.dashboard_processes():
                raise RuntimeError('Normal dashboard cleanup not complete; no force-kill')
        try:
            connection = socket.create_connection(('127.0.0.1', 8765), timeout=.5)
        except socket.error:
            return {'ready': True}
        else:
            connection.close()
            raise RuntimeError('Robot port 8765 still occupied by another process; it was not killed')

    def deploy(self, stage):
        if not re.match(r'^[0-9a-f]{32}$', stage):
            raise RuntimeError('Invalid staging identity')
        if self.dashboard_processes():
            raise RuntimeError('Dashboard still running; runtime was not overwritten')
        source = self.safe(os.path.join(self.root, 'staging', stage))
        with open(self.safe(os.path.join(source, 'manifest.json'))) as handle:
            manifest = json.load(handle)
        if manifest.get('version') != VERSION or set(manifest.get('files', {})) != set(RUNTIME_FILES) or manifest.get('bundle_id') != bundle_id(manifest['files']):
            raise RuntimeError('Incomplete or wrong-version runtime bundle')
        for name in RUNTIME_FILES:
            path = self.safe(os.path.join(source, name))
            if os.path.getsize(path) > 524288 or digest(path) != manifest['files'][name]:
                raise RuntimeError('Runtime checksum failed; not installed')
        self.directory(self.runtime)
        backup = self.directory(os.path.join(self.root, 'backups', stage))
        # Manifest is written last: interrupted/partial installs cannot start a
        # managed base/dashboard. Existing files are copied into a private backup.
        for name in RUNTIME_FILES:
            destination = self.safe(os.path.join(self.runtime, name))
            self.directory(os.path.dirname(destination))
            if os.path.exists(destination):
                saved = self.safe(os.path.join(backup, name))
                self.directory(os.path.dirname(saved))
                if not os.path.exists(saved):
                    shutil.copy2(destination, saved)
            temporary = destination + '.hub-' + stage
            shutil.copyfile(os.path.join(source, name), temporary)
            os.chmod(temporary, 0o600)
            atomic_replace(temporary, destination)
        self.write_json(os.path.join(self.runtime, 'hub_manifest.json'), manifest)
        return {'installed': VERSION, 'verified': self.runtime_matches(), 'backup': backup}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('status', 'start', 'logs', 'stop-drive', 'prepare-update', 'deploy'))
    parser.add_argument('value', nargs='?')
    args = parser.parse_args(argv)
    try:
        manager = Manager()
        if args.action == 'status': result = manager.status()
        elif args.action == 'start': result = manager.start(args.value)
        elif args.action == 'logs': result = manager.logs(args.value)
        elif args.action == 'stop-drive': result = stop_drive()
        elif args.action == 'prepare-update': result = manager.prepare_update()
        else: result = manager.deploy(args.value)
        response = {'ok': True, 'result': result}
    except Exception as exc:
        response = {'ok': False, 'error': str(exc)[:1500]}
    print('FAHAD_HUB_JSON:' + json.dumps(response, allow_nan=False))


if __name__ == '__main__': main()
