"""One offline quality command. No ROS startup, robot access or dependency installs.

Runs fixed test commands in isolated child processes. HTTP/fake SSH tests use
localhost only. Missing dependencies, timeouts and skips remain visible.
Reports are local/private and may include local paths and test tracebacks.
"""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]


def source_inventory(git, root=ROOT):
    """Hash source-only tracked/allowed untracked files; never stage or upload."""
    result = subprocess.run([git, 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                            cwd=root, capture_output=True)
    if result.returncode:
        return None
    files = {}
    for name in result.stdout.decode('utf8').split('\0'):
        if not name:
            continue
        path = root/name
        if path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()):
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def executable(explicit, candidates):
    if explicit:
        return str(Path(explicit).resolve()) if Path(explicit).is_file() else shutil.which(explicit)
    return next((str(path) for path in candidates if Path(path).is_file()), None)


def run_command(name, argv, directory, timeout=120, result_file=None):
    started = time.monotonic()
    record = {'name': name, 'status': 'blocked', 'elapsed_s': 0, 'returncode': None}
    if not argv or not argv[0]:
        record['reason'] = 'Required runtime unavailable; nothing installed.'
        return record
    try:
        completed = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout)
        output = (completed.stdout + completed.stderr).decode('utf8', 'replace')
        record.update(returncode=completed.returncode, status='pass' if completed.returncode == 0 else 'fail')
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or b'') + (exc.stderr or b'')).decode('utf8', 'replace')
        record.update(status='timeout', reason='Deadline exceeded; child process stopped. No automatic retry.')
    except OSError as exc:
        output = type(exc).__name__
        record.update(status='blocked', reason='Runtime could not be started.')
    log = directory / (name + '.log')
    log.write_text(output[-150000:], encoding='utf8')
    record.update(log=log.name, elapsed_s=round(time.monotonic() - started, 3))
    if result_file is not None:
        if result_file.is_file():
            try:
                value = json.loads(result_file.read_text(encoding='utf8'))
                required = ('tests_run', 'failures', 'errors', 'skipped', 'expected_failures', 'successful')
                if not isinstance(value, dict) or any(key not in value for key in required):
                    raise ValueError('Incomplete test result')
                record['unittest'] = value
                if not value['successful'] or value['tests_run'] <= 0:
                    record['status'] = 'fail'
            except (OSError, ValueError):
                record.update(status='fail', reason='Invalid worker test report.')
        elif record['status'] == 'pass':
            record.update(status='fail', reason='Worker did not produce its required test report.')
    return record


def static_checks():
    """Dependency-free syntax/contract checks, not a substitute for a full linter."""
    excluded = {'__pycache__', '.venv', 'node_modules', 'quality_reports', 'diagnostic_reports'}
    paths = sorted(path for path in (ROOT / 'Tools').rglob('*.py') if not excluded.intersection(path.parts))
    paths += sorted((ROOT / 'Testing other Models' / 'DetectorTest').glob('*.py'))
    for path in paths:
        text = path.read_text(encoding='utf8')
        robot = (path.parent.name in ('remote_dashboard', 'fahad_core') and not path.name.startswith('test')) or path.name in (
            'agent.py', 'robot_inventory.py', 'fusion_prototype.py', 'fusion_fixtures.py', 'box_depth_viewer.py', 'camera_diagnostics_ros1.py', 'person_detection_filter.py',
            'record_detection_test.py', 'record_fusion_session.py', 'ros_message_sample.py')
        if robot:
            ast.parse(text, filename=str(path), feature_version=(3, 6))
        else:
            ast.parse(text, filename=str(path))
    # Validate configuration with its real validator without running its entry point.
    import importlib.util
    spec = importlib.util.spec_from_file_location('quality_configuration', ROOT/'Tools/remote_dashboard/configuration.py')
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    config.load()
    return len(paths)


def write_summary(directory, checks, metadata):
    ok = all(check['status'] == 'pass' for check in checks)
    value = {'schema_version': 1, 'overall': 'pass' if ok else 'attention_required',
             'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'scope': 'offline_tests_and_static_checks_not_robot_validation',
             'environment': metadata, 'checks': checks,
             'not_run': ['live ROS/robot, model inference, physical stopping and old Jetson runtimes',
                         'annotation browser integration (UI unchanged; separate browser workflow)',
                         'third-party linter/formatter (not installed by this checker)']}
    (directory/'summary.json').write_text(json.dumps(value, indent=2), encoding='utf8')
    rows = ['# Project quality report', '', 'Overall: **'+value['overall']+'**', '',
            'Offline only. Localhost tests are not live robot checks.', '',
            '| Check | Result | Details |', '| --- | --- | --- |']
    for check in checks:
        detail = check.get('reason', '')
        if 'unittest' in check:
            test = check['unittest']
            detail = '{} tests; {} failures, {} errors, {} skipped, {} expected failures'.format(
                test['tests_run'], len(test['failures']), len(test['errors']), len(test['skipped']), len(test['expected_failures']))
            if test.get('reason'):
                detail += '; ' + test['reason']
        rows.append('| {} | {} | {} |'.format(check['name'], check['status'], detail.replace('|', '/')))
    rows += ['', 'See summary.json and individual logs for errors/skips. No retries or exclusions hide failures.',
             'Reports may contain local paths/test traces. They are ignored by Git and never uploaded.']
    (directory/'summary.md').write_text('\n'.join(rows)+'\n', encoding='utf8')
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', help='Python with existing NumPy for root tools tests')
    parser.add_argument('--hub-python', help='Existing Python with Paramiko/Tk for Hub tests')
    parser.add_argument('--node', help='Existing Node executable')
    parser.add_argument('--output', type=Path, help='New report folder; existing folders are refused')
    args = parser.parse_args(argv)
    helper = executable(args.python, [Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe', sys.executable])
    import os
    hub = executable(args.hub_python, [Path(os.environ.get('LOCALAPPDATA', str(Path.home())))/'FahadRobotHub/runtime/Scripts/python.exe', sys.executable])
    node = executable(args.node, [shutil.which('node') or ''])
    directory = args.output or ROOT/'tmp/quality_reports'/(
        datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    checks = []
    def add(name, argv, result_file=None):
        print('Checking '+name+' ...', flush=True)
        record = run_command(name, argv, directory, result_file=result_file)
        checks.append(record)
        print('  '+record['status'], flush=True)
    try:
        count = static_checks()
        checks.append({'name': 'python_syntax_and_configuration', 'status': 'pass', 'files_checked': count})
    except (SyntaxError, ValueError, OSError) as exc:
        checks.append({'name': 'python_syntax_and_configuration', 'status': 'fail', 'reason': str(exc)[:1500]})
    add('git_whitespace', [shutil.which('git'), 'diff', '--check', 'HEAD'])
    for name, python, start in [('tools_python', helper, 'Tools'),
                                ('dashboard_python', sys.executable, 'Tools/remote_dashboard'),
                                ('hub_python', hub, 'Tools/robot_hub')]:
        result_file = directory/(name+'.json')
        add(name, [python, str(ROOT/'Tools/quality_suite.py'), '--start', str(ROOT/start), '--result', str(result_file)], result_file)
    for relative in ['Tools/remote_dashboard/test_frontend.js', 'Tools/remote_dashboard/test_sensor_view.js',
                     'Tools/remote_dashboard/test_joystick.js', 'Tools/remote_dashboard/test_web_frontend.js',
                     'Tools/test_analysis_modules.js', 'Tools/test_annotation_review_core.js']:
        add(Path(relative).stem, [node, str(ROOT/relative)])
    js_files = sorted((ROOT/'Tools').glob('*.js')) + sorted((ROOT/'Tools/remote_dashboard').glob('*.js')) + sorted((ROOT/'Tools/remote_dashboard/dist').glob('*.js'))
    for path in js_files:
        add('syntax_'+path.parent.name+'_'+path.name, [node, '--check', str(path)])
    inventory_code = "import platform,json;from importlib import metadata;print(json.dumps({'python':platform.python_version(),'numpy':metadata.version('numpy')}))"
    add('tools_environment', [helper, '-c', inventory_code])
    hub_code = "import platform,json;from importlib import metadata;print(json.dumps({'python':platform.python_version(),'paramiko':metadata.version('paramiko')}))"
    add('hub_environment', [hub, '-c', hub_code])
    add('node_environment', [node, '--version'])
    add('git_environment', [shutil.which('git'), '--version'])
    metadata = {'runner_python': platform.python_version(), 'platform': platform.system(),
                'tools_python': helper, 'hub_python': hub, 'node': node}
    git = shutil.which('git')
    if git:
        commit = subprocess.run([git,'rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
        dirty = subprocess.run([git,'status','--porcelain'],cwd=ROOT,capture_output=True,text=True)
        metadata.update(source_commit=commit.stdout.strip() if commit.returncode==0 else None,
                        source_dirty=bool(dirty.stdout.strip()) if dirty.returncode==0 else None,
                        source_sha256=source_inventory(git))
    result = write_summary(directory, checks, metadata)
    print('\nReport: '+str(directory/'summary.md'), flush=True)
    print('PASS' if result == 0 else 'ATTENTION REQUIRED: inspect report; no failures were hidden.', flush=True)
    return result


if __name__ == '__main__':
    sys.exit(main())
