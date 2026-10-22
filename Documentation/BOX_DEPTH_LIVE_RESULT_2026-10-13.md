# Manual box-patch depth: first live result

Evidence: `Terminal Reports/box_depth_20261013_131056.txt`, uploaded 2026-10-13.
User says they moved the box(es) forwards/backwards and finally farther away to
camera-right; the old pixel selection then pointed to the lab wall, before they
clicked the box again. No screenshot, raw images or measured reference distances
accompany this report. Original report preserved.

## Milestone demonstrated

The helper ran on the robot, received RGB/registered-depth pairs and printed ten
SELECTED events plus thirty periodic LIVE rows. Reported manual clicks support
live window interaction; 32FC1 conversion and local patch readings are demonstrated
without a shown exception or rejected-pair warning. A rendered screenshot and the
exact Python/OpenCV versions are not captured. Source remains read-only; this
analysis does not prove no unrelated motion-capable nodes were running.

## Sequence and interpretation

| Stage | Recorded patch median | Interpretation |
|---|---|---|
| Early selections at several pixels | 0.801-0.814 m | Repeated near-target readings; box identity based on user's account, not paired images. |
| Following movement/selection | 1.079-1.093 m | Readings consistent with a farther surface; reference distance unknown. |
| Farther stage | 1.944 m, then 2.061-2.074 m | Values near/beyond the documented planning range; cannot quantify accuracy. |
| Old selection (232,287) after box moved right | 3.803-3.846 m | User identifies the sampled surface as the lab wall, not a faulty jump on a tracked box. |
| New click at (381,304) | 2.498 m in SELECTED and two LIVE rows | User identifies the reselected surface as the box; reselection changed the sampled location. |

The old-patch median changes and the final reselected median match the user's
qualitative description. This helper samples fixed image coordinates until
clicked again. It does not know that an object moved, preserve identity or follow
it. Therefore do not count wall rows as box errors or infer target motion from
every depth change alone.

Within some sampled plateaus the same median repeats and the patch's min/max are
close. That is short-run local consistency, not millimetre accuracy, a complete
temporal noise measurement or reliable maximum range. Forty printed rows are
sparse observations, not all frames or independent calibration trials.

## Availability and timing

- Thirty-six of forty rows show 100.0% finite-positive pixels in the selected
  patch. Four rows show 98.3%, 85.1%, 93.4% and 91.7%. This is selected-region
  availability, not improved full-image coverage compared with yesterday's ~59%.
- The `in 0.4-2m` value drops to 0% for the >2 m stages because that is the
  implemented numeric range rule, not a driver failure or a zero-confidence score.
- Thirty printed LIVE header differences span 1.3-34.6 ms, below the helper's
  50 ms approximate-pairing limit. These are reported header differences, not
  inference latency, exact same-exposure pairing or proof of spatial registration.
- SELECTED metadata names `camera_rgb_optical_frame`, `32FC1`, and `frozen False`.
  No frozen-mode run is recorded. Text alone does not verify surface boundaries
  against RGB or resolve the prior CameraInfo offset discrepancy.

## Range and accuracy boundary

The robot can publish positive readings beyond 2 m. That does not establish
accurate extended-range operation of the driver-identified Astra S; the documented
0.4-2 m specification remains the planning reference until measured experiments
or stronger hardware evidence establish otherwise. Do not discard or rescale the
observed 2.498 m value by guesswork. Yesterday's repeated 9.78 m maximum is still
unexplained; today's user-identified wall selection does not validate it.

No ruler/tape was used. Consequently absolute error, percentage error, successful
1 m calibration and accurate wall/box distances cannot be calculated. The user
estimated initial placement, so 0.81 m cannot be interpreted as 19 cm sensor error.
ROS depth is optical-axis Z, not necessarily Euclidean range to a side-positioned
object or distance from the robot's chassis.

## Next step

Manual patch extraction is now live-demonstrated; do not repeat its basic startup
test. Obtain one screenshot with both panels and the box patch visible (Space
can freeze a labelled historical pair). This permits a preliminary visual check
before a limited person-depth prototype; it is not a full calibration requirement
or another annotation exercise.

The next prototype would refresh its region from each YOLO person box, associate
the box's original image header with corresponding RGB/depth rather than an arbitrary
latest frame, and report unavailable/unverified depth instead of fabricating distance.
A fixed centre or whole-box median can still hit background/floor/chair under
occlusion; region choice and validity checks need testing. No tracking, person-depth
node, measured calibration, semantic map or navigation change is implemented by
this analysis. Final accuracy still requires independent measured references.
