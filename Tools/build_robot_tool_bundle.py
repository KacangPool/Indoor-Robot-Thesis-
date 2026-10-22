"""Build a laptop-side ZIP of existing diagnostic tools plus their shared code.

No robot connection, execution, ROS import, dependency install or overwrite.
Copy/extract the archive into the personal tools folder, not the vendor workspace.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ENTRY_POINTS = (
    'box_depth_viewer.py', 'camera_diagnostics_ros1.py',
    'person_detection_filter.py', 'record_detection_test.py',
    'ros_message_sample.py', 'ros_topic_report.sh',
)


def build(output, source=None):
    source = Path(source or Path(__file__).resolve().parent).resolve()
    output = Path(output)
    files = list(ENTRY_POINTS) + sorted(str(p.relative_to(source)).replace('\\', '/')
                                      for p in (source / 'fahad_core').glob('*.py'))
    if 'fahad_core/__init__.py' not in files:
        raise RuntimeError('Shared package is missing; no incomplete bundle created')
    contents = {name: (source / name).read_bytes() for name in files}
    manifest = {'schema_version': 1, 'files': {
        name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}}
    # Exclusive creation refuses an existing archive rather than replacing it.
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            archive.writestr(name, data)
        archive.writestr('tool_bundle_manifest.json', json.dumps(manifest, sort_keys=True, indent=2))
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    result = build(args.output)
    print('Created {} with {} verified-source files. Nothing uploaded or run.'.format(args.output, len(result['files'])))


if __name__ == '__main__':
    main()
