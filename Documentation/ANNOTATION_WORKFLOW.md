# Fast pilot annotation and why it matters

Open `Annotation Review/pilot_annotation_review.html` on the Windows computer
with Edge or Chrome. The page includes the camera images and needs no ROS,
Python installation, account, internet access or server. It makes no network
requests. Its source/generator are in `Tools/annotation_review_template.html`,
`Tools/annotation_review_core.js` and `Tools/build_annotation_review.py`.

## What is already automated

- Ten regularly spaced saved images from each of the three pilot runs were
  selected (30 total). The exact source paths, image SHA-256 hashes, timestamps
  and original detections are stored in `Annotation Review/pilot_manifest.json`.
- The previously identified missed-person image 0030 in the chair run was added
  as a separate challenge example. It is excluded from the regular sample's
  scores so a selected failure case does not silently skew that comparison.
- Original YOLO person/chair predictions can be copied as editable suggestions.
  They are never automatically confirmed as correct. Original other-class boxes
  can be viewed, but are not imported as person/chair truth.
- Reviewed images are automatically scored at confidence cutoffs 0.3, 0.5 and
  0.7, with and without class-specific duplicate suppression at IoU > 0.5.
- Labels can be saved/reloaded as JSON; browser storage is a convenience and
  exported JSON is the portable backup. No original recording is changed.

## What the human needs to do

1. Inspect the raw camera image. Choose Person or Chair and drag a rectangle
   around every visible instance, including partly visible instances that you
   can confidently identify. Label the actual objects, not the model's errors.
2. Enclose all visible parts using a tight rectangle. Do not infer hidden limbs,
   chair parts or the full object beyond the image boundary. Apply the same
   visible-extent convention throughout this pilot. This choice can influence
   overlap scores for partially hidden objects; it should be documented in
   later model comparisons.
3. Add YOLO suggestions if useful, then adjust positions, remove duplicates and
   false boxes, and add objects the model missed. Suggestions are optional;
   drawing independently first reduces anchoring to the tested model.
4. A person sitting in/behind a chair is a person object plus a chair object when
   both can be identified. Tick Partly hidden for affected objects. This stores
   the circumstance but does not change the scoring rule.
5. For areas where identity genuinely cannot be judged (for example an ambiguous
   tiny background shape), draw Ignore region. Do not ignore a clearly visible
   person just because the model missed them. Other classes are outside this
   two-class pilot; hand/table/animal work remains a separate project branch.
6. Check the whole image, then Confirm reviewed & next. Empty images can be
   confirmed with no person/chair boxes. Drafts are excluded from calculations.
7. Export labels periodically and when finished. Save `pilot_annotations.json`
   inside `Annotation Review/` or upload the exported file for analysis. The
   file identifies the source set; the page can reload it using Load saved labels.

Select/move/resize mode permits moving existing boxes and resizing from their
lower-right corner. Exact coordinates can also be edited in the side panel.
Undo restores recent changes for the current image. Changes to a confirmed
image return it to draft so it must be checked again.

## Clarification: small fragments, black objects and uncertainty

"Every visible instance" means every target that can be confidently identified
from the image, including its visible context. It does not mean guessing a chair
label for every dark patch because the annotator remembers the room. A cropped
chair back can still be identifiable; a tiny featureless patch may not be.
Colour or small size alone does not determine whether to ignore an object.

- Identifiable whole/partial object: label it using one tight rectangle enclosing
  all visible parts. If a back and seat belong to one chair, do not count them as
  two chairs. The rectangle may contain the occluding object between visible
  parts; do not invent hidden extents beyond the visible envelope.
- Identifiable but hard object: retain it. Mark Partly hidden for occlusion by
  another object and optionally explain low contrast/cropping in notes. A crop
  at the image edge is different from another object hiding it; the current page
  has no separate truncation flag. The occlusion flag currently records context,
  not an automatic separate scoring group.
- Genuinely unidentifiable region: use Ignore region instead of forcing a person
  or chair category. The current scorer excludes unmatched predictions with at
  least half their area within an ignore region. Do not put a clear target in an
  ignore region merely because a detector missed it.

Use this rule consistently before comparing settings/models. No minimum pixel
size or visible-fraction threshold is being introduced here. A later difficulty-
stratified experiment would need explicit criteria and software support.
Changing the label policy changes evaluation, not the camera or the detector.
If labels are later used for training, their correctness and handling of ignore
regions must be checked for that specific trainer; omitting an uncertain object
from a standard training file does not necessarily make its pixels ignored.

This clarification was prompted by the user's v2 export and uncertainty on
2026-10-12. COCO reports that even experts can disagree on ambiguous object
presence. VOC distinguishes cropping, occlusion and difficult-to-identify
objects, with difficult instances ignored in its evaluation. Our reviewer is
a simpler custom pilot, not a full implementation of either benchmark:

- https://arxiv.org/html/1405.0312v3 (Image Annotation / Annotation Performance Analysis)
- https://www.robots.ox.ac.uk/~vgg/projects/pascal/VOC/voc2012/htmldoc/index.html (section 2.5)

## How comparison works

Person and chair are evaluated separately. Predictions are sorted by score;
each can match at most one same-class reference box, and each reference box can
match at most one prediction. Matching requires intersection-over-union (IoU)
>= 0.5. A duplicate beyond the first successful match counts as a false
prediction unless candidate duplicate suppression removed it.

- Correct: prediction matches a marked object (true positive).
- False: unmatched predicted person/chair (false positive).
- Missed: marked person/chair with no matching prediction (false negative).
- Precision: correct / (correct + false).
- Recall: correct / (correct + missed).

Unmatched predictions with at least half their area in an Ignore region are
excluded. Successful target matches take precedence over ignore regions.
Undefined precision/recall is displayed as a dash rather than invented as 100%.
Other labels such as traffic light are not directly counted as false target
predictions in this two-class comparison; a chair predicted only as traffic
light can still be a missed chair. This is not all-80-class accuracy or mAP.

## How it helps the thesis and the robot

These checked labels are a reference, often called ground truth, against which
the detector can be tested. They distinguish detection of the actual person
from a person label on an unrelated background shape, and distinguish one
object from several duplicate boxes. The same images permit repeatable
comparisons between score cutoffs and postprocessing candidates.

This converts observations such as "it flickers" into documented successes,
misses and false alarms. It supports decisions about the final model and helps
prevent unreliable object labels becoming map markers. It does not itself
change YOLO or teach the robot: deployment of postprocessing or later training
is a separate step requiring its own verification.

The selected images are nearby frames from one room, one participant and three
short sessions. Their scores are development/pilot findings, not a final thesis
benchmark or a proven safety performance. Labels may later help training, but
images used to tune/train must not also supply the final unbiased evaluation.
Collect additional sessions/rooms/subjects and split at session level. The
extra challenge image is useful for debugging and should be reported separately.

## Larger datasets and automation boundary

Established tools such as CVAT support detector-assisted labelling and tracking
to reduce manual work across sequences. Human review of object identities and
missed/duplicate boxes remains necessary. Treating uncorrected predictions from
the same detector as the truth would largely measure agreement with itself.
No CVAT installation or account/cloud upload was made for this pilot.

Primary references inspected on 2026-10-09:

- https://docs.cvat.ai/docs/annotation/auto-annotation/ai-tools/
- https://docs.cvat.ai/docs/api_sdk/sdk/auto-annotation/
- https://docs.cvat.ai/docs/qa-analytics/auto-qa/

## Verification

Scoring checks pass for identical/disjoint boxes, duplicates, missing targets,
wrong classes, confidence cutoff, ignore regions, draft exclusion, challenge
cohort separation and undefined denominators. An isolated headless Edge session
tested drawing, coordinate editing, occlusion flags, confirmation, suggestions,
delete/undo, JSON export/import, browser reload, 31 embedded images and no
JavaScript page errors. Desktop and 390-pixel layouts were visually inspected;
the narrow-screen overflow found during testing was corrected. QA used
simulated annotations in a temporary browser context and did not create human
ground truth or modify user browser data.
