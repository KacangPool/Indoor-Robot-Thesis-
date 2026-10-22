'use strict';

// Shared by the offline page and its tests. Coordinates use image pixels.
function boxArea(box) {
  return Math.max(0, box.xmax - box.xmin) * Math.max(0, box.ymax - box.ymin);
}
function intersection(a, b) {
  return Math.max(0, Math.min(a.xmax, b.xmax) - Math.max(a.xmin, b.xmin)) *
    Math.max(0, Math.min(a.ymax, b.ymax) - Math.max(a.ymin, b.ymin));
}
function boxIoU(a, b) {
  const overlap = intersection(a, b), union = boxArea(a) + boxArea(b) - overlap;
  return union > 0 ? overlap / union : 0;
}
function suppressDuplicates(boxes, cutoff = 0.5) {
  const retained = [];
  for (const box of [...boxes].sort((a, b) => (b.score || 0) - (a.score || 0))) {
    if (!retained.some(other => other.class === box.class && boxIoU(other, box) > cutoff)) retained.push(box);
  }
  return retained;
}
function evaluateFrame(truth, predictions, scoreCutoff, useNms = false) {
  const targets = ['person', 'chair'];
  const actual = truth.filter(box => targets.includes(box.class));
  const ignored = truth.filter(box => box.class === 'ignore');
  let predicted = predictions.filter(box => targets.includes(box.class) &&
    Number.isFinite(box.score) && box.score >= scoreCutoff);
  if (useNms) predicted = suppressDuplicates(predicted);
  predicted.sort((a, b) => b.score - a.score);
  const matched = new Set();
  const result = Object.fromEntries(targets.map(label => [label, {tp: 0, fp: 0, fn: 0, ignored: 0}]));
  for (const prediction of predicted) {
    let best = -1, overlap = -1;
    actual.forEach((box, index) => {
      const iou = boxIoU(box, prediction);
      if (!matched.has(index) && box.class === prediction.class && iou >= 0.5 && iou > overlap) {
        best = index; overlap = iou;
      }
    });
    if (best >= 0) { matched.add(best); result[prediction.class].tp += 1; }
    else if (ignored.some(box => boxArea(prediction) > 0 && intersection(box, prediction) / boxArea(prediction) >= 0.5)) {
      result[prediction.class].ignored += 1;
    } else result[prediction.class].fp += 1;
  }
  actual.forEach((box, index) => { if (!matched.has(index)) result[box.class].fn += 1; });
  return result;
}
function evaluateReviewed(frames, states, cutoff, useNms, cohort = 'regular') {
  const totals = {person: {tp: 0, fp: 0, fn: 0, ignored: 0}, chair: {tp: 0, fp: 0, fn: 0, ignored: 0}};
  let reviewed = 0;
  for (const frame of frames) {
    const state = states[frame.id];
    if (frame.cohort !== cohort || !state || state.reviewed !== true) continue;
    reviewed += 1;
    const result = evaluateFrame(state.boxes, frame.predictions, cutoff, useNms);
    for (const label of ['person', 'chair']) for (const field of ['tp', 'fp', 'fn', 'ignored']) totals[label][field] += result[label][field];
  }
  for (const value of Object.values(totals)) {
    value.precision = value.tp + value.fp > 0 ? value.tp / (value.tp + value.fp) : null;
    value.recall = value.tp + value.fn > 0 ? value.tp / (value.tp + value.fn) : null;
  }
  return {reviewed, totals};
}
const AnnotationCore = {boxArea, boxIoU, suppressDuplicates, evaluateFrame, evaluateReviewed};
if (typeof module !== 'undefined' && module.exports) module.exports = AnnotationCore;
