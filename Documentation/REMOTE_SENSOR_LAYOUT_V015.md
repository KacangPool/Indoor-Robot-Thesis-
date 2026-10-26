# Sensor-first console v0.15 — 26 October 2026

## Change and boundary

Desktop follows the user's red sketch: full-height camera on the left, LiDAR
upper middle, controls below it, compact readings on the right. The camera fills
its panel without cropping, by stretching on desktop. This changes appearance,
not original image pixels, calibration, detector boxes or inference resolution.
Narrow screens retain the stacked camera/LiDAR/controls/readings layout.

The scan drawing buffer follows its panel dimensions with equal X/Y metric
scale. No change to laser coordinates, distances or distance-to-point colours.
There is no inferred camera/LiDAR alignment from their visual placement.

## Scan shading is not a map or driving permission

When fresh scan data is available but /map is absent:

- Grey squares mean **unknown**, including invalid/omitted beams and space
  beyond finite returns. They do not mean traversable floor.
- Pale sectors show the part of individual finite valid beams before their
  returns, from the message's range_min to at most 4 m. A provisional 3 cm
  display-only endpoint margin avoids shading right onto the return. This is
  not a measured sensor error bound or clearance inflation.
- The angular bin width comes from angle_increment, not a measured optical beam
  footprint. Shading is a visibility sketch, not proof that gaps between physical
  rays are clear. A real occupancy mapper needs its own validated sensor model.
- No polygon joins different endpoints. Invalid/NaN/infinite/out-of-range beams
  do not fill holes. At most 720 original-index rays are shown; decimation keeps
  their original angular width rather than widening across omitted rays.
- Points retain fixed distance colours: red at 0 m through blue at 4 m. Neither
  point colour nor shading classifies an object/material.
- Stale/unavailable scans hide both points and shading. No data accumulation,
  occupancy probabilities, saved room map, collision avoidance or footprint
  clearance is created. This scan-plane evidence misses overhangs/drops/heights.

Existing real /map rendering remains separate: published OccupancyGrid cells,
map geometry and validated TF overlays, not fabricated map cells. White is zero
occupancy, grey unknown and black high occupancy. Published free space still
does not certify whole-robot clearance.

## Orientation

The previous scan-only car pointed along laser +X without a verified body
transform. It was an illustration, not evidence of the physical heading. It is
now replaced with a laser-origin square: +X up and +Y left. Do not flip points
or assume a 180-degree correction from a screenshot. The actual laser-to-body
transform must be checked. In map mode, a car appears only with the existing
fresh body TF; an explicit arrow marks its +X front. Missing TF still hides it.

## Motion and deployment

The requested 0.50 m/s increase was not implemented. Command ceiling remains
0.30 m/s and feedback guards/arming/lease/watchdog behavior are unchanged. Prior
feedback faults and stopping distance remain unmeasured; visual changes must
not silently relax those checks. No motor adapter was edited.

Hub and dashboard advertise v0.15; the same 17-file checksum bundle remains.
Keep Hub and sibling remote_dashboard folders together. No robot upload or
installation has been performed by these source changes.

To install through the existing user-operated Hub: release inputs, Stop, confirm
standstill, close old controller tabs, Disconnect & close the old Hub, reopen
Tools/robot_hub/Start Robot Hub.cmd from this checkout, then Connect & prepare.
The Hub can update its personal runtime after checking ownership and checksums;
do not start duplicate servers or overwrite vendor files. Reload one console
and verify v0.15. Keep driving disabled for the sensor checks.

## Today's evidence and next checks

User-supplied terminal results on 26 October show one /lsn10 publisher and
fresh /scan at approximately 10.01 Hz. The earlier no-message condition is not
present in this run; its prior root cause is not thereby diagnosed. /map has no
publisher. The screenshot's v0.14 interface predates these v0.15 source changes.
Robot/header clock dates can differ from the laptop date; establish clock domains
before evaluating fusion timing. No calibration or live fusion is validated.

Follow-up user output: tf_echo reports base_footprint absent; the visible tree
contains only camera_link, camera_rgb/depth_frame and their optical frames.
That does not establish a laser/body/camera transform. RGB CameraInfo reports
640×480, plumb_bob, non-zero D, raw focal lengths about582.80/584.40 pixels and
principal point321.42/245.99; rectified P differs. These are published values,
not an independent accuracy check. Raw YOLO coordinates cannot simply use P.
Registered-depth and rectified-RGB topic names are listed, but listing does not
prove frame delivery or registration. One RGB header epoch corresponds to
15 October14:13:16UTC despite this client's26 October date; inspect robot/ROS
time mode before combining with host-clock records, without changing clocks.

Registered-depth follow-up: /camera/depth_registered/image_raw delivers about
29.75Hz after the initial short window. This is delivery rate, not depth accuracy
or RGB registration proof. The calibration-info attempt used camera_inf (missing
the final o), so its warning is not evidence that camera_info is unavailable.
/use_sim_time is unset; robot date -u output and correctly spelled CameraInfo
are still pending. No clock/parameter change is indicated by that alone.

Next, in the sourced robot SSH terminal while stationary:

```bash
source ~/wheeltec_robot/devel/setup.bash
timeout -k 2s 8s rosrun tf tf_echo base_footprint laser
timeout -k 2s 8s rostopic echo -n 1 /camera/rgb/camera_info
timeout -k 2s 8s rostopic list | sort
```

These read transforms/calibration metadata/topic names, not image arrays or
movement commands. A missing TF is a diagnostic result, not a reason to invent
an orientation. Identify exact registered-depth topic names before further
commands; do not confuse depth-generated scan with physical /scan.

Then run the prepared software inventory (ROBOT_SOFTWARE_CATALOGUE.md), inspect
the actual mapping launch configuration before starting any stack, measure/fix
sensor mounting/tilt and capture a small stationary aligned dataset. Use an
independent measured reference distance. Fusion stays offline/read-only until
calibration, rectification, foreground/height and timestamp checks pass.
University-network/eduroam testing remains explicitly paused.

## Verification

Focused JS checks exercise ray gaps, blind range, endpoint/radius caps, bounds,
stale/invalid handling, metric canvas resize, map cache and no guessed heading.
Python tests check finite beams, missing-beam gaps and bounded sampling. The
existing frontend test was updated for the intentionally changed grid layout;
an old SCAN ONLY label remains to preserve the honest fallback contract.
Full offline checker results and browser verification limits are in CHANGELOG.
No old-Jetson execution, physical orientation or live visual behavior is implied
by laptop tests.
