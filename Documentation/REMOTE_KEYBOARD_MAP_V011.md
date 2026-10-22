# v0.11 — keyboard steering and sensor-first map workspace

2026-10-22. Local source, not deployed or tested on the robot by tools.

## Controls and speed

W/Up and S/Down retain the five-second .30 m/s held-input S-curve. A/D now select
left/right steering while held; release centres steering, both A+D centre too.
Steering alone never starts travel. Normal travel release keeps a healthy session;
release/B still requests zero without easing. Explicit Stop/Space/Escape disables.
Steering pressed before Enable, in an editable field/shortcut or through a fault
does not queue or replay: release and press it afresh once enabled. Mouse steering
is disconnected in the supported keyboard layout. The pad is hidden for desktop
pointers; a touch-only coarse-pointer fallback is retained but phone use is untested.
No selectable Circular/Independent layouts in the current UI; old backend/logic
test profiles are retained, not advertised as the new operator workflow.

**The requested .40 ceiling was not enabled.** The supplied recording
Videos/20261022_140118.mp4 (~261.72 s, 1920x1080) starts with an explicit reported
speed fault: vx=.176 m/s, vy=0, yaw=.379 rad/s. This exceeds the current .35 yaw
guard. A sampled late frame (~230 s) shows a command timeout. Neither proves the
root cause, calibrated physical turning, a collision stop or an exact Wi-Fi range.
The .30 command/.32 longitudinal/.35 yaw/.04 lateral limits, freshness, lease,
controller uniqueness, sequencing, release feedback and recovery checks are
unchanged. Do not increase fault limits simply to hide an unexplained reading.
The copied driver serialises Twist angular.z and returns controller Robot_Vel.Z
as odometry yaw; its source is not proof of the installed binary/firmware behaviour.
Next speed work needs matched requested-command/odometry/time observations and
normal stopping checks, not intentional collisions or moving connection-loss tests.

## What the RViz-style display means

ROS OccupancyGrid values are -1 for unknown, 0 for zero occupancy and up to 100 for
high occupancy. This console shows unknown grey, zero occupancy white, occupancy
>=65 black and intermediate probabilities as grey shades. Colours are a rendering
choice; a grey area in an RViz photograph is not proof of clear/safe floor.
Reference: [ROS message definition](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/nav_msgs/msg/OccupancyGrid.msg).
The screenshot appears to combine a grid map, laser returns and robot/TF visuals;
its exact enabled RViz layers cannot be identified from the photograph alone.

The new display reads `/map` only; it neither creates a SLAM map nor starts
navigation, saves/overwrites maps, publishes a goal or changes movement based on
cells. The map may represent older observations, so snapshot age is displayed.
An unoccupied cell at a LiDAR scan height is not complete three-dimensional
clearance, robot-footprint clearance or a driveability guarantee.

- Exactly one current map publisher connection and a valid OccupancyGrid are
  required. Disconnected, conflicting, invalid or oversized maps are hidden.
- Static/latched map snapshots need not be republished continuously; age is
  explicitly shown. Reconnecting cannot by itself prove a map describes this room.
- Maximum input is 1,000,000 cells. Maximum display is 256x256; larger accepted
  grids are conservatively pooled: occupied cells win, otherwise unknown/padded
  cells prevent a block being displayed as free. Original origin/yaw is honoured.
  Large default SLAM extents may exceed the input limit and need a separately
  reviewed bounded/vectorised display implementation; no configuration was changed.
- Separate bounded map worker and ~1 Hz browser fetch; `/api/map?revision=...`
  omits unchanged cell arrays. No map-cell arrays are added to the drive/status
  response. Old-Jetson runtime load and wireless impact remain unmeasured.
- A small illustrative car appears on the map only with a fresh planar TF pose
  from the map frame to `base_footprint` (the existing isolated base's configured
  frame), not by treating odometry coordinates as map coordinates. Icon size is
  illustrative, not a measured footprint. No TF means no mapped car.
- Fresh scan points are overlaid only with a timestamp-matched map-to-laser TF,
  recent ROS stamp, single scan connection and valid current scan. No TF means
  those points are not mixed into the map. Optional missing tf2_ros leaves the
  grid usable, with no invented overlays. Motion deskew is not implemented.
- Without `/map`, the panel honestly falls back to current mint scan dots on an
  unknown background. The origin car is explicitly illustrative at the laser
  origin, not a verified base footprint. Intensity/distance selectors removed.

## Layout and update

Desktop sidebars are now 170/245 CSS pixels. At 1280x720 the central panels are
about 795 px wide versus 645 previously, with a larger map row. Images remain
uncropped and undistorted; a 4:3 source cannot fill a very wide, shallow frame
without cropping or stretching. One-viewport cockpit, pinned Stop and narrow-screen
stacking retained. Phone steering/connection has not been validated.

At standstill, close old console tabs and Hub, reopen Hub and use Connect & prepare.
Open one fresh page and verify v0.11. No manual duplicate server/base launch needed.
With the robot stationary, in a **robot SSH terminal** inspect:

```bash
source ~/wheeltec_robot/devel/setup.bash
timeout -k 2s 8s rostopic info /map
```

If missing, mapping must be prepared separately. Do not start the full vendor
mapping/3D-navigation launch on top of the Hub's active base/camera/LiDAR: it can
duplicate drivers, and some RTAB-Map launches can delete their old database.
The new Hub update intentionally does not start those programs automatically.

## Wireless boundary

The ~10 m distance is a user estimate under current indoor conditions, not a
measured radio specification. A timeout does not distinguish radio coverage,
interference, network/CPU load, Jetson scheduling or a stalled request. No software
can create connectivity without a working communications path; another controller
would still need a suitable link/backhaul and would not by itself solve it.
No networking, Internet routing or port exposure was changed.

The native Hub remains a Windows Python application, not an installable Android/
iOS app. A phone browser could be an operator client later, but the current
laptop localhost SSH tunnel is not automatically accessible on the phone. Secure
phone access and stopping behaviour need their own setup/test; do not expose this
prototype control server publicly. A nearby operator is supervised teleoperation,
not remote autonomous search-and-rescue capability.

## Verification and open items

251 dashboard Python tests (including 12 new map tests), 114 JavaScript checks
(89 frontend/11 geometry-ramp/14 one-shot) and 45 Hub tests run (44 pass, one Windows
symlink-privilege skip). Tests use fake ROS and localhost peers, no robot.
Python 3.6 grammar and JS syntax checked. Native Python2/Jetson not executed.

Disconnected synthetic-map fixture inspected at 1280x720: correct panel order,
larger centre, visible A/D and Stop, no page overflow. Fixture rejects every POST;
the map/pose are synthetic and visibly labelled. Artifacts:
`tmp/hud_v011_review/preview.py` and `hud_1280x720_fixture.png`.
Video review sampled frames/crops only; audio not analysed and no distance,
actual speed or stopping performance measured. Original media unchanged.

Still needed: live `/map` publisher/dimensions/TF readiness, map processing cost
on the old Jetson, real A/D driving/turn feedback, stopping evaluation, phone UI,
wireless root-cause checks and independent firmware/host/serial failure stopping.
