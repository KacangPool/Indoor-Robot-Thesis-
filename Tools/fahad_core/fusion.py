"""Offline stationary camera/planar-LiDAR association, not a detector or SLAM.

Full projection creates candidates only. Optional independently confirmed object
depth can corroborate a candidate; bounding-box overlap alone never maps a label.
No ROS imports, subscribers, publishers, network, model loading or file I/O.
"""
from statistics import median
from .fusion_geometry import (number, header_stamp, same_image, rigid_transform,
                              transform_point, camera_model, project, inside, scan_clusters)

DEFAULTS = {'min_score': 0.5, 'cluster_gap_m': 0.25, 'min_points': 3,
            'min_cluster_fraction': 0.5, 'max_sync_s': 0.1, 'max_age_s': 0.5,
            'max_scan_duration_s': 0.15, 'max_tf_delta_s': 0.05,
            'depth_tolerance_m': 0.2, 'depth_spread_m': 0.15}


def settings(overrides=None):
    result = dict(DEFAULTS)
    for key, value in (overrides or {}).items():
        if key not in result:
            raise ValueError('Unknown fusion setting')
        result[key] = number(value)
    if not 0 <= result['min_score'] <= 1 or not 0 < result['min_cluster_fraction'] <= 1:
        raise ValueError('Invalid score/fraction')
    if result['min_points'] != int(result['min_points']) or not 2 <= result['min_points'] <= 100:
        raise ValueError('Invalid minimum point count')
    for key in ('cluster_gap_m', 'max_sync_s', 'max_age_s', 'max_scan_duration_s', 'max_tf_delta_s', 'depth_tolerance_m', 'depth_spread_m'):
        if not 0 < result[key] <= 5:
            raise ValueError('Invalid positive threshold')
    return result


def depth_support(evidence, image, box, config):
    """A manually verified object patch, not an arbitrary box centre/background."""
    if not evidence:
        return None, 'no_independent_object_depth'
    if not isinstance(evidence, dict):
        return None, 'invalid_depth_evidence'
    try:
        if evidence.get('region_verified') is not True or evidence.get('registered_to_rgb') is not True:
            return None, 'object_patch_or_registration_not_verified'
        if not same_image(evidence['image_header'], image['header']):
            return None, 'depth_source_image_mismatch'
        if not inside([number(evidence.get('u')), number(evidence.get('v'))], box):
            return None, 'depth_patch_outside_detection'
        rows = evidence['values']
        if not isinstance(rows, list) or not 1 <= len(rows) <= 31 or not isinstance(rows[0], list) or not 1 <= len(rows[0]) <= 31:
            return None, 'invalid_depth_patch'
        if any(not isinstance(row, list) or len(row) != len(rows[0]) for row in rows):
            return None, 'invalid_depth_patch'
        for row in rows:
            for value in row:
                if value is not None:
                    number(value)
                    if evidence.get('encoding', '').upper() == '16UC1' and (value != int(value) or not 0 <= value <= 65535):
                        return None, 'invalid_uint16_depth'
        # Reuse the existing unit conversion/statistics, importing NumPy only here.
        import numpy as np
        from .depth import depth_metres, patch_stats
        values = np.asarray([[float('nan') if v is None else v for v in row] for row in rows])
        metres = depth_metres(values, evidence['encoding'])
        stats = patch_stats(metres, len(rows[0])//2, len(rows)//2, radius=31)
        if stats['count'] < 5 or stats['valid_percent'] < 50 or stats['maximum']-stats['minimum'] > config['depth_spread_m']:
            return None, 'insufficient_or_mixed_depth'
        if not 0.1 <= stats['median'] <= 20:
            return None, 'object_depth_outside_prototype_range'
        return stats['median'], 'verified_object_patch'
    except (KeyError, ValueError, TypeError, OverflowError):
        return None, 'invalid_depth_evidence'


def fuse_snapshot(snapshot, overrides=None):
    """Return evidence records. Malformed contracts raise; unready data stays blocked."""
    config = settings(overrides)
    if not isinstance(snapshot, dict) or snapshot.get('schema_version') != 1 or snapshot.get('mode') not in ('synthetic', 'recorded'):
        raise ValueError('Unsupported fusion snapshot')
    image, scan = snapshot['image'], snapshot['scan']
    detections = snapshot['detections']
    if not all(isinstance(value, dict) for value in (image, scan, detections)):
        raise ValueError('Invalid image/scan/detection object')
    if any(isinstance(image.get(key), bool) or not isinstance(image.get(key), int) or not 1 <= image[key] <= 8192 for key in ('width', 'height')):
        raise ValueError('Invalid image dimensions')
    image_time, scan_time = header_stamp(image['header']), header_stamp(scan['header'])
    header_stamp(detections['image_header'])
    now = number(snapshot['reference_stamp'])
    boxes = detections.get('boxes')
    if not isinstance(boxes, list) or len(boxes) > 100:
        raise ValueError('Unsupported detection count')
    observations = []
    for index, box in enumerate(boxes):
        if not isinstance(box, dict):
            raise ValueError('Invalid detection object')
        label = box.get('class')
        if not isinstance(label, str) or not label or len(label) > 80:
            raise ValueError('Invalid class label')
        score = number(box.get('score'))
        bounds = {k: number(box.get(k)) for k in ('xmin', 'ymin', 'xmax', 'ymax')}
        if not 0 <= score <= 1 or not (0 <= bounds['xmin'] < bounds['xmax'] <= image['width'] and 0 <= bounds['ymin'] < bounds['ymax'] <= image['height']):
            raise ValueError('Invalid detection bounds/score')
        observations.append({'id': index, 'class': label, 'score': score,
                             'bbox': bounds, 'status': 'camera_only', 'reason': 'no_projected_cluster',
                             'candidates': [], 'laser_point_m': None, 'map_point_m': None})
    result = {'schema_version': 1, 'mode': snapshot['mode'], 'config': config,
              'image_stamp': image_time, 'scan_stamp': scan_time,
              'calibration_id': snapshot.get('calibration_id'), 'gate': 'blocked',
              'reason': None, 'projected_points': [], 'observations': observations,
              'map_markers': [], 'mapping_issue': None,
              'limitations': ['Stationary snapshot only; no deskew, tracking, SLAM or motion output.',
                              'Projection/depth consistency is conditional evidence, not object-identity ground truth.',
                              'Markers are temporary surface observations, not object centres or occupancy.']}
    def blocked(reason):
        result['reason'] = reason
        for record in observations:
            record.update(status='unavailable', reason=reason)
        return result
    if not same_image(detections['image_header'], image['header']):
        return blocked('detection_source_image_mismatch')
    if snapshot.get('stationary') is not True:
        return blocked('moving_or_unknown_motion_not_supported')
    status = snapshot.get('calibration_status')
    calibration_id = snapshot.get('calibration_id')
    if not isinstance(calibration_id, str) or not 1 <= len(calibration_id) <= 120 or not (status == 'validated' or (snapshot['mode'] == 'synthetic' and status == 'synthetic')):
        return blocked('calibration_not_validated')
    values = scan.get('ranges')
    if not isinstance(values, list) or not 1 <= len(values) <= 7200:
        raise ValueError('Unsupported scan length')
    interval = number(scan.get('time_increment'))
    duration = interval * (len(values)-1)
    if interval < 0 or duration > config['max_scan_duration_s']:
        return blocked('scan_duration_unsupported')
    if max(abs(scan_time-image_time), abs(scan_time+duration-image_time)) > config['max_sync_s']:
        return blocked('acquisition_times_not_aligned')
    if now-min(scan_time, image_time) > config['max_age_s'] or max(scan_time+duration, image_time)-now > 0.02:
        return blocked('stale_or_future_measurements')
    camera = camera_model(snapshot['camera'], image)
    camera_tf = rigid_transform(snapshot['laser_to_camera'], scan['header']['frame_id'], image['header']['frame_id'], scan_time, config['max_tf_delta_s'])
    groups = scan_clusters(scan, config['cluster_gap_m'])
    if not groups:
        return blocked('no_valid_laser_returns')
    for cluster_id, group in enumerate(groups):
        for point in group:
            point['camera_xyz_m'] = transform_point(point['laser_xyz_m'], camera_tf)
            point['pixel'] = project(point['camera_xyz_m'], camera)
            point['cluster_id'] = cluster_id
            if point['pixel'] is not None:
                result['projected_points'].append(point)
    result.update(gate='ready', reason='synthetic_geometry_only' if snapshot['mode'] == 'synthetic' else 'recorded_contract_accepted')
    for record, box in zip(observations, boxes):
        if record['score'] < config['min_score']:
            record.update(status='filtered', reason='low_detector_score')
            continue
        depth, depth_reason = depth_support(box.get('object_depth'), image, box, config)
        record['object_depth_m'] = depth
        record['depth_evidence'] = depth_reason
        rejected_depth = False
        for cluster_id, group in enumerate(groups):
            visible = [p for p in group if p['pixel'] is not None]
            hits = [p for p in visible if inside(p['pixel'], box)]
            if len(hits) < config['min_points'] or len(hits)/float(len(visible)) < config['min_cluster_fraction']:
                continue
            camera_z = median(p['camera_xyz_m'][2] for p in hits)
            if depth is not None and abs(camera_z-depth) > config['depth_tolerance_m']:
                rejected_depth = True
                continue
            centre = [median(p['laser_xyz_m'][axis] for p in hits) for axis in range(3)]
            representative = min(hits, key=lambda p: sum((p['laser_xyz_m'][axis]-centre[axis])**2 for axis in range(3)))
            record['candidates'].append({'cluster_id': cluster_id, 'point_count': len(hits),
                'camera_z_m': camera_z, 'laser_point_m': representative['laser_xyz_m'],
                'laser_range_m': median(p['range_m'] for p in hits)})
        if not record['candidates']:
            record['reason'] = 'object_depth_disagrees_with_laser' if rejected_depth else 'no_projected_cluster'
        elif len(record['candidates']) > 1:
            record.update(status='ambiguous', reason='multiple_clusters')
        elif depth is None:
            record.update(status='candidate_only', reason='projection_is_not_identity_proof')
        else:
            record.update(status='depth_supported', reason='projection_and_independent_object_depth_consistent')
    # Do not reuse one cluster to label two overlapping detections.
    for record in observations:
        if len(record['candidates']) == 1:
            cluster = record['candidates'][0]['cluster_id']
            if sum(any(c['cluster_id'] == cluster for c in other['candidates']) for other in observations) > 1:
                record.update(status='ambiguous', reason='cluster_shared_by_detections')
    map_tf = None
    if snapshot.get('laser_to_map'):
        try:
            if not isinstance(snapshot['laser_to_map'], dict) or snapshot['laser_to_map'].get('static') is not False:
                raise ValueError('Map pose must be acquisition-timed, not a static substitute')
            map_tf = rigid_transform(snapshot['laser_to_map'], scan['header']['frame_id'], 'map', scan_time, config['max_tf_delta_s'])
        except (ValueError, TypeError, KeyError):
            result['mapping_issue'] = 'invalid_or_untimed_map_transform'
    else:
        result['mapping_issue'] = 'no_map_transform'
    for record in observations:
        if record['status'] != 'depth_supported':
            continue
        point = record['candidates'][0]['laser_point_m']
        record['laser_point_m'] = point
        if map_tf is not None:
            mapped = transform_point(point, map_tf)
            record['map_point_m'] = mapped
            result['map_markers'].append({'observation_id': record['id'], 'class': record['class'],
                'frame': 'map', 'surface_xyz_m': mapped, 'stamp': scan_time,
                'expires_at': min(image_time, scan_time)+config['max_age_s'],
                'evidence': 'depth_supported', 'synthetic': snapshot['mode'] == 'synthetic'})
    return result
