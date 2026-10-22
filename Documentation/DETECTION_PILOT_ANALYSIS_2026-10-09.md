# First timed detection pilot: analysis reported 2026-10-09

The recorder successfully collected three 30-second sessions under
`Tool reports/detection_tests/`. This establishes usable RGB/detection evidence
for subsequent comparisons. It also documents false classifications, duplicate
boxes and a visible person missed during occlusion.

The robot clock names these runs 2026-10-06; this document uses the date of the
user's upload and analysis. Acquisition date and clock correctness are not
independently established. All three session labels are `empty_room`, but their
notes and images describe different experiments. Original files were preserved.

## Session inventory and recording checks

| Folder suffix | Interpretation from notes/images | Duration | RGB messages | Detection records | Saved images |
|---|---|---:|---:|---:|---:|
| `095017_8Aunv9` | No people; chairs visible | 30.017 s | 889 | 278 | 53 |
| `095152_mBfTDG` | One person moving close/far | 30.029 s | 888 | 282 | 52 |
| `095313_DPE9UF` | One person moving with a chair | 30.054 s | 888 | 281 | 52 |

All statuses are `completed`, with no recorded errors or unwritten detections.
The JSONL files contain 841 detection records and 157 image samples. All 841
detection records have `image_match: exact_header`, and every detection refers
to a different source image header within its run. Every sample is in
`matched_detection` mode. All referenced image files exist, all saved image
references agree with their header keys, and the stored geometry is 640x480.

Raw JPEGs and preview JPEGs are both present for all 157 samples. Only sampled
images are archived; matching the other detection records in the live cache
does not mean their source images were also saved. This analysis checks
metadata/header agreement, not independently instrumented sensor synchronization
or the detector's internal buffer correctness.

Seven supplied offline recorder tests passed locally on Python 3 on 2026-10-09.
The uploaded completed runs additionally demonstrate the recording path working
on the robot; no separate Python 2 offline-test transcript was supplied.

## Detection observations

| Scene | Messages containing a class | Box hypotheses across messages |
|---|---|---|
| Empty room | chair 278/278; traffic light 277/278; person 0/278 | chair 814; traffic light 736 |
| Person moving | person 282/282; chair 143/282 | person 656; chair 143 |
| Person with chair | person 279/281; chair 281/281; traffic light 2/281; cup 1/281 | person 279; chair 429; traffic light 2; cup 1 |

These fractions describe labels in received detector messages. They are not
recall, precision or accuracy. A person label can refer to a background false
positive, and several boxes can refer to the same person. Distances are not
measured or supplied in the close/far session notes.

The empty-room run contains no person labels, unlike some earlier screenshots.
This is useful negative evidence for this one short scene, not a general
guarantee against false person detections. Traffic-light misclassification is
persistent in this run, rather than just a rare transient label.

Representative previews 0001, 0025 and 0045 were inspected in each run:

- Empty-room previews label foreground chairs as chairs and traffic lights,
  including overlapping boxes.
- Moving-person previews identify the visible participant, but also contain
  nested person boxes and a small background person box where a person cannot
  be verified visually. In preview 0045 that background box has score about
  0.53, so a cutoff of 0.5 would retain it.
- Person-with-chair previews show a visible person and separate chair labels.
  This establishes that chair detection can sometimes coexist with person
  detection; individual hidden chairs still need object-level evaluation.

An additional exact raw/preview pair was inspected in the third run:
`images/0030_raw.jpg` and `images/0030_preview.jpg`, at elapsed 17.13 s. The
participant is visible behind a red chair, with face/upper body exposed. The
detector supplies two chair boxes and no person box. This is a concrete missed
person example under partial occlusion. It does not establish the mechanism
causing the miss or a general occlusion failure rate.

## Timing evidence

| Scene | Median output-header minus image-header time | Range |
|---|---:|---:|
| Empty room | 306.4 ms | 269.8-384.3 ms |
| Person moving | 303.2 ms | 268.1-399.4 ms |
| Person with chair | 305.7 ms | 269.4-421.4 ms |

The repeated approximately 300 ms header gap agrees with the prior single
message observation. This reflects the published header timing; it is not
isolated neural-network execution time. The input/output receipt counts are
consistent with the previously measured roughly 29.6 Hz RGB and 9.25 Hz output.
Recording did not show a large throughput collapse in these short runs; no
controlled with/without-recorder benchmark or GPU-load check was performed.

## Confidence-cutoff comparison using saved boxes

This is a filtering calculation on existing outputs. It does not alter the
robot or rerun the model, and changing the model's internal threshold could
affect suppression/postprocessing differently.

| Scene/class | Messages with a label at >=0.3 | At >=0.5 | At >=0.7 |
|---|---:|---:|---:|
| Empty room: traffic light | 277 | 41 | 0 |
| Empty room: chair | 278 | 277 | 1 |
| Moving person: person | 282 | 276 | 171 |
| Moving person: chair | 143 | 4 | 0 |
| Person with chair: person | 279 | 277 | 259 |
| Person with chair: chair | 281 | 208 | 50 |

A cutoff of 0.5 would discard many low-score false labels, but some false
traffic-light and background-person boxes survive. A cutoff of 0.7 removes
nearly all chair labels in the empty-room run and substantially reduces person
label availability in the moving run. These tradeoffs support evaluating a
postprocessing layer against annotated images before adopting a threshold.
Persistence alone would not fix the repeatedly mislabelled traffic lights.

## Next work

1. Preserve these sessions as the baseline; use distinct labels for future runs,
   such as `empty_room`, `person_moving` and `person_with_chair`.
2. Review saved raw images with ground truth for visible people/chairs and match
   predicted boxes to actual objects. Distinguish duplicates, false positives
   and misses. Do not treat a label-anywhere count as successful detection.
3. Compare candidate score cutoffs and duplicate-box suppression using the same
   captured examples. Keep model selection open and avoid attaching unverified
   persistent labels to map objects.
4. For distance experiments, measure camera-to-person distance and use separate
   runs with repeatable poses and lighting. Depth association still requires
   the earlier RGB/depth calibration check; this RGB pilot measures no range.

## Integrity identifiers

SHA-256 of each original `events.jsonl`:

- `095017_8Aunv9`: `36dfcb8d11a51c8dc277870d12ff311e1bb88c5e9ff669b4f4d8ec80297c1a6c`
- `095152_mBfTDG`: `891d0c0e12506a95a7254dbc3d4fc6e40d1a4fd6d714fe6bbee398cc3f16c624`
- `095313_DPE9UF`: `ac45e9499412b5856905db2b82acd875670ae505199b954ccc29eeafc16319ee`
