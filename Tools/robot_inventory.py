"""Explicit, read-only robot inventory. No launches, sudo, publishers or installs."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys

from fahad_core.inventory import catalogue


def observe(argv, timeout=8):
    """Fixed-argument diagnostic with bounded output and explicit failure evidence."""
    if not shutil.which(argv[0]):
        return {'status': 'unavailable', 'lines': []}
    try:
        # A temporary file avoids unbounded captured-output memory. Never executes a shell.
        import tempfile
        with tempfile.TemporaryFile() as stream:
            process = subprocess.Popen(argv, stdout=stream, stderr=subprocess.DEVNULL)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return {'status': 'timeout', 'lines': []}
            stream.seek(0)
            raw = stream.read(1024 * 1024 + 1)
        return {'status': 'ok' if code == 0 else 'failed', 'returncode': code,
                'truncated': len(raw) > 1024 * 1024,
                'lines': raw[:1024 * 1024].decode('utf8', 'replace').splitlines()}
    except OSError:
        return {'status': 'failed', 'lines': []}


def live_inventory():
    """Registration observations only, never a statement of sensor freshness."""
    commands = {
        'architecture': ['uname', '-m'], 'os': ['lsb_release', '-ds'],
        'ros_distribution': ['rosversion', '-d'], 'discoverable_packages': ['rospack', 'list'],
        'registered_nodes': ['rosnode', 'list'], 'registered_topics': ['rostopic', 'list', '-v'],
        'registered_services': ['rosservice', 'list'],
        'selected_installed_packages': ['dpkg-query', '-W', '-f=${binary:Package}\t${Version}\n'],
    }
    result = {name: observe(command) for name, command in commands.items()}
    selected = result['selected_installed_packages']
    selected['lines'] = [line for line in selected['lines'] if line.lower().startswith(
        ('ros-', 'cuda-', 'libopencv', 'python-opencv', 'python3-opencv', 'nvidia-jetpack', 'librealsense'))]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', action='append', default=[], help='Explicit source tree; may be repeated')
    parser.add_argument('--robot', action='store_true', help='Read fixed installed/registered ROS observations on this machine')
    parser.add_argument('--output', required=True, help='NEW JSON report path; existing files are never replaced')
    args = parser.parse_args(argv)
    if not args.source_root and not args.robot:
        parser.error('Select --source-root and/or --robot; nothing is scanned by default')
    output = Path(args.output).expanduser()
    if output.exists():
        parser.error('Report already exists; choose a new filename')
    report = {'schema_version': 1, 'recorded_utc': datetime.datetime.utcnow().isoformat() + 'Z',
              'sources': [], 'runtime': None,
              'limitations': ['Not an exhaustive disk scan; packages outside supplied roots/active ROS environment may be missed.',
                              'Registration is not message delivery. No device or sensor capability is inferred.',
                              'No parameter dump, credentials, images, raw messages or launch execution. Review paths before sharing.']}
    try:
        for root in args.source_root:
            report['sources'].append({'root_label': Path(root).name, 'catalogue': catalogue(root)})
        if args.robot:
            report['runtime'] = live_inventory()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf8') as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
        print('Read-only inventory saved: ' + str(output))
        print('Sources: %d | packages: %d | launch declarations: %d' % (
            len(report['sources']), sum(len(s['catalogue']['packages']) for s in report['sources']),
            sum(len(s['catalogue']['launches']) for s in report['sources'])))
        print('Nothing launched, installed or moved. Runtime errors/unavailable checks remain in the report.')
        return 0
    except (OSError, ValueError):
        print('Inventory could not complete. Check roots, limits and report path; no retry or overwrite.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
