# Hub/dashboard v0.7 · activity, driving diagnostics and scan colours

Current source v0.8 (2026-10-22) adds default separate held travel and steering;
see `REMOTE_PEDALS_STEERING_ROS1.md`. v0.7 diagnostic/colour/shutdown notes below
remain applicable, but its joystick defaults do not describe the current layout.

Prepared 2026-10-21. Local source implemented and tested with fake ROS/SSH;
this update has not been deployed to or physically verified on the robot by tools.
User reports the real hub opens/works and 0.1 m/s is useful, but sometimes driving
disables or mouse grip is lost. These are user observations, not measured speed,
fault attribution or evidence of independent firmware stopping.

## Install this update

1. Release controls, click browser **Stop**, and verify the robot is stationary.
2. Close the existing hub. Reopen `Tools/robot_hub/Start Robot Hub.cmd` **without
   `--demo`**. A running Python app does not reload source edits automatically.
3. Join robot Wi-Fi, enter the password locally, acknowledge stationary setup,
   then **Connect & prepare**. This updates only the personal trial dashboard,
   after the existing disabled/ready checks, with backups and checksum verification.
4. Confirm **v0.7** on the hub and browser. Reload the old browser page while
   stationary so it fetches the new scripts. Keep only one driving page enabled.
5. First test a short, small straight input/release under direct observation.
   If it disables, do not repeatedly enable and guess: collect the reason below.

Do not update while holding a control. If the hub refuses to replace an active,
faulted or unready server, inspect the report; do not kill arbitrary listeners or
restart the base to bypass that check. Original viewer/vendor files stay unchanged.

## Visible progress

An animated bar, current step and elapsed seconds indicate active connection/
preparation work. Steps include SSH connection, personal helper, camera, runtime
update, LiDAR, base, dashboard and tunnel. It is **indeterminate**, not a fabricated
completion percentage. Background status checks do not flash the loading bar.
Cancel requests wait for the current bounded step; already-started services remain.
SFTP operations now have a ten-second channel timeout. Disconnection also animates
while attempting Stop and closing the connection.

## Why controls disable

Open **Why did driving stop?** under the controls. It retains separately:

- last browser-side stop, e.g. lost focus, missing/old preview, lost pointer
  capture, failed heartbeat or removed physical acknowledgement;
- last robot-side disable, e.g. stale odometry, reported speed, worker delay,
  graph/unique-controller failure or expired heartbeat;
- bounded recent event details, last command round-trip duration, lease and
  camera metadata. No dashboard key/browser owner/generation token is included.

Copy the details after an unexpected event. The hub **Save report** also includes
the backend history; its activity log notices new backend disable records. Browser
events live only in that page; backend history lasts for that server process,
up to twenty events. Restarting processes destroys their in-memory history.

Specific browser reasons previously could be replaced by generic status text;
the new separate panel retains them. A backend idle-fault reason could also be
overwritten by a later Stop; its first disable event is now separately retained.
That is a confirmed observability issue, **not a proven cause of the user's
physical input dropouts**. Native browser drag-start is suppressed on the stick,
but this is not proof that pointer capture/focus/network/feedback faults are fixed.

No heartbeat, stale-data, capture/focus, release/feedback, sequence/owner or
scheduling check is relaxed. There is no automatic re-enable/resume. Normal
release still preserves idle permission after braking; focus/capture/fault Stop
requires deliberate Enable. Moving the stick through zero/reverse still requires
release and a fresh press; nothing is queued through braking.

## Independent throttle and steering

The Layout selector offers the existing **Circular** mapping and optional
**Independent throttle + steering**. Circular normalization reduces vertical
throttle near the side/corners. Independent mode clamps each axis separately:
full up/down remains full requested throttle while full left/right requests
steering. It is one grip rather than two simultaneous sticks, so it works with
a mouse. Its pad is square. Changing layout disables an active session; choose
while stationary, then Enable again. Horizontal-only input still requests zero
travel; no sideways motion or in-place spin.

The ceiling remains **0.10 m/s request**, buttons 0.03, curvature <=1/m. User's
suggestion of 0.20 is **not implemented** while unexplained disable events remain.
Reported-speed guard already stops above |vx|=0.10, |vy|=0.04, |yaw|=0.15; merely
doubling the request would conflict with it, and raising it would obscure diagnosis.
At 0.10, measured overshoot could already trip it. The new reason includes reported
velocity values; use evidence before choosing a new request/feedback envelope.
No physical steering/speed calibration or independent fault-stop test is implied.

## LiDAR colours are data channels, not object recognition

Solid mint remains the default. New selectable views:

- **Raw return intensity**: preserves finite values aligned with valid range
  indices and decimated points. Higher raw values are drawn brighter with the
  current scan's auto-scaled minimum/maximum explicitly labelled. Equal values
  have no intensity contrast. Missing/mismatched/nonfinite values are not
  fabricated; missing points use mint and absent data is labelled unavailable.
- **Distance**: red near zero to blue at 4 m, with the explicit distance legend.
  It does not use intensity or label materials/objects. Display remains clipped
  at 4 m; underlying valid-return statistics use the scan's advertised limits.

[ROS LaserScan](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/sensor_msgs/msg/LaserScan.msg)
defines intensities as device-specific and allows an empty array. RViz colour
depends on the selected transformer/channel/palette and bounds, as shown in its
[official implementation](https://raw.githubusercontent.com/ros-visualization/rviz/melodic-devel/src/rviz/default_plugin/point_cloud_transformers.cpp).
The new dashboard palette is labelled, not an asserted match to the user's
uninspected RViz settings. Brighter in this view means higher **reported value**,
not more absorption, calibrated reflectance, object identity or guaranteed detection.

Copied local source `From Robotics Lab/wheeltec_dev/wheeltec_robot_src/lsn10/src/lsn10.cpp`
lines 375–435 assigns `points[i].intensity` to valid scan returns and zeros invalid/
masked ones, with low nonzero intensity filtering. The copied wrapper defaults
to `ls_N10`. This supports the configured driver path's intensity publication,
not physical label confirmation, equivalence to the currently running binary,
or a live measured intensity distribution. Raw values must be checked on robot.

## Grey RViz maps are a separate next step

An [OccupancyGrid](https://raw.githubusercontent.com/ros/common_msgs/noetic-devel/nav_msgs/msg/OccupancyGrid.msg)
contains occupancy probabilities 0–100 and unknown=-1. In the usual map palette,
grey denotes unknown, white estimated free and black occupied; display settings
can differ. It does not prove terrain is safe or clear at every height. Navigation
costmaps additionally represent obstacles/inflation costs, not raw scan intensity.

This update does **not** create/launch a map, costmap, planner or avoidance.
Next, inspect an actual existing OccupancyGrid topic (often `/map`) and TF/map
frames while stationary before adding a read-only map layer. Scan/camera spatial
association and semantic labels remain the thesis implementation goal.

## Disconnect versus stopping everything

- **Stop driving**: software stop/disable; keeps hub connection and sensors.
- **Disconnect & close** (or X): first release and verify stationary, confirm the
  dialog; the hub attempts Stop and closes its own SSH/tunnel. Remote camera,
  LiDAR, ROS and base can remain running. External reused tunnels are not killed.
- **Finish the day / stop all robot software**: after Stop and a confirmed
  physical standstill, disconnect the hub. In laptop PowerShell connect with
  `ssh wheeltec@192.168.0.100`, then in the robot terminal run
  `sudo shutdown -h now`. Enter the password locally. SSH disconnection alone
  does not prove shutdown finished; let Ubuntu finish and follow the robot's
  normal physical power-off procedure. This does not add a shutdown button,
  remotely cut hardware power or establish firmware stopping guarantees.

If motion is abnormal, use the reachable physical power-off; do not wait for
the app, pick up a moving robot, or treat closing Wi-Fi/SSH as an emergency stop.

## Verification

234 dashboard Python tests, 75 JavaScript checks (55 main fake-DOM, six geometry,
14 historical one-shot), and 44 passing hub tests plus one skipped Windows
symlink-privilege case. Includes persistent reason/history, no automatic resume,
independent axes, intensity alignment/decimation/NaN/constant/missing values,
loading phases and fake localhost encrypted SSH/tunnel tests. JS syntax and
robot Python 3.6 grammar checks pass; not actual Jetson Python 2 execution.
No live robot commands/deployment, GUI focus manipulation or physical motion
by tools. No fresh interactive GUI QA this turn, to avoid interrupting the user's
live browser controls. Real layout, progress timing, dropout cause, intensity
and new turning behaviour still require stationary-first live verification.
