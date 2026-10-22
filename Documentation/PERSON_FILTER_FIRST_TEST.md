# Next experiment: person-only perception output

Update 2026-10-22 (modular source): the updated Python tools require the sibling
`fahad_core/` folder. Do not follow the older single-file copy steps below alone.
Use the complete bundle instructions in [Tools/README.md](../Tools/README.md).
Original command names and existing installed robot copies are unchanged; this
local refactor was not deployed. See [architecture/verification notes](MODULAR_CODE_ARCHITECTURE.md).

Prepared 2026-10-12. The user requested proceeding without further annotation
polishing. Freeze both exports unchanged as provisional development references.
V2's draft frame stays excluded by the existing rules; do not silently confirm it
or present all 31 as approved ground truth. Uncertain/partial-chair labels are not
a blocker for this person-focused implementation milestone. Animals remain a
later thesis target, not removed from the project.

Live-result update, 2026-10-12: the uploaded combined terminal report demonstrates
ROS subscription and readable person-only publication at cutoff 0.5. That first
connection milestone is complete; exact Python version and a paired source/output
comparison are not captured. See `PERSON_FILTER_LIVE_RESULT_2026-10-12.md` for
interpretation and the next depth diagnostic. The original preparation-time
verification boundary below is historical, not a request to repeat this test.

## What has been implemented

`Tools/person_detection_filter.py` subscribes to existing
`/darknet_ros/bounding_boxes`, retains only `person` boxes with score >=0.5, and
publishes the same ROS message type to `/fahad/person_boxes`. It preserves input
image/output headers, scores, class IDs and pixel coordinates. It never changes
the original message/list, alters YOLO settings, starts sensors or publishes
movement commands. It has no API/cloud integration or new model dependency.

This is a lightweight output-processing experiment, not training or a new neural
network. It does not recover missing detections, improve box positions, add depth,
measure biological life or guarantee improved real-world accuracy. The threshold
is configurable and is a trial motivated by saved-output comparisons, not a
validated optimum. The original YOLO window continues to show its original labels.

The copied detector already runs NMS. We add no duplicate suppression or tracking:
the pilot's extra same-class IoU >0.5 suppression did not change its results.

## Copy files to the robot

Copy the actual `.py` files using the SSD into the personal folder:

- `Tools/person_detection_filter.py` -> `/home/wheeltec/fahad/tools/person_detection_filter.py`
- `Tools/test_person_detection_filter.py` -> `/home/wheeltec/fahad/tools/test_person_detection_filter.py`

No edits to the robot's original workspace are required. Use its ROS Python 2.7
environment, not the Windows virtual environment. Keep the robot stationary and
do not connect this experimental topic to a following/navigation controller.

## Start

If the already-working generic camera/detector is running, leave it running. If
not, start it once in its usual terminal:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch darknet_ros yolo_v3.launch
```

That launcher starts the camera too; do not start a duplicate camera driver.
Do not restart mapping or navigation for this test.

In a new terminal, check the new files:

```bash
source ~/wheeltec_robot/devel/setup.bash
python ~/fahad/tools/test_person_detection_filter.py
python ~/fahad/tools/person_detection_filter.py --help
```

If imports fail, send the error; do not install/upgrade ROS or Python to fix it.

Start the separate filter:

```bash
python ~/fahad/tools/person_detection_filter.py --threshold 0.5
```

It keeps running to receive messages; this is expected. Ctrl+C in this terminal
stops only this extra node. YOLO/camera remain untouched.

In another ROS-sourced terminal, while a person is visible:

```bash
source ~/wheeltec_robot/devel/setup.bash
timeout -k 2s 15s rostopic echo -n 1 /fahad/person_boxes
```

Expected type: `darknet_ros_msgs/BoundingBoxes`. Results contain only person
boxes with scores >=0.5, or `bounding_boxes: []` for an incoming source message
without qualifying people. An empty result is not necessarily a correct absence
decision; a missed person remains possible. Exact IDs identify classes, not tracks.

If no source box message arrives, the filter cannot know whether YOLO found
nothing or stopped. The copied detector can stop publishing boxes when zero
objects are detected. Do not treat silence as absence. Output headers retain the
original timestamp and are not a new latency measurement. A subscriber queue of
five bounds waiting data but does not guarantee all camera frames are processed.

## First short evidence collection

Use the existing recorder on the **original** box topic to retain all scores and
classes. This allows comparing cutoffs later on exactly the same frames instead
of discarding low-score predictions at capture time. If it is already copied to
the robot, run in a separate ROS-sourced terminal:

```bash
python ~/fahad/tools/record_detection_test.py --label filter_chair_negative --duration 20 --delay 10 --notes "No people; chairs visible; original detector output retained; person filter 0.5 running"
```

After it finishes, perform a distinct person scene:

```bash
python ~/fahad/tools/record_detection_test.py --label filter_person_occlusion --duration 20 --delay 10 --notes "One person; first 10 seconds standing, then behind chair; original detector output retained; person filter 0.5 running"
```

Keep camera tilt/lighting fixed; stand at a safe stationary position and do not
drive the robot. The first run tests false-person hypotheses; the second tests
retention under partial occlusion. Two snapshots/second sample the output, not
every moment of flicker. The recorder currently lacks the source object-count
topic, so no-message cases remain unknown. Share the complete new session folders
and the filter's terminal output. No additional annotation exercise is required
to establish that the new topic functions; rigorous accuracy remains separate.

## Verification boundary and next milestone

Nine local Python 3 offline tests pass for person-only selection, inclusive
cutoff, invalid scores, unmodified source/headers/coordinates, explicit empty
results, defaults, namespace/feedback-loop protections and invalid cutoffs.
Help parsing succeeds without ROS. Syntax is written for Python 2.7/3, but a live
Python 2/ROS message-serialization test is still required on the robot. No robot
connection, live subscriber test, motion or model change was performed here.

Once the output is confirmed, it becomes the detection interface for a separate
depth-association prototype. RGB/depth alignment, depth validity and transforms
still need verification before trustworthy distance/map markers. Do not interpret
the person filter as completed semantic mapping or a reason to launch navigation.
