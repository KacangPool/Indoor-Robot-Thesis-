# Offline fusion prototype v0.1

This is an original small association prototype, not a new detector, a live ROS
integration, a calibrated digital twin, SLAM or a navigation controller. Nothing
starts on import. No model/weights/downloads or robot connection. Uses existing
YOLO-style box records, exact source-image keys and shared depth conversion.

## What it does

1. Require an exact match between detection `image_header` and the supplied image
   header (time, sequence and optical frame). Detector output time is not a
   substitute for the input-image acquisition time.
2. Reject unknown motion, unvalidated calibration, stale/future or unsynchronised
   measurements, unsupported scan duration and missing valid returns.
3. Cluster adjacent valid scan rays by a distance-gap threshold; preserve actual
   scan-plane points `(r*cos(theta), r*sin(theta), 0)` in the laser frame.
4. Transform points using full3D rotation/translation into the optical camera
   frame and project into a **rectified** image using its matching intrinsics.
   Box membership in both horizontal and vertical pixel coordinates gives only
   candidate support. No artificial object-height lift, nearest-bearing match or
   box-centre/background distance substitution.
5. Leave projection-only candidates unconfirmed. Optionally compare candidate
   optical Z against an independently human-confirmed object depth patch from the
   registered image; reject depth disagreement, mixed/invalid evidence and shared
   or multiple candidate clusters. This patch is a validation aid, not automatic
   foreground segmentation or a mandated new RGB-D architecture.
6. Emit a temporary **surface observation** map point only for depth-supported
   evidence and a valid acquisition-timed laser-to-map transform. Preserve local
   evidence when map TF is missing. Do not invent an object centre/footprint,
   change occupancy, persist moving people or plan motion.

The result `depth_supported` means consistency under the supplied evidence and
thresholds, not identity ground truth or measured accuracy. A false detector label,
wrongly confirmed depth patch or bad calibration can still create a wrong result.

## Run at home

From laptop PowerShell in the project folder, using an existing NumPy Python:

```powershell
& 'C:\Users\fahad\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\Tools\fusion_prototype.py --demo --output .\tmp\fusion_demo_new
```

Use a new output directory; existing outputs are refused. Open its `index.html`.
The standalone page contains embedded report data and no network requests. It
does **not** show camera photographs or execute YOLO; rectangles/labels are toy
test inputs. Eight scenes exercise supported/raised/background/overlap/stale/
missing-map/uncalibrated cases. The hand-authored synthetic occupancy grid is
explicitly marked, not derived from our lab. Grey means unknown, not traversable.

Generated `report.json` preserves thresholds, input SHA-256, provenance, rejection
reasons, candidate/accepted support and marker timestamp/expiry. Outputs stay in
ignored `tmp/`. Open a new report after changes; old outputs are not rewritten.

Recorded-data mode, after preparing a validated normalized contract:

```text
python Tools/fusion_prototype.py --input snapshot.json --output tmp/real_snapshot_new
```

It reads at most2MiB, rejects nonstandard JSON constants, never opens bags or
replays a ROS publisher. A successful command is not proof the source hardware
or recorded calibration is correct. No actual aligned recording has been run yet.

## Snapshot contract

The synthetic fixture builder in `Tools/fusion_fixtures.py` is the executable
schema example. Do not copy its made-up camera/TF numbers onto the robot.

| Field | Required meaning |
| --- | --- |
| `schema_version`, `mode` | 1; explicit synthetic or recorded provenance |
| `stationary` | Explicit confirmed stationary acquisition; moving fusion/deskew is unsupported |
| `calibration_status`, `calibration_id` | Validated real calibration reference, or synthetic only for toy mode; flags are declarations to review, not an automatic calibration test |
| `reference_stamp` | Evaluation-clock time in seconds, in the same domain as source headers; not laptop wall time for old bags |
| `image` | Exact ROS-style `seq/secs/nsecs/frame_id` header, width/height, rectified=true |
| `detections` | Exact source-image header + existing `boxes_list` schema (`class`, `class_id`, `score`, xmin/ymin/xmax/ymax); <=100 boxes |
| `camera` | Matching rectified image dimensions/optical frame and fx/fy/cx/cy in pixels |
| `scan` | Source header, ranges in metres (null = invalid JSON return), angles in radians, range limits and per-beam time increment; <=7200 rays |
| `laser_to_camera` | T_camera-optical_laser, proper3x3 rotation and translation in metres; explicitly static mounting or acquisition-timed transform |
| optional per-box `object_depth` | Independently confirmed foreground patch: same source-image header, registered_to_rgb=true, region_verified=true, patch centre u/v in box, encoding16UC1 mm or32FC1 optical-Z metres, rectangular values <=31×31 |
| optional `laser_to_map` | T_map_laser, same scan frame, target map, static=false and time matching the scan; no latest/zero-origin fallback |

Optical convention: X right, Y down, Z forward. Laser convention: X forward,
Y left, Z normal to the actual scan plane. A sensor's floor mounting height is
represented by extrinsics, not by changing all laser points to a guessed object
height. The patch depth is optical Z, not radial laser range; comparison happens
after the laser point is in the camera frame.

Important: the installed YOLO currently takes `/camera/rgb/image_raw`. Existing
raw-image detections cannot simply be asserted rectified. A later adapter must
use appropriately rectified detector inputs or a separately validated distortion-
aware projection path. v0.1 implements neither live adapter nor raw distortion.
Registered depth must likewise be independently checked; topic names or equal
dimensions do not prove pixel registration.

## Conservative prototype settings, not sensor specifications

Default detector score0.5; adjacency gap0.25m; minimum3 supporting points and
50% of the visible cluster; maximum image-to-entire-scan delta0.1s; age0.5s;
scan duration0.15s; dynamic-TF delta0.05s; depth agreement0.2m, patch spread0.15m.
These are explicit initial engineering choices, not validated confidence bounds.
No parameter tuning against the eight cases can establish general performance.

The representative is one real supporting laser ray nearest the cluster's
component-wise median, not a fabricated centroid between objects. Bounding-box
pixels still include background, clusters can split real legs or merge adjacent
objects, and uncertain evidence must remain unmatched. The current one-cluster
rule may reject a person with separately visible legs; recall improvement is
future work after reliable ground truth, not a reason to force a match now.

## Modular layout and lab acceptance

- `fahad_core/fusion_geometry.py`: strict headers, camera/transform validation,
  full3D projection and planar scan clustering.
- `fahad_core/fusion.py`: timing/evidence/association and marker eligibility.
- Existing `recording.frame_key`, `detections.finite_number` and optional
  `depth.depth_metres/patch_stats` are reused rather than copied.
- `fusion_prototype.py`: explicit file/report adapter; `fusion_fixtures.py`:
  synthetic inputs; `fusion_demo_template.html`: read-only view.
- `test_fusion.py`: offline boundary/failure regression tests. Diagnostic bundle
  includes entry, fixtures, template and all shared dependencies.

Next lab: verify fresh physical `/scan`, inventory actual dependencies, inspect
camera intrinsics/distortion/registration and full TF mounting, then record a
stationary matched RGB/detection/scan/calibration/TF example. Check projection
overlay against independently measured targets before accepting semantic labels.
Only then implement a subscribe-only ROS1 adapter and read-only marker display.
Use the existing mapper for `/map`; creating this report does not create a room
map. Evaluate false matches, misses, ambiguous/unsupported cases, position error
and acquisition-to-output latency. Actual Jetson Python/NumPy/ROS, live TF,
performance and physical outcomes remain untested.

Research shortlist and source inspection: [research note](CAMERA_LIDAR_RESEARCH_2026-10-23.md).
