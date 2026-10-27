"""Offline semantic observations; no persistence, ROS, inference or motion."""
from copy import deepcopy
from .fusion import fuse_snapshot, depth_support
from .fusion_geometry import camera_model, rigid_transform, transform_point


def semantic_snapshot(snapshot):
    result = fuse_snapshot(snapshot)
    records = deepcopy(result['observations'])
    labelled_rays, camera_points = [], []
    camera = camera_tf = map_tf = None
    camera_ready = result['gate'] == 'ready' or result['reason'] == 'no_valid_laser_returns'
    if camera_ready:
        camera = camera_model(snapshot['camera'], snapshot['image'])
        try:
            camera_tf = rigid_transform(snapshot['laser_to_camera'], snapshot['scan']['header']['frame_id'],
                                        snapshot['image']['header']['frame_id'], result['image_stamp'], result['config']['max_tf_delta_s'])
        except ValueError:
            camera_tf = None
        map_value = snapshot.get('laser_to_map')
        if isinstance(map_value, dict) and map_value.get('static') is False:
            try:
                map_tf = rigid_transform(snapshot['laser_to_map'], snapshot['scan']['header']['frame_id'],
                                         'map', result['image_stamp'], result['config']['max_tf_delta_s'])
            except ValueError:
                map_tf = None
    for record, box in zip(records, snapshot['detections']['boxes']):
        record.update(source_image=deepcopy(snapshot['detections']['image_header']),
                      synthetic=snapshot['mode'] == 'synthetic', sample_height_relation='unknown',
                      clearance='unknown', support_relation='unknown', camera_surface=None)
        if camera_ready and result['reason'] == 'no_valid_laser_returns':
            record.update(status='camera_only', reason='no_valid_laser_returns')
            if record['score'] < result['config']['min_score']:
                record.update(status='filtered',reason='low_detector_score')
            else:
                depth, reason = depth_support(box.get('object_depth'), snapshot['image'], box, result['config'])
                record.update(object_depth_m=depth, depth_evidence=reason)
        if record['status'] == 'depth_supported':
            labelled_rays.append({'observation_id': record['id'], 'class': record['class'],
                                 'indices': list(record['candidates'][0]['ray_indices']),
                                 'frame': snapshot['scan']['header']['frame_id'],
                                 'scan_header': deepcopy(snapshot['scan']['header']),
                                 'image_header': deepcopy(snapshot['detections']['image_header']),
                                 'synthetic': snapshot['mode'] == 'synthetic',
                                 'expires_at': min(result['image_stamp'],result['scan_stamp'])+result['config']['max_age_s'],
                                 'evidence': 'depth_supported'})
        if camera is None or camera_tf is None or record.get('object_depth_m') is None or record['status'] in ('filtered', 'ambiguous'):
            continue
        evidence, depth = box['object_depth'], record['object_depth_m']
        optical = [(evidence['u']-camera['cx'])*depth/camera['fx'],
                   (evidence['v']-camera['cy'])*depth/camera['fy'], depth]
        rotation, translation = camera_tf
        local = [sum(rotation[j][i]*(optical[j]-translation[j]) for j in range(3)) for i in range(3)]
        relation = 'above_scan_plane' if local[2] > .15 else 'below_scan_plane' if local[2] < -.15 else 'near_scan_plane'
        record.update(sample_height_relation=relation,
                      camera_surface={'optical_xyz_m': optical, 'laser_xyz_m': local,
                                      'evidence': 'independently_verified_registered_depth',
                                      'frame': snapshot['scan']['header']['frame_id'],
                                      'height_margin_m': .15, 'not_object_centre': True})
        if map_tf is not None:
            point = {'observation_id': record['id'], 'class': record['class'],
                     'surface_xyz_m': transform_point(local, map_tf), 'frame': 'map',
                     'stamp': result['image_stamp'], 'synthetic': snapshot['mode'] == 'synthetic',
                     'expires_at': min(result['image_stamp'], result['scan_stamp'])+result['config']['max_age_s'],
                     'evidence': 'camera_depth_only' if record['status'] != 'depth_supported' else 'camera_depth_with_laser_support'}
            camera_points.append(point)
    return {'schema_version': 1, 'fusion': result, 'observations': records,
            'labelled_laser_rays': labelled_rays, 'camera_depth_map_observations': camera_points,
            'persistence': 'none_latest_snapshot_only',
            'limits': 'No floating/table/clearance inference; surface points, not occupancy or object centres.'}
