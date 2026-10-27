"""Laptop-only fusion workbench and normalized replay. No ROS or motor adapter."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from fahad_core.experiment import decode, canonical, evaluate_session, read_json, save_run, verify_run, MAX_BYTES
from fahad_core.semantic_memory import object_layer
from home_lab_scenes import cases, virtual_scene, session_for, demo_session


def evaluate_request(value):
    if not isinstance(value, dict):
        raise ValueError('Expected one workbench operation')
    index = 0
    if set(value) == {'scene'}:
        session = session_for([virtual_scene(value['scene'])])
    elif set(value) == {'case'}:
        i = value['case']
        if type(i) is not int or not 0 <= i < len(cases()):
            raise ValueError('Invalid case index')
        session = session_for([cases()[i]['snapshot']])
    elif set(value) <= {'session', 'index'} and 'session' in value:
        session, index = value['session'], value.get('index', 0)
    elif set(value) <= {'session_json', 'index'} and isinstance(value.get('session_json'), str):
        session, index = decode(value['session_json'].encode('utf8')), value.get('index', 0)
    else:
        raise ValueError('Unknown workbench operation')
    results = evaluate_session(session)
    if type(index) is not int or not 0 <= index < len(results):
        raise ValueError('Replay frame outside session')
    return {'session': session, 'index': index, 'scene': results[index],
            'snapshot': session['snapshots'][index], 'layer': object_layer(session, results),
            'time_basis': 'recorded_reference_not_current_time', 'motor_output': False}


class Handler(BaseHTTPRequestHandler):
    server_version, sys_version = 'FahadHomeLab/1', ''

    def log_message(self, *args):
        pass  # Never dump imported labels, payloads or exceptions into logs.

    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.connection.settimeout(5)

    def trusted(self):
        origin = 'http://127.0.0.1:%d' % self.server.server_port
        return self.headers.get('Host') == origin[7:] and self.headers.get('Origin') in (None, origin)

    def reply(self, status, data, content='application/json; charset=utf-8'):
        raw = canonical(data) if content.startswith('application/json') else data
        self.send_response(status)
        self.send_header('Content-Type', content)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if not self.trusted():
            return self.reply(403, {'error': 'Local origin required'})
        if self.path == '/':
            return self.reply(200, Path(__file__).with_name('home_lab.html').read_bytes(), 'text/html; charset=utf-8')
        if self.path == '/api/cases':
            return self.reply(200, [{'name': v['name'], 'explanation': v['explanation']} for v in cases()])
        return self.reply(404, {'error': 'No such offline route'})

    def do_POST(self):
        if not self.trusted():
            return self.reply(403, {'error': 'Local origin required'})
        if self.path != '/api/evaluate':
            return self.reply(404, {'error': 'No such offline route'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= MAX_BYTES or self.headers.get('Content-Type') != 'application/json':
                raise ValueError('Invalid content')
            value = decode(self.rfile.read(size))
            result = evaluate_request(value)
        except (ValueError, TypeError, KeyError, OverflowError, UnicodeError, RecursionError):
            return self.reply(400, {'error': 'Invalid bounded fusion input; check schema, frames, values and session identity.'})
        return self.reply(200, result)


def make_server(port=8878):
    if type(port) is not int or not (1024 <= port <= 65535 or port == 0):
        raise ValueError('Invalid local port')
    return HTTPServer(('127.0.0.1', port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--serve', action='store_true')
    mode.add_argument('--demo', action='store_true', help='Save a new synthetic replay/semantic-layer run')
    mode.add_argument('--replay', type=Path, help='Normalized session JSON or verified run directory; never rosbag play')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--port', type=int, default=8878)
    args = parser.parse_args(argv)
    if not (args.serve or args.demo or args.replay):
        parser.print_help()
        return 0
    try:
        if args.serve:
            server = make_server(args.port)
            print('Offline fusion lab: http://127.0.0.1:%d/ — NO ROBOT / NO MOTOR OUTPUT' % server.server_port, flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
        else:
            if args.output is None:
                parser.error('Choose a NEW --output directory')
            session = demo_session() if args.demo else verify_run(args.replay) if args.replay.is_dir() else read_json(args.replay)
            layer = save_run(args.output, session)
            print('Historical offline run saved; observations=%d; provisional static groups=%d; no robot replay.' %
                  (len(layer['observations']), len(layer['static_provisional_groups'])))
        return 0
    except (ValueError, TypeError, KeyError, OSError, ImportError) as error:
        print('Home lab could not complete: %s. No robot was contacted.' % type(error).__name__)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
