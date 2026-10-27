"""Checksummed fixed-runtime manifest, independent of SSH and native UI."""
import hashlib
from pathlib import Path
from agent import VERSION, RUNTIME_FILES, SHARED_RUNTIME_FILES, bundle_id


def source_file(source, name):
    if name not in RUNTIME_FILES:
        raise RuntimeError('Unlisted runtime dependency')
    root = Path(source).resolve()
    shared = name in SHARED_RUNTIME_FILES
    allowed_root = (root.parent / 'fahad_core').resolve() if shared else root
    if shared and not allowed_root.is_relative_to(root.parent):
        raise RuntimeError('Shared dependency escapes source workspace')
    path = (allowed_root / (Path(name).name if shared else name)).resolve()
    if not path.is_relative_to(allowed_root) or path.stat().st_size > 524288:
        raise RuntimeError('Invalid local runtime file: ' + name)
    return path


def local_manifest(source):
    files = {}
    root = Path(source).resolve()
    for name in RUNTIME_FILES:
        path = source_file(root, name)
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {'version': VERSION, 'files': files, 'bundle_id': bundle_id(files)}
