# Camera and LiDAR software capability map

## Evidence boundary

The confirmed Orbbec Astra S has produced working camera output, and the user has observed live LiDAR points. The copied ROS source contains many sensor-related packages, launch files, model files, and demonstrations. Their presence proves that software was copied, not that every dependency, model, accessory, calibration, or launch path still works on the physical robot.

The categories below distinguish direct sensor capabilities from higher-level software and flag launch files that include the physical robot base.

## Camera: direct capabilities

The copied Astra driver can provide:

- RGB images for detection and recording;
- infrared images;
- raw depth images;
- registered depth aligned to RGB;
- RGB and depth calibration information;
- XYZ point clouds;
- registered XYZRGB coloured point clouds;
- live exposure/gain-related controls;
- device type and serial services;
- internal camera TF frames.

Useful topic patterns include:

```text
/camera/rgb/image_raw
/camera/rgb/camera_info
/camera/ir/image_raw
/camera/depth/image_raw
/camera/depth/camera_info
/camera/depth_registered/image_raw
/camera/depth/points
/camera/depth_registered/points
```

The exact live topic list takes priority. Some streams start only when a subscriber such as RViz, `rqt_image_view`, or `rosbag` connects.

## LiDAR: direct capabilities

The configured N10-class driver provides a 360-degree 2D `sensor_msgs/LaserScan`, normally:

```text
/scan
```

Each scan contains angle, range, timing, and intensity data. Direct uses include:

- top-down geometry visualization;
- obstacle distance measurement;
- wall/corner detection;
- scan recording and playback;
- known-distance accuracy testing;
- 2D map construction;
- localization against a saved map;
- navigation cost-map obstacle input.

It does not provide colour, object class, height, a full 3D shape, or proof that an object is living.

## Software connected to the camera

### Viewing and recording — sensor-only

- `rqt_image_view`, `image_view`, and RViz Image display show RGB/depth images.
- RViz PointCloud2 shows the Astra depth cloud in 3D.
- `rosbag record` can save RGB, depth, camera information, TF, and point clouds.
- `web_video_server` can expose a ROS image stream to a browser, although the saved command sheet's ready-made example launches the alternative `usb_cam` path rather than the confirmed Astra S path.

### Legacy TensorFlow examples — perception-only launch path

`ros_tensorflow` contains three examples that start the WHEELTEC camera wrapper:

- ImageNet image classification;
- MS-COCO object detection using a saved frozen TensorFlow graph;
- handwritten-digit recognition.

The object detector subscribes to `/camera/rgb/image_raw` and publishes an annotated image on `/result_ripe`. The model and label files are present in the copied tree. This is legacy TensorFlow software and must be compatibility/performance-tested before use; it is not a thesis-quality evaluation by itself.

### Darknet/YOLO examples — perception-only core, mixed launch defaults

The copied `darknet_ros` package subscribes to `/camera/rgb/image_raw` and can publish:

```text
/darknet_ros/found_object
/darknet_ros/bounding_boxes
/darknet_ros/detection_image
```

The copied tree includes YOLOv2, YOLOv3, YOLOv3-tiny, YOLOv4-tiny, gesture, and demonstration-driving weights/configurations. The generic YOLOv3-tiny configuration includes COCO classes such as person, cat, and dog. However, the package's main `darknet_ros.launch` currently defaults to the custom YOLOv3-tiny **gesture** configuration, not the generic person/animal model. Do not assume that launching it directly performs the thesis task.

### AR-marker recognition — camera/depth perception

`ar_label.launch` uses registered depth points and RGB camera information to estimate marker poses. The recognition launch does not include the chassis, but `simple_follower/ar_follower.launch` adds the physical base and can move the robot.

### Visual/KCF tracking and following — motion-capable demonstrations

- `simple_follower/visual_follower.launch` starts the camera, visual tracker/follower, and robot base.
- `kcf_track/kcf_tracker.launch` starts the camera, KCF tracker/PID follower, and robot base.

KCF tracks a selected visual target over frames. It does not semantically decide that the target is a person or animal unless another detector supplies that decision.

### Gesture and skeleton software — motion-capable or accessory-dependent

- `wheeltec_yolo_action/gesture.launch` starts the robot base and uses custom gesture detections for actions.
- `bodyreader` includes posture interaction, skeleton following, feedback, and image-output nodes.

These are vendor demonstrations and may depend on specific software/hardware assumptions. They should not be used during sensor-only tests.

## Software connected to the LiDAR

### 2D mapping — motion-capable overall launch

`mapping.launch` supports configured choices including GMapping, Hector, Cartographer, and Karto. It starts the physical LiDAR and robot base. The LiDAR supplies geometry; odometry supplies robot motion. The result is a top-down occupancy map, not a 3D object model.

### 2D navigation — motion-capable

`navigation.launch` starts the robot base, physical LiDAR, saved map server, AMCL localization, and navigation components. The LiDAR detects obstacles and helps localize the robot in the map.

### LiDAR following — motion-capable

`simple_follower/laser_follower.launch` starts a laser tracker/follower, physical LiDAR, and the robot base. It must not be used as a harmless LiDAR viewer.

### Autonomous exploration — motion-capable

`rrt_slam.launch` supports frontier/random-tree exploration using LiDAR mapping information. RViz Publish Point inputs define exploration boundaries, after which the robot can move autonomously.

## Software combining camera and LiDAR

### Line following with LiDAR avoidance — motion-capable

`simple_follower/line_follower.launch` starts:

- the camera for line detection;
- the physical LiDAR and laser tracker for obstacle information;
- the robot base for movement.

### 3D mapping with RTAB-Map plus 2D LiDAR — motion-capable

`3d_mapping.launch` combines:

- the normal 2D mapping launch, including physical LiDAR and base;
- the Astra camera;
- RTAB-Map RGB-D mapping.

This is the clearest saved launch connecting both sensors to a mapping function. It is much more computationally demanding than viewing the streams and is not the recommended first thesis experiment.

### 3D navigation — motion-capable

`3d_navigation.launch` starts the base, physical LiDAR, Astra camera, RTAB-Map navigation, AMCL, and navigation cost-map integration.

### Camera depth converted into virtual 2D LiDAR scans — motion-capable launch

`pure3d_navigation.launch` uses `depthimage_to_laserscan` to convert selected rows of the Astra depth image into `/scan` and `/scan2`. This is a software alternative to using the physical LiDAR for short-range navigation, although the Astra S depth range and field of view are much more limited. The complete launch starts the base and navigation and must not be used merely to inspect camera data.

## Recording combinations for experiments

ROS bags can record selected synchronized evidence without starting navigation. Useful combinations include:

### Camera baseline

```text
RGB image + RGB camera information
```

### RGB-D baseline

```text
RGB image + registered depth image + both camera-information topics + TF
```

### Camera/LiDAR comparison

```text
RGB image + registered depth + /scan + TF
```

The third option allows offline comparison, but valid spatial fusion also requires a measured camera-to-LiDAR transform and synchronized timestamps.

## Recommended order for this thesis

1. Validate and record RGB.
2. Validate registered depth and estimate distance inside the Astra S's usable range.
3. Run a modern pretrained RGB detector for person and relevant animal classes.
4. Build a small labelled evaluation set from the robot camera.
5. Validate LiDAR range/geometry separately.
6. Decide whether LiDAR answers a defined research need, such as longer-range obstacle geometry or navigation support.
7. Attempt camera-LiDAR fusion only if it improves a pre-declared metric enough to justify calibration, synchronization, and added evaluation work.

For the current thesis scope, RGB detection plus optional registered depth is the strongest starting point. The LiDAR is useful contextual/navigation geometry, not a replacement for the semantic camera detector.
