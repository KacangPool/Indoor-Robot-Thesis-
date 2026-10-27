"""Bounded camera-only observations; Python 2.7/3.6, no I/O or ROS imports."""
import math
from .detections import boxes_list
from .recording import header_dict, frame_key


def camera_observations(message):
    if len(message.bounding_boxes) > 100:
        raise ValueError('Too many detections')
    header = header_dict(message.image_header)
    if (not header['frame_id'] or len(header['frame_id']) > 200 or
            not 0 <= header['nsecs'] < 1000000000 or header['secs'] <= 0 or
            not 0 <= header['seq'] < 2**32):
        raise ValueError('Invalid source image header')
    records = []
    for index, box in enumerate(boxes_list(message)):
        label, score = box['class'], box['score']
        if (not label or len(label) > 80 or any(ord(c) < 32 or ord(c) == 127 for c in label) or score is None or not 0 <= score <= 1 or
                not 0 <= box['xmin'] < box['xmax'] <= 8192 or
                not 0 <= box['ymin'] < box['ymax'] <= 8192):
            raise ValueError('Invalid detection')
        records.append({'id': index, 'class': label, 'score': score,
                        'bbox': {k: box[k] for k in ('xmin', 'ymin', 'xmax', 'ymax')},
                        'status': 'camera_only', 'position': None, 'height': 'unknown',
                        'clearance': 'unknown', 'source_image': dict(header)})
    return {'image_header': header, 'image_key': list(frame_key(header)), 'records': records}


def source_age(observation, now):
    stamp = observation['image_header']
    age = float(now)-(stamp['secs']+stamp['nsecs']/1e9)
    if math.isnan(age) or math.isinf(age) or not -0.05 <= age < 2:
        raise ValueError('Stale/future detector source')
    return age
