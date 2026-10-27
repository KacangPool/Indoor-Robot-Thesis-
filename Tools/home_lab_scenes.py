"""Synthetic workbench inputs built on existing fixtures and geometry."""
from copy import deepcopy
from fusion_fixtures import demo_snapshots, semantic_demo_snapshots
from fahad_core.fusion_geometry import number, rigid_transform, transform_point, camera_model, project


def cases():
    return demo_snapshots() + semantic_demo_snapshots()


def virtual_scene(values):
    if not isinstance(values, dict) or set(values) - {'distance', 'height', 'background', 'depth', 'calibrated'}:
        raise ValueError('Unsupported virtual-scene control')
    controls = {'distance': 1.6, 'height': 0.0, 'background': 1.6, 'depth': True, 'calibrated': True}
    controls.update(values)
    for key in ('distance', 'background'):
        if not 1 <= number(controls[key]) <= 4:
            raise ValueError('Synthetic range must be 1..4 metres')
    if not 0 <= number(controls['height']) <= .3 or any(type(controls[k]) is not bool for k in ('depth', 'calibrated')):
        raise ValueError('Invalid virtual height/flags')
    snapshot = deepcopy(demo_snapshots()[0]['snapshot'])
    image, camera = snapshot['image'], snapshot['camera']
    transform = rigid_transform(snapshot['laser_to_camera'], 'laser', image['header']['frame_id'], 10, .05)
    optical = transform_point([controls['distance'], 0, controls['height']], transform)
    u, v = project(optical, camera_model(camera, image))
    box = snapshot['detections']['boxes'][0]
    box.update({'class': 'chair', 'xmin': max(0, u-60), 'xmax': min(640, u+60),
                'ymin': max(0, v-50), 'ymax': min(480, v+50)})
    box['object_depth'].update({'u': u, 'v': v, 'encoding': '32FC1',
                                'values': [[optical[2]]*3 for _ in range(3)]})
    if not controls['depth']:
        del box['object_depth']
    snapshot['scan']['ranges'] = [controls['background']]*5
    if not controls['calibrated']:
        snapshot['calibration_status'] = 'unvalidated'
    return snapshot


def session_for(snapshots, mode='synthetic', run_id='home-demo', map_id='toy-room'):
    return {'schema_version': 1, 'kind': 'fusion_session', 'mode': mode,
            'run_id': run_id, 'map_id': map_id,
            'calibration_id': snapshots[0]['calibration_id'], 'detector_id': 'toy-labels-not-yolo',
            'snapshots': snapshots}


def demo_session():
    snapshots = []
    for index in range(3):
        s = virtual_scene({})
        delta = index
        seen = set()
        for header in (s['image']['header'], s['scan']['header'], s['detections']['image_header'],
                       s['detections']['boxes'][0]['object_depth']['image_header']):
            if id(header) in seen:
                continue
            seen.add(id(header))
            header['secs'] += delta
            header['seq'] += delta
        s['reference_stamp'] += delta
        s['laser_to_map']['stamp'] += delta
        snapshots.append(s)
    return session_for(snapshots)
