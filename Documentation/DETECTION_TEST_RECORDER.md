# Record a detection test while working alone

Update 2026-10-22 (modular source): the updated Python tools require the sibling
`fahad_core/` folder. Do not follow the older single-file copy steps below alone.
Use the complete bundle instructions in [Tools/README.md](../Tools/README.md).
Original command names and existing installed robot copies are unchanged; this
local refactor was not deployed. See [architecture/verification notes](MODULAR_CODE_ARCHITECTURE.md).

This recorder subscribes to the camera and YOLO box topics that already work on
the robot. It saves a timed session under your personal `~/fahad` folder. It does
not start a driver, change model settings, publish motion commands, or record
audio/depth/LiDAR. Run it on the robot's Ubuntu system using its ROS Python 2.7
environment. The source is also written to be compatible with Python 3.

## Copy and start

1. Copy `Tools/record_detection_test.py` from Windows into
   `/home/wheeltec/fahad/tools/record_detection_test.py` on the robot, using your
   SSD or an already-working file-transfer connection. Create `tools` inside
   `fahad` if needed. Save the actual `.py` file, rather than a `.txt` copy.
2. Keep the robot stationary. Start the existing generic detector once in its own
   terminal; its launcher also starts the camera:

   ```bash
   source ~/wheeltec_robot/devel/setup.bash
   roslaunch darknet_ros yolo_v3.launch
   ```

   If the detector is already running, leave it running and skip this command.
3. Open a second terminal. Check the script before the first capture:

   ```bash
   source ~/wheeltec_robot/devel/setup.bash
   python ~/fahad/tools/record_detection_test.py --help
   ```

4. Record the first scene:

   ```bash
   python ~/fahad/tools/record_detection_test.py --label empty_room --duration 30 --delay 10 --notes "No people; chairs visible; fixed camera tilt"
   ```

You have 10 seconds to move out of view. It prints `RECORDING`, captures for 30
seconds, then stops itself. YOLO keeps running. To interrupt the recorder,
press Ctrl+C in its own terminal. Every run gets a new folder, so a later test
does not overwrite an earlier one.

## Run separate scenes

After the first test finishes, use a separate run for a person scene:

```bash
python ~/fahad/tools/record_detection_test.py --label person_2m --duration 30 --delay 10 --notes "One standing person; measured 2 m from camera; fixed tilt"
```

Measure the distance before writing `measured` in the notes. If you cannot
measure it, write `estimated` instead. Additional runs can use `person_4m` or
`person_seated`; change the notes to describe the actual test. Keep the camera
pose, model settings and lighting consistent when comparing scenes. Move away
from the computer during the countdown, then hold the intended position.

The default snapshot limit is two per second. Detection-message metadata is
logged at the received rate. This is a sample of the live output: it is not a
continuous video and cannot capture every brief label flicker. Use longer/more
frequent sampling later if that becomes necessary.

## Files and how to read them

The terminal prints the exact new folder under:

```text
/home/wheeltec/fahad/detection_tests/test_DATE_TIME_UNIQUE/
    session.json
    events.jsonl
    summary.json
    report.txt
    images/
        0001_raw.jpg
        0001_preview.jpg
        ...
```

- `report.txt`: readable status, counts, notes and saved-image list. Start here.
- `images/*_raw.jpg`: camera snapshots without detector graphics. JPEG compression
  is lossy; these are practical pilot examples, not lossless sensor archives.
- `images/*_preview.jpg`: the matching boxes and scores drawn on saved images.
  These are created by this recorder, so their appearance differs from YOLO's
  own window. Scores are model confidence, not measured accuracy.
- `events.jsonl`: one JSON record per line for all received box messages and
  saved images. Original pixel bounds, class IDs, scores and both ROS headers
  are retained. IDs identify classes, not tracked people. Image paths are
  relative to the session folder. A null image path usually means that message
  was logged between saved snapshots; check `image_match` too.
- `summary.json`: completion status and diagnostic counts. Class counts include
  repeated and overlapping boxes and do not count unique physical objects.

Detections are paired only when their `image_header` matches the raw image's
timestamp, sequence and frame ID exactly. The cache retains 60 raw frames,
approximately 55 MiB for the previously observed 640x480 RGB format. It also
waits briefly for images that arrive after a box message. Unmatched detections
are still logged, with `image_match: unavailable`; boxes are not drawn on an
arbitrary nearby frame. Existing robot timestamps are preserved even if its
calendar clock is incorrect.

When there are no recent box messages, the recorder still saves raw scene
snapshots and marks detector status as unknown. The copied detector publishes
object-count messages instead of bounding-box messages when it finds no objects.
Therefore absent boxes alone cannot distinguish an empty result from a stalled
detector. This first recorder does not subscribe to the count topic.

`header_gap_s` is the output-header time minus the image-header time. It is not
isolated model execution time. The recorder's `elapsed_s` uses local elapsed
time (Python 3 monotonic time where available; Python 2 wall time).

## Finish and share

Copy the complete session folder back to the project, for example inside
`Terminal Reports/detection_tests/`. Keeping images beside the JSON files
preserves the links. Send `report.txt` and a few raw/preview image pairs first.
Review recordings for other people before sharing outside this project.

If the recorder reports `no_rgb_messages`, check that YOLO/camera are still
running. If it reports `no_detection_messages_verify_detector`, check YOLO's
terminal and include a clearly visible person in a repeat test. Missing modules
should be reported rather than installing a new Python or replacing ROS.
Capture stops when free output space falls below 256 MiB. Image conversion or
write errors stop the run and are recorded in the summary when possible.

## Verification status

Prepared on 2026-10-09 against the reported ROS 1 interface and copied message
definitions. Initial sandbox/Node execution failed; approved local execution
subsequently ran all seven offline checks successfully on Python 3. Three
uploaded completed robot sessions demonstrate live recording: 841 detection
records matched exact image headers and 157 raw/preview pairs were saved.
Details and limitations are in `DETECTION_PILOT_ANALYSIS_2026-10-09.md`.
Separate Python 2 offline-test output was not supplied. On the robot, after
copying both scripts to your personal tools folder, the checks can run without
starting ROS:

```bash
python ~/fahad/tools/test_record_detection_test.py
```

First use should be the short empty-room run above. Check the reported status,
image files and matching previews before collecting a larger dataset.
