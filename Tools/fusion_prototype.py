"""Offline fusion report/demo; never connects to ROS, robot or model services."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from fahad_core.fusion import fuse_snapshot
from fahad_core.semantic_scene import semantic_snapshot
from fahad_core.fusion_geometry import rigid_transform, transform_point


def make_report(scenarios, grid=None):
    results = []
    for scenario in scenarios:
        snapshot = scenario['snapshot']
        semantic = semantic_snapshot(snapshot)
        result = semantic['fusion']
        # Visualization coordinates use the same validated map transform as the core.
        visual_points = []
        if snapshot.get('laser_to_map') and not result['mapping_issue'] and result['gate'] == 'ready':
            transform = rigid_transform(snapshot['laser_to_map'], snapshot['scan']['header']['frame_id'], 'map', result['scan_stamp'], result['config']['max_tf_delta_s'])
            visual_points = [transform_point(p['laser_xyz_m'], transform) for p in result['projected_points']]
        results.append({'name': scenario.get('name', 'Recorded snapshot'),
                        'explanation': scenario.get('explanation', ''), 'result': result,
                        'image': {'width': snapshot['image']['width'], 'height': snapshot['image']['height']},
                        'map_scan_points': visual_points, 'semantic': semantic})
    return {'schema_version': 1, 'prototype': 'offline-semantic-fusion-v0.2', 'scenarios': results,
            'toy_map': grid, 'limits': 'No live camera, YOLO inference, LiDAR, SLAM, network or motor output.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--demo', action='store_true', help='Explicit synthetic scenes, not hardware results')
    mode.add_argument('--input', type=Path, help='Normalized recorded snapshot JSON, <=2MiB; no bag replay')
    parser.add_argument('--output', required=True, type=Path, help='NEW output directory; refuses existing paths')
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error('Output already exists; choose a new directory')
    try:
        if args.demo:
            from fusion_fixtures import demo_snapshots, semantic_demo_snapshots, toy_grid
            scenarios = demo_snapshots()+semantic_demo_snapshots()
            report = make_report(scenarios, toy_grid())
            source = json.dumps(scenarios, sort_keys=True, allow_nan=False).encode('utf8')
        else:
            with args.input.open('rb') as handle:
                source = handle.read(2*1024*1024+1)
            if len(source) > 2*1024*1024:
                raise ValueError('Oversized input')
            snapshot = json.loads(source.decode('utf8'), parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonstandard JSON constant')))
            if not isinstance(snapshot, dict) or snapshot.get('mode') != 'recorded':
                raise ValueError('Recorded input mode required; use --demo for synthetic scenes')
            report = make_report([{'snapshot': snapshot}])
        report['input_sha256'] = hashlib.sha256(source).hexdigest()
        text = json.dumps(report, ensure_ascii=True, allow_nan=False, indent=2)
        template_path = Path(__file__).with_name('fusion_demo_template.html')
        html = template_path.read_text(encoding='utf8').replace('__FUSION_REPORT_JSON__', text.replace('<', '\\u003c'))
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'report.json').write_text(text+'\n', encoding='utf8')
        (args.output/'index.html').write_text(html, encoding='utf8')
        print('Offline report: '+str(args.output/'index.html'))
        print('Scenes: %d. Synthetic: %s. No robot connection, inference or SLAM.' % (len(report['scenarios']), args.demo))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print('Cannot prepare offline fusion report: '+str(error)[:160], file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
