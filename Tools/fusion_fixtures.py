"""Explicit toy regression scenes. Not recordings, measured calibration or ML output."""
from copy import deepcopy
import math


def demo_snapshots():
    header = {'seq': 1, 'secs': 10, 'nsecs': 0, 'frame_id': 'camera_rgb_optical_frame'}
    rotation = [[0, -1, 0], [0, 0, -1], [1, 0, 0]]
    camera_tf = {'source_frame': 'laser', 'target_frame': header['frame_id'], 'static': True,
                 'rotation': rotation, 'translation': [0, -0.02, -0.03]}
    yaw = 0.35
    map_tf = {'source_frame': 'laser', 'target_frame': 'map', 'static': False, 'stamp': 10.0,
              'rotation': [[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]],
              'translation': [2, 2, 0.15]}
    box = {'class': 'person', 'class_id': 0, 'score': 0.9, 'xmin': 260, 'ymin': 140, 'xmax': 380, 'ymax': 430,
           'object_depth': {'region_verified': True, 'registered_to_rgb': True, 'image_header': deepcopy(header),
                            'u': 320, 'v': 300, 'encoding': '16UC1', 'values': [[1570]*3 for _ in range(3)]}}
    base = {'schema_version': 1, 'mode': 'synthetic', 'stationary': True,
            'calibration_status': 'synthetic', 'calibration_id': 'TOY-NOT-ROBOT-CALIBRATION',
            'reference_stamp': 10.02,
            'image': {'header': header, 'width': 640, 'height': 480, 'rectified': True},
            'camera': {'frame_id': header['frame_id'], 'width': 640, 'height': 480, 'fx': 500, 'fy': 500, 'cx': 320, 'cy': 240},
            'detections': {'image_header': deepcopy(header), 'boxes': [box]},
            'scan': {'header': {'seq': 1, 'secs': 10, 'nsecs': 0, 'frame_id': 'laser'},
                     'angle_min': -0.04, 'angle_increment': 0.02, 'range_min': 0.1, 'range_max': 10,
                     'time_increment': 0.001, 'ranges': [1.6]*5},
            'laser_to_camera': camera_tf, 'laser_to_map': map_tf}
    scenarios = []
    def add(name, text, change=None):
        s = deepcopy(base)
        if change:
            change(s)
        scenarios.append({'name': name, 'explanation': text, 'snapshot': s})
    add('Supported foreground person', 'Toy person label, intersecting scan cluster and independently verified object depth agree. A temporary surface marker is eligible, not a permanent person-shaped obstacle.')
    def raised(s):
        s['detections']['boxes'][0].update(ymin=80, ymax=180)
        s['detections']['boxes'][0]['object_depth']['v'] = 130
    add('Raised object: same bearing, different level', 'The laser projects below the box. Sharing horizontal direction is insufficient; no label is attached to the wall/scan.', raised)
    def background(s):
        s['scan']['ranges'] = [3.2]*5
    add('Background wall inside a broad box', 'Projected wall points fall inside the rectangle, but object depth is near1.57m and wall depth near3.17m. Reject the false association.', background)
    def no_depth(s):
        del s['detections']['boxes'][0]['object_depth']
    add('Projection only: do not force a match', 'A single cluster projects into the box, but no independent foreground support is present. Keep a candidate and do not create a semantic map marker.', no_depth)
    def overlap(s):
        other = deepcopy(s['detections']['boxes'][0])
        other.update({'class': 'chair', 'class_id': 56})
        s['detections']['boxes'].append(other)
    add('Overlapping labels share one cluster', 'The same measured points cannot confidently label both a person and a chair. Both remain ambiguous.', overlap)
    def stale(s):
        s['scan']['header']['secs'] = 9
    add('Old scan: reject stale pairing', 'The image and scan acquisition times disagree. No projection/association or map marker is emitted.', stale)
    def no_map(s):
        del s['laser_to_map']
    add('No map transform: local evidence only', 'Object/depth support can exist in laser coordinates without a valid map transform. No fake map-origin position is substituted.', no_map)
    def unknown_calibration(s):
        s['calibration_status'] = 'unvalidated'
    add('Unvalidated calibration', 'Approximate heights and guessed transforms must not generate labelled positions.', unknown_calibration)
    return scenarios


def toy_grid():
    """Hand-authored synthetic room, not ray-traced free space or robot data."""
    width, height = 60, 50
    cells = []
    for y in range(height):
        for x in range(width):
            value = -1
            if 5 <= x <= 54 and 5 <= y <= 44:
                value = 100 if x in (5, 54) or y in (5, 44) else 0
            cells.append(value)
    return {'width': width, 'height': height, 'resolution': 0.1, 'origin': [0, 0], 'cells': cells,
            'evidence': 'hand_authored_synthetic_occupancy_grid'}


def semantic_demo_snapshots():
    """Toy monitor/table geometry: no inferred support or clearance relationship."""
    raised = deepcopy(demo_snapshots()[1])
    raised['name'] = 'Monitor above scan plane; table intersects laser'
    raised['explanation'] = 'Synthetic monitor sample is above the laser plane and retained as camera-depth-only. Only the independently supported table cluster labels laser rays. This does not prove the monitor floats, is supported by the table or is safe to drive under.'
    monitor = raised['snapshot']['detections']['boxes'][0]
    monitor['class'] = 'tvmonitor'
    table = deepcopy(monitor)
    table.update({'class': 'diningtable', 'ymin': 200, 'ymax': 430})
    table['object_depth']['v'] = 240
    raised['snapshot']['detections']['boxes'].append(table)
    unknown = deepcopy(raised)
    unknown['name'] = 'Monitor without verified object depth stays position-unknown'
    unknown['explanation'] = 'Camera label is kept, not attached to an unrelated laser return. Without verified depth the monitor height, position and clearance remain unknown.'
    del unknown['snapshot']['detections']['boxes'][0]['object_depth']
    return [raised, unknown]
