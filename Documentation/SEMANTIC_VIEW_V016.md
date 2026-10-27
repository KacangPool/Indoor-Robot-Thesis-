# v0.16: viewer and semantic-observation contract

Design recorded before implementation, 27 October 2026. Source-only work away
from the lab: no robot deployment or autonomous navigation is part of this task.

## Viewer

Camera and LiDAR get equal desktop columns and full workspace height. The side
column has independently scrollable control/readings halves. Viewer zoom, pan
and orbit change only the projection of displayed data, never ROS coordinates,
intrinsics, control intent or map occupancy. Orbit is an orthographic 3D view of
the existing flat scan/map plane, not new 3D sensor measurements. Zoom is bounded
and Reset returns to top view. Viewer mouse/touch listeners have no motor API.

The car glyph has wheels, headlights and an explicit +X front, is not to scale
and is drawn at a sensor/map position only when a valid body transform exists.
Missing body TF remains unknown. An illustrative orientation key can show the
glyph without claiming an actual pose. No guessed 180-degree correction.

## Observations and fusion

- A camera detection retains class, score, bounding box and exact source-image
  header, even with no laser match. This is a timestamped observation, not a
  persistent/tracked object or saved per-run map. Live snapshots are bounded to
  100 records, expire after two seconds, and do not write files.
- Live YOLO input is a read-only BoundingBoxes subscriber. Missing message
  package, invalid/stale headers or bad boxes must not break camera viewing.
  Browser text rendering must not interpret detector labels as HTML. The list
  belongs to the detector's source frame, not necessarily the current preview.
- Camera-only means position/height unknown, not floating/table/clearance.
  Neither a missing laser return nor successful travel proves drive clearance.
- Offline semantic construction reuses fuse_snapshot and its existing calibrated
  full-3D projection, exact source-image matching, stationary/timing/foreground
  and ambiguity gates. Only a depth-supported unambiguous cluster labels actual
  laser ray indices. Unsupported rays are never given the camera class.
- Independently verified registered depth may supply an additional camera-only
  surface point. Rectified optical XYZ is in metres, with +Z forward, +X right,
  +Y down. Convert through the validated inverse laser-to-camera rigid transform
  before describing height relative to the laser plane (laser +Z normal).
  This is a sampled surface, not an object centre or proven floor height.
- Above/below-plane classification uses a provisional 0.15 m ambiguity margin;
  it is evidence under supplied calibration, not measured sensor uncertainty.
  No automatic table/floating label, support relation, robot-clearance inference
  or autonomous command is emitted. Floor/headroom require further geometry.
- Map-frame camera-depth and LiDAR-supported observations remain separate
  evidence layers, acquisition-timed and expiring. Missing map TF yields no map
  point; occupancy is never changed. All synthetic evidence is marked synthetic.

Actual live positional fusion is still blocked by the lab's missing body/laser
TF, unvalidated calibration/registration, raw-versus-rectified YOLO inputs and
clock provenance. This update must not describe the live label list as calibrated
fusion. Existing 0.30 m/s ceiling and every motion/security guard stay unchanged.

## Verification and installation

Test pure projection/reset/zoom bounds, viewer input isolation, stale hiding,
import side effects, bounded/escaped camera labels, unmatched observation
retention and raised-object height without false laser association. Reuse the
offline quality checker, verify bundled dependencies in isolation and record
actual skips/failures. No Jetson compatibility or physical accuracy is inferred
from laptop tests. Runtime/source manifests and copying instructions change
together; verification/deployment results are recorded in CHANGELOG.md.

## Use and next lab

Viewer: +/− or wheel zoom(0.25–8×),3D orbit selects an oblique plane view; drag
rotates it. Pan toggles drag translation; Reset restores top view/1×/centre.
This works without a motor-enabled session; stale scans stay hidden on redraw.
The prominent car reference key is illustrative, not a fake robot position.
Scan points/individual ray bins have a16m display cap so zooming out can reveal
more than the old4m display radius; this is not a sensor range/accuracy claim.
Point colours still saturate blue at4m. No synthetic max-range/invalid returns.

The live camera-only list is not attached to the presently displayed image's
pixels: it belongs to its own exact YOLO source header. It is a bounded in-memory
snapshot, not persistent run history, tracking or machine learning retraining.

Runtime manifest:22files. New shared files are __init__.py,detections.py,
recording.py,observations.py; the pure scene_geometry.js adds one asset. Hub
source_file resolves only this allowlist; checksum/upload/tests use the same
resolver. The diagnostic tools ZIP has21source files after shared-core additions.
No third-party dependency/model/framework upgrade required.

Read-only offline example, using the laptop's existing Python with NumPy:

```text
python Tools/fusion_prototype.py --demo --output tmp/semantic_demo_new
```

Choose a new directory; the tool refuses overwrite. Ten explicit synthetic cases
include a monitor above a laser-supported table and the same monitor with no
verified depth. Original eight regression cases remain. These are toy boxes and
geometry, not YOLO inference or physical experiments. JSON/HTML are explicit
offline reports, not the deferred on-robot/per-run map-saving feature.

Next lab: Stop/confirm stationary before reopening the updated Hub and preparing
the22file runtime. Confirm v0.16; test viewer inputs with driving disabled, then
read-only source detections and their expiry. Verify real RGB/depth edges,
rectification, laser/body/camera transforms and clock provenance before enabling
any separate positional fusion adapter. No such adapter is silently started.
