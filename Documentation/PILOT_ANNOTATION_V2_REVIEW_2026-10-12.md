# V2 review and the boundary between partial and uncertain objects

Reviewed 2026-10-12. No human annotations, original photographs, model settings
or camera settings were changed by this analysis.

## Export checks and progress

`Annotation Review/pilot_annotations_v2.json` matches the manifest dataset ID.
All 31 entries exist; classes and finite, ordered, in-image coordinates validate.
All 31 raw-image SHA-256 hashes match the manifest. V2 changes 17 frame records
relative to the first export and contains 21 person and 73 chair boxes (+23 chair
boxes). These are per-picture appearances, not unique object counts.

Thirty images are confirmed: 29 regular and the challenge. Picture 11,
`test_20261006_095152_mBfTDG/images/0001_raw.jpg`, is still `reviewed: false` after
adding its two chair boxes. It is currently excluded by the page's scoring rule.
No ignore regions, occlusion flags or notes are present in v2.

The moving-run picture 18 person rectangle is expanded to include head/lower
legs (approximately y=256.6..427.0 instead of y=288..378). The challenge person
rectangle is also expanded to include more visible body parts, rather than only
the head/upper region. Added chair labels cover the left/right foreground or edge
objects in multiple frames. Four raw pictures were visually inspected this turn:
moving-run 0041, chair-run 0018 and 0030, and empty-run 0001. This is a spot check,
not full independent approval of every v2 rectangle.

V2 SHA-256: `3f44399268ff754d6fe68baac687763528eda19b3f4b0c2dfd00a210dc07521d`.

## What the user's concern means

The visible identity boundary matters more than simply requiring more boxes.
In inspected examples, a substantial cropped chair back at the right edge can
be identified from its outline/context. That does not justify labelling every
unrecognizable black sliver elsewhere. A low-contrast object can be difficult
without being impossible to identify; neither black colour nor partial visibility
is itself a rule for exclusion.

Clarified policy (already implicit in "confidently identify"):

1. Label confidently identifiable whole or partial targets; one box per actual
   object, enclosing its visible parts. Do not make separate chair objects for
   the back, seat and legs of the same chair.
2. Keep identifiable hard targets rather than deleting known misses. Record
   occlusion by another object with Partly hidden; note cropping/low contrast
   if useful. Cropping and occlusion are distinct.
3. Use Ignore region where the object's identity genuinely cannot be judged
   from the image, instead of forcing a class based on memory of the scene.

No automatic minimum-size or visibility cutoff is chosen. An explicit difficulty
breakdown could later be added, but the current page only has normal target boxes,
occlusion metadata and ignore regions. Its ignored-region behavior is custom and
does not replicate VOC's difficult-object handling. Apply rules consistently,
not selectively to increase a model's score.

## These annotations do not affect the camera

They are an offline reference. The same images and YOLO predictions remain
unchanged. Adding previously omitted labels may reveal additional unmatched
objects; correcting a person's extent may reveal a poorly localized prediction.
Neither change means the camera or trained model became worse.

If the labels later feed a training process, ambiguous forced labels can provide
misleading supervision. How ignore regions are represented must be verified for
the chosen trainer; a omitted uncertain object may otherwise be treated as
background. No training is happening in this review, and v2 is not being used to
train automatically. The visible-extent convention also needs documenting when
comparing pretrained detectors whose box conventions may differ.

## Conditional calculation, not final accuracy

Using the page's existing one-to-one same-class IoU >=0.5 rule on the 29
confirmed regular pictures, and excluding the separate challenge:

| Cutoff | Person matched / extra / unmatched reference | Chair matched / extra / unmatched reference |
| --- | --- | --- |
| 0.3 | 18 / 14 / 1 | 34 / 15 / 35 |
| 0.5 | 18 / 4 / 1 | 23 / 0 / 46 |
| 0.7 | 15 / 3 / 4 | 2 / 0 / 67 |

The current regular reference denominators are 19 person and 69 chair boxes.
Direct v1/v2 headline comparison is inappropriate because v1 scored 30 regular
images, whereas v2 currently scores 29 and has different reference coverage.

The person mismatch at picture 18 is a localization failure under our matching
rule: a person-labelled prediction exists, but covers too little of the corrected
human box to reach IoU 0.5. It is not absence of person recognition. The separate
challenge still has no saved person prediction and remains a detection miss.
Unmatched predictions can be wrong labels, duplicates or poor localization.

These results remain conditional pending confirmation of picture 11 and consistent
handling of ambiguous regions/occlusion. The repeated small pilot does not establish
final generalization or rescue performance.

## Suggested immediate action

Keep identifiable partial-chair labels. Only change specific genuinely ambiguous
patches to Ignore region; do not redo all labels or exclude every partial object.
Confirm picture 11 and mark clearly occluded examples. Keep both existing exports
and save any further revisions as a new version. No new lab recording or detector
threshold change is required for this clarification.

## Verification and sources

Read-only local comparison of both JSON exports, manifest and raw-file hashes;
scored using the existing `Tools/annotation_review_core.js`, not the v1 analyser's
hard-coded input/output/audit. No v1 evaluation JSON overwritten. Four raw images
viewed; source images and user annotation files preserved.

Primary sources checked:

- [COCO paper, expanded HTML](https://arxiv.org/html/1405.0312v3): ambiguous
  appearances/context and expert disagreement in annotation.
- [VOC2012 development kit](https://www.robots.ox.ac.uk/~vgg/projects/pascal/VOC/voc2012/htmldoc/index.html):
  section 2.5 distinguishes truncated, occluded and difficult objects.

The current annotation policy is our simpler project policy; this review does
not claim a universal benchmark convention or newly confirm hardware causes.
