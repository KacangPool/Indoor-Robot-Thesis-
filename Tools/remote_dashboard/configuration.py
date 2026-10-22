"""Strict ordinary settings only; never configures motion, ROS startup or hosts.

Python 2.7/3.6 compatible. Reading is explicit; importing performs no file I/O.
"""
import json
import math
import os

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_config.json')
MAX_BYTES = 8192


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate configuration key')
        result[key] = value
    return result


def _keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError('Configuration has missing or unsupported fields')


def _fps(value):
    if type(value) not in (int, float) or not 1 <= value <= 5 or math.isnan(value) or math.isinf(value):
        raise ValueError('Configured fps must be a finite number in 1..5')
    return float(value)


def validate(value):
    _keys(value, ('schema_version', 'profiles'))
    if type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ValueError('Unsupported configuration schema')
    _keys(value['profiles'], ('preview', 'robot'))
    preview, robot = value['profiles']['preview'], value['profiles']['robot']
    _keys(preview, ('port', 'fps'))
    _keys(robot, ('fps',))
    port = preview['port']
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError('Preview port must be an integer in 1024..65535')
    return {'preview': {'port': port, 'fps': _fps(preview['fps'])},
            'robot': {'port': 8765, 'fps': _fps(robot['fps'])}}


def load(path=None):
    with open(path or DEFAULT_PATH, 'rb') as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('Configuration exceeds size limit')
    return validate(json.loads(data.decode('utf-8'), object_pairs_hook=_object))
