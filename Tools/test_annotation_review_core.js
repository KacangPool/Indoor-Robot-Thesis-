'use strict';
const assert = require('node:assert/strict');
const core = require('./annotation_review_core.js');
const box = (label = 'person', score = 0.9, xmin = 10, xmax = 110) =>
  ({class: label, score, xmin, ymin: 10, xmax, ymax: 110});
assert.equal(core.boxIoU(box(), box()), 1);
assert.equal(core.boxIoU(box(), box('person', .9, 200, 300)), 0);
const duplicate = core.evaluateFrame([box()], [box(), box()], .3);
assert.deepEqual(duplicate.person, {tp: 1, fp: 1, fn: 0, ignored: 0});
assert.deepEqual(core.evaluateFrame([box()], [box(), box()], .3, true).person,
  {tp: 1, fp: 0, fn: 0, ignored: 0});
assert.equal(core.evaluateFrame([box()], [], .3).person.fn, 1);
assert.equal(core.evaluateFrame([], [box()], .3).person.fp, 1);
assert.equal(core.evaluateFrame([box()], [box('chair')], .3).person.fn, 1);
assert.equal(core.evaluateFrame([box()], [box('chair')], .3).chair.fp, 1);
assert.equal(core.evaluateFrame([box()], [box('person', .4)], .5).person.fn, 1);
assert.deepEqual(core.evaluateFrame([box('ignore')], [box()], .3).person,
  {tp: 0, fp: 0, fn: 0, ignored: 1});
const frames = [{id: 'a', cohort: 'regular', predictions: [box()]},
  {id: 'b', cohort: 'challenge', predictions: []}];
assert.equal(core.evaluateReviewed(frames, {a: {reviewed: false, boxes: [box()]}}, .3, false).reviewed, 0);
assert.equal(core.evaluateReviewed(frames, {b: {reviewed: true, boxes: [box()]}}, .3, false).reviewed, 0);
assert.equal(core.evaluateReviewed(frames, {b: {reviewed: true, boxes: [box()]}}, .3, false, 'challenge').totals.person.fn, 1);
assert.equal(core.evaluateReviewed(frames, {}, .3, false).totals.person.precision, null);
console.log('Annotation scoring checks passed: matching, duplicates, misses, cutoff, ignores, review status and separate challenge cohort.');
