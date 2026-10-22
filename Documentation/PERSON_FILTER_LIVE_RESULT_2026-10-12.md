# First live person-filter result

Evidence: `Terminal Reports/report_1500_12102026.txt`, supplied as two terminal outputs combined by the user on 2026-10-12. This is uploaded terminal evidence, not a direct connection to the robot.

## Confirmed milestone

The robot ran `python ~/fahad/tools/person_detection_filter.py --threshold 0.5` without a shown import/traceback error, received original detection messages, and published serializable `darknet_ros_msgs/BoundingBoxes` output readable on `/fahad/person_boxes`. Live ROS subscription/filter/publication is now demonstrated; the exact interpreter version is not printed by this report.

Two filtered samples contain one box each:

- `person`, class ID 0, score 0.814858675003, rectangle (196, 0)-(473, 476), image sequence 12214.
- `person`, class ID 0, score 0.924618005753, rectangle (234, 114)-(472, 480), image sequence 12494.

Both exceed the trial 0.5 cutoff and include input-image timestamps in `camera_rgb_optical_frame`. Coordinates are image pixels, not physical distances. Boundary-reaching rectangles may represent a truncated target; without the paired raw images we cannot judge localization correctness.

An earlier original-topic sample contains a `chair` box at score 0.389126747847, class ID 56. It is not timestamp-paired with the filtered samples, so it does not prove field preservation on an identical source/output pair.

## Reading the periodic logs

- `retained 1 / 1`: one received box passed the class/score rules.
- `retained 1 / 2`: one passed and another did not.
- `retained 0 / 1`: the received box was another class or a person below cutoff; it is not proof that the scene had no person.
- `retained 2 / 2`: two person hypotheses passed, not proof of two unique people. They might be distinct people, duplicates or false detections; this report cannot decide.

The log is throttled to roughly one print every three seconds when callbacks arrive; these lines are not every message and cannot establish detector FPS, retention percentages or detection stability. No explicit empty-output echo was captured. Silence still remains unknown. The terminal returns to a shell prompt at the end; the reason for stopping is not shown, and continued operation must not be assumed.

## What this does not establish

Scores are not measured accuracy or calibrated probabilities of correctness. This test does not demonstrate reduced false positives, recall, tracking, depth distances, map positions, exact Python version, or general detection reliability. No model, sensor setting or annotation was changed during this analysis. The final model remains open.

## Next bounded step

Keep the robot stationary with the already-running camera/YOLO; do not start another camera or mapping/navigation. Reuse `Tools/camera_diagnostics_ros1.py` on the existing registered-depth topic to measure current encoding, resolution and full-frame valid-depth fraction under the detector workload. A short run can be saved in the personal `~/fahad/reports` folder. If the script is missing, copy it there rather than altering the vendor workspace.

This checks usable depth, not the person's distance: the printed depth median is scene-wide. RGB/depth spatial alignment, the prior CameraInfo discrepancy, synchronized input-image association, invalid-depth handling and a known-distance check still precede trustworthy person distance output. No new code or upgrade is needed for this diagnostic step.
