# Annotated English translation: ROS common function commands 5.5

## What this file is

The Chinese title `ROS常用功能命令5.5` translates to **ROS Commonly Used Function Commands 5.5**. The `5.5` is best understood as the command-sheet revision, not a ROS distribution or ROS version.

This is a WHEELTEC quick-reference list of launch commands for many optional demonstrations included in its wider software bundle. It is not a log of what the robot has done, it contains no recorded camera/LiDAR data, and its presence does not prove that every listed sensor, accessory, package, or demonstration is installed or working on this particular robot.

The uploaded root copy is almost the same as the Chinese copy already inside `From Robotics Lab/wheeltec_dev/wheeltec_robot_src/`. Its meaningful text differences are network addresses: the uploaded copy uses `192.168.2.102`, while the extracted copy uses `192.168.0.100` in the browser, SSH, and NFS examples.

## Safety labels

- **SAFE VIEW/INSPECTION**: normally does not command the physical chassis.
- **MOTION-CAPABLE**: may start the base or publish movement commands. Raise the wheels or use the lab's normal physical safety procedure before testing.
- **SYSTEM CHANGE**: changes files, packages, permissions, mounts, builds, time, or system configuration. Do not run merely to experiment.
- **SIMULATION**: intended for the virtual-machine/Gazebo environment, not the physical robot.

## Translation of the 21 functions

### 1. Keyboard control — MOTION-CAPABLE

Start the initialization/base node first when keyboard control is being started on its own. Other complete demonstrations may already include this node, so it should not be launched twice.

```bash
roslaunch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch
roslaunch wheeltec_robot_rc keyboard_teleop.launch
```

### 2. Line following with LiDAR obstacle avoidance — MOTION-CAPABLE

```bash
roslaunch simple_follower line_follower.launch
```

### 3. LiDAR following — MOTION-CAPABLE

```bash
roslaunch simple_follower laser_follower.launch
```

This is not the safe command for merely testing the LiDAR. Use the LiDAR-only guide instead.

### 4. Visual following — MOTION-CAPABLE

```bash
roslaunch simple_follower visual_follower.launch
```

This is not the safe command for merely viewing the Astra S camera because it can include base control.

### 5. 2D mapping and 2D navigation — MOTION-CAPABLE

```bash
roslaunch turn_on_wheeltec_robot mapping.launch
roslaunch turn_on_wheeltec_robot navigation.launch
```

One-command map saving, producing `WHEELTEC.pgm` and `WHEELTEC.yaml`:

```bash
roslaunch turn_on_wheeltec_robot map_saver.launch
```

Mapping and navigation are separate modes; these lines are not intended to be pasted together blindly.

### 6. 3D mapping and 3D navigation — MOTION-CAPABLE

```bash
roslaunch turn_on_wheeltec_robot 3d_mapping.launch
roslaunch turn_on_wheeltec_robot 3d_navigation.launch
```

### 7. Pure-vision mapping and navigation — MOTION-CAPABLE

```bash
roslaunch turn_on_wheeltec_robot pure3d_mapping.launch
roslaunch turn_on_wheeltec_robot pure3d_navigation.launch
```

### 8. Voice control — MOTION-CAPABLE; OPTIONAL HARDWARE

Start the base, navigation, and LiDAR scan nodes:

```bash
roslaunch xf_mic_asr_offline base.launch
```

Start microphone-array initialization:

```bash
roslaunch xf_mic_asr_offline mic_init.launch
```

### 9. KCF tracking/following — POTENTIALLY MOTION-CAPABLE

```bash
roslaunch kcf_track kcf_tracker.launch
```

KCF is a visual object-tracking algorithm. The Chinese heading says “following,” so do not assume this is display-only without inspecting the launch hierarchy.

### 10. Autonomous mapping — MOTION-CAPABLE

The original says to consult the separate autonomous-mapping tutorial.

```bash
roslaunch turn_on_wheeltec_robot rrt_slam.launch
```

In RViz, choose **Add > By Topic** and add:

- `clicked_point`: displays the random-tree region points and start point;
- `detected_points`: detected boundary points;
- `frontiers`: boundary points received by the filter;
- `centroids`: valid filtered boundary points;
- `global_detector_shapes`: global tree;
- `local_detector_shapes`: local tree.

Using RViz's **Publish Point** tool, set four tree-growth boundary points clockwise or counter-clockwise and one start point close to the robot's initial position. The robot then explores the map autonomously. Do not test this during a sensor-only session.

### 11. WHEELTEC app: video, mapping, and navigation — MOTION-CAPABLE

Connect the phone to the robot's Wi-Fi and open the WHEELTEC app. The app can control movement, save maps, and view a camera feed.

For video, the sheet gives:

```bash
roslaunch usb_cam usb_cam-test.launch
```

This command is for the `usb_cam` driver and may refer to an optional ordinary RGB camera rather than the confirmed Astra S. Use `wheeltec_camera.launch` for the Astra S baseline test.

For mapping:

```bash
roslaunch turn_on_wheeltec_robot mapping.launch
```

For navigation:

```bash
roslaunch turn_on_wheeltec_robot navigation.launch
```

### 12. Multi-robot formation — MOTION-CAPABLE; REQUIRES MULTIPLE ROBOTS

The lead and follower robots must share a correctly configured network. The leader needs a saved 2D map, the vehicles must be placed at their initial positions, and their clocks must be synchronized.

The sheet gives this example, which changes system time and must not be copied as a current value:

```bash
sudo date -s "2022-04-01 15:15:00"
```

Leader: start 2D navigation:

```bash
roslaunch turn_on_wheeltec_robot navigation.launch
```

Followers: start formation software:

```bash
roslaunch wheeltec_multi wheeltec_slave.launch
```

Leader: start keyboard control or use a controller:

```bash
roslaunch wheeltec_multi keyboard_teleop.launch
```

Optional visualization:

```bash
rviz
```

### 13. Display a camera in a web browser — SAFE VIEW/INSPECTION, BUT ALTERNATIVE CAMERA DRIVER

On the host:

```bash
roslaunch usb_cam usb_cam-test.launch
rosrun web_video_server web_video_server
```

Host browser address:

```text
http://localhost:8080/
```

Client browser example in the uploaded copy:

```text
http://192.168.2.102:8080
```

The note recommends Google Chrome and says the tested 360 browser and Internet Explorer could not display the image. The IP is only an old example and must be checked on the live robot. Again, `usb_cam` may not be the confirmed Astra S path.

### 14. TensorFlow integrated with ROS — SAFE VIEW/INSPECTION; LEGACY DEMO

The Jetson series must enter the specified virtual environment first. The original says the Raspberry Pi 2 GB version cannot run this feature.

TensorFlow object classification:

```bash
roslaunch ros_tensorflow ros_tensorflow_classify.launch
```

TensorFlow object detection:

```bash
roslaunch ros_tensorflow ros_tensorflow_detect.launch
```

Open `rqt_image_view` and select the `result_ripe` topic.

TensorFlow handwritten-digit recognition:

```bash
roslaunch ros_tensorflow ros_tensorflow_mnist.launch
```

These are vendor examples, not evidence of a ready or suitable thesis detector.

### 15. AR-marker recognition and following

Recognition — normally SAFE VIEW/INSPECTION:

```bash
roslaunch turn_on_wheeltec_robot ar_label.launch
```

Create marker ID 0 with side length 5 in the tool's units:

```bash
rosrun ar_track_alvar createMarker -s 5 0
```

AR-marker following — MOTION-CAPABLE:

```bash
roslaunch simple_follower ar_follower.launch
```

### 16. 2.4 GHz wireless controller — MOTION-CAPABLE

Start initialization/base, then the controller node:

```bash
roslaunch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch
roslaunch wheeltec_joy joy_control.launch
```

### 17. Deep learning, Jetson controllers only

Start the Darknet/YOLO ROS node — normally perception-only, but inspect the launch before use:

```bash
roslaunch darknet_ros darknet_ros.launch
```

Gesture-action and demonstration-table driving nodes — MOTION-CAPABLE:

```bash
roslaunch wheeltec_yolo_action gesture.launch
roslaunch wheeltec_yolo_action dp_drive.launch
```

This shows that legacy YOLO-related software exists in the wider bundle. It does not establish model accuracy, supported classes, compatibility, or suitability for the thesis.

### 18. Gazebo mapping/navigation simulation — SIMULATION

2D mapping:

```bash
roslaunch wheeltec_gazebo_function mapping.launch
```

Keyboard control:

```bash
roslaunch wheeltec_gazebo_function keyboard_teleop.launch
```

Save `WHEELTEC.pgm` and `WHEELTEC.yaml`:

```bash
roslaunch wheeltec_gazebo_function map_saver.launch
```

2D navigation:

```bash
roslaunch wheeltec_gazebo_function navigation.launch
```

### 19. ROS Qt function, run on the virtual-machine side — SYSTEM/REMOTE CONTROL

Run a script that configures passwordless SSH and starts `roscore` on the robot:

```bash
bash initssh.sh
```

After it finishes, start the Qt interface:

```bash
roslaunch qt_ros_test qt_ros_test.launch
```

Do not run `initssh.sh` without reviewing it because it changes remote-login configuration.

### 20. Text-to-speech audio generation — NON-MOTION

```bash
roslaunch tts tts_make.launch
```

The generated audio is said to be under `/tts_make/audio`.

### 21. Human-skeleton following and posture control, Jetson only — MOTION-CAPABLE

Posture control:

```bash
roslaunch bodyreader bodyinteraction.launch
```

Human-skeleton following:

```bash
roslaunch bodyreader bodyfollow.launch
```

Combined posture control and following:

```bash
roslaunch bodyreader final.launch
```

The combined demonstration starts in posture-control mode. Crossing both hands in front of the chest changes modes.

## Translation of the additional common commands

These are administrative/reference commands, not one sequence to execute.

### Recursively change timestamps in the current directory — SYSTEM CHANGE

```bash
find ./* -exec touch {} \;
```

This overwrites modification times and would damage file-history evidence. Do not run it on the thesis copy or robot backup.

### Install missing ROS package dependencies — SYSTEM CHANGE

Run from a catkin workspace:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

This may download and install packages. It is unnecessary for the initial camera/LiDAR tests.

### Change system time — SYSTEM CHANGE

```bash
sudo date -s "2022-06-15 09:00:00"
```

This is an obsolete example date and should not be run.

### Build only one ROS package — SYSTEM/BUILD CHANGE

```bash
catkin_make -DCATKIN_WHITELIST_PACKAGES="package_name"
```

Remove the package whitelist:

```bash
catkin_make -DCATKIN_WHITELIST_PACKAGES=""
```

### Install a Python package through the Douban mirror — SYSTEM CHANGE

```bash
pip install -i https://pypi.doubanio.com/simple/ package_name
```

This legacy mirror example should not be used without a reviewed dependency plan.

### Log in over SSH — REMOTE ACCESS

```bash
ssh -Y wheeltec@192.168.2.102
```

The IP is only an example from this copy. Confirm the current address before use.

### Mount or unmount the robot workspace over NFS — SYSTEM CHANGE

```bash
sudo mount -t nfs 192.168.2.102:/home/wheeltec/wheeltec_robot /mnt
sudo umount -t nfs 192.168.2.102:/home/wheeltec/wheeltec_robot /mnt
```

### Give every file in a directory full permissions — UNSAFE SYSTEM CHANGE

```bash
sudo chmod -R 777 folder
```

Do not use this as general troubleshooting. It gives all users read, write, and execute access and recursively changes every item.

### Open the map directory and save a map manually — WRITES FILES

```bash
cd /home/wheeltec/wheeltec_robot/src/turn_on_wheeltec_robot/map
rosrun map_server map_saver -f 20220615
```

The last argument is an example output filename, not a required date.

### Start the confirmed camera wrapper and view image topics — SAFE BASELINE

```bash
roslaunch turn_on_wheeltec_robot wheeltec_camera.launch
rqt_image_view
```

Run these in separate terminals. This is the relevant camera entry for the confirmed Orbbec Astra S.

### View the relationship between ROS nodes and topics — SAFE INSPECTION

```bash
rqt_graph
```

### Generate or inspect the TF coordinate-frame tree — SAFE INSPECTION

```bash
rosrun tf view_frames
rosrun rqt_tf_tree rqt_tf_tree
```

### Adjust VNC display resolution — DISPLAY CHANGE

```bash
xrandr --fb 1024x768
```

## Relevance to the thesis

The most relevant entries are:

1. the camera wrapper plus `rqt_image_view` for the Astra S baseline;
2. the separate LiDAR-only procedure in `LIDAR_QUICK_START_ROS1.md`, rather than the motion-capable laser follower;
3. the legacy TensorFlow and Darknet/YOLO examples as evidence that vendor demonstration software exists, not as a recommended thesis implementation;
4. `rqt_graph` and the TF viewers for later diagnosis;
5. ROS bag recording commands from the camera/LiDAR quick-start guides, which this command sheet does not include.

For the immediate next session, do not test mapping, navigation, following, gestures, skeleton control, formation driving, or administrative commands. First validate camera RGB/depth and LiDAR `/scan` separately while the robot remains stationary.
