"""Read-only source catalogue. Parsing files never imports or launches ROS code."""
import os
from pathlib import Path
import xml.etree.ElementTree as ET

MAX_XML_BYTES = 512 * 1024
SKIP = {'.git', 'node_modules', '__pycache__', 'build', 'devel', 'install', '.venv'}


def xml_root(path):
    """Parse bounded XML without DTD/entity expansion."""
    with open(str(path), 'rb') as handle:
        data = handle.read(MAX_XML_BYTES + 1)
    if len(data) > MAX_XML_BYTES or b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('Unsupported or oversized XML')
    return ET.fromstring(data)


def discover_files(root, limit=25000):
    """Sorted, bounded traversal; never follow directory or file symlinks."""
    root = Path(root).resolve()
    count = 0
    for directory, dirs, files in os.walk(str(root), followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not Path(directory, d).is_symlink())
        for name in sorted(files):
            path = Path(directory, name)
            if path.is_symlink():
                continue
            count += 1
            if count > limit:
                raise ValueError('File traversal limit reached; select a smaller root')
            yield path


def catalogue(root, limit=25000):
    """Index package manifests and launch declarations, not hardware capability."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Source root is not a directory')
    packages, launches, issues = [], [], []
    for path in discover_files(root, limit):
        if path.name != 'package.xml' and path.suffix != '.launch':
            continue
        relative = path.relative_to(root).as_posix()
        try:
            element = xml_root(path)
            if path.name == 'package.xml':
                if element.tag != 'package':
                    raise ValueError('Unexpected manifest root')
                packages.append({'name': (element.findtext('name') or '').strip(),
                                 'version': (element.findtext('version') or '').strip(),
                                 'path': relative,
                                 'dependencies': sorted(set((e.text or '').strip() for e in element
                                                           if e.tag.endswith('depend') and (e.text or '').strip()))})
            elif element.tag == 'launch':
                # Do not export parameter values, command arguments or raw XML.
                launches.append({'path': relative, 'nodes': [
                    {'package': e.get('pkg', ''), 'type': e.get('type', '')}
                    for e in element.iter('node')][:200],
                    'includes': [e.get('file', '') for e in element.iter('include')][:100]})
        except (OSError, ValueError, ET.ParseError):
            issues.append({'path': relative, 'issue': 'unreadable_or_unsupported_xml'})
    return {'packages': packages, 'launches': launches, 'issues': issues,
            'evidence': 'source_files_only',
            'limitations': ['Presence is not proof of build, installation, matching hardware or successful operation.',
                            'Conditional launches/includes are declarations, not resolved or executed.']}
