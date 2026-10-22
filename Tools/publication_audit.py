"""Read-only, best-effort public-source/history audit; never prints matched secrets.

This is not a proof that data is non-sensitive. Review the publication scope too.
No robot access, credential lookup, staging, push or network requests.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {'.py', '.js', '.html', '.css', '.md', '.launch', '.sh', '.cmd', '.json'}
BLOCKED_PARTS = {'__pycache__', '.venv', 'node_modules', 'logs', 'quality_reports', 'diagnostic_reports'}
PATTERNS = {
    'private_key_header': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'github_classic_token': re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{36,}\b'),
    'github_fine_grained_token': re.compile(rb'\bgithub_pat_[A-Za-z0-9_]{40,}\b'),
    'openai_project_key': re.compile(rb'\bsk-proj-[A-Za-z0-9_-]{20,}\b'),
    'aws_access_key': re.compile(rb'\bAKIA[0-9A-Z]{16}\b'),
    'literal_credential_assignment': re.compile(
        rb'''(?i)\b(?:password|passwd|api_key|access_token|secret)["']?\s*[:=]\s*(["'])[^"'\r\n]+\1'''),
}

# One manually reviewed synthetic redaction marker. The waiver is pinned to the
# entire exact file version + location/category, never all tests or passwords.
REVIEWED_FIXTURES = {
    ('Tools/robot_hub/test_diagnostics.py', '32ecd90370c76d72f6c703c846c562b22ac857ec',
     34, 'literal_credential_assignment'): 'Synthetic redaction-test marker; not an account credential.'
}


def allowed(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or any(part in BLOCKED_PARTS for part in path.parts):
        return False
    if (path.name.startswith('.env') or path.suffix.lower() in {'.pem', '.key'} or
            any(word in path.name.lower() for word in ('credentials', 'secrets'))):
        return False
    if len(path.parts) == 1:
        return name in ('.gitignore', '.gitattributes') or path.suffix == '.md'
    if path.parts[0] == 'Documentation':
        return len(path.parts) == 2 and path.suffix == '.md'
    if path.parts[:2] == ('Testing other Models', 'DetectorTest'):
        return len(path.parts) == 3 and path.name in ('test_detector.py', 'detector_model.py')
    if path.parts[0] == '.github':
        return name == '.github/ci-requirements.txt' or (path.parts[:2] == ('.github', 'workflows') and path.suffix in ('.yml', '.yaml'))
    if path.parts[0] == 'Tools':
        return path.suffix in EXTENSIONS or path.name == '.gitignore' or (
            path.name.startswith('requirements') and path.suffix == '.txt')
    return False


def findings(data):
    return [{'category': kind, 'line': data.count(b'\n', 0, match.start()) + 1}
            for kind, pattern in PATTERNS.items() for match in pattern.finditer(data)]


def git(*args, root=ROOT):
    return subprocess.run(['git', *args], cwd=root, check=True, capture_output=True).stdout


def audit(root=ROOT):
    commits = git('rev-list', '--all', root=root).decode('ascii').splitlines()
    issues, seen, blobs, reviewed = [], set(), {}, []
    for commit in commits:
        entries = git('ls-tree', '-r', '-z', commit, root=root).split(b'\0')
        for entry in filter(None, entries):
            metadata, name = entry.split(b'\t', 1)
            mode, kind, sha = metadata.decode('ascii').split()
            name = name.decode('utf8')
            if not allowed(name) or kind != 'blob' or mode not in ('100644', '100755'):
                issues.append({'commit': commit, 'path': name, 'category': 'outside_source_allowlist'})
                continue
            if (name, sha) in seen:
                continue
            seen.add((name, sha))
            if sha not in blobs:
                blobs[sha] = git('cat-file', 'blob', sha, root=root)
            data = blobs[sha]
            if len(data) > 2097152:
                issues.append({'commit': commit, 'path': name, 'category': 'source_file_over_2MiB'})
            if b'\0' in data:
                issues.append({'commit': commit, 'path': name, 'category': 'binary_source'})
            for item in findings(data):
                reason = REVIEWED_FIXTURES.get((name, sha, item['line'], item['category']))
                if reason:
                    reviewed.append(dict(item, path=name, blob_sha=sha, review=reason))
                else:
                    issues.append(dict(item, commit=commit, path=name))
    return {'schema_version': 1, 'commits_checked': len(commits), 'unique_blobs_checked': len(blobs),
            'reviewed_synthetic_findings': reviewed,
            'issues': issues, 'status': 'attention_required' if issues else 'pass',
            'limitations': ['Pattern/path audit is not a guarantee that all secrets/private information were detected.',
                            'Audits committed reachable history only; stage/commit intended changes and rerun before publication.',
                            'Reports categories/locations, never secret values; no publication or history rewriting occurs.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    result = audit()
    if args.output:
        # Do not replace an existing audit record.
        with args.output.open('x', encoding='utf8') as handle:
            json.dump(result, handle, indent=2)
    print(json.dumps(result, indent=2))
    return 1 if result['issues'] else 0


if __name__ == '__main__':
    sys.exit(main())
