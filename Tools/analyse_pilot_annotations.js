'use strict';

// Offline analysis only: reads exported human labels and the saved predictions.
// Uses the exact matching rules shared by the annotation page; no ROS access.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const core = require('./annotation_review_core.js');

function buildPilotEvaluation(projectRoot=path.resolve(__dirname,'..')) {
  const root = path.resolve(projectRoot);
  const annotationPath = path.join(root, 'Annotation Review', 'pilot_annotations.json');
  const manifestPath = path.join(root, 'Annotation Review', 'pilot_manifest.json');
  const annotationBytes = fs.readFileSync(annotationPath);
  const manifestBytes = fs.readFileSync(manifestPath);
  const labels = JSON.parse(annotationBytes);
  const manifest = JSON.parse(manifestBytes);
  const sha = data => crypto.createHash('sha256').update(data).digest('hex');
  const errors = [];
  const warnings = [];
  if (labels.schema_version !== 1 || manifest.schema_version !== 1) errors.push('Unexpected schema version.');
  if (labels.dataset_id !== manifest.dataset_id) errors.push('Dataset identity mismatch.');
  if (!Array.isArray(manifest.frames) || !labels.annotations || typeof labels.annotations !== 'object') {
    throw new Error('Missing frame list or annotation object.');
  }
  const ids = new Set();
  const counts = {frames: manifest.frames.length, reviewed: 0, regular_reviewed: 0, challenge_reviewed: 0,
    boxes: {person: 0, chair: 0, ignore: 0}, occluded: {person: 0, chair: 0}, sources: {}, notes: [],
    image_hashes_checked: 0};
  const exactSuggestions = [];
  for (const frame of manifest.frames) {
    if (ids.has(frame.id)) errors.push(`Duplicate frame: ${frame.id}`);
    ids.add(frame.id);
    const state = labels.annotations[frame.id];
    if (!state) { errors.push(`Missing annotation entry: ${frame.id}`); continue; }
    if (typeof state.reviewed !== 'boolean' || !Array.isArray(state.boxes)) {
      errors.push(`Invalid annotation structure: ${frame.id}`); continue;
    }
    if (state.reviewed) {
      counts.reviewed++;
      if (frame.cohort === 'regular') counts.regular_reviewed++;
      if (frame.cohort === 'challenge') counts.challenge_reviewed++;
    }
    if (state.notes) counts.notes.push({id: frame.id, notes: state.notes});
    for (const [index, box] of state.boxes.entries()) {
      if (!['person', 'chair', 'ignore'].includes(box.class)) errors.push(`Unknown class: ${frame.id} box ${index}`);
      const coords = ['xmin', 'ymin', 'xmax', 'ymax'];
      if (!coords.every(key => Number.isFinite(box[key])) ||
          !(box.xmax > box.xmin && box.ymax > box.ymin) ||
          box.xmin < 0 || box.ymin < 0 || box.xmax > frame.width || box.ymax > frame.height) {
        errors.push(`Invalid coordinates: ${frame.id} box ${index}`);
      }
      if (state.reviewed && Object.hasOwn(counts.boxes, box.class)) counts.boxes[box.class]++;
      if (state.reviewed && box.occluded && Object.hasOwn(counts.occluded, box.class)) counts.occluded[box.class]++;
      counts.sources[box.source || 'unspecified'] = (counts.sources[box.source || 'unspecified'] || 0) + 1;
      if (frame.predictions.some(pred => pred.class === box.class && coords.every(key => pred[key] === box[key]))) {
        exactSuggestions.push({id: frame.id, box: index, class: box.class});
      }
    }
    const imagePath = path.resolve(root, frame.source_path);
    if (!imagePath.startsWith(root + path.sep)) { errors.push(`Source path outside workspace: ${frame.id}`); continue; }
    if (!fs.existsSync(imagePath)) { errors.push(`Missing raw image: ${frame.id}`); continue; }
    counts.image_hashes_checked++;
    if (sha(fs.readFileSync(imagePath)) !== frame.raw_sha256) errors.push(`Raw image hash mismatch: ${frame.id}`);
  }
  for (const id of Object.keys(labels.annotations)) if (!ids.has(id)) errors.push(`Unknown exported frame: ${id}`);
  if (counts.reviewed !== counts.frames) warnings.push('Some frames are not confirmed and are excluded from scoring.');
  if (counts.boxes.ignore === 0) warnings.push('No uncertain/ignore regions were marked; check ambiguous background instances.');
  if (counts.occluded.person === 0 && counts.occluded.chair === 0) warnings.push('No partial-occlusion flags were marked; visible occlusion examples need review.');
  if (errors.length) return {report:null,summary:{errors,counts},outputPath:null,exitCode:1};
  
  const settings = [];
  for (const cutoff of [0.3, 0.5, 0.7]) for (const nms of [false, true]) {
    const cohorts = {};
    for (const cohort of ['regular', 'challenge']) cohorts[cohort] = core.evaluateReviewed(manifest.frames, labels.annotations, cutoff, nms, cohort);
    const scenes = {};
    for (const session of [...new Set(manifest.frames.filter(f => f.cohort === 'regular').map(f => f.session))]) {
      const frames = manifest.frames.filter(f => f.session === session);
      scenes[session] = {scene: frames[0].scene, ...core.evaluateReviewed(frames, labels.annotations, cutoff, nms)};
    }
    settings.push({cutoff, additional_same_class_nms: nms, cohorts, scenes});
  }
  const frames = manifest.frames.map(frame => {
    const state = labels.annotations[frame.id];
    const base = core.evaluateFrame(state.boxes, frame.predictions, 0.3, false);
    const extraNms = core.evaluateFrame(state.boxes, frame.predictions, 0.3, true);
    const targets = state.boxes.filter(b => ['person', 'chair'].includes(b.class));
    return {id: frame.id, scene: frame.scene, cohort: frame.cohort, reviewed: state.reviewed,
      actual: {person: targets.filter(b => b.class === 'person').length, chair: targets.filter(b => b.class === 'chair').length},
      baseline: base, additional_same_class_nms: extraNms,
      targets: targets.map(box => {
        const sameClass = frame.predictions.filter(p => p.class === box.class);
        const overlaps = sameClass.map(p => ({iou: core.boxIoU(box, p), score: p.score, box: p})).sort((a,b) => b.iou - a.iou);
        return {...box, best_prediction: overlaps[0] || null};
      }), predictions: frame.predictions, notes: state.notes || ''};
  });
  const qualitativeAudit = {status: 'provisional_needs_label_revision', raw_images_spot_checked: 8,
    observations: [
      {id: 'test_20261006_095152_mBfTDG/images/0001_raw.jpg', issue: 'No chair labels despite identifiable left foreground and right-edge chairs.'},
      {id: 'test_20261006_095152_mBfTDG/images/0029_raw.jpg', issue: 'No chair labels despite visible foreground chairs.'},
      {id: 'test_20261006_095152_mBfTDG/images/0041_raw.jpg', issue: 'Person box spans y=288..378; visible head and lower legs extend outside it. Right-edge chair unlabelled; check left chair box includes visible seat as well as back.'},
      {id: 'test_20261006_095313_DPE9UF/images/0001_raw.jpg', issue: 'Foreground left and right chairs are visible; only one chair label. Check coverage/occlusion conventions.'},
      {id: 'test_20261006_095313_DPE9UF/images/0030_raw.jpg', issue: 'Challenge person has head/upper-region box only, omitting visible body parts beside/below chair; partial occlusion flag is false.'}
    ],
    instruction: 'Preserve original export. User should revise coverage and visible-extent boxes in reviewer and export a new copy. Metrics below are conditional on current incomplete labels, not accepted final ground truth.'};
  const report = {schema_version: 1, dataset_id: manifest.dataset_id, exported_at: labels.exported_at,
    status: qualitativeAudit.status, qualitative_audit: qualitativeAudit,
    policy: labels.policy, rules: {match_iou: 0.5, prediction_score_cutoffs: [0.3, 0.5, 0.7],
      additional_nms_iou: 0.5, ignore_prediction_fraction: 0.5, reviewed_only: true, cohorts_separate: true},
    hashes: {annotations_sha256: sha(annotationBytes), manifest_sha256: sha(manifestBytes)},
    errors, warnings, counts, exact_original_prediction_boxes: exactSuggestions.length,
    settings, frames,
    limitations: ['Small development pilot, repeated frames from one room/participant.',
      'Human-reviewed labels require consistency/coverage checks; suggested labels are not independent until checked.',
      'Box matching measures category plus localization, not biological life, range or general rescue reliability.',
      'Challenge frame selected for a known failure is excluded from regular metrics.',
      'Cutoff results are post-filtering of saved outputs, not fresh robot inference or a runtime benchmark.']};
  const outputPath = path.join(root, 'Annotation Review', 'pilot_evaluation_2026-10-12.json');
  const summary = {output: outputPath, counts, warnings,
    status: qualitativeAudit.status,
    exact_original_prediction_boxes: exactSuggestions.length,
    regular: settings.map(s => ({cutoff: s.cutoff, nms: s.additional_same_class_nms, ...s.cohorts.regular})),
    challenge: settings[0].cohorts.challenge,
    scenes: settings[0].scenes,
    frames: frames.map(f => ({id: f.id, cohort: f.cohort, actual: f.actual, baseline: f.baseline,
      no_match_targets: f.targets.filter(t => !t.best_prediction || t.best_prediction.iou < 0.5).map(t => ({class: t.class,
        best_iou: t.best_prediction?.iou, score: t.best_prediction?.score}))}))};
  return {report,summary,outputPath,exitCode:0};
}

function main(){
  const {report,summary,outputPath,exitCode}=buildPilotEvaluation();
  if(report)fs.writeFileSync(outputPath,JSON.stringify(report,null,2)+'\n');
  process.stdout.write(JSON.stringify(summary,null,2)+'\n');
  process.exitCode=exitCode;
}

module.exports={buildPilotEvaluation,main};
if(require.main===module)main();
