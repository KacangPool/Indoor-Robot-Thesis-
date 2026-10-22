# Astra S camera output diagnostics (ROS 1)

Update 2026-10-22 (modular source): the updated Python tools require the sibling
`fahad_core/` folder. Do not follow the older single-file copy steps below alone.
Use the complete bundle instructions in [Tools/README.md](../Tools/README.md).
Original command names and existing installed robot copies are unchanged; this
local refactor was not deployed. See [architecture/verification notes](MODULAR_CODE_ARCHITECTURE.md).

This is a read-only measurement procedure for the WHEELTEC robot's confirmed Orbbec Astra S. It does not move the robot or alter camera settings.

## 1. Start the camera

In terminal 1:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch turn_on_wheeltec_robot wheeltec_camera.launch
```

Leave this terminal running. If the workspace path is different, use the actual `devel/setup.bash` path on the robot.

## 2. Discover the live interfaces

In terminal 2:

```bash
source ~/wheeltec_robot/devel/setup.bash
rostopic list | grep '^/camera/'
rosnode list | grep camera
rosservice list | grep camera
```

The copied launch configuration suggests the topic names below, but the live list is the experimental truth.

## 3. Read exact numeric metadata with standard ROS commands

```bash
rostopic type /camera/rgb/image_raw
rostopic echo -n 1 /camera/rgb/camera_info
rostopic hz /camera/rgb/image_raw
rostopic bw /camera/rgb/image_raw
```

Let each `hz` or `bw` command run for about 15 seconds, then stop it with `Ctrl+C`. Run them one at a time so the measurement tool itself adds as little load as possible.

`camera_info` reports the resolution, optical frame, distortion model, distortion coefficients, and calibration matrices. In its `K` array:

- `K[0]` is horizontal focal length `fx` in pixels;
- `K[4]` is vertical focal length `fy` in pixels;
- `K[2]` and `K[5]` are the optical centre `cx` and `cy`.

Repeat the rate and bandwidth measurements for depth and the point cloud:

```bash
rostopic hz /camera/depth_registered/image_raw
rostopic bw /camera/depth_registered/image_raw
rostopic hz /camera/depth_registered/points
rostopic bw /camera/depth_registered/points
```

If a name does not exist, select the matching live name from `rostopic list` rather than inventing one.

## 4. Use the single read-only diagnostic monitor

The script does not need to be placed inside the original WHEELTEC ROS source or built with `catkin_make`. Keeping it in the user's separate folder is preferable. Copy `Tools/camera_diagnostics_ros1.py` to:

```text
/home/wheeltec/fahad/tools/camera_diagnostics_ros1.py
```

In the Ubuntu file manager, this is normally `Home` -> `fahad` -> `tools`. Create the `tools` subfolder if necessary. With the camera still running:

```bash
source ~/wheeltec_robot/devel/setup.bash
python ~/fahad/tools/camera_diagnostics_ros1.py
```

It reports every two seconds:

- RGB resolution, encoding, received frame rate, mean brightness, very-dark pixels, and very-bright pixels;
- depth resolution, encoding, received frame rate, valid-depth percentage, and minimum/median/maximum valid distance;
- optical frame and the main calibration values from `CameraInfo`.

The program joins ROS as a new subscriber named `camera_diagnostics`. It listens to copies of messages that the camera driver is already publishing; it does not command the camera, change parameters, move the robot, modify the original ROS workspace, or save images. It counts every arriving message for the FPS estimate but performs the more expensive pixel/depth calculation only twice per second by default, reducing load on the older Jetson. It prints the results in the terminal until stopped with `Ctrl+C`.

Example shape of the output (the numbers are illustrative, not measurements of this robot):

```text
RGB:   640x480 rgb8 | 29.8 fps | brightness 112.4/255 | dark 15.2% | bright 8.1%
Depth: 640x480 16UC1 | 29.5 fps | valid 72.6% | min/median/max 0.43/1.21/1.98 m
Info:  frame camera_rgb_optical_frame | calibration 640x480 | fx/fy 570.1/570.3 px | cx/cy 319.5/239.5 | plumb_bob
```

If the robot publishes different names, override them on the command line:

```bash
python ~/fahad/tools/camera_diagnostics_ros1.py _rgb_topic:=/actual/rgb/topic _depth_topic:=/actual/depth/topic _camera_info_topic:=/actual/camera_info/topic
```

If terminal output should be preserved for the project, use `tee`; this creates only a report inside the separate `fahad` folder:

```bash
mkdir -p ~/fahad/reports
python -u ~/fahad/tools/camera_diagnostics_ros1.py | tee ~/fahad/reports/camera_diagnostics.txt
```

The dark/bright percentages are useful for comparing the same scene under different lighting. They are not pass/fail image-quality scores. Minimum and maximum depth are also scene-wide extremes; use a controlled target and tape measure for accuracy testing.

## 5. Recognition distance is a detector experiment

ROS can report image resolution, focal length, frame rate, brightness, and depth validity. It cannot report the maximum distance at which a future machine-learning model will recognize a person, cat, or dog. That depends on target size, pose, occlusion, lighting, motion blur, training data, model input size, and confidence threshold.

For a repeatable pilot, mark 0.5, 1, 1.5, 2, 3, 4, and 5 m where the room permits. At every position, collect standing, crouching, lying, and partly occluded examples in normal, dim, and backlit light. Record whether the whole target is visible and later measure detector recall at each distance. Evaluate Astra depth mainly inside its documented planning range; continue RGB detection beyond that range.

As a rough optical check, the expected image height of an upright object is:

```text
pixel height approximately equals fy times real height divided by distance
```

This predicts scale only. It is not proof that a detector will recognize the object.

## 6. What the four screenshots already show

The screenshots `Car Camera 1 (1).png` through `Car Camera 1 (4).png` visibly show `/camera/rgb/image_raw` in `rqt_image_view` and an image area consistent with approximately 640 x 480. Exact live numeric confirmation must still come from `CameraInfo`.

They also reveal deployment-relevant cases:

- the approximately 12-13 cm viewpoint contains a large amount of floor;
- a nearby crouched or standing person can be cut off by image boundaries;
- chairs and other furniture substantially occlude the person;
- a bright wall or doorway can leave the person comparatively dark;
- a more distant person fits more completely in the image but occupies fewer pixels.

These are not merely camera faults. They define important training and final-test conditions: close-target truncation, furniture occlusion, backlighting, target scale, and low-angle floor-level imagery.

## 7. Safe next measurement session

Keep the robot stationary for the first camera measurements. Movement is not required to measure the streams or collect the initial distance series. Test driving later as a separate supervised session with clear floor space, an emergency-stop procedure, and the correct controller/teleoperation launch verified first.
