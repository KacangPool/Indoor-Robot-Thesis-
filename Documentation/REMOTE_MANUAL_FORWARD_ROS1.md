# Main dashboard: repeatable supervised forward holds

Superseded for current operation on 2026-10-21 by `REMOTE_JOYSTICK_ROS1.md`:
main v0.3 now implements six car-like directions plus joystick at the same speed/
hold limits. That guide lists all six changed deployment files. Keep this guide
as the forward-only milestone record, not the current complete update procedure.

End-of-session live update (2026-10-20): user reports this integrated dashboard
now moves the robot and works well, with a short hold estimated around one
second. This supersedes the not-yet-deployed/run wording in the original build
verification below for basic forward operation only. Actual duration/speed/
distance are unmeasured; configured command cap is two seconds and no tuning is
made. Updated-mode release-to-stop and page re-enable were not separately reported.
Prior one-shot self-stop is independently user-confirmed. User stops for today;
next session inspect page stop reason and verify hold/release/re-enable before
further directions. Shutdown completion remains unreported.

Prepared 2026-10-20 after user confirms the first browser pulse produced tiny
movement and stopped by itself without power-off. That is normal-case physical
evidence, not measured speed/distance or independent failure stopping. The user
wants to work from the actual dashboard without per-action terminal restarts.

## What this version does

- Same familiar camera/YOLO/LiDAR dashboard and local URL. Live mode starts once
  with explicit `--ros --drive`; `server.py --ros` remains read-only.
- No `CRAWL` prompt, 60-second terminal permit, five-second Prepare window or
  one-action-per-process restriction in this integrated mode.
- Check the physical-setup acknowledgement, click **Enable forward controls**,
  then press and hold the **Forward** arrow. Release, Stop, Space/Escape, lost
  focus, hidden page, lost/expired heartbeat or stale preview/status requests
  software stop. Normal release disables the current token immediately.
- Backend attempts zeros for two seconds, then requires fresh stationary
  feedback. The same page then allows a new explicit Enable without restarting
  its process. Reconnecting/refreshing never restores a held request.
- Forward request remains **0.03 m/s**; the maximum per-hold intent is **2 s**.
  Holding longer disables that attempt rather than extending motion. This is a
  deliberate increase from the earlier 0.4 s one-shot request, not a calibrated
  physical speed, distance, timing or stopping guarantee. No arbitrary speed,
  duration, topic, shell or launch endpoint exists. Reverse/steering stay disabled.
- Single owner/generation, increasing sequences, monotonic 0.35 s lease, worker
  scheduling guard, fixed rate/bounds, fresh camera/graph/real odometry and unique
  isolated controller checks remain. The worker publishes; HTTP only changes
  intent. A two-second hold cap does not constitute a hardware watchdog.

## Physical scope and known stopping limit

Directly supervised clear, level floor only, people/objects/cables clear of the
wheels/steering and known normal main-power control safely reachable. Watch the
robot directly; camera preview is capped at 3 Hz and not validated for video-only
driving. No obstacle avoidance, autonomous navigation or outdoor readiness.

The controller may retain a command if the Jetson stalls/dies or serial fails.
Firmware timeout, queue/backlog behavior and independent fault stopping remain
unverified. Browser release alone cannot guarantee physical stopping. Use normal
physical power-off if abnormal; do not lift/catch a moving robot. No moving
communications-loss or forced-crash test is proposed. Do not equate confidence
in manual operation with fault-stop proof. Failed zero publications block re-enable
pending inspection; not every fault is recoverable with a page click.

## Update the known personal copy, preserving the old viewer

The user already copied a complete personal trial folder and ran its default
offline/readiness/live one-shot entries. This update targets that known folder
only; original `~/fahad/remote_dashboard` remains the rollback viewer.

1. Robot stationary: in the terminal running the old `web_crawl.py --live`,
   Ctrl+C once and wait for cleanup/prompt. Keep camera/master, isolated base
   launch and laptop-local SSH tunnel running. Do not stop the master first.

2. In LOCAL Windows PowerShell (`PS C:\...>`, not a robot SSH shell):

   ```powershell
   Set-Location -LiteralPath "C:\Users\fahad\OneDrive\Documents\Bachelor Arbeit - Search and Rescue Robot Image Living Classification\Tools\remote_dashboard"
   scp .\server.py .\manual_drive.py wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial/
   scp .\dist\index.html .\dist\app.js wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial/dist/
   ```

   Wait for each successful completion. Do not start a partially copied version.
   No additional packages/Python/ROS upgrades, vendor edits or boot changes.

3. In the available ROBOT SSH shell:

   ```bash
   source ~/wheeltec_robot/devel/setup.bash
   python -u ~/fahad/remote_dashboard_web_trial/server.py --ros --drive
   ```

   Expect `Mode: ros_manual_forward | LIVE MOTOR CAPABILITY`. Startup alone does
   not request motion. Leave this process running; no per-hold terminal restart.

4. Refresh `http://127.0.0.1:8765/` in the laptop browser. Verify the live warning,
   current camera image, **Manual forward control**, acknowledgement checkbox and
   **Enable forward controls**. Other arrows intentionally remain unavailable.
   Check the physical conditions, enable and use one brief hold/release for the
   first updated-version verification. Observe stopping and the displayed reason;
   report an error/abnormal motion rather than continue repeatedly.

After observed normal stopping in this version, ordinary operation is Enable →
hold → release → wait for cleanup/feedback → Enable again on the page. No blind
hardware iteration, speed escalation, automatic retry or latch-to-run behavior.
Application faults still require inspection before more motion.

## Next boot and shutdown

The camera/YOLO launch, isolated base launch, live dashboard and laptop tunnel
still require manual startup once per session, unless already running. There is
no new boot service. Preserve robot-versus-laptop prompt distinction; the tunnel
must run on Windows, not robot loopback. Existing quick-start covers camera,
tunnel and orderly shutdown; the isolated base must also be present for live
readiness. No duplicated base/master/camera processes.

On shutdown, stationary robot: stop the live dashboard and wait for zero cleanup,
then base, then camera/master; orderly Ubuntu shutdown before main power-off.
If abnormal physical movement occurs, power-off fallback takes precedence over
software cleanup. Closing the browser or tunnel is not a physical stop.

Rollback (after stopping this live server and, for viewing only, its base):

```bash
python -u ~/fahad/remote_dashboard/server.py --ros
```

## Verification and status

- 142 Python checks pass: 40 new manual control/adapter/lifecycle/HTTP checks plus
  102 earlier dashboard/one-shot regressions. ROS is fake; HTTP is laptop loopback.
- 21 main-page fake-DOM checks (12 existing + 9 live-mode checks) and 14 separate
  one-shot fake-DOM regressions pass. JS syntax and runtime Python 3.6 grammar
  checked; robot Python 2 execution of the updated version is not yet tested.
- Tests cover fixed requests/cap, release/zero tail, deliberate repeated Enable
  without restarting, post-stop stationary feedback, stale/retired generations,
  sequence/owner faults, no auto-resume, scheduler gaps, camera/graph/odometry
  failures, transport errors, default motor-free mode and explicit opt-in cleanup.
- Lock-order regression prevents dashboard status holding the image lock while
  taking a drive-control lock. Slow health checks cannot enqueue late positives.
- Actual browser QA against a clearly labelled simulated JPEG/no-ROS callback
  verifies acknowledgement gating, Forward-only Enable, 600 ms hold/release,
  cleanup and a second Enable in the same server, then Stop. This is not a robot
  result. Old one-shot normal self-stop is user-confirmed; the updated integrated
  version is locally verified, not yet deployed/physically verified.

Remaining work: robot-side updated mode validation, independently characterised
failure stopping and separately reviewed steering/reverse integration. The main
thesis camera-LiDAR association/map/evaluation work remains unchanged.
