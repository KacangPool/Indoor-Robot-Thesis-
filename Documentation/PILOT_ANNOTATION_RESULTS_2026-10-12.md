# First annotation export: validation, provisional results and corrections

Analysed 2026-10-12. Status: **usable first pass; label revision needed before accepting evaluation scores**.

## Saved export validated

`Annotation Review/pilot_annotations.json` has the correct dataset identity (`pilot-e2507a3c25ac4254aa1e`). All 31 frames are marked reviewed: 30 regular examples and one separately selected challenge case. All entries have known classes and valid finite, ordered, in-image rectangles. All 31 raw-image hashes match the manifest. No unknown/missing frame entries or source changes were found.

The export contains 21 person boxes and 50 chair boxes across all 31 images. Of these, the regular cohort contains 20 person boxes and 48 chair boxes. These are repeated object appearances across images, not 21 unique people or 50 unique chairs. There are no ignore regions, partial-occlusion flags or notes. Sixty-seven boxes retain suggestion provenance and four have manual provenance; 49 match an original same-class prediction rectangle exactly. Suggestions are allowed and this does not itself invalidate labels, but acceptance must be based on actual image contents rather than agreement with YOLO.

Original export SHA-256: `d044fbe5ca7629df0809e1f8c61c543dc6fa7830a1aad8cac3c97ebf94c576b3`.

Manifest SHA-256: `05d215bb4897b9ec4e59fc50f06efa7a8db498ea262058c826e8801b8298c1ef`.

## Visual quality checks reveal two consistency issues

Eight raw images were spot-checked against exported box coordinates. This is not a complete independent relabelling of all 31 images.

1. **All identifiable target objects need labels.** In moving-person images `0001_raw.jpg` and `0029_raw.jpg`, there are zero chair labels although identifiable chairs appear at the left foreground and right image edge. The seated-person run's `0001_raw.jpg` also shows foreground chairs at both sides while only one chair is labelled. The scene name does not restrict the categories to label. Omissions can hide missed chairs or make real chair predictions count as false alarms.
2. **Boxes must consistently enclose the visible parts of the object.** Moving-person `0041_raw.jpg` has a person rectangle from y=288 to y=378, leaving the visible head and lower legs outside it. In the extra challenge image (chair run `0030_raw.jpg`), the person rectangle covers the head/upper region but omits visible body parts beside/below the red chair. The person is partly occluded, yet the flag is false. Box-position and occlusion conventions need a correction pass. Some chair boxes should also be checked to include the visible seat, not only the back.

Relevant page positions in the original manifest order:

| Position | Run / raw filename | Check |
| --- | --- | --- |
| 11 | Person moving / 0001 | Add identifiable edge/foreground chairs |
| 16 | Person moving / 0029 | Add identifiable edge/foreground chairs |
| 18 | Person moving / 0041 | Expand person box to all visible parts; check chair coverage |
| 21 | Person with chair / 0001 | Check both edge chairs and visible seat/back extents |
| 31 | Challenge / 0030 | Expand visible-person rectangle and tick Partly hidden |

These are examples, not the entire correction list. Scan the other frames for the same two patterns. Background objects should be labelled if confidently identifiable. Use Ignore region only for genuinely ambiguous identities; do not ignore clear targets or missed objects merely to improve scores.

The challenge image already correctly records that a person is present despite no YOLO person prediction. It remains a clear failure case regardless of the needed rectangle correction.

## Provisional calculation using the export exactly as received

The following results are **conditional on incomplete/current labels**, not accepted accuracy estimates. One-to-one same-class matching requires IoU >=0.5. Other classes are outside this person/chair scoring. The 30 regular images are kept separate from the challenge.

| Cutoff | Person matched / extra / unmatched reference | Person precision / recall | Chair matched / extra / unmatched reference | Chair precision / recall |
| --- | --- | --- | --- | --- |
| 0.3 | 20 / 14 / 0 | 58.8% / 100.0% | 34 / 15 / 14 | 69.4% / 70.8% |
| 0.5 | 20 / 3 / 0 | 87.0% / 100.0% | 23 / 0 / 25 | 100.0% / 47.9% |
| 0.7 | 16 / 2 / 4 | 88.9% / 80.0% | 2 / 0 / 46 | 100.0% / 4.2% |

An unmatched prediction can be a false category, duplicate or poor localization; it is not necessarily an invented physical object. A poorly positioned prediction can contribute both an extra box and an unmatched reference object. Unmarked/poorly boxed actual objects affect these calculations, which is why chair numbers and localization scores must be recomputed after revision.

Additional same-class duplicate suppression at IoU >0.5 does not change these counts at any tested cutoff in either cohort. This does not prove duplicates are absent; overlapping boxes can have IoU below that criterion. The copied detector already performs NMS internally.

The separate challenge image contains one labelled person and two labelled chairs. At cutoff 0.3, both chair boxes match and the person has no matching prediction. No saved person prediction exists there, so raising the cutoff cannot recover that miss. Do not combine the selected challenge into the regular headline score.

All 14 baseline extra person boxes in the regular cohort occur in the moving-person run under the current labels. The 0.5 cutoff retains matches to all 20 current regular person references and reduces extra person boxes to three. This is an offline candidate worth retesting, not an instruction to change the robot's global threshold. A common 0.5 cutoff removes many chair matches, and the tiny pilot does not establish safe target recall.

## Next action

1. Reopen the existing review page. If needed, use Load saved labels to import `pilot_annotations.json` rather than starting from blank annotations.
2. Correct coverage and visible-extent rectangles using the examples above; mark partial occlusion where appropriate. Keep one reference box per actual object, not one per predicted box.
3. Reconfirm each changed image; edits return it to draft.
4. Export a new file named `pilot_annotations_v2.json` into `Annotation Review/`. Keep the first export for provenance. No user label was altered by this analysis.
5. Recompute and visually check the revised results, then choose a measured output-processing/model-comparison experiment. Independent data are still required before final accuracy or model selection. No new lab recording is needed for this correction pass.

## Reproducibility and evidence boundary

`Tools/analyse_pilot_annotations.js` reads the original export and manifest, validates references/geometry/hashes, reuses `Tools/annotation_review_core.js` for the page's exact scoring, and writes `Annotation Review/pilot_evaluation_2026-10-12.json`. The result includes settings, per-scene and per-frame counts, box-overlap diagnostics and explicit provisional/quality flags.

Shared scoring tests passed. Additional checks passed for 31 reviewed/source counts, per-scene sums, regular reference denominators, identical additional-NMS counts and preservation of the original annotation SHA-256. Visual inspection used eight raw images; original JPGs, annotations, manifest, reviewer and robot/vendor files are unchanged.

This is a small development pilot from three short sessions in one room with one participant. It does not measure unique people, final mAP, distance capability, pure inference FPS, biological life, or general search-and-rescue performance. No model training, configuration change, robot command or remote connection occurred.
