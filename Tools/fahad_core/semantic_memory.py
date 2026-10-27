"""Historical semantic layer, never occupancy or live navigation state. No I/O."""
from copy import deepcopy
from .experiment import digest, identifier
from .fusion_geometry import number
from .recording import frame_key

DYNAMIC = frozenset(('person', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe'))


def object_layer(session, scenes, merge_distance_m=0.25):
    distance = number(merge_distance_m)
    if not 0 < distance <= 1 or len(scenes) != len(session['snapshots']):
        raise ValueError('Invalid layer dimensions/merge distance')
    for key in ('run_id', 'map_id', 'calibration_id', 'detector_id'):
        identifier(session[key])
    if session.get('mode') not in ('synthetic', 'recorded'):
        raise ValueError('Missing evidence mode')
    events = {}
    for snapshot, scene in zip(session['snapshots'], scenes):
        if snapshot['mode'] != session['mode'] or snapshot['calibration_id'] != session['calibration_id']:
            raise ValueError('Mixed evidence is forbidden')
        camera_points = {p['observation_id']: p for p in scene['camera_depth_map_observations']}
        laser_points = {p['observation_id']: p for p in scene['fusion']['map_markers']}
        for observation in scene['observations']:
            source = observation['source_image']
            identity = {k: session[k] for k in ('run_id', 'map_id', 'calibration_id', 'detector_id', 'mode')}
            identity.update(image_key=list(frame_key(source)), observation_id=observation['id'])
            point = camera_points.get(observation['id']) or laser_points.get(observation['id'])
            mapped = point['surface_xyz_m'] if point else None
            if mapped is not None:
                mapped = [number(v) for v in mapped]
                if len(mapped) != 3 or point['frame'] != 'map':
                    raise ValueError('Expected map-frame surface XYZ')
            record = dict(identity, id=digest(identity), label=observation['class'],
                          detector_score=observation['score'], bbox=deepcopy(observation['bbox']),
                          source_image=deepcopy(source), observed_at=scene['fusion']['image_stamp'],
                          position_m=mapped, frame='map' if mapped else None,
                          evidence=point['evidence'] if point else 'camera_label_position_unknown',
                          association=observation['status'], reason=observation['reason'],
                          dynamic=observation['class'].lower() in DYNAMIC,
                          surface_not_object_centre=True, historical_not_live=True)
            old = events.get(record['id'])
            if old is not None and old != record:
                raise ValueError('Conflicting records for one exact source observation')
            events[record['id']] = record
    groups = []
    for event in sorted(events.values(), key=lambda e: (e['observed_at'], e['id'])):
        if event['dynamic'] or event['position_m'] is None:
            continue
        candidate = None
        for group in groups:
            if group['label'] == event['label'] and sum((a-b)**2 for a, b in zip(group['anchor_surface_m'], event['position_m'])) <= distance**2:
                candidate = group
                break
        if candidate is None:
            candidate = {'id': 'group-' + event['id'][:16], 'label': event['label'],
                         'anchor_surface_m': list(event['position_m']), 'observation_ids': [],
                         'first_seen': event['observed_at'], 'last_seen': event['observed_at'],
                         'provisional_group_not_identity': True}
            groups.append(candidate)
        candidate['observation_ids'].append(event['id'])
        candidate['last_seen'] = event['observed_at']
    return {'schema_version': 1, 'kind': 'historical_semantic_layer',
            'provenance': {k: session[k] for k in ('run_id', 'map_id', 'calibration_id', 'detector_id', 'mode')},
            'input_sha256': digest(session), 'observations': list(events.values()),
            'static_provisional_groups': groups, 'merge_distance_m': distance,
            'limits': 'No occupancy changes, moving-object permanence, current freshness, identity proof or clearance inference.'}
