"""Pure planar scan/map validation and geometry. No ROS/node/HTTP imports.

Python 2.7/3.6 compatible. Accepts message-shaped objects for offline tests.
"""
import math


def finite(value):
    return not math.isnan(value) and not math.isinf(value)


def planar_pose(position, orientation):
    values = [float(getattr(position, k)) for k in ('x', 'y', 'z')]
    q = [float(getattr(orientation, k)) for k in ('x', 'y', 'z', 'w')]
    if not all(finite(v) for v in values + q) or abs(sum(v*v for v in q)-1) > .01:
        raise ValueError('Invalid position/quaternion')
    x, y, z, w = q
    if abs(x) > .01 or abs(y) > .01:
        raise ValueError('Non-planar transform is not supported by this 2D display')
    return {'x': values[0], 'y': values[1], 'yaw': math.atan2(2*w*z, 1-2*z*z)}


def occupancy_summary(message):
    """Bounded conservative display, not a costmap, clearance or motion planner."""
    info = message.info
    width, height, resolution = int(info.width), int(info.height), float(info.resolution)
    if width <= 0 or height <= 0 or width*height > 1000000 or len(message.data) != width*height or not finite(resolution) or resolution <= 0:
        raise ValueError('Map size/resolution outside display limits')
    origin = planar_pose(info.origin.position, info.origin.orientation)
    frame = message.header.frame_id
    if not isinstance(frame, str) or not frame or len(frame) > 200:
        raise ValueError('Invalid map frame')
    stride = max(1, int(math.ceil(max(width, height)/256.0)))
    out_width, out_height = int(math.ceil(width/float(stride))), int(math.ceil(height/float(stride)))
    cells = []
    for by in range(out_height):
        for bx in range(out_width):
            unknown = bx*stride+stride > width or by*stride+stride > height
            maximum = 0
            for y in range(by*stride, min(height, (by+1)*stride)):
                for x in range(bx*stride, min(width, (bx+1)*stride)):
                    v = message.data[y*width+x]
                    if isinstance(v, bool) or int(v) != v or v < -1 or v > 100:
                        raise ValueError('Invalid occupancy cell')
                    unknown = unknown or v == -1
                    maximum = max(maximum, int(v))
            cells.append(maximum if maximum >= 65 else -1 if unknown else maximum)
    return {'frame': frame, 'width': out_width, 'height': out_height,
            'resolution': resolution*stride, 'origin': origin, 'cells': cells,
            'source_resolution': resolution, 'stride': stride,
            'publisher': (getattr(message, '_connection_header', {}) or {}).get('callerid')}


def scan_summary(message, maximum_points=240):
    """Laser-frame geometry only; no base transform or obstacle avoidance."""
    low, high = float(message.range_min), float(message.range_max)
    start, step = float(message.angle_min), float(message.angle_increment)
    if not all(finite(x) for x in (low, high, start, step)) or low < 0 or high <= low or step == 0:
        raise ValueError('Invalid LaserScan geometry/range limits')
    values = []
    count = len(message.ranges)
    points = []
    intensities = getattr(message, 'intensities', [])
    intensity_aligned = len(intensities) == count and count > 0
    point_intensities = []
    valid_intensities = []
    for index, value in enumerate(message.ranges):
        distance = float(value)
        if not finite(distance) or not low <= distance <= high:
            continue
        values.append((index, distance))
        if intensity_aligned:
            try:
                intensity = float(intensities[index])
                if finite(intensity): valid_intensities.append(intensity)
            except (TypeError, ValueError, OverflowError):
                pass
    # Decimate valid returns, not raw indices: isolated valid points must not
    # vanish just because invalid ranges occupied the sampled indices.
    stride = max(1, int(math.ceil(len(values) / float(maximum_points))))
    for index, distance in values[::stride]:
        angle = start + index * step
        points.append([round(distance * math.cos(angle), 3),
                       round(distance * math.sin(angle), 3)])
        intensity = None
        if intensity_aligned:
            try:
                value = float(intensities[index])
                if finite(value): intensity = value
            except (TypeError, ValueError, OverflowError):
                pass
        point_intensities.append(intensity)
    header = getattr(message, '_connection_header', {}) or {}
    stamp = getattr(message.header, 'stamp', None)
    stamp = float(stamp.to_sec()) if hasattr(stamp, 'to_sec') else None
    if stamp is not None and not finite(stamp):
        stamp = None
    return {'frame': message.header.frame_id, 'samples': count,
            'valid_samples': len(values), 'minimum_m': min(v for i, v in values) if values else None,
            'publisher': header.get('callerid'), 'stamp': stamp,
            'range_min_m': low, 'range_max_m': high, 'points': points,
            'point_intensities': point_intensities,
            'intensity_state': 'available' if valid_intensities else 'unavailable',
            'intensity_min': min(valid_intensities) if valid_intensities else None,
            'intensity_max': max(valid_intensities) if valid_intensities else None,
            'intensity_units': 'device-specific; not calibrated reflectance'}
