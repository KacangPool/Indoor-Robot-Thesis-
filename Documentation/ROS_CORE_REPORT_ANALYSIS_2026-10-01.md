# Analysis of the completed 22-topic robot report

Reviewed 2026-10-02. Evidence: `reports/Ros topic report 22 topics.txt`, generated on `wheeltec` at 2026-10-01 13:09:20 +02:00, ROS Melodic. Original SHA256: `457C37FFD8E0EE471AD605AD95BD355C74950C5E79FFA4C36A4D0F5A6DC56744`.

## Main conclusions

The report completed. Of 22 attempted topics, 15 delivered a message; seven delivered none during their individual ten-second subscription windows. No outer command-deadline messages were recorded. Status 3 is the helper's explicit no-sample return, not a ROS sensor-failure code.

There are 188 unique topics and 39 message types in the full inventory. 74 topics are configuration descriptions/updates; many others are image transport variants. This is not 188 sensors. The full index and type counts are in `ROS_TOPIC_INVENTORY_2026-10-01.md`. Only the 22 core topics received detailed samples/definitions; the other 166 remain inventory-only.

Confirmed in this snapshot:

- 640x480 RGB pixel data, camera calibration, floating-point depth, integer depth and camera point-cloud messages arrived.
- A selected central depth pixel reports approximately 1.272 m. This is a measurement example, not an accuracy or maximum-range test.
- The LiDAR delivered 464 planar rays; 351 were finite and within declared bounds (75.65%). Their minimum/maximum were 0.571/3.915 m in that scan.
- Both GMapping and RTAB-Map supplied nonempty occupancy-grid messages. Their headers are about 35 minutes older than the report start, so current updating and saved database state remain unverified.
- Odometry, IMU and battery telemetry were all silent while registered to the same `/wheeltec_robot` publisher. Investigate the shared base-data path before relying on mapping or robot-pose-dependent functions.
- Registered-depth image and CameraInfo metadata disagree in frame and principal point. Resolve the intended calibration/registration path before assigning depth to RGB detections or computing accurate XYZ positions.

## 1. Reading the types and fields

A topic is the channel name; a message type is the structured layout sent over it. `sensor_msgs/Image` is a package/type identifier, not a filename or a stored photograph. One message contains both metadata and a data buffer.

| Type notation | Meaning | Example in this report |
|---|---|---|
| `uint8` | Unsigned 8-bit integer, 0..255 | RGB channel bytes |
| `int8` | Signed 8-bit integer, -128..127 | Occupancy cells, including -1 unknown |
| `uint32` | Unsigned 32-bit integer | Image width/height, sequence counter |
| `int32` | Signed 32-bit integer | Graph IDs, configuration values |
| `float32` | 32-bit floating-point number | Depth, scan distances; may include NaN/Inf |
| `float64` | 64-bit floating-point number | Calibration values, poses |
| `bool` | True/false | `is_dense`, `do_rectify` |
| `string` | Text | Frame names and encoding names |
| `time` | Seconds plus nanoseconds | `header.stamp` |
| `T[]` | Variable-length list of values of type T | LiDAR `float32[] ranges` |
| `T[9]` | Exactly nine values | Camera `float64[9] K` |
| Another message type | Nested group of fields | `pose.pose.position.x` |

`header.stamp` labels the data time, while `header.frame_id` names the coordinate system. A sequence number is not a reliable global clock or a direct rate measurement; it can reset when a stream starts. This report samples topics seconds apart, so its RGB/depth timestamps cannot be used as a synchronization-error measurement.

Image encodings are separate from message-field types: `rgb8` means three 8-bit colour channels; `16UC1` means one unsigned 16-bit channel; `32FC1` means one 32-bit floating-point channel. `Image.data` is still a byte buffer in all three cases, decoded according to encoding, dimensions, row stride and byte order.

## 2. Camera image topics: measured payloads

| Topic | Encoding | Width x height | Bytes per row (`step`) | Pixel-buffer bytes | Centre example |
|---|---|---|---:|---:|---|
| `/camera/rgb/image_raw` | `rgb8` | 640x480 | 1920 | 921,600 | RGB (171,163,182) |
| `/camera/depth/image` | `32FC1` | 640x480 | 2560 | 1,228,800 | 1.272000074 |
| `/camera/depth/image_raw` | `16UC1` | 640x480 | 1280 | 614,400 | 1272 |
| `/camera/depth_registered/image_raw` | `32FC1` | 640x480 | 2560 | 1,228,800 | 1.271999955 |

All four received images report `camera_rgb_optical_frame` and little-endian data (`is_bigendian=0`). Centre means pixel (320,240), not a recognized target. Pixel coordinates start at the upper left; they are not centimetres or robot coordinates. Buffer sizes agree with width x height x bytes per pixel and with `height * step`; these are payload sizes, excluding message overhead.

The 1272 integer and approximately 1.272 floating readings are consistent with OpenNI millimetres and canonical ROS metres. Depth represents camera-optical-axis Z, not necessarily straight-line distance from the robot centre. These messages were sampled at different times, so agreement is not a paired-frame accuracy test. [ROS depth-image specification](https://github.com/ros-infrastructure/rep/blob/master/rep-0118.rst)

Important naming trap: `/camera/depth_registered/image_raw` is **32FC1 in this run**, despite its `image_raw` suffix. Programs must inspect `encoding`, not infer units from the name or divide every depth topic by 1000.

### Invalid depth

In each of the three depth previews, eight of the nine sampled positions were invalid: NaN in floating-point depth and zero in integer depth. Only the centre sample was finite/nonzero. Neither means a valid object at zero metres. They indicate unavailable depth in these samples under the depth convention above.

This is NOT proof that 88.9% of the whole image is invalid: the sampler checks corners, edge midpoints and centre, not all 307,200 pixels or a representative random sample. Reasons could include scene geometry, surface/illumination effects, range, border effects or processing/alignment, but this report does not identify which. Measure full-frame valid-depth fraction and inspect a depth image with a known target next.

No current camera FPS, sustained drop rate, exposure accuracy, motion blur, recognition range, or training-set quality can be calculated from these isolated messages. Earlier approximately 30 Hz measurements remain separate experiments.

## 3. Calibration: CameraInfo

`/camera/rgb/camera_info` delivered `plumb_bob` calibration for 640x480:

- K focal lengths: fx=582.795354, fy=584.395006 pixels.
- K principal point: cx=321.415982, cy=245.989410 pixels.
- D coefficients: [-0.068613, 0.174404, 0.001015, 0.006240, 0].
- R is the identity matrix.
- P focal lengths: fx'=586.186035, fy'=590.631409; principal point cx'=324.702427, cy'=246.167765.
- Zero binning/ROI fields use full-image defaults; they do not mean zero resolution.

K describes raw-image intrinsics, D distortion, R rectification and P projection for rectified images. Intrinsics relate pixels to rays; they are not the physical camera mounting height or LiDAR-to-camera transform. Do not mix raw-image K with rectified-image pixels without accounting for the processing. [ROS CameraInfo definition](https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/msg/CameraInfo.msg)

### Registration discrepancy requiring verification

| Field | RGB CameraInfo | Registered-depth CameraInfo | Registered-depth image |
|---|---|---|---|
| Frame | `camera_rgb_optical_frame` | `camera_depth_optical_frame` | `camera_rgb_optical_frame` |
| K cx | 321.415982 | 316.415982 | Not stored here |
| K cy | 245.989410 | 241.989410 | Not stored here |
| K fx/fy | 582.795354 / 584.395006 | Same | Not stored here |

The registered-depth CameraInfo principal point is exactly 5 pixels left and 4 pixels up from RGB; its P principal point has the same offsets. This is enough to reject an unverified assumption that these are interchangeable calibration messages. It does NOT, alone, prove every depth image is spatially wrong or justify manually changing calibration numbers.

The copied `ros_astra_camera/src/astra_driver.cpp` contains a plausible mechanism: around lines 838-845, depth registration selects the RGB image frame but still calls `getDepthCameraInfo`; around lines 1074-1089, that CameraInfo inherits a depth frame and subtracts configurable depth/IR offsets. This source snapshot is not proof of the exact live binary, parameters or downstream remaps. The existing RTAB-Map launch uses `/camera/depth/image` with RGB CameraInfo; it does not necessarily use the registered-depth CameraInfo examined here.

Before fusion: identify live registration settings and image-processing connections, then compare RGB/depth object boundaries on a stationary known target. Do not fix the discrepancy by renaming frames or subtracting offsets by guesswork.

## 4. Camera 3D point clouds

| Field | `/camera/depth/points` | `/camera/depth_registered/points` |
|---|---|---|
| Message | PointCloud2 | PointCloud2 |
| Organization | 640x480 point slots | 640x480 point slots |
| Fields | x,y,z | x,y,z,rgb |
| Field offsets | 0,4,8 bytes | 0,4,8,16 bytes |
| Field datatype code | 7 = FLOAT32 | 7 = FLOAT32 |
| `point_step` | 16 bytes | 32 bytes |
| `row_step` | 10,240 bytes | 20,480 bytes |
| Data buffer | 4,915,200 bytes | 9,830,400 bytes |
| Frame | camera_rgb_optical_frame | camera_rgb_optical_frame |
| `is_dense` | false | false |

The point stride includes padding; do not assume XYZ is tightly packed at 12 bytes per point. The colour field is packed bits in a float-sized field, not a physical floating-point quantity or a depth confidence. Decode through a ROS-compatible library.

Both clouds delivered real messages, but the first eight point slots were all NaN for XYZ. These are the first positions in the cloud, not a search for valid points. A whole-cloud count or sample across its interior is required to prove finite XYZ coverage. `is_dense=false` indicates that invalid points may be present; it does not mean the entire cloud is empty.

This supports the availability of camera cloud output, not a demonstrated accurate full-room 3D reconstruction. `/rtabmap/cloud_map` produced no sample. Cloud payloads are much larger than RGB/depth images; avoid collecting every representation redundantly without a reason. This report does not measure cloud frequency or bandwidth.

## 5. LiDAR: LaserScan

Publisher `/lsn10`, frame `laser`; GMapping, RTAB-Map and RViz are listed as subscribers. The physical model label is still not verified by the node name.

| Quantity | Observed / calculated |
|---|---|
| Ray count | 464 |
| Angular endpoints | approximately -pi to +pi radians (-180 to +180 degrees) |
| Angular increment | 0.0135705946 rad, approximately 0.77754 degrees |
| `scan_time` | 0.102347709 s |
| Reciprocal scan time | approximately 9.77 scans/s implied by this metadata; NOT a measured topic rate |
| `time_increment` | approximately 0.000221053 s per ray |
| Finite, in-declared-bound rays | 351/464 = 75.65% |
| Remaining rays | 113 not usable under the summary criterion |
| Minimum / maximum usable range in this scan | 0.571 / 3.915 m |
| Declared range limits | 0 / 100 m; NOT verified physical capability |

`ranges[i]` is the distance for angle `angle_min + i*angle_increment`. `intensities[i]` is a device-specific return-strength value, not RGB colour or object identity. In the shown entries, ray 1 has `inf` range and zero intensity. An infinite return is not proof that the entire ray is safe/clear; no finite measurement was available. [ROS LaserScan definition](https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/msg/LaserScan.msg)

Examples: the approximately forward ray (index 232, angle 0.006785 rad in the laser frame) has `inf`; index 116 is approximately -90 degrees at 3.541 m; index 348 approximately +90 degrees at 2.390 m. Relating these to robot left/right/front requires the laser-to-base transform. The angular endpoint convention can include the same physical direction at both ends; this snapshot does not establish uniform effective angular resolution across all operating conditions.

This remains planar sensing. The scan cannot measure a person's vertical shape, and the 3.915 m observation is neither maximum sensor range nor person-recognition range.

## 6. Motion, state and transforms

| Topic | Data type and intended contents | What this report establishes |
|---|---|---|
| `/odom` | nav_msgs/Odometry: pose, quaternion, velocity, covariances and frames | `/wheeltec_robot` registered; no sample in ten seconds |
| `/imu` | sensor_msgs/Imu: orientation, angular velocity, acceleration, covariances | Same publisher; no sample |
| `/PowerVoltage` | std_msgs/Float32: one `data` value | Same publisher; no sample; copied source intends volts |
| `/joint_states` | sensor_msgs/JointState: names, position, velocity, effort arrays | Four joint names, all positions zero, velocity/effort empty, publisher `/joint_state_publisher` |
| `/tf` | tf2_msgs/TFMessage: array of transforms | One received transform: base_footprint -> gyro_link, zero translation, identity rotation |
| `/tf_static` | Same message format for static transforms | One received transform: /camera_link -> /camera_rgb_frame, translation (0,-0.045,0), identity rotation |

The joint states are not evidence of measured wheel encoder motion: their publisher is the model joint-state publisher, and zeros can be model defaults. Quaternion (0,0,0,1) is identity orientation, not four angular measurements. Covariance describes estimated uncertainty; the IMU and odometry covariance values were not received. Standard IMU units are m/s² and rad/s; check validity/covariance conventions before use. [ROS IMU definition](https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/msg/Imu.msg)

One message on `/tf` or `/tf_static` does not capture the full graph: there are eight and five registered publishers respectively. The observed -0.045 m is a software camera-link offset, not a measurement of camera height or camera-LiDAR spacing. Old static-transform timestamps are not themselves a fault. No full sensor-to-base-to-map chain is validated here.

### Shared base telemetry silence

The copied `turn_on_wheeltec_robot/src/wheeltec_robot.cpp`, around lines 424-440, publishes odometry, IMU and voltage only after `Get_Sensor_Data_New()` accepts controller serial data. Battery publication is further divided down in `Publish_Voltage()`. Therefore, silence in all three supports checking the shared controller/serial data path first, rather than diagnosing three independent sensors. This is a source-supported hypothesis, not proof that the serial port, controller or battery is faulty; the installed binary, logs and longer live samples are still needed. A stationary robot can still publish zero-velocity odometry and telemetry.

## 7. Maps and RTAB-Map

| Quantity | `/map` (GMapping) | `/rtabmap/grid_map` |
|---|---|---|
| Type | nav_msgs/OccupancyGrid | nav_msgs/OccupancyGrid |
| Frame | map | map |
| Resolution | approximately 0.05 m/cell | approximately 0.05 m/cell |
| Width x height | 672x384 | 285x173 |
| Grid extent | 33.60x19.20 m | 14.25x8.65 m |
| Cell count | 258,048 | 49,305 |
| Origin x,y | -17.8,-4.0 m | -8.13814,-4.03004 m |
| Header seconds | 1790850840.9743 | 1790850874.2183 |
| Header age at report start | approximately 35m19s | approximately 34m46s |

These extents describe the allocated grid, including unknown cells; they are not measured room dimensions. Both origins have identity orientation. The grids sharing frame name `map` does not prove that their geometry or simultaneous TF publishers agree.

Occupancy cells use -1 for unknown and 0..100 for occupancy estimates. The helper counted only the first 100,000 GMapping cells: 90,684 unknown, 8,360 zero, 956 positive. Do not extrapolate that fraction to the full grid. RTAB-Map's complete 49,305 cells were counted: 36,310 unknown, 11,331 zero and 1,664 positive. Approximately 26.36% of that grid had known values. Positive values should not automatically be called definite obstacles without inspecting values/thresholds. [ROS OccupancyGrid definition](https://github.com/ros/common_msgs/blob/noetic-devel/nav_msgs/msg/OccupancyGrid.msg)

Old map headers with live camera/scan messages are consistent with maps being retained while updates have stopped or slowed, but do not by themselves establish why. They may be retained/latched outputs. Missing odometry is a plausible related input issue; alternatively mapping may be paused or otherwise waiting. The report cannot show map correctness, loop-closure quality, a saved database, or current autonomous-navigation readiness.

`/map_metadata` separately delivered matching GMapping dimensions/resolution/origin without occupancy cells. Its zero `map_load_time` should not be interpreted as proof the map was created in 1970.

`/rtabmap/info` did not deliver a message. Its installed definition contains reference/loop/proximity/landmark IDs, loop transform, state/probability arrays, labels/statistics arrays, local path, current goal and cached graph. None of their values was measured, so no loop-closure or active-mapping success is inferred.

`/rtabmap/cloud_map` also had no sample; an occupancy grid arriving is not proof that a full 3D room cloud is being produced. The copied vendor mapping configuration uses `Grid/FromDepth=false`, selecting LiDAR-derived occupancy, and planar registration; live parameter values were not captured in this report.

## 8. Commands are not measurements

- `/cmd_vel` is geometry_msgs/Twist: requested linear and angular velocity. It had no publisher and `/wheeltec_robot` as subscriber. Silence is expected if no controller is issuing commands. It is not a measured velocity stream.
- `/move_base_simple/goal` is geometry_msgs/PoseStamped: a goal pose and frame/time. RViz was registered as publisher; there were no subscribers and no sample. This does not show a navigation executor listening there.
- Do not publish motion or goals just to fill empty report sections. No movement command is needed for the next sensor tests.

## 9. Other advertised interfaces

The full inventory groups into camera transports/processing, settings, mapping/graph/cloud/path outputs, robot state, command inputs and logs. RGB/IR/depth image variants come from processing and transport plugins, not separate physical cameras. `parameter_descriptions` describes configurable options; `parameter_updates` carries setting values. `/rosout` is logging; `bond` is node-liveness coordination.

Path, pose, graph, OctoMap, marker and label topics are possible software interfaces, not proof that they produced meaningful data. In particular `/rtabmap/gps/fix` and `/rtabmap/tag_detections` are subscriber-only in this inventory: they do not establish installed GPS hardware or a running AprilTag detector. `/rtabmap/imu` is likewise only an advertised input. Custom topic meaning, such as `/rev_order`, needs its consumer/source inspected before use.

## 10. Practical next sequence

1. Camera-first characterization: use the existing camera diagnostic tool for sustained RGB/depth rates and full-frame valid-depth fraction, with a stationary matte target at a measured distance and documented lighting/tilt. Record the scene as well as numerical output. This distinguishes sparse corner previews from genuinely poor coverage.
2. Verify RGB-depth registration and the correct CameraInfo/frame pairing. A finite centre pixel alone is insufficient for attaching distance to a person's box.
3. Check `/wheeltec_robot` logs and the shared base telemetry path read-only. Confirm odometry/IMU/voltage before interpreting map freshness or attempting pose-dependent navigation/fusion. Do not change serial settings or restart mapping as a first diagnostic action.
4. Recheck map timestamps/update activity and preserve the current database before any vendor mapping restart. The previous uploaded empty `test.db` is historical and says nothing about the current database.
5. Develop the RGB detector first. Add distance only after depth validation; add map locations only after valid transforms and robot pose; add LiDAR fusion only when it solves a defined thesis need.

The text report is a programming-interface reference, not a labelled ML dataset, synchronized sensor recording, calibration certificate or safety validation. No robot code, calibration or settings were changed in this analysis.

## Verification boundaries

All 22 detailed sections were read and their outcomes counted. The inventory was deduplicated to 188 topic names and 39 types; sample status was matched by exact name. Arithmetic for image strides/buffer lengths, angular increment, scan fraction and map extents/header ages was checked. Official ROS 1 message definitions supply semantics, not the live software version (the robot remains Melodic). The uploaded file was preserved; no connection to the live robot was made.
