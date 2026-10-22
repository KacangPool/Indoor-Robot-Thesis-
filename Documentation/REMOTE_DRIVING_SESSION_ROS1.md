# Dashboard v0.4: enable once, drive while held

Current v0.5 source is documented in `REMOTE_JOYSTICK_LIDAR_ROS1.md`: same
session semantics, joystick ceiling raised to 0.08 m/s, buttons still 0.03 m/s,
and detailed live /scan diagnostics. This file retains the v0.4 milestone and
does not describe the latest joystick ceiling.

Prepared 2026-10-21 after the user reports every direction works and requests
continuous held driving without clicking Enable after each release. This report
is normal-case user observation, not measured speed/steering or independent
failure-stop verification. The new session behaviour is locally tested, **not
yet deployed or physically tested on the robot**.

## What changes

- Acknowledge placement and Enable once. Enable disappears during that session.
  Hold an arrow or drag the joystick to request continuous slow travel. There
  is **no fixed two-second hold cap** in this new session profile.
- Release requests zero and centres the joystick. The session stays enabled.
  A brief neutral phase requires at least 0.15 s and three fresh near-zero
  physical odometry samples received strictly after release. When ready,
  press again; no additional Enable or terminal restart. The exact pause can
  be longer depending on feedback. An input pressed while stopping is discarded,
  not queued for later; release and make a fresh press when ready.
- Forward/reverse sign changes while holding, or joystick travel returning to
  zero, enter this same neutral/feedback phase and retire the current hold.
  No automatic reverse or restart as a held joystick crosses the centre.
  Release before reversing. Steering within the same travel direction remains
  adjustable without releasing or resetting the session.
- Stop / disable, Escape, Space outside a direction button, lost focus, hidden
  page, offline/restart, camera/status/odometry/graph faults, cancelled touch,
  unexpected pointer-capture loss or expired heartbeat disable the session.
  Recovery requires explicit Enable again, never automatic resumption.
- Maximum absolute requested speed remains 0.03 m/s, curvature at most 1/m,
  no sideways travel or zero-speed spin. Joystick dead zone stays 12% per axis;
  small deflections may not overcome real motor starting friction. No speed boost.
- Same 0.35 s lease, scheduler/unique isolated controller/source/sequence/key/
  origin checks. Backend worker publishes; web handlers only change intent.
  Fault/Stop still attempts a two-second zero tail. Normal braking that cannot
  confirm stationary feedback within two seconds faults/disables. Failed zero
  publication blocks further Enable pending inspection.

Each press has its own monotonic motion ID, distinct from the session generation
and command sequence. Release retires that motion ID. Older/in-flight/out-of-order
requests cannot undo a release, and a new press is required after a normal stop.
Release can overtake a pending held command; obsolete responses cannot reinstate
the UI hold or cancel a newer successful release. Initial button intent is sent
immediately rather than waiting for the next 100 ms browser heartbeat. Output
is still worker-scheduled, not a guaranteed response to every short tap.

## Why a press sometimes shows no movement

Cause is not confirmed from the user's report. The old cap explains ending a
hold at two seconds, not necessarily no initial movement. A tap released before
worker publication can correctly yield only zero; a small joystick deflection
requests even less than 0.03 m/s and may not start real motors. Waiting for
feedback, stale images/status, scheduling or another guard can also inhibit it.
Read the displayed reason if it recurs; do not assume the timer or silently
increase speed. This update improves request timing and removes the fixed cap,
not a claim to have diagnosed or fixed the actual physical cause.

## Update the already-running robot

1. Release controls and confirm the robot is stationary. Ctrl+C **only the live
   dashboard terminal**, wait for cleanup and shell prompt. Leave camera/YOLO,
   isolated base and laptop tunnel running. Do not copy into a live process.
2. In **local Windows PowerShell** (not the robot SSH shell), copy the runtime
   update into the existing complete personal trial copy:

```powershell
Set-Location -LiteralPath 'C:\Users\fahad\OneDrive\Documents\Bachelor Arbeit - Search and Rescue Robot Image Living Classification\Tools\remote_dashboard'
scp .\server.py .\manual_drive.py wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial/
scp .\dist\index.html .\dist\app.js .\dist\joystick.js .\dist\controls.css wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial/dist/
```

Both transfers must succeed before startup. Six files are included for a complete
UI update, though controls.css is unchanged in this revision. Existing control.py,
crawl_test.py and dist/style.css remain required. Keep the original
`~/fahad/remote_dashboard/` viewer unchanged as rollback. Do not reinstall or
upgrade the robot ROS/Python environment.

3. In the **robot dashboard SSH terminal**:

```bash
source ~/wheeltec_robot/devel/setup.bash
python -u ~/fahad/remote_dashboard_web_trial/server.py --ros --drive
```

Terminal retains mode `ros_manual_ackermann`, now also prints enable-once/no
fixed hold cap. On the laptop refresh `http://127.0.0.1:8765/` with Ctrl+F5;
look for **v0.4** and enable-once instructions. Older frontend + new backend
cannot drive without the new motion ID; refresh rather than bypass validation.
For a fresh boot, use the camera/base/tunnel startup in REMOTE_JOYSTICK_ROS1.md;
do not duplicate already-running clients. Default `--ros` remains read-only.

## First normal session check

Directly observe the robot on a clear level floor, with people/cables clear and
known normal physical power-off safely reachable. Enable once; make a brief
straight hold and release. Confirm physical stopping, then make another fresh
hold after the controls become available, without Enable. Only after normal
release/repeat is observed, check a supervised hold longer than two seconds and
release. Stop if direction, stopping or displayed health is abnormal; retain the
reason rather than restarting past a fault. No moving link-loss experiment.

Continuous means **held input with fresh heartbeats**, never click-to-latch
motion. Removing the fixed cap permits longer requested travel; it does not
establish a hardware watchdog. Release/Stop are software requests and cannot
guarantee stopping after host, firmware, serial or command-backlog failure.
The screen Stop is not a physical emergency stop. Use physical power-off if
abnormal motion requires it; do not lift a moving robot or close its camera/
tunnel as a stop method. Firmware/queue/failure stopping remains unverified.

Normal shutdown remains: stationary robot; Ctrl+C dashboard/wait zero cleanup,
then base, then camera/master; orderly Ubuntu shutdown and verified halt before
main power-off. No boot, firmware, vendor driver, Wi-Fi, model, map or hosted
planner changes. Original forward-only and bounded Ackermann classes remain
for legacy tests; the explicit ROS live adapter selects ManualSession now.

## Verification boundary

208 Python fake-ROS/laptop-loopback tests and 60 JS checks pass (42 main page,
four joystick geometry, 14 old one-shot). Tests include a healthy simulated
15-second hold, six-second hold through HTTP, release/reverse under the same
session, post-release physical sample timing, Stop/lease/health/zero failures,
motion/sequence replay, delayed requests, initial centred joystick, fresh-press
requirement, keyboard/capture/blur/reconnect and read-only/legacy regressions.
Python 3.6 grammar and JS syntax checks pass. Python 2 runtime, real phone and
v0.4 robot behaviour remain untested; automated GUI interaction was not repeated
on the user's live robot page. A separate laptop-only synthetic-image preview
was served successfully; native preview handoff was queued, not confirmed opened.
