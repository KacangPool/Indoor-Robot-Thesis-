# Box-depth viewer: preliminary floor-level check

Update 2026-10-22 (modular source): the updated Python tools require the sibling
`fahad_core/` folder. Do not follow the older single-file copy steps below alone.
Use the complete bundle instructions in [Tools/README.md](../Tools/README.md).
Original command names and existing installed robot copies are unchanged; this
local refactor was not deployed. See [architecture/verification notes](MODULAR_CODE_ARCHITECTURE.md).

Status clarification, 2026-10-14: the user confirms personally selecting the box.
Accept that account; do not require a fresh screenshot just to prove manual
selection. The live extraction milestone is complete. Spatial RGB/depth
registration and measured accuracy still require validation, but this confirmation
does not authorize further hardware/software changes or select a new detector.

Prepared 2026-10-13. The user has a box on the floor and estimates its distance
as approximately 1 m without a ruler. This is a plausibility/alignment experiment,
not measured accuracy validation. A box is suitable if its visible surface is
not transparent or highly reflective. It need not be recognised by YOLO.

Live-result update, 2026-10-13: uploaded `box_depth_20261013_131056.txt` demonstrates
manual clicks, paired-stream receipt and local depth readout. The first live
workflow milestone is complete; do not repeat it as a prerequisite. The user's
wall/reselection explanation and remaining accuracy/alignment limits are in
`BOX_DEPTH_LIVE_RESULT_2026-10-13.md`. Preparation-time verification limits below
remain historical; exact versions and image-based alignment are still unverified.

User clarification later on 2026-10-13: YOLO labels a person but not the box or
a chair at this floor-level view; the new viewer has not been run. The copied
general YOLO class configuration has person/chair but no generic box category.
A missing label is different from the object being outside the camera image.
If the box face is visible in RGB, proceed with manual selection even without
any YOLO rectangle. If it is not visible, reposition the target on a stable
support into view or share a colour image; do not assume the cause of a chair
miss or change camera tilt/calibration merely to obtain a label.

## Copy and run

Copy `Tools/box_depth_viewer.py` to
`/home/wheeltec/fahad/tools/box_depth_viewer.py`. It uses the robot's existing
ROS Python environment, NumPy, OpenCV, cv_bridge and message_filters. No new
model, catkin build, ROS upgrade or vendor-file edit is required. If a dependency
is missing, report the error rather than installing/upgrading blindly.

Keep the robot stationary. If camera/YOLO is already running, leave it alone;
do not start another camera driver or any navigation/following launch. The
person-filter node is not required for this manual box test. If the camera is
not running, the previously working `roslaunch darknet_ros yolo_v3.launch`
starts it together with the detector; no separate camera launch is needed.

In a new terminal on the robot's **graphical desktop**:

```bash
source ~/wheeltec_robot/devel/setup.bash
mkdir -p ~/fahad/reports
python -u ~/fahad/tools/box_depth_viewer.py 2>&1 | tee ~/fahad/reports/box_depth_$(date +%Y%m%d_%H%M%S).txt
```

This creates a uniquely timestamped text report in the personal folder. It does
not save images automatically. Take a screenshot yourself when the selected box
and footer are visible. Do not use a headless SSH terminal for the GUI.

## Use the window

1. Left image: live RGB. Right image: registered-depth visualization. The same
   pixel position in both is a hypothesis to test, not already proven registration.
2. Keep robot and box still; ensure the box's front face is actually visible,
   not hidden below the camera view or behind the floor/another object.
3. Click well inside that visible face, away from edges. The default patch is
   11x11 pixels. The same small green patch appears in both panels.
4. Read `median`, `numeric %` and `in 0.4-2m %` in the footer/terminal. A click
   prints coordinates, stamps, frame, encoding and patch statistics. Live selected
   statistics print approximately every two seconds; these are not frame-rate data.
5. Press `o` to toggle a 30% depth overlay over RGB. Look for obvious boundary
   displacement or depth belonging to the background. This is only a visual
   registration check, not calibration or proof of perfect alignment.
6. Optional: press Space to freeze/unfreeze the displayed pair. Frozen data is
   explicitly labelled historical; it does not update if the scene changes.
7. Press `c` to clear selection, `q`/Escape to quit, or Ctrl+C in the terminal.
   These stop only this viewer; the camera/detector remain unchanged.

The selected pixel location stays fixed during live display. It does not follow
a moving box or person. Do not move the box and then interpret the old selection
as an object tracker. Avoid accidentally selecting a patch on the floor or wall.

## Colours and numerical meaning

- Dark grey to light grey: near to far on a fixed 0.4-2 m display scale.
- Magenta: finite positive value outside that display/planning range, including
  values closer than 0.4 m or farther than 2 m. The actual value is retained in
  the patch statistics, not silently removed or replaced.
- Black: no finite positive depth. Numerical failure does not establish empty space.
- Green: selected patch, not a detection label or confidence colour.

`numeric %` counts finite positive pixels. It does not establish correctness.
`in 0.4-2m %` counts pixels inside the documented Astra S range, out of the
whole patch; it is not a confidence score or accuracy certificate. The median
uses all finite positive pixels, including out-of-range values. If none exist,
the viewer explicitly prints NO FINITE POSITIVE DEPTH rather than a zero distance.

Depth is camera-optical-axis Z under ROS depth conventions, not necessarily
straight-line distance from the robot centre. Encoding 32FC1 is interpreted in
metres; 16UC1 is converted from millimetres. Unknown encodings are rejected.

An estimated 1 m placement has no measured reference distance or tolerance.
A roughly similar patch reading is plausibility evidence only; a very different
reading merits checking selection, correspondence, invalid data and configuration,
not automatically assuming a bad sensor or changing depth scale. Later use a tape
measure and a target facing the camera before calculating distance errors.

## Pairing and failure handling

The viewer reads `/camera/rgb/image_raw` and
`/camera/depth_registered/image_raw`. Melodic ApproximateTimeSynchronizer uses
five buffered messages per stream and a 50 ms header-time tolerance. This is
approximate pairing for a stationary preliminary check, not exact detector-image
association or measured RGB/depth synchronization. Conversion/display is bounded
to approximately five iterations per second; subscriptions/sync can receive faster.

Same-pixel sampling requires equal image geometry and equal nonempty frame IDs,
but these are necessary checks, not sufficient proof of calibrated registration.
The earlier RGB/registered-depth CameraInfo discrepancy remains unresolved. Pairs
with excessive header differences, zero/nonfinite/future stamps, mismatched
size/frame or unsupported encoding are rejected. Receipt/acquisition age above
one second disables live numerical display; freezing intentionally retains a
labelled historical pair. ROS clock errors may therefore produce waiting/rejection
messages and must be investigated rather than bypassed by editing calibration.

If the window says WAITING, send the terminal warnings. Do not restart mapping,
rename optical frames, broaden synchronization tolerance or alter camera parameters
by guesswork. Standard ROS logging may write its normal node logs; no automatic
image/data export or movement-topic publishing is implemented by this helper.

## Verification and next milestone

Thirteen offline Python 3 numerical/metadata tests pass, and CLI help succeeds.
Tests cover units, unsupported shapes/encodings, local-versus-scene statistics,
NaN/Inf/zero/negative handling, retained out-of-range values, empty/clipped patches,
geometry/frame/time/age rejection and defaults. Source uses Python 2.7/3 syntax.
ROS/Melodic, Python 2, OpenCV mouse/window interaction and live image pairing have
not been executed locally; this computer has no cv2 module. Those remain robot-side
checks. No dependency was installed or upgraded to work around that limitation.

Share the text report and a screenshot of the selected box in both panels. Only
after inspecting these results should we build a person-box depth association;
automatically assigning a median rectangle value could read floor/background.
No map/3D position, object tracking or biological-life inference is implemented.

Primary conventions/API references checked during preparation:

- [ROS REP 118, canonical and OpenNI depth representations](https://github.com/ros-infrastructure/rep/blob/master/rep-0118.rst).
- [Melodic message_filters implementation](https://github.com/ros/ros_comm/blob/melodic-devel/utilities/message_filters/src/message_filters/__init__.py).
- [Orbbec original Astra series range](https://www.orbbec.com/products/structured-light-camera/astra-series/), rechecked 2026-10-12.

The ros.org generated documentation was blocked by its access protection;
official ROS repositories were fetched instead.
