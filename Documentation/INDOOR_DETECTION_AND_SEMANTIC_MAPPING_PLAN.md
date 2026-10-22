# Indoor object detection and labelled mapping: foundation plan

Current decision, 2026-10-14: the user chooses the existing pretrained YOLO
detector with no custom training/fine-tuning, and prioritises camera-LiDAR
association and labels. An alternative-model comparison is no longer a required
prerequisite. See `AGREED_PRETRAINED_FUSION_SCOPE_2026-10-14.md` for the authoritative
updated scope, staged outputs and evaluation limits. The original planning/status
text below is historical and must not override subsequent live results or this
decision. No model files or vendor settings changed by recording it.

Date: 2026-10-07. Status: user-proposed direction with recommended staged implementation. No detector, fusion system or robot launch was implemented or run in this planning session.

## Objective and scope

Build an indoor camera system that detects and classifies visible objects, initially person, chair, table and eventually hand, using an existing pretrained algorithm where practical. Extend it to place object labels on a LiDAR-supported map. This is commonly called semantic mapping: geometry plus meanings such as chair/person.

The user's new direction broadens the earlier person/cat/dog detector-only prototype toward general indoor detection and camera-LiDAR mapping. Furniture classes are useful integration test cases. The final thesis deliverable and whether mapping is a required evaluated result should still be aligned with the lecturer; autonomous movement and physiological life-sign detection are not implied by this plan.

## Sensor roles

- Camera RGB: supplies appearance used by a detector for a class, confidence score and image bounding box. Detection includes locating objects in the image, not just classifying the whole image.
- Camera depth: candidate source of 3D surface positions for visible objects, once full-image validity, calibration pairing and RGB-depth alignment are verified. A depth sample is not automatically an object's geometric centre.
- 2D LiDAR: supplies planar geometry for occupancy mapping and, where there is a defensible association, object distance/scan support. Existing LaserScan data does not itself provide person/chair/table labels. Specialized LiDAR classification would be a separate trained/validated task, not a capability supplied by the current driver.
- Robot pose and TF: transform time-matched sensor observations into a consistent map frame. Global object mapping needs trustworthy pose even if driving remains manual.

Both camera display and map/scan display can show consistent labels from a shared fused object record. This does not imply two independent classifiers agreeing. If the LiDAR scan plane misses an object, retain a camera-only detection or a valid depth-based position and explicitly mark that there is no LiDAR association.

The LiDAR is approximately 14-16 cm above the floor based on user measurements. It may intersect legs/supports, but miss a hand or tabletop. A bounding box can contain foreground and background; projecting a wall return into that box does not prove the return belongs to the detected object. Use calibration, timing, geometry/occlusion gates and an explicit unassociated/unknown state; do not label every return inside a box blindly.

## Reusable baseline found in the copied source

Root: `From Robotics Lab/wheeltec_dev/wheeltec_robot_src/darknet_ros/`.

- `darknet_ros/config/yolov3-tiny.yaml`: 80 class names, threshold 0.3, `yolov3-tiny.cfg` and `yolov3-tiny.weights` references.
- `darknet_ros/yolo_network_config/weights/yolov3-tiny.weights`: file present, 35,434,956 bytes. Presence is not a successful model-load, accuracy or runtime test.
- `darknet_ros/launch/yolo_v3.launch`: selects the generic tiny configuration through the main launch.
- `darknet_ros/launch/darknet_ros.launch`: defaults to the gesture configuration and includes camera startup. Do not invoke it blindly when a camera is already running or expect its default to be generic object recognition.
- `darknet_ros/config/ros.yaml`: RGB input `/camera/rgb/image_raw`; outputs include `/darknet_ros/bounding_boxes` and `/darknet_ros/detection_image`.
- `darknet_ros_msgs/msg/BoundingBoxes.msg` retains image header and boxes; each BoundingBox supplies class string, ID, probability score and xmin/ymin/xmax/ymax. Preserve acquisition time and image coordinates when adapting these outputs. Class ID is not a persistent object/track ID, and a confidence score is not a guaranteed calibrated correctness probability.
- `yolov3-tiny-gesture.yaml` has `0-hand` through `5-hand` classes. Its training data, reliability and suitability for arbitrary/occluded hand detection are unknown; this is not an 80-class model plus a generic hand class.

Recommendation: verify the existing generic detector as a compatibility-first baseline before introducing a new runtime. This is not final model selection or a promise of frame rate/accuracy. A modern lightweight detector can later be compared on the same recorded robot scenes; the inference implementation should be replaceable. Check actual Jetson/JetPack/CUDA/TensorRT/Python versions before selecting/installing newer dependencies. Do not upgrade or overwrite the robot's working ROS environment as a starting step.

COCO-pretrained detectors commonly supply 80 categories, including person, chair and dining table, but no separate hand category. A dining-table class is not proof of reliable detection of every workbench/desk/table. Display filtering can show a short class list without retraining; removing labels from the display does not remove the model's main inference work. [COCO class reference](https://docs.ultralytics.com/datasets/detect/coco/)

Hand detection is a later explicit branch: assess the existing gesture model, a separate hand detector such as MediaPipe, or custom labelled training. Do not assume ordinary full-person detection will find an isolated hand. MediaPipe provides hand detection/landmark functions, but compatibility and performance on this Jetson are not established. [Official HandLandmarker API](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/HandLandmarker)

## Milestones and boundaries

| Stage | Deliverable | Evidence needed before moving on |
|---|---|---|
| 1. RGB baseline | Live image with class, score and box; initial display person/chair/dining table; optional other pretrained classes | Detector runs on the chosen computer, retains timestamps/coordinates, no command publishing; record latency, processed FPS and misses/false detections on robot-view scenes |
| 2. Object records | Consistent message/log format and optional per-session track IDs, isolated from model-specific outputs | Class ID distinguished from track ID; repeated observations handled; configurable label filter; sample saved/replayed consistently |
| 3. Position estimates | Valid depth-based object surface position, or supported LiDAR association | Resolve registered-depth metadata discrepancy; test measured distance, validity, RGB-depth alignment, full TF and timestamp matching; leave position unavailable when unsupported |
| 4. Labelled map | Existing occupancy grid plus separate object-marker layer in RViz | Restore/verify base telemetry, current map pose and update activity; known-object localization error and duplicate-label tests |
| 5. Fusion and evaluation | Camera labels associated with supported scan geometry; compare against camera/depth baseline | Explicit association rules and false-match evaluation; no invented association when the planar LiDAR misses the target |
| Later. Hands/refinement | Hand detection and robot-view adaptation as justified | Chosen hand task/dataset, model/runtime compatibility and evaluation; not presumed covered by generic COCO weights |

The stages do not require a new SLAM implementation. Reuse GMapping or RTAB-Map after validation, and keep object markers separate from occupancy values. A label marker is a first semantic-map overlay, not automatically a fully segmented object footprint. If poses/maps shift after SLAM optimization, anchored object records need updates rather than leaving stale markers at old coordinates.

Keep detector, object-position estimator and map-marker publisher separate. Proposed object fields: source image timestamp/frame; class and score; bounding box; optional track ID; optional position and its frame; position validity/uncertainty; observation source (camera/depth/LiDAR); association status; last-seen time. Unknown distance is not zero. Source evidence should remain distinguishable rather than falsely treating an inherited label as independent LiDAR recognition.

Moving people and hands belong in a transient tracked-observation layer with expiry; do not permanently accumulate every person observation into the static furniture map. Furniture can move too; persistent records need re-observation/update policies. Stable unique physical-object identity is not guaranteed by a basic detector/tracker.

## Current blockers by stage

Stage 1 is not blocked by missing odometry or map freshness. RGB arrival is confirmed at 640x480/rgb8; pretrained accuracy under the 12-13 cm camera viewpoint remains unknown. Training a new model is not required to run a pretrained baseline, but a small labelled evaluation set is needed to assess it fairly.

Stages 3-5 remain gated by the completed report's registered-depth frame/principal-point discrepancy, incomplete depth/cloud validity measurements, silent odometry/IMU/voltage and roughly 35-minute-old map headers. No change to these systems was made during planning.

## Immediate next action

Verify the existing detector package is installed/discoverable on the robot, not merely present in the copied source:

```bash
source ~/wheeltec_robot/devel/setup.bash
rospack find darknet_ros
```

This is a read-only package lookup and does not start a camera, detector or motors. If found, next inspect the installed generic configuration, weights and built executable, then prepare a separate personal detector-only launch under `~/fahad/` that subscribes to the already-running camera. Do not start mapping, gesture-following or navigation for the first detector test. If unavailable, choose between an isolated install and an off-robot prototype after checking hardware/runtime availability.

All integration code should remain in the user's personal directory. Preserve vendor files and the current map database. Review software/model/data licenses before redistribution; selecting a named model family alone does not settle licensing.
