# Camera-only quick start for the WHEELTEC robot

## Purpose

Use this guide during the next robotics-lab visit to activate, identify, view, and briefly record the configured Orbbec Astra camera without starting robot motion, navigation, visual following, or LiDAR.

The copied robot is configured for ROS 1 Melodic and `camera_mode="Astra_S"`.

Runtime confirmation from the robot on 2026-09-09:

- device type: **Orbbec ASTRA S**;
- serial number: **17121811539**;
- the camera was observed working.

A photograph of the readable physical label is still useful as supporting thesis evidence. The RGB stream, depth stream, frame rates, and recording performance should each be checked separately because one working view does not prove that every stream is valid.

## Safety boundary

- Use the existing robot installation; do not reinstall drivers or update Ubuntu, ROS, JetPack, Python, or OpenNI.
- Do not edit the live WHEELTEC launch files during the first test.
- Do not run `roslaunch simple_follower visual_follower.launch` for a camera-only test. That demonstration also starts the robot base and can publish movement commands.
- Keep the robot powered and connected according to normal lab procedure. The camera is powered through USB and has no separate recording button.
- If any command produces unexpected errors, stop and save or photograph the output instead of trying random installation commands.

## 1. Open a terminal on the robot

Use the robot's desktop terminal or the normal lab SSH connection.

Confirm the environment:

```bash
echo $ROS_DISTRO
rospack find turn_on_wheeltec_robot
rospack find astra_camera
```

Expected:

- ROS distribution: `melodic`;
- paths inside the existing `wheeltec_robot` workspace.

If a package is not found, load the existing workspace once in that terminal:

```bash
source ~/wheeltec_robot/devel/setup.bash
```

Then repeat the three checks. Do not add or change anything in `.bashrc` during this test.

## 2. Record the USB identity before launching

Run:

```bash
lsusb
```

Save or photograph the complete output. An Orbbec device may appear by manufacturer name or by its USB vendor/product numbers.

Also photograph every readable label on the physical camera.

## 3. Start only the configured camera

Run:

```bash
roslaunch turn_on_wheeltec_robot wheeltec_camera.launch
```

This is the preferred command because it follows the WHEELTEC configuration, whose current default is `Astra_S`. It includes the Orbbec Astra launch file but does not include the chassis/base launch.

Leave this terminal open. Normal informational messages are expected. If red error messages appear, photograph or copy them.

The generic driver command below exists, but use it only as a later diagnostic if the WHEELTEC wrapper fails:

```bash
roslaunch astra_camera astra.launch
```

Do not run both launch commands at the same time.

## 4. Inspect the running camera from a second terminal

Open another terminal and, if necessary, load the workspace again:

```bash
source ~/wheeltec_robot/devel/setup.bash
```

List camera nodes, topics, and services:

```bash
rosnode list | grep camera
rostopic list | grep camera
rosservice list | grep camera
```

Save the complete results. Likely topics include some of the following, but the live list takes priority:

```text
/camera/rgb/image_raw
/camera/rgb/camera_info
/camera/depth/image_raw
/camera/depth/camera_info
/camera/depth_registered/image_raw
/camera/depth_registered/camera_info
/camera/depth/points
/camera/depth_registered/points
```

Some image and point-cloud streams only become active when a viewer or recorder subscribes.

### What the different camera entries mean

These names normally describe different outputs from the same physical camera, not several cameras:

- `/camera/rgb/image_raw`: ordinary colour pictures; this is the main input for a person/animal detector;
- `/camera/rgb/camera_info`: calibration and lens geometry, not pictures;
- `/camera/depth/image_raw`: a distance value for each valid depth pixel;
- `/camera/depth_registered/image_raw`: depth aligned with the colour image, useful for estimating the distance of a detected object;
- `/camera/depth/points`: a 3D point cloud made from depth;
- `/camera/depth_registered/points`: a colour-aligned 3D point cloud;
- topics containing `compressed` or `rect` are encoded or corrected versions derived by ROS software.

Start the thesis with `/camera/rgb/image_raw`. Test registered depth next. Leave point clouds until later because they add processing load and create much larger recordings.

## 5. Ask the driver for the device identity

If these services appeared in the service list, run:

```bash
rosservice call /camera/get_device_type
rosservice call /camera/get_serial
```

Save both results. The 2026-09-09 test returned Orbbec ASTRA S and serial `17121811539`. Repeat only if you need to document a new session or verify that the hardware was not replaced. This is stronger evidence than the launch-file default, although a readable physical label remains valuable.

## Where camera data is stored

The camera does **not** normally save previous use inside itself. It behaves more like a live sensor than a phone camera:

1. the camera measures colour/depth;
2. its ROS driver publishes live topics;
3. a viewer or machine-learning program subscribes to those topics;
4. the data disappears after use unless a program deliberately writes it to storage.

`rqt_image_view` only displays a stream. It does not create a recording. `rosbag record` writes a `.bag` file to the Jetson's storage. If no output path is supplied, the file is created in the terminal's current directory, which can be checked with:

```bash
pwd
```

The recording procedure below deliberately changes into `~/thesis_camera_test`, so its file will be stored there. A custom Python/ROS machine-learning program stores nothing unless its code explicitly saves images, video, detections, or logs.

Machine-learning inference does not require a permanent image collection on the robot. A pretrained detector can process each live RGB frame and discard it after producing detections. A labelled collection is required for training or fine-tuning, and saved test data is strongly recommended for repeatable thesis evaluation. That collection can combine suitable public datasets with deliberately recorded and labelled images from this robot.

## 6. View the RGB image

On the robot's graphical desktop, run:

```bash
rqt_image_view
```

Select `/camera/rgb/image_raw` from the topic menu.

If `rqt_image_view` is unavailable, try:

```bash
rosrun image_view image_view image:=/camera/rgb/image_raw
```

Check that:

- the image updates continuously;
- colours look plausible;
- the image is not frozen or corrupted;
- the robot body does not obstruct too much of the view;
- nearby and distant people are visible.

## 7. View the depth image

In `rqt_image_view`, select the depth topic shown by `rostopic list`, initially trying:

```text
/camera/depth/image_raw
```

Then check for registered/aligned depth:

```text
/camera/depth_registered/image_raw
```

Place a simple object or person approximately 0.5-2 m in front of the camera. If the device is physically an Astra S, depth may be unavailable closer than about 0.4 m or beyond about 2 m.

Do not change exposure, infrared laser, registration, or filter settings during this initial baseline.

## 7A. View RGB and the 3D depth cloud together in RViz

Yes: leave `wheeltec_camera.launch` running before opening RViz. RViz subscribes to the live topics; it does not start the camera itself.

First identify the exact live image, point-cloud topic, and point-cloud coordinate frame:

```bash
rostopic list | grep -E '^/camera/.*(image_raw|points)$'
rostopic type /camera/rgb/image_raw
rostopic type /camera/depth_registered/points
rostopic echo -n 1 /camera/depth_registered/points/header
```

Expected message types are `sensor_msgs/Image` and `sensor_msgs/PointCloud2`. The last command should contain a `frame_id`, likely `camera_rgb_optical_frame` for a registered cloud. Use the live value rather than assuming its name. If the registered cloud is absent, try the available `/camera/depth/points` topic and read its header instead.

Start RViz:

```bash
rviz
```

Configure it as follows:

1. Under **Global Options**, set **Fixed Frame** to the exact point-cloud `frame_id` returned above.
2. Choose **Add > By topic > `/camera/rgb/image_raw` > Image**. This creates a 2D image panel.
3. Choose **Add > By topic > `/camera/depth_registered/points` > PointCloud2**. If that topic is unavailable, use the confirmed `/camera/depth/points` topic.
4. For the registered cloud, try **Color Transformer: RGB8**. If it is unavailable or the cloud has no colour field, use **AxisColor**.
5. Use **Style: Points** with approximately 2-4 pixels, or **Flat Squares** with a small size such as 0.005-0.015 m.
6. Select the **Orbit** view, rotate with the left mouse button, zoom with the wheel, and pan with the middle mouse button.

Place a person, chair, or matte cardboard box approximately 0.5-2 m from the Astra S. The Image panel should show the ordinary colour image. PointCloud2 should show a rotatable 3D surface made from depth measurements; gaps and noisy edges are normal. The Astra S will not reliably provide depth outside its approximate 0.4-2 m specified depth range.

### Running the camera and LiDAR at the same time

Use separate terminals:

Terminal 1:

```bash
roslaunch turn_on_wheeltec_robot wheeltec_camera.launch
```

Terminal 2:

```bash
roslaunch turn_on_wheeltec_robot wheeltec_lidar.launch
```

Terminal 3:

```bash
rviz
```

The two sensor wrappers do not start the robot base. An Image display can remain visible independently. However, RViz can place the camera PointCloud2 and LiDAR LaserScan in the same 3D scene only if ROS has a valid TF transform connecting their frames.

Check without changing anything:

```bash
rosrun tf tf_echo laser camera_rgb_optical_frame
```

Substitute the point cloud's actual `frame_id` if different. If it repeatedly reports that the frames are not connected, view the sensors separately for now: use the camera frame as Fixed Frame for PointCloud2, and `laser` as Fixed Frame for LaserScan. Do not invent a static transform or start the chassis merely to remove the RViz error; a camera-to-LiDAR transform is calibration evidence needed for later fusion.

### RViz troubleshooting

- **Image display says no image:** confirm the selected topic and run `rostopic hz /camera/rgb/image_raw`.
- **PointCloud2 is red with a transform error:** set Fixed Frame to the exact value in the cloud's header.
- **Point-cloud topic exists but nothing appears:** put a matte target inside 0.5-2 m, wait for the subscriber to activate the stream, and check `rostopic hz` on that exact topic.
- **Cloud is black or has strange colours:** change Color Transformer from RGB8 to AxisColor.
- **Cloud looks flat or unrecognizable:** use Orbit view and rotate around it; unlike the N10 LaserScan, the depth cloud should contain varying Z/depth values.
- **RViz becomes slow:** remove or disable PointCloud2 temporarily. The uncompressed registered cloud is much heavier than an Image or LaserScan display.

## 8. Measure the live rates

Use the exact topics that appeared on the robot:

```bash
rostopic hz /camera/rgb/image_raw
```

After roughly 15 seconds, stop the measurement with `Ctrl+C`. Repeat for the available depth topic:

```bash
rostopic hz /camera/depth/image_raw
```

Also capture one camera-information message:

```bash
rostopic echo -n 1 /camera/rgb/camera_info
```

The copied configuration requests 640 x 480 at 30 Hz, but the measured rate is the result that matters.

## 9. Check storage before recording

Run:

```bash
df -h
```

Do not make a long uncompressed recording if storage is low. RGB plus depth can grow quickly.

## 10. Make a short ROS bag

Create a separate thesis test directory:

```bash
mkdir -p ~/thesis_camera_test
cd ~/thesis_camera_test
```

Use only topic names confirmed by `rostopic list`. If registered depth is available, a likely 15-second test command is:

```bash
rosbag record -O astra_rgbd_test.bag \
  /camera/rgb/image_raw \
  /camera/rgb/camera_info \
  /camera/depth_registered/image_raw \
  /camera/depth_registered/camera_info \
  /tf /tf_static
```

Let it record for approximately 15 seconds, then press `Ctrl+C` once.

If registered-depth topics are not present, substitute the available `/camera/depth/...` image and camera-info topics. Missing topics do not necessarily mean a hardware fault; save the live topic list for analysis.

Inspect the resulting file:

```bash
rosbag info astra_rgbd_test.bag
ls -lh astra_rgbd_test.bag
```

Copy the bag, terminal outputs, and camera photographs to a USB drive or another approved lab storage method.

## 11. Stop the camera cleanly

Return to the first terminal running `roslaunch` and press:

```text
Ctrl+C
```

Wait for the nodes to shut down before disconnecting the camera or powering down the robot.

## Troubleshooting boundaries

### `Resource not found` or package not found

Run:

```bash
source ~/wheeltec_robot/devel/setup.bash
```

If the path does not exist, stop and record the error. Do not rebuild the workspace yet.

### No camera topics

Capture:

```bash
lsusb
rosnode list
rostopic list
```

Also save the launch-terminal error messages. Check only the physical USB connection and normal power state; do not install replacement drivers during the first session.

### RGB works but depth is blank

- Confirm that the correct depth topic is selected.
- Put a diffuse object within approximately 0.5-2 m.
- Avoid direct sunlight and very reflective or transparent targets.
- Save the result as an observed limitation if it persists.

### No graphical window over SSH

Use the robot's local desktop if available. Graphical forwarding may require an SSH connection configured for X forwarding. If viewing is inconvenient, record a short ROS bag and inspect it later on a compatible ROS machine.

## Evidence to bring back

- Clear camera-label photographs.
- Complete `lsusb` output.
- Output of the ROS distribution and package-location checks.
- Camera node, topic, and service lists.
- Device type and serial results.
- Measured RGB and depth rates.
- Storage output.
- A 15-second RGB-D ROS bag.
- Any launch error messages.

With this evidence, the next session can determine the exact camera model, confirm usable topics, evaluate recording quality, and create the first thesis detector against the real camera interface.
