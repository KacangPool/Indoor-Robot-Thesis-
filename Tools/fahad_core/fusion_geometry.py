"""Validated rigid geometry for recorded/synthetic fusion; no ROS or I/O."""
import math
from numbers import Real
from .detections import finite_number
from .recording import frame_key


def number(value):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError('Expected a finite number')
    result = finite_number(value)
    if result is None:
        raise ValueError('Expected a finite number')
    return result


def header_stamp(header):
    if not isinstance(header, dict):
        raise ValueError('Invalid acquisition header')
    for key, maximum in [('seq', 2**32-1), ('secs', 2**32-1), ('nsecs', 999999999)]:
        value = header.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
            raise ValueError('Invalid acquisition header')
    frame = header.get('frame_id')
    if not isinstance(frame, str) or not frame or len(frame) > 200:
        raise ValueError('Missing coordinate frame')
    stamp = header['secs'] + header['nsecs'] / 1e9
    if stamp <= 0:
        raise ValueError('Missing acquisition timestamp')
    return stamp


def same_image(a, b):
    header_stamp(a)
    header_stamp(b)
    return frame_key(a) == frame_key(b)


def rigid_transform(value, source, target, stamp, max_delta):
    """Explicit T_target_source; validates a proper3D rotation, not just yaw."""
    if not isinstance(value, dict):
        raise ValueError('Invalid transform object')
    if value.get('source_frame') != source or value.get('target_frame') != target:
        raise ValueError('Transform direction/frame mismatch')
    if value.get('static') is not True:
        if abs(number(value.get('stamp')) - stamp) > max_delta:
            raise ValueError('Transform does not match acquisition time')
    rotation, translation = value.get('rotation'), value.get('translation')
    if not isinstance(rotation, list) or len(rotation) != 3 or any(not isinstance(row, list) or len(row) != 3 for row in rotation):
        raise ValueError('Invalid rotation shape')
    if not isinstance(translation, list) or len(translation) != 3:
        raise ValueError('Invalid translation shape')
    r = [[number(v) for v in row] for row in rotation]
    t = [number(v) for v in translation]
    for i in range(3):
        for j in range(3):
            if abs(sum(r[k][i]*r[k][j] for k in range(3)) - (1 if i == j else 0)) > 1e-5:
                raise ValueError('Rotation is not orthonormal')
    determinant = sum(r[0][i]*(r[1][(i+1)%3]*r[2][(i+2)%3]-r[1][(i+2)%3]*r[2][(i+1)%3]) for i in range(3))
    if abs(determinant-1) > 1e-5:
        raise ValueError('Rotation is not right handed')
    return r, t


def transform_point(point, transform):
    r, t = transform
    return [sum(r[i][j]*point[j] for j in range(3)) + t[i] for i in range(3)]


def camera_model(value, image):
    if not isinstance(value, dict) or not isinstance(image, dict):
        raise ValueError('Invalid camera/image object')
    if image.get('rectified') is not True:
        raise ValueError('Projection requires rectified image and matching boxes')
    width, height = image.get('width'), image.get('height')
    if any(isinstance(v, bool) or not isinstance(v, int) or not 1 <= v <= 8192 for v in (width, height)):
        raise ValueError('Invalid image dimensions')
    if value.get('frame_id') != image['header']['frame_id'] or value.get('width') != width or value.get('height') != height:
        raise ValueError('Camera model/image mismatch')
    k = {key: number(value.get(key)) for key in ('fx', 'fy', 'cx', 'cy')}
    if not 0 < k['fx'] <= 100000 or not 0 < k['fy'] <= 100000:
        raise ValueError('Invalid focal length')
    k.update(width=width, height=height)
    return k


def project(point, camera):
    x, y, z = point
    if z <= 0:
        return None
    u, v = camera['fx']*x/z + camera['cx'], camera['fy']*y/z + camera['cy']
    return [u, v] if 0 <= u < camera['width'] and 0 <= v < camera['height'] else None


def inside(pixel, box):
    return box['xmin'] <= pixel[0] <= box['xmax'] and box['ymin'] <= pixel[1] <= box['ymax']


def scan_clusters(scan, gap=0.25):
    """Adjacent valid rays only; invalid rays split clusters. No invented heights."""
    values = scan.get('ranges')
    if not isinstance(values, list) or not 1 <= len(values) <= 7200:
        raise ValueError('Unsupported scan length')
    low, high = number(scan.get('range_min')), number(scan.get('range_max'))
    angle, step = number(scan.get('angle_min')), number(scan.get('angle_increment'))
    if low < 0 or high <= low or high > 1000 or step == 0 or abs(step)*max(0, len(values)-1) > 2*math.pi+0.01:
        raise ValueError('Invalid scan geometry')
    groups, group, previous = [], [], None
    for index, value in enumerate(values):
        try:
            distance = number(value)
            if distance <= 0 or distance < low or distance > high:
                raise ValueError('Invalid return')
        except (ValueError, TypeError):
            if group:
                groups.append(group)
            group, previous = [], None
            continue
        theta = angle + index*step
        point = [distance*math.cos(theta), distance*math.sin(theta), 0.0]
        if previous is not None and math.hypot(point[0]-previous[0], point[1]-previous[1]) > gap:
            groups.append(group)
            group = []
        group.append({'index': index, 'laser_xyz_m': point, 'range_m': distance})
        previous = point
    if group:
        groups.append(group)
    return groups
