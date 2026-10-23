# Wheeltec software catalogue — 23 October 2026

## What we know from home

The copied `From Robotics Lab/wheeltec_dev` tree contains **75 package.xml
manifests and 273 XML launch declarations**. These include multiple robot
variants, arm projects and drivers for hardware that may not be fitted to this
car. This is not an inventory of everything currently installed on the Jetson.
Private generated index: `tmp/robot_inventory/copied_source_20261023.json`.

The Chinese command sheet is a selection of examples, not an exhaustive software
registry. ROS distinguishes a package (software folder), an executable node
(a program), a launch file (a startup recipe) and a running node (an instance).
`rosnode list` sees only registered running instances, not dormant capabilities.

## Features worth knowing about

| Area | Copied source evidence | Meaning and limits |
| --- | --- | --- |
| Object detection | `darknet_ros`, `darknet_ros_msgs`; `yolo_v3.launch`, `yolo_v4.launch` | v3 launch selects **yolov3-tiny.yaml**. v4 launch selects **yolov4-tiny.yaml**. Finding v4 config/launch is not a successful v4 build, loaded weights, acceptable speed or a model-change recommendation. |
| Camera/depth | `astra_camera`, `depthimage_to_laserscan`, `cv_bridge`, `image_geometry` | Camera/depth handling, image conversion, geometry and generating a scan from depth. A depth-derived scan is not the physical LiDAR stream. |
| Additional camera support | `usb_cam`, RealSense and ZED packages | Other camera drivers in the source tree, not proof those devices are fitted. |
| Tracking/following | `kcf_track`, `simple_follower`; visual/laser/line/AR follower launches | Tracking and following demos. Followers may command movement; inspect/remap before any future trial. |
| Marker/body-related tools | `ar_label.launch` references `ar_track_alvar`; `bodyreader`; tracker face/gesture demos | Marker, body or face-related candidates. A referenced package need not be present or compiled, and a demo is not physiological life detection. |
| Mapping | `mapping.launch`, gmapping/hector/karto includes; 3D/RTAB-Map launch references | Existing mapping recipes; referenced dependencies and configuration need checking. 3D mapping software does not turn a planar LiDAR into a 3D scanner. |
| Localisation/navigation | `amcl`, `move_base`, `map_server`, costmaps, DWA, TEB, `robot_pose_ekf` | Robot localisation, map serving, path planning and pose fusion. Navigation can drive the base; not an inspection command. |
| Exploration/multiple robots | `rrt_exploration`, `rrt_slam.launch`, `wheeltec_multi` | Exploration/multi-robot candidates, not an installed working system or needed thesis extension. |
| Video streaming | `web_video_server` | Existing alternative browser-streaming software. Our dashboard already has its own image path; no reason to replace it without a measured need. |
| Speech | `xf_mic_asr_offline`, `tts`, voice-control launch | Speech recognition/synthesis-related source. Does **not** confirm a microphone, working language/model, licensing or successful audio capture. Voice-control demos may move hardware. |
| Manual/base control | `wheeltec_joy`, `wheeltec_robot_rc`, `turn_on_wheeltec_robot`, `wheeltec_yolo_action` | Joystick, base and action/control packages; inspect implementations before use. |
| Robot arms | `wheeltec_arm_src`, MoveIt configurations and picking demos | Vendor distribution includes arm variants. Not evidence an arm is attached to this robot. |

Priority for this thesis: actual RGB/depth/LiDAR inputs, frame transforms and
timing, recording/replay, then defensible association and map observations.
Other demos remain optional. Gazebo and campus Wi-Fi are deferred by user choice.

## Next lab: one bounded inventory, not a blind full-disk scan

Prepared `Tools/robot_inventory.py` plus the reusable `fahad_core/inventory.py`.
The tool parses package/launch declarations; it never imports the ROS packages or
runs their launch recipes. `--robot` explicitly adds fixed observations:

- OS/architecture and ROS distribution;
- packages discoverable in the currently sourced ROS environment;
- registered nodes, topic types/publishers/subscribers and services;
- selected installed ROS/CUDA/OpenCV/JetPack/RealSense package versions.

It does not echo every topic, dump parameters/environment/passwords, use sudo,
install software or request movement. Missing commands, failure, timeout and
truncation are recorded. Each command has an eight-second deadline; source
traversal and XML size are bounded. It is not every file on the computer and
does not claim sensor freshness. Paths and metadata still need review before
sharing; raw output stays out of the public source repository.

### Copy from laptop PowerShell (next time connected)

Run from the project folder. These transfer tools to the personal directory only;
they do not install dependencies or launch the robot:

```powershell
scp .\Tools\robot_inventory.py wheeltec@192.168.0.100:/home/wheeltec/fahad/tools/
scp -r .\Tools\fahad_core wheeltec@192.168.0.100:/home/wheeltec/fahad/tools/
ssh wheeltec@192.168.0.100
```

This refreshes the personal tool files; it does not replace vendor code. The
`fahad_core` folder must accompany the script. Existing SSH authentication is
handled normally; do not send passwords in chat. Confirm the destination folder
exists first (`ls -ld ~/fahad/tools ~/fahad/reports`).

### In that robot SSH terminal

```bash
source /opt/ros/melodic/setup.bash
source ~/wheeltec_robot/devel/setup.bash
python3 ~/fahad/tools/robot_inventory.py --robot --source-root /home/wheeltec/wheeltec_robot/src --output /home/wheeltec/fahad/reports/software_inventory_20261023.json
```

Use a new dated filename for the actual visit; existing reports are refused.
Use the robot's existing Python3, not a new interpreter or ROS upgrade. Python3.6
grammar is checked locally; actual Jetson execution is still untested. If no ROS
master is running, package/source discovery can still succeed while registered
node/topic/service checks fail or time out. Do not start navigation merely to
populate this report. Other workspaces require additional explicit source roots
and/or inspection in their own sourced environment.

Back in **laptop** PowerShell (not the robot SSH shell), download the exact report:

```powershell
scp wheeltec@192.168.0.100:/home/wheeltec/fahad/reports/software_inventory_20261023.json .\tmp\robot_inventory\robot_20261023.json
```

Review missing dependencies and configuration before choosing any optional demo.
Installed/discoverable, registered/running and validated/working are separate
evidence levels. No physical scan or robot access was performed from home.
