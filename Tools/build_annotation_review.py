"""Build a self-contained local annotation page from existing pilot captures.

Run with Python 3 on Windows. Raw recording files are only read.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path


def build(project_root, output):
    source = project_root / 'Tool reports' / 'detection_tests'
    frames = []
    scenes = {'095017': 'Empty room', '095152': 'Person moving', '095313': 'Person with chair'}
    for folder in sorted(source.iterdir()):
        if not folder.is_dir() or not (folder / 'events.jsonl').is_file():
            continue
        session = json.loads((folder / 'session.json').read_text(encoding='utf-8'))
        records = [json.loads(line) for line in (folder / 'events.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        samples = [record for record in records if record.get('kind') == 'image_sample']
        if not samples:
            continue
        count = min(10, len(samples))
        positions = sorted(set(round(i * (len(samples) - 1) / max(1, count - 1)) for i in range(count)))
        chosen = [(samples[position], 'regular') for position in positions]
        if '095313' in folder.name:
            challenge = next((sample for sample in samples if sample['raw_image'] == 'images/0030_raw.jpg'), None)
            if challenge and all(sample['raw_image'] != challenge['raw_image'] for sample, _ in chosen):
                chosen.append((challenge, 'challenge'))
        scene = next((label for key, label in scenes.items() if key in folder.name), session.get('notes', folder.name))
        for sample, cohort in chosen:
            original = folder / sample['raw_image']
            content = original.read_bytes()
            frames.append({
                'id': folder.name + '/' + sample['raw_image'], 'session': folder.name,
                'scene': scene, 'cohort': cohort, 'sample': sample['sample'],
                'notes': session.get('notes', ''), 'elapsed_s': sample['elapsed_s'],
                'width': sample['width'], 'height': sample['height'],
                'image_header': sample['image_header'], 'raw_sha256': hashlib.sha256(content).hexdigest(),
                'source_path': str(original.relative_to(project_root)).replace('\\', '/'),
                'predictions': sample['boxes'] or [],
                'image': 'data:image/jpeg;base64,' + base64.b64encode(content).decode('ascii')})
    fingerprint = hashlib.sha256(''.join(frame['id'] + frame['raw_sha256'] for frame in frames).encode()).hexdigest()[:20]
    dataset = {'schema_version': 1, 'dataset_id': 'pilot-' + fingerprint, 'frames': frames,
               'policy': 'Visible-extents boxes; person and chair; uncertain regions ignored; reviewed-only scoring; IoU >= 0.5.'}
    tools = project_root / 'Tools'
    template = (tools / 'annotation_review_template.html').read_text(encoding='utf-8')
    core = (tools / 'annotation_review_core.js').read_text(encoding='utf-8')
    encoded = json.dumps(dataset, ensure_ascii=True).replace('<', '\\u003c')
    for token in ('__CORE_SCRIPT__', '__DATA_JSON__'):
        if template.count(token) != 1:
            raise ValueError('Expected one template placeholder: ' + token)
    result = template.replace('__CORE_SCRIPT__', core).replace('__DATA_JSON__', encoded)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, encoding='utf-8')
    manifest = dict(dataset)
    manifest['frames'] = [{key: value for key, value in frame.items() if key != 'image'} for frame in frames]
    (output.parent / 'pilot_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(output), 'frames': len(frames), 'regular': sum(f['cohort'] == 'regular' for f in frames),
                      'challenge': sum(f['cohort'] == 'challenge' for f in frames), 'bytes': output.stat().st_size}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    build(args.project, args.output or args.project / 'Annotation Review' / 'pilot_annotation_review.html')
