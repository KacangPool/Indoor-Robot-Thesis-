"""Checksummed fixed-runtime manifest, independent of SSH and native UI."""
import hashlib
from pathlib import Path
from agent import VERSION, RUNTIME_FILES, bundle_id


def local_manifest(source):
    files = {}
    root = Path(source).resolve()
    for name in RUNTIME_FILES:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or path.stat().st_size > 524288:
            raise RuntimeError('Invalid local runtime file: ' + name)
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {'version': VERSION, 'files': files, 'bundle_id': bundle_id(files)}
