"""Explicit bounded normalized-session IO. No ROS/network/model side effects."""
import hashlib
import json
import re
from pathlib import Path
from .recording import write_json
from .semantic_scene import semantic_snapshot

MAX_BYTES = 2 * 1024 * 1024
MAX_SNAPSHOTS = 100


def identifier(value):
    if not isinstance(value, str) or not re.match(r'^[A-Za-z0-9_.-]{1,100}$', value):
        raise ValueError('Use a short non-personal run/map/calibration identifier')
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(',', ':')).encode('utf8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def decode(data):
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise ValueError('JSON input exceeds 2 MiB')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('Non-finite JSON number')
    return json.loads(data.decode('utf8'), object_pairs_hook=pairs, parse_constant=constant)


def read_json(path):
    with Path(path).open('rb') as stream:
        return decode(stream.read(MAX_BYTES + 1))


def evaluate_session(session):
    if not isinstance(session, dict) or type(session.get('schema_version')) is not int or session.get('schema_version') != 1 or session.get('kind') != 'fusion_session':
        raise ValueError('Expected normalized fusion_session schema 1')
    for field in ('run_id', 'map_id', 'calibration_id', 'detector_id'):
        identifier(session.get(field))
    if session.get('mode') not in ('synthetic', 'recorded'):
        raise ValueError('Explicit synthetic/recorded mode required')
    snapshots = session.get('snapshots')
    if not isinstance(snapshots, list) or not 1 <= len(snapshots) <= MAX_SNAPSHOTS:
        raise ValueError('Session needs 1..100 normalized snapshots')
    if len(canonical(session)) > MAX_BYTES:
        raise ValueError('Oversized normalized session')
    results = []
    rays, boxes, work = 0, 0, 0
    for snapshot in snapshots:
        if not isinstance(snapshot, dict) or snapshot.get('mode') != session['mode'] or snapshot.get('calibration_id') != session['calibration_id']:
            raise ValueError('Mixed session mode/calibration is forbidden')
        scan, detections = snapshot.get('scan'), snapshot.get('detections')
        if not isinstance(scan, dict) or not isinstance(detections, dict) or not isinstance(scan.get('ranges'), list) or not isinstance(detections.get('boxes'), list):
            raise ValueError('Missing normalized scan/detection arrays')
        rays += len(scan['ranges'])
        boxes += len(detections['boxes'])
        work += len(scan['ranges'])*(len(detections['boxes'])+1)
        if rays > 20000 or boxes > 1000 or work > 2000000:
            raise ValueError('Session calculation budget exceeded; split the session')
        results.append(semantic_snapshot(snapshot))
    return results


def save_run(directory, session):
    """New directory only. Replay calls calculations, never a ROS publisher."""
    from .semantic_memory import object_layer
    results = evaluate_session(session)
    layer = object_layer(session, results)
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=False)
    write_json(str(target / 'session.json'), session)
    write_json(str(target / 'semantic_layer.json'), layer)
    write_json(str(target / 'replay.json'), {
        'schema_version': 1, 'input_sha256': digest(session), 'scenes': results,
        'evaluation_time_basis': 'recorded_reference_stamp_not_current_live_time',
        'ros_replay': False, 'motor_output': False})
    hashes = {name: hashlib.sha256((target / name).read_bytes()).hexdigest()
              for name in ('session.json', 'semantic_layer.json', 'replay.json')}
    write_json(str(target / 'manifest.json'), {
        'schema_version': 1, 'files': hashes, 'mode': session['mode'],
        'run_id': session['run_id'], 'map_id': session['map_id'],
        'calibration_id': session['calibration_id'], 'detector_id': session['detector_id'],
        'input_sha256': digest(session), 'motor_output': False,
        'limits': 'Historical offline evidence, not live obstacles, SLAM or calibration proof.'})
    return layer


def verify_run(directory):
    """Fixed local files only; manifest cannot select paths or symlink targets."""
    root = Path(directory).resolve()
    names = ('manifest.json', 'session.json', 'semantic_layer.json', 'replay.json')
    for name in names:
        path = root / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 32 * MAX_BYTES:
            raise ValueError('Missing, linked or oversized run file')
    manifest = read_json(root / 'manifest.json')
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1 or not isinstance(manifest.get('files'), dict) or set(manifest['files']) != set(names[1:]):
        raise ValueError('Unexpected manifest file set')
    for name in names[1:]:
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != manifest['files'][name]:
            raise ValueError('Run hash mismatch')
    session = read_json(root / 'session.json')
    if digest(session) != manifest.get('input_sha256'):
        raise ValueError('Session identity mismatch')
    if any(manifest.get(k) != session.get(k) for k in ('mode', 'run_id', 'map_id', 'calibration_id', 'detector_id')):
        raise ValueError('Manifest provenance mismatch')
    evaluate_session(session)
    return session
