# Robot ROS topic reference and October report diagnosis

Follow-up: the completed 22-topic report is analysed in `ROS_CORE_REPORT_ANALYSIS_2026-10-01.md`, with every advertised topic indexed in `ROS_TOPIC_INVENTORY_2026-10-01.md`. Those documents contain newer received-value evidence; the section below describes the earlier incomplete report.

## Evidence from the uploaded report

Source: `reports/ros_topic_report_20261001_123744.txt`, robot timestamp 2026-10-01 12:37:44 +02:00; reviewed 2026-10-02. The original file was not modified.

- ROS Melodic, host `wheeltec`, local ROS master, 188 topic names in the inventory.
- Only seven per-topic sections were reached. The file ends in the sample step for `/camera/depth/image/compressed/parameter_updates`; it contains no completion marker.
- Samples for `/PowerVoltage`, `/camera/depth/camera_info`, and `/camera/depth/image` contain `ROSInitException: init_node interrupted before it could complete`. The old three-second deadline expired during reader initialization in these attempts. This does not show a broken sensor.
- `/camera/depth/image/compressed/parameter_descriptions` printed a message before the old script printed `[No message received within 3s]`. That label incorrectly inferred message absence from a process timeout, which also includes startup/output/shutdown.
- The old timeout sent SIGINT without a forced-stop fallback. A reader remaining alive after that signal is a plausible explanation for a persistent stall, but the partial report does not identify the underlying process state. It cannot distinguish every shutdown/network/resource problem or an interrupted file copy.
- Publisher registrations are present for RGB/depth/IR/cloud outputs, `/scan`, `/odom`, `/imu`, `/map`, `/rtabmap/grid_map`, and RTAB-Map cloud/map interfaces. `/rtabmap/rgbd_sync` is listed as a depth subscriber. This is stronger evidence of mapping-related software running than the earlier sensor-only report, but does not prove valid maps, successful reconstruction, navigation, motion or saved database contents.

## How to interpret a ROS interface

A **topic** is a named channel, such as `/scan`. A **message type** is the field layout, such as `sensor_msgs/LaserScan`. A **publisher** sends messages; a **subscriber** reads them. A topic can be registered without delivering a usable message during the measurement window.

There are three distinct questions:

1. What is the interface? The inventory, connections and message definition answer this.
2. What values actually arrive? A received sample answers this for one instant.
3. Is it reliable/accurate enough for the thesis? Repeated measurements against known conditions answer this, not a single sample.

The version-2 report separates definitions from measured samples. Its live definitions come from the installed robot packages, which is preferable to guessing custom RTAB-Map fields from another software version. A field present in the definition is not evidence that the robot fills it correctly.

## Main programming interfaces advertised in this report

The contents below describe message semantics/intended use, not successfully measured payloads from the incomplete upload.

| Topic / family | Useful fields or contents | Potential use and limitation |
|---|---|---|
| `/camera/rgb/image_raw` | timestamp/frame, width/height, encoding, row step, pixel data | RGB input for person/cat/dog detection. Pixel bytes are not already detections. |
| `/camera/rgb/camera_info` | `K`, `D`, `R`, `P`, distortion model, dimensions | Camera geometry/calibration for pixel rays and RGB-D work; matrices must match the image used. |
| `/camera/depth/image`, `/camera/depth/image_raw` | image geometry, encoding, depth pixels | Range along camera optical axis for valid pixels; verify units, invalid codes and registration. Different names may expose converted encodings. |
| `/camera/depth_registered/image_raw` | depth resampled into another camera's geometry | Candidate for distance within RGB detection boxes; verify actual alignment, calibration and timestamps before using it. |
| `/camera/depth/points`, `/camera/depth_registered/points` | field definitions, binary layout, x/y/z and possibly colour | 3D camera geometry. Inspect actual `fields`; do not assume every cloud has colour or every point is valid. |
| `/camera/ir/image` | infrared intensity image | Optional alternate visual signal; advertisement does not prove it is delivering alongside RGB in the chosen device mode. |
| `/scan` | angles, timing, `ranges`, `intensities`, declared range limits | Planar obstacle distances. A ray is not a human/animal label; intensity units are device-specific. |
| `/odom` | pose, orientation quaternion, velocity, covariance, parent/child frames | Estimated robot movement; can drift and is not global ground truth. |
| `/imu` | orientation, angular velocity, linear acceleration, covariances | Motion/orientation inputs where populated correctly; do not assume every field is valid. |
| `/tf`, `/tf_static` | arrays of timestamped parent-to-child transforms | Relate camera, LiDAR, base and map coordinates. One `/tf` message need not contain the whole tree, especially with multiple publishers. |
| `/map`, `/rtabmap/grid_map` | resolution, width/height, origin, occupancy cells | 2D occupancy representation for spatial context/planning, not object recognition. |
| `/rtabmap/cloud_map` | accumulated PointCloud2 | Candidate reconstructed geometry; registration alone does not establish a populated, accurate room model. |
| `/rtabmap/info`, `/rtabmap/mapData`, `/rtabmap/mapGraph` | installed RTAB-Map status/graph/data definitions | Mapping diagnostics and stored observations; exact fields depend on installed version. |
| `/PowerVoltage` | Float32 `data` | Candidate battery telemetry; verify driver units/scaling before treating it as measured volts. |
| `/joint_states` | names, positions, velocities, efforts | Robot joint-state interface; arrays may be empty or visualization-oriented. |
| `/cmd_vel` | requested linear/angular velocity | A command input, not measured speed. The report only listens; publishing here can move the robot. |
| `/move_base_simple/goal`, `/initialpose` | target pose / pose with covariance | Navigation/localization interfaces. Existence can originate from RViz, not an active navigation controller. |
| `.../parameter_updates`, `.../parameter_descriptions` | current settings / settings definitions | Configuration rather than image/scan data. Arrays contain setting names and values. They may be latched/event-driven rather than continuous measurements. |
| `.../compressed`, `.../compressedDepth`, `.../theora` | transport-encoded image payloads | Alternate delivery formats, not extra physical cameras; plugin advertisement does not imply every encoding is usable for every image. |
| `/rosout`, `/rosout_agg`, `.../bond` | logs / node-liveness messages | Software diagnostics, not the main perception dataset. |

For `LaserScan`, ray index `i` has angle `angle_min + i * angle_increment`, in radians, and distance `ranges[i]`, in metres. Nonfinite and out-of-declared-range returns must be rejected. In the scan frame, a valid planar return can be represented as `x = r*cos(angle)`, `y = r*sin(angle)`, `z = 0`. This does not create vertical observations. See the [official ROS LaserScan definition](https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/msg/LaserScan.msg). The link documents standard ROS 1 semantics; it does not identify the robot as Noetic.

PointCloud2 data is a binary buffer described by `fields`, point/row strides and byte order; simply printing raw `data` is not a readable x/y/z listing. The helper decodes a small point sample using ROS's point-cloud library. See the [official PointCloud2 definition](https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/msg/PointCloud2.msg).

## What to collect next

Run the revised default core report first, keeping the existing sensor/mapping session running and the robot stationary. Do not restart vendor mapping merely to gather a report: its launch can delete the default database. Copy BOTH report-tool files into `~/fahad/tools`; commands are in `ANALYSE_ALL_ROS_TOPICS.md`.

Review RGB encoding, camera calibration arrays, depth units/valid samples, cloud fields, scan angles/ranges and coordinate-frame names. Then measure sustained rates, timestamp compatibility, depth accuracy and sensor alignment separately. Training data needs deliberate image/annotation collection (and potentially selected ROS bags), not this text report alone.

For the first detector, subscribe to RGB and produce class, confidence and bounding box. Registered depth/calibration can later support distance estimates; TF and a verified robot/map pose can later locate detections on a map. LiDAR should be added only for a defined benefit and tested fusion, not merely because its topic exists.

Topics are only one part of the robot API: ROS services (request/reply), actions (long-running operations) and parameters also exist. This tool does not inventory or invoke those interfaces, and their absence from the report does not mean the robot lacks them.
