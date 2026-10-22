"""Depth conversion, local patch statistics and RGB/depth pairing checks.

No ROS, GUI, files or motor access. Python 2.7/3 compatible; NumPy required.
"""
import math
import numpy as np


def depth_metres(values, encoding):
    if np.asarray(values).ndim != 2:
        raise ValueError('Depth must be a single-channel two-dimensional image')
    result = np.asarray(values).astype(np.float32)
    if encoding.upper() == '16UC1':
        return result / 1000.0
    if encoding.upper() == '32FC1':
        return result
    raise ValueError('Unsupported depth encoding: %s' % encoding)


def patch_stats(metres, x, y, radius=5):
    height, width = metres.shape
    if radius < 0 or not (0 <= x < width and 0 <= y < height):
        raise ValueError('Patch centre/radius outside image')
    x0, x1 = max(0, x-radius), min(width, x+radius+1)
    y0, y1 = max(0, y-radius), min(height, y+radius+1)
    patch = metres[y0:y1, x0:x1]
    # Compare only finite values, avoiding invalid-value comparison warnings.
    finite = patch[np.isfinite(patch)]
    positive = finite[finite > 0]
    count = int(positive.size)
    in_range = int(np.sum((positive >= 0.4) & (positive <= 2.0)))
    return dict(x=x, y=y, bounds=(x0, y0, x1, y1), total=int(patch.size),
                count=count, valid_percent=100.0*count/patch.size,
                in_range_percent=100.0*in_range/patch.size,
                median=float(np.median(positive)) if count else None,
                minimum=float(np.min(positive)) if count else None,
                maximum=float(np.max(positive)) if count else None)


def pair_problem(rgb_shape, depth_shape, rgb_stamp, depth_stamp,
                 rgb_frame, depth_frame, max_delta, now_stamp=None):
    if rgb_shape[:2] != depth_shape[:2]:
        return 'Different image sizes; same-pixel sampling disabled'
    if not rgb_frame or rgb_frame != depth_frame:
        return 'Different/missing optical frames; same-pixel sampling disabled'
    if any(math.isnan(v) or math.isinf(v) for v in (rgb_stamp, depth_stamp)):
        return 'Nonfinite timestamps'
    if rgb_stamp <= 0 or depth_stamp <= 0:
        return 'Missing/zero timestamps'
    if abs(rgb_stamp-depth_stamp) > max_delta:
        return 'RGB/depth timestamps too far apart'
    if now_stamp is not None:
        if now_stamp-min(rgb_stamp, depth_stamp) > 1.0:
            return 'Old acquisition timestamps; numeric readings disabled'
        if max(rgb_stamp, depth_stamp)-now_stamp > 0.1:
            return 'Future acquisition timestamps; check ROS clock'
    return None
