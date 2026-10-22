"""Bounded, allowlisted support reports and structured event logs (laptop only).

No connection, file creation, logging handler or threads are started on import.
Raw SSH output, activity text, commands, images and exception text are excluded.
"""
import collections
import datetime
import json
import logging
from logging.handlers import RotatingFileHandler
import math
import re
import uuid
from agent import VERSION

SERVICES = ('camera', 'lidar', 'base', 'dashboard')
EVENTS = {'task_started', 'task_finished', 'task_failed', 'status_checked', 'disconnect'}
STATES = {'ready', 'stopped', 'partial', 'conflict', 'disabled', 'armed', 'holding',
          'braking', 'fault', 'spent', 'preview', 'waiting', 'live', 'stale',
          'no_publisher', 'waiting_messages', 'no_valid_returns', 'invalid',
          'multiple_publishers', 'ros_read_only', 'ros_manual_ackermann'}


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def number(value):
    try:
        return value if type(value) in (int, float) and math.isfinite(value) else None
    except OverflowError:
        return None


def mapping(value):
    return value if isinstance(value, dict) else {}


def label(value):
    return value if isinstance(value, str) and value in STATES else 'unknown'


def version(value):
    return value if isinstance(value, str) and re.fullmatch(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?', value) else None


def report(status, snapshot_age_s=None, run_id=None, events=(), demo=False):
    """Project known fields only. This analyzes an existing snapshot; never probes ROS."""
    status = mapping(status)
    snapshot_age_s = number(snapshot_age_s)
    if snapshot_age_s is not None and snapshot_age_s < 0:
        snapshot_age_s = None
    run_id = run_id if isinstance(run_id, str) and re.fullmatch('[a-f0-9]{32}', run_id) else None
    dash = mapping(status.get('dashboard'))
    scan, control = mapping(dash.get('scan')), mapping(dash.get('control'))
    graph, owned = mapping(status.get('graph')), mapping(status.get('owned'))
    cameras = {}
    for name in ('rgb', 'yolo'):
        item = mapping(mapping(dash.get('cameras')).get(name))
        cameras[name] = {'available': item.get('available') is True, 'arrival_age_s': number(item.get('age_s'))}
    services = {name: label(mapping(status.get('services')).get(name)) for name in SERVICES}
    issues = []
    if snapshot_age_s is None or snapshot_age_s > 10:
        issues.append('STATUS_AGE_UNKNOWN_OR_OLD')
    if graph.get('reachable') is not True:
        issues.append('ROS_MASTER_NOT_REPORTED_REACHABLE')
    if not cameras['rgb']['available']:
        issues.append('NO_RECENT_RGB_REPORTED')
    if scan.get('available') is not True:
        issues.append('NO_CURRENT_VALID_SCAN_REPORTED')
    if scan.get('state') == 'waiting_messages':
        issues.append('SCAN_CONNECTION_WITHOUT_RECEIVED_MESSAGES')
    if scan.get('state') == 'multiple_publishers':
        issues.append('MULTIPLE_SCAN_SOURCES')
    if dash and dash.get('version') != VERSION:
        issues.append('DASHBOARD_SOURCE_VERSION_MISMATCH')
    bundle = status.get('installed_bundle')
    bundle = bundle if isinstance(bundle, str) and re.fullmatch('[a-f0-9]{64}', bundle) else None
    return {'schema_version': 1, 'captured_at_utc': utc_now(), 'run_id': run_id,
            'evidence': 'demo_snapshot' if demo else 'last_checked_snapshot_not_a_new_probe',
            'snapshot_age_s': number(snapshot_age_s), 'local_source_version': VERSION,
            'agent_version': version(status.get('agent_version')), 'dashboard_version': version(dash.get('version')),
            'installed_bundle_sha256': bundle, 'runtime_verified_by_agent': status.get('runtime_ok') is True,
            'services': services, 'ros_master_reported_reachable': graph.get('reachable') is True,
            'cameras': cameras,
            'scan': {'state': label(scan.get('state')), 'available': scan.get('available') is True,
                     'arrival_rate_hz': number(scan.get('arrival_rate_hz')),
                     'arrival_age_s': number(scan.get('last_message_age_s')),
                     'publisher_connections': number(scan.get('publisher_connections')),
                     'messages_received': number(scan.get('messages_received'))},
            'control': {'stage': label(control.get('stage')), 'armed': control.get('armed') is True,
                        'ready': control.get('ready') is True},
            'owned_processes': {name: {'alive': mapping(owned.get(name)).get('alive') is True,
                                      'pid': number(mapping(owned.get(name)).get('pid'))} for name in SERVICES},
            'runtime': {key: number(mapping(status.get('runtime')).get(key))
                        for key in ('python_major', 'python_minor', 'disk_free_bytes')},
            'issues': issues, 'events': [clean_event(event) for event in list(events)[-200:]],
            'limitations': ['No images, commands, passwords, tokens, raw logs or model/calibration verification included.',
                            'Availability is reported by the prior status snapshot, not guaranteed live now.',
                            'Process registration is not sensor freshness; report does not diagnose a hardware root cause.',
                            'No restart, configuration change or motion request was made by report generation.']}


def clean_event(event):
    """Do not trust callers to have removed secrets in extra fields."""
    event = event if isinstance(event, dict) else {}
    name = event.get('event')
    return {'event': name if isinstance(name, str) and name in EVENTS else 'unknown',
            'elapsed_s': number(event.get('elapsed_s'))}


class SessionLog:
    def __init__(self, clock, path=None):
        self.clock, self.started = clock, clock()
        self.run_id = uuid.uuid4().hex
        self.events = collections.deque(maxlen=200)
        self.logger = logging.getLogger('fahad.hub.' + self.run_id)
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)
        self.handler = None
        if path is not None:
            self.handler = RotatingFileHandler(str(path), maxBytes=262144, backupCount=2, encoding='utf8')
            self.handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(self.handler)

    def record(self, event):
        if event not in EVENTS:
            raise ValueError('Unknown structured event')
        entry = clean_event({'event': event, 'elapsed_s': round(self.clock() - self.started, 3)})
        self.events.append(entry)
        # Only fixed event names, generated identifiers and time reach the file.
        self.logger.info(json.dumps(dict(entry, schema_version=1, run_id=self.run_id,
                                        component='robot_hub', time_utc=utc_now()), allow_nan=False))

    def close(self):
        if self.handler:
            self.logger.removeHandler(self.handler)
            self.handler.close()
            self.handler = None
