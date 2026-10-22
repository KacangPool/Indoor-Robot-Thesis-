# Camera–LiDAR association: scan height, ambiguity and honest labels

2026-10-22. Conceptual clarification following the user's raised-object/rack
example. No fusion implementation, calibration, robot operation or new agreed
architecture. Existing pretrained/no-custom-training scope remains authoritative.

## Data and display are separate

The current driver represents LiDAR returns as planar LaserScan: range samples
with angular geometry and acquisition metadata. Each individual range is a scalar,
but a scan describes a 2D cross-section, not just a one-dimensional line. It does
not measure all heights. Its height in the room depends on mounting, robot pitch/
roll and terrain. User-estimated level mounting is roughly 14–16 cm above floor,
not a calibrated beam-plane measurement or a physically confirmed model label.

RGB images give appearance in image coordinates, not direct metric range. The
identified Astra S also supplies depth; selected-patch readings were demonstrated
on 2026-10-13. Full alignment and accuracy remain open, including the recorded
RGB/registered-depth CameraInfo discrepancy. Neither topic existence nor a depth
point cloud validates calibration or reconstructs complete hidden object shape.

RViz is a ROS visualizer. Drawing the same scan differently does not add sensor
dimensions or semantic labels. A room occupancy map needs a mapping process,
valid scans and motion/pose information, rather than merely changing a colour
setting. Current /scan delivery failure is separate from this geometric design
issue: previous functioning and current missing messages do not establish cause.

## The raised-object failure mode

For an object on a shelf, camera appearance may support a class while the laser
passes underneath and returns from a wall or shelf support. Similar horizontal
direction is insufficient to associate the returns. Even a laser point projected
inside a 2D detection rectangle can be background seen through gaps/occlusions.
Perfect calibration cannot make a non-intersecting beam see the raised object.

Examples, conditional on actual mounting/visibility:

- Standing person: low plane may hit legs, not the torso in the RGB box centre.
- Chair: may hit legs/base, or background through gaps; seat/back height differs.
- Raised object: beam may miss it entirely; do not label wall/support as that object.
- Occluding foreground: camera and laser can see different surfaces because the
  sensors occupy different positions, even when directions/projections overlap.

## What software must know

1. Camera intrinsics/distortion/processed-image geometry from the correct
   CameraInfo, including compatibility with actual RGB/depth topics and detector
   image resizing. Raw distorted pixels and rectified projections are not interchangeable.
2. Validated 3D camera–laser position/orientation, not just approximate height.
   TF expresses transforms but does not prove they are physically correct.
   Manual camera tilt changes extrinsics and requires an updated/revalidated transform.
3. Source acquisition times: associate YOLO results with the image actually used,
   not the newest camera frame after inference. Validate time tolerance; motion
   and camera/LiDAR viewpoint differences matter even with correct calibration.
4. Shared field of view, scan-plane intersection, source/data validity and
   visibility. Transform laser returns into camera coordinates and project only
   with the correct camera model; image overlap gives candidates, not identity.
5. Additional evidence such as reliable registered depth or a well-supported
   spatial cluster/surface match. A whole-box/central-pixel median can select
   wall/floor/chair, so these are hypotheses needing evaluation, not guaranteed rules.
6. For room-map markers: valid map/robot/sensor transforms and robot pose at
   observation time, measurement provenance/uncertainty, and expiring moving targets.

## Two distinct connections

**Object-level association:** camera supplies class; actual matched laser points
support geometry only if defensible. No matched measurement is a valid outcome.

**Map-level combination:** LiDAR-based SLAM provides room geometry/localization;
camera detection plus validated RGB-D can independently supply a surface-location
estimate transformed onto that map. This does not mean the LiDAR saw the object.
Keep the RGB-D-only marker distinct from a laser-supported observation. A 2D map
marker can summarize horizontal position while retaining estimated height and
measurement time in the observation record; it is not automatically an occupancy
cell or navigable target.

Recommended observation provenance: camera detection only (range unknown),
camera+valid-depth location (laser unassociated), or camera+defensible-laser
association (depth may corroborate). Rejected/ambiguous association must not
silently become a wall label or a made-up object range.

These clarify rather than replace the 2026-10-14 commitment: RGB-D is an aid or
comparison source, not a substitute for demonstrating the requested physical
camera–LiDAR association on an appropriate case. No mandatory RGB-D architecture,
new trained LiDAR classifier, camera tilt change or 3D LiDAR purchase is decided.

## Practical next work (proposed, not run)

Restore/verify real scan delivery first. Then check stationary calibration/TF
and source-image timing by overlaying projected laser returns on the RGB image.
Inspect supported targets at floor/leg height, a raised target and occlusion/
background cases. Use independent measured references and distinguish correct
associations, false associations, unmatched detections and position error. A
reliable system should reject the raised-object/wall match, not force every RGB
label onto a scan point. Moving fusion follows only after stationary checks.

## Evidence and boundaries

Local project evidence: AGREED_PRETRAINED_FUSION_SCOPE_2026-10-14.md,
BOX_DEPTH_LIVE_RESULT_2026-10-13.md and BOX_DEPTH_FIRST_CHECK.md. User-estimated
mounting and old depth report are not new measurements. Runtime sensor alignment,
physical range accuracy and robot pose remain unverified. No code/runtime tests
apply to this explanatory note; verification was source/report review only.

Primary ROS1 references (Noetic schema/API inspected; robot remains Melodic,
no migration or installed-version compatibility test implied):

- [LaserScan](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/sensor_msgs/msg/LaserScan.msg)
- [CameraInfo](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/sensor_msgs/msg/CameraInfo.msg)
- [image_geometry projection API](https://raw.githubusercontent.com/ros-perception/vision_opencv/noetic/image_geometry/include/image_geometry/pinhole_camera_model.h)
- [RViz visualizer](https://github.com/ros-visualization/rviz)
