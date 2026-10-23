# Existing camera–2D LiDAR work and prototype choice

Reviewed 23 October 2026. This is a scoped search and source inspection, not a
claim that no other suitable software exists. No external repository was executed,
installed, benchmarked or copied into our code. Robot remains ROS1 Melodic.

## Main finding

Yes: this problem has been studied and implemented. There is reusable software,
but no package reviewed here is a verified drop-in solution for this low-mounted
Astra/planar-LiDAR/YOLO setup. A detector supplies semantic evidence; spatial
association additionally requires calibrated geometry, source-image timestamps,
visibility assumptions and a way to reject false matches. Missing vertical
measurements cannot be recovered merely by assigning a camera label to a bearing.

## Practical software shortlist

| Project | What it offers | Fit and limitation |
| --- | --- | --- |
| [SPENCER](https://github.com/spencer-project/spencer_people_tracking) | ROS people-detection/tracking framework combining RGB-D, monocular and 2D-laser detector outputs; configurable association components | Strong real-robot architectural reference for person-level fusion. Not general chair/table semantic mapping or a confirmed Melodic/Jetson build. Default RGB-D mounting assumptions differ substantially from our floor camera; package-specific licences/dependencies need review before reuse. |
| [DROW3 / DR-SPAAM](https://github.com/RWTHVision/2D_lidar_person_detection) | Pretrained 2D-range person detectors and ROS wrapper; repository describes ankle/knee-height input | Closest analogue to a pretrained detector on the laser side. Person-specific, not general object recognition; scan resolution/height/domain and compute compatibility need measured tests. GPL-3.0 repository; optional future comparison, not a decision to train or add a second model now. |
| [scan_detection_fusion](https://github.com/HexboxRC/scan_detection_fusion) | ROS2 Jazzy wrapper and ROS-free Python fusion class; camera-bearing range estimation, registry and footprint defaults | Relevant lightweight reference (Apache-2.0). Inspected `lidar_camera_fuser.py`: core `fuse` accepts angular bounds, not full vertical image geometry. Bearing windows and class-size priors do not independently prove physical intersection. No adoption of assumed footprint dimensions as measured free/occupied area. |
| [Warehouse multi-modal perception](https://github.com/AhmedBayoumey94/multi-modal-perception-for-dynamic-warehouse-environments) | ROS2 Jazzy/Gazebo example with scan clusters, camera detections, TF projection and markers | Similar overall pipeline (MIT). Inspected association implementation creates a point from centroid XY plus configurable `cluster_height_for_projection`; this is not a measured object's height. Different stack, custom warehouse detector and simulator context; not an automatic Melodic/YOLO replacement. |
| [camera_2d_lidar_calibration](https://github.com/ehong-tl/camera_2d_lidar_calibration) | ROS camera/planar-laser extrinsic calibration tool, README reports Kinetic testing | Potential calibration aid, not a detector or semantic mapper. Dependencies and target procedure require inspection and lab measurements; no local compatibility claim. |

Inspected source revisions, not floating README claims alone:

- SPENCER: `09b256ba4bc22c5cae8a5ae88960de1a387cfd7f` (framework/README).
- DROW/DR-SPAAM successor: `d12e90225d52ba6c85d20061f1e7286d6a64aade`.
- [Bearing-based core](https://github.com/HexboxRC/scan_detection_fusion/blob/0d7de316f49db2ee76e43866b3f07f1aba51444b/scan_detection_fusion/lidar_camera_fuser.py):
  `0d7de316f49db2ee76e43866b3f07f1aba51444b`, especially `fuse` lines296–407.
- [Warehouse association](https://github.com/AhmedBayoumey94/multi-modal-perception-for-dynamic-warehouse-environments/blob/af3c7774c64db730e1dd48855abfad276d67c082/multi_modal_ws/src/multi_modal_perception/multi_modal_perception/camera_lidar_association_node.py):
  `af3c7774c64db730e1dd48855abfad276d67c082`, centroid/projection lines124–167.

## Papers to read first

1. Jia, Steinweg, Hermans and Leibe, **Self-Supervised Person Detection in 2D
   Range Data using a Calibrated Camera**, ICRA2021.
   [Author preprint](https://arxiv.org/abs/2012.08890).
   Camera detections generate pseudo-labels for laser-person-detector training;
   illustrates the importance of calibration and sensor-domain adaptation.
   This is not our selected no-training implementation.
2. Jia, Hermans and Leibe, **DR-SPAAM: A Spatial-Attention and Auto-regressive
   Model for Person Detection in 2D Range Data**, IROS2020.
   [Author preprint](https://arxiv.org/abs/2004.14079).
   Uses temporal range information for person detection; pretrained code exists.
   Reported embedded-GPU results concern the authors' hardware, not our Jetson.
3. Li and Stevenson, **2D LiDAR and Camera Fusion Using Motion Cues for Indoor
   Layout Estimation**, FUSION2021 / preprint2022.
   [Full author paper](https://arxiv.org/html/2204.11202).
   Aligns room-contour laser measurements with visual floor/wall boundaries under
   vertical-wall/single-floor assumptions. Useful layout reference, not arbitrary
   shelf-object instance association or general obstacle-clearance proof.
4. Xu et al., **Monocular camera and laser based semantic mapping system with
   temporal-spatial data association for indoor mobile robots**, 2023.
   [Publisher](https://link.springer.com/article/10.1007/s11042-023-14796-1).
   Publisher abstract supports staged calibration, semantic mapping and temporal/
   spatial association. Full implementation/calibration details not verified here;
   do not infer an exact planar-LiDAR hardware match from the title/abstract.

Additional lead: *Semantic surrounding projection for object height estimation
using single-line lidar and image*, DOI10.1016/j.compeleceng.2023.109034. Indexed
abstract describes height estimation; publisher full page blocked access during
this review. Similarly, a2026 Sensors angular-sector-fusion article was found but
publisher retrieval failed. These are reading leads, not inspected solutions or
evidence that the height ambiguity has been solved for our installation.

## Why shelf objects and walls remain ambiguous

A laser ray measures a point on its actual scan plane, not the complete object in
the camera box. Even full3D projection into that box can fall on visible background
inside the rectangle. A bounding box is not a foreground segmentation mask.
Do not artificially lift laser points to a convenient guessed object height.

Proposed first prototype therefore separates:

- camera-only detection: no usable laser support;
- projected candidate: geometrically plausible, identity unverified;
- ambiguous: competing clusters or shared support;
- depth-supported association: consistent with an independently confirmed object
  depth patch from a registered RGB-D image; still conditional, not ground truth.

Depth support is optional and conservative. It must not be silently derived from
the same unknown background pixels, nor required as a new thesis architecture by
this experiment. Without independent support, retain candidates for lab review
rather than manufacture a range/semantic map point. A later calibrated mask,
validated leg detector or recorded human-reviewed association could provide other
evidence. Real data and quantitative evaluation are still needed.

## Mapping and visuals are separate layers

Use an existing SLAM occupancy map for geometry. Add timestamped observation
markers only with an appropriately timed laser-to-map transform. Marker positions
are observed surface points, not object centres/footprints, permanent static
landmarks or navigation targets. A person observation must not permanently mark
the room occupied. No SLAM/nav launch or occupancy rewrite in the offline prototype.

[ROS OccupancyGrid](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/nav_msgs/msg/OccupancyGrid.msg)
defines unknown as-1 and occupancy0–100. In the usual RViz Map palette, white is
free, black occupied and grey unknown. Free means at that mapping sensor's plane,
not a guarantee of full-robot clearance, no overhang or no drop-off. See the
[RViz map renderer](https://github.com/ros-visualization/rviz/blob/noetic-devel/src/rviz/default_plugin/map_display.cpp).
An empty `/map` cannot be fixed by colouring a live scan background as free floor.

## Scope now and next lab

Keep pretrained YOLO and existing robot software. Implement original small pure
geometry/association modules and offline synthetic regression cases, then inspect
saved real data after fresh `/scan`, camera calibration, registration and TF/time
are verified. No imported third-party implementation, new model weights, custom
training, dependency upgrade, Wi-Fi change, Gazebo install or motor commands.

Stationary lab cases: supported foreground target, same-bearing raised object,
background wall, partially occluded person/chair, overlapping detections and
missing/stale streams. Measure false associations as well as accepted ones.
