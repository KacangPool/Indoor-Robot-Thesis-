"""Offline image/calibration summaries used by the ROS diagnostics adapter.

These reproduce the monitor's legacy interpretation, not a calibration claim.
For strict known depth encodings use fahad_core.depth.depth_metres instead.
"""
import numpy as np


def rgb_statistics(image):
    data = np.asarray(image)
    b = data[:, :, 0].astype(np.float32)
    g = data[:, :, 1].astype(np.float32)
    r = data[:, :, 2].astype(np.float32)
    gray = 0.114 * b + 0.587 * g + 0.299 * r
    return {'mean': float(np.mean(gray)),
            'dark': float(np.mean(gray < 30.0) * 100.0),
            'bright': float(np.mean(gray > 225.0) * 100.0)}


def depth_statistics(image, encoding):
    values = np.asarray(image).astype(np.float32)
    # Preserve diagnostics' existing dtype fallback; do not silently change its
    # policy to the stricter registered-depth viewer's accepted encodings.
    metres = values / 1000.0 if '16UC1' in encoding.upper() or np.asarray(image).dtype == np.uint16 else values
    valid = metres[np.isfinite(metres) & (metres > 0.0)]
    total = float(metres.size)
    return {'valid': 100.0 * valid.size / total if total else 0.0,
            'min': float(np.min(valid)) if valid.size else float('nan'),
            'median': float(np.median(valid)) if valid.size else float('nan'),
            'max': float(np.max(valid)) if valid.size else float('nan')}


def camera_info_summary(message):
    if len(message.K) < 9:
        return None
    return {'width': message.width, 'height': message.height,
            'distortion': message.distortion_model, 'fx': message.K[0],
            'fy': message.K[4], 'cx': message.K[2], 'cy': message.K[5],
            'frame': message.header.frame_id}
