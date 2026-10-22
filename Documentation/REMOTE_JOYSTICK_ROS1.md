# Dashboard v0.3: six directions and joystick

Superseded for current source operation by `REMOTE_DRIVING_SESSION_ROS1.md`
(v0.4, 2026-10-21): enable once per session, no fixed two-second hold cap,
normal release preserves the idle session; Stop/fault still disables. Keep
this document as the v0.3 record and fresh-boot client startup reference.

Prepared 2026-10-21. The user confirmed that the previous integrated forward
control moved the robot slowly and was controllable. This update adds reverse
and steering in the same robot-local page. It has been tested with fake ROS,
local HTTP and a disconnected browser simulation, **not physically tested on
the robot**. The hosted Fieldnotes planner is unchanged.

## How it behaves

- Six buttons: Forward, Left arc, Right arc, Reverse, Reverse L, Reverse R.
  Hold one button; releasing requests stop and disables that hold.
- Joystick: up/down requests forward/reverse travel; left/right adjusts the
  wheel-steering curve. A larger vertical deflection requests more speed, up
  to the unchanged absolute limit of **0.03 m/s**. Small deflections may be too
  weak to move the real motors; do not automatically increase the limit.
- The robot is car-like (Ackermann), not an omnidirectional platform. Horizontal
  joystick input alone requests zero travel/yaw. It cannot drive sideways or
  spin in place. Reverse L means steering the front wheels left while reversing;
  the resulting heading change is opposite to forward-left.
- Joystick input is clamped to a circle, with a 12% dead zone on each axis.
  The knob centres on release, cancellation, lost pointer capture or focus.
  Buttons also support holding Enter/Space while focused; Space elsewhere or
  Escape requests stop. A second touch cannot take over a held control.
- Release before changing between forward and reverse. Crossing between them
  while holding stops and retires the current request; Enable again after
  cleanup/stationary feedback. Steering changes do not extend the hold timer.
- Same **two-second maximum per hold**, **0.35 s command lease** and two-second
  repeated-zero cleanup. New explicit page Enable works without a terminal
  restart once feedback is stationary. Nothing automatically rearms/resumes.
- Existing recent camera, physical odometry/source/graph, unique isolated
  controller, scheduler, request-origin/key/owner/sequence and stale-command
  checks remain. Reverse feedback is now accepted while travelling; opposite
  reported longitudinal travel or excessive reported speed requests stop.
  The first backend stop reason is retained for diagnosis.

The backend requests `linear.x = 0.03 * throttle`,
`angular.z = -linear.x * steering * 1.0` after dead-zone rescaling. Other Twist
components remain zero. This bounds requested curvature to 1/m (requested radius
at least 1 m when turning); it is **not a calibrated physical turning radius**.
The copied senior_akm navigation configuration has nominal 0.750 m minimum radius,
0.322 m wheelbase and Twist yaw-rate input; these are configuration values, not
new measurements or firmware verification. Steering response/sign on this
specific robot still requires direct observation.

## Copy the update once

If the live dashboard is running, release controls, confirm the robot is
stationary, then Ctrl+C **only its dashboard terminal** and wait for cleanup.
Leave the existing camera, isolated base and laptop SSH tunnel running. Do not
copy over a running live dashboard. Preserve the original
`~/fahad/remote_dashboard/` viewer; update only the already-created personal
`~/fahad/remote_dashboard_web_trial/` copy.

In **local Windows PowerShell**, not the robot's SSH shell:

```powershell
Set-Location -LiteralPath 'C:\Users\fahad\OneDrive\Documents\Bachelor Arbeit - Search and Rescue Robot Image Living Classification\Tools\remote_dashboard'
scp .\server.py .\manual_drive.py wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial/
scp .\dist\index.html .\dist\app.js .\dist\joystick.js .\dist\controls.css wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial/dist/
```

These six files extend the existing complete trial copy; unchanged dependencies
`control.py`, `crawl_test.py` and `dist/style.css` must already be there. If SCP
fails, do not start a partially updated version. No internet download is needed:
the files travel over the local robot Wi-Fi/SSH connection.

## Start and use

In a **robot SSH terminal**:

```bash
source ~/wheeltec_robot/devel/setup.bash
python -u ~/fahad/remote_dashboard_web_trial/server.py --ros --drive
```

Expected terminal mode: `ros_manual_ackermann`. Refresh
`http://127.0.0.1:8765/` on the laptop; if needed use Ctrl+F5. The page should say
v0.3 and **Manual driving · buttons + joystick**. Without `--drive` the viewer
remains motor-free/read-only. No services start automatically at robot power-on.

If starting from a fresh boot, start/reuse the existing camera and isolated base
once, in separate robot SSH terminals, before enabling controls:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch darknet_ros yolo_v3.launch
```

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch ~/fahad/remote_dashboard/base_crawl_check.launch
```

The second command uses the existing isolated base launch, not a new vendor
launch or an extra driver alongside one already running. It must provide
`/fahad_base_crawl_check`, `/odom` and the isolated
`/fahad/crawl_test/cmd_vel` subscription. Do not launch duplicate controllers.

If no laptop tunnel exists, run this in another **local Windows PowerShell**:

```powershell
ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 -o ExitOnForwardFailure=yes -o ServerAliveInterval=5 -o ServerAliveCountMax=3 wheeltec@192.168.0.100
```

Do not run that tunnel inside the robot SSH shell: it would occupy the robot's
dashboard port. An existing working tunnel can be reused.

For the first new-direction checks, keep the robot directly visible on a clear
level floor, wheels/steering clear and known normal physical power-off safely
reachable. Confirm current video, acknowledge placement, then Enable. Make one
brief straight reverse request, release and observe the actual stop/direction.
Then check forward-left and forward-right separately before reverse arcs and
joystick. Re-enable on the page after each cleanup; no terminal restart.
If response/direction/stop is unexpected, stop testing and retain the displayed
reason. Do not automatically flip steering signs, increase speed or restart
past a fault. A small gentle curve may be hard to see during a short slow hold.

To see existing object-detection boxes, choose **YOLO detections** in the View
selector while the working darknet node runs. This update does not change the
detector, fuse labels with LiDAR or implement obstacle avoidance.

## Limits, shutdown and rollback

Release/Stop/lease are software requests, not an independent hardware emergency
stop. Firmware/serial/host-failure stopping and the vendor command queue remain
unverified. Do not perform a moving connection-loss experiment. Do not lift a
moving robot or close its camera/tunnel as a stop method; use physical power-off
if abnormal motion requires it. Actual speed, distance and steering are not
guaranteed by requested Twist values or simulated tests. Mobile touch behaviour
is unit-tested but has not been tested on a physical phone this session.

Normal shutdown: stationary robot; Ctrl+C live dashboard and wait for zero
cleanup, then isolated base, then camera/master. Orderly Ubuntu shutdown, verify
it has halted, then main power off; close the laptop tunnel afterward. If only
viewing is needed, stop live mode normally and restart without `--drive`.
The untouched original `~/fahad/remote_dashboard/server.py --ros` remains the
previous viewer rollback. No firmware, vendor configuration, boot, Wi-Fi, models
or maps are modified by this update.

## Local verification

178 Python fake-ROS/loopback tests and 45 JavaScript checks pass (27 main-page,
4 joystick geometry, 14 previous one-shot). Tests cover six signed vectors,
bounded axes/curvature, no sideways/spin, invalid inputs, signed feedback,
opposite-travel guard, hold/lease/cleanup, forward/reverse reversal, origin/key/
sequence and worker-only publication, release/cancel/capture loss, second touch,
blur/reconnect and legacy read-only behaviour. JS syntax and Python 3.6 grammar
checks pass. Python 2 runtime and the new robot directions remain untested.

Disconnected desktop browser QA verifies the six-button/joystick rendering,
acknowledgement gating, Enable, drag/release returning the knob to centre and
disabled state, and same-page re-enable. Synthetic image explicitly states
NO ROBOT CONNECTION; callbacks only print simulated values. This is not a robot
motion/latency/firmware or phone-device test.
