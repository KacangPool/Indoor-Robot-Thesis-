# First supervised browser-forward trial

Progress: user reports first browser pulse moved a tiny amount and confirms it
stopped by itself without power-off. Normal trial is complete, not measured or
fault-stop proof. User requests repeatable main-page operation without terminal
restarts. The new integrated version is described in
`REMOTE_MANUAL_FORWARD_ROS1.md`; it is locally tested, not yet robot-deployed.
The one-shot instructions below describe the preceding version.

Prepared 2026-10-20. **Not yet copied to or tested on the robot.**
The normal `remote_dashboard/server.py --ros` remains read-only. The separate
`web_crawl.py` is default-offline; `--check` only reads the existing isolated
driver/odometry graph. `--live` is a deliberately different physical-output mode,
not a general controller, continuous driving or autonomous navigation.

## What changes and what stays unchanged

- Reuse the working camera/YOLO topics and loopback SSH tunnel, not cloud hosting.
- One terminal-confirmed permission per process, expiring after 60 seconds.
  Prepare in the browser, then hold Forward within five seconds. Only one attempt
  is permitted, even if cancelled/expired; no reconnect/reload replay or retry.
- Fixed intent: forward 0.03 m/s for at most 0.4 seconds from receipt of the
  original browser start, zero steering/lateral, then repeated zero requests for
  two seconds. This is software intent, not measured speed, distance, real-time
  timing, braking or a guaranteed physical stop.
- Release/Stop/blur/hidden/offline requests cancellation. Robot-side heartbeat
  expires after 0.35 seconds, independently of browser UI timers. Commands require
  one owner/token and increasing sequence. Readiness is rechecked before forward
  and each nonzero publication. A delayed worker cannot extend the original
  action deadline. Snapshot and worker guards retire expired permits.
- Existing graph/real-odometry guards are reused from `crawl_test.py`: exclusive
  expected isolated base, recent advancing stationary feedback before starting,
  fresh graph, no competing ordinary/test command publisher. Recent colour-camera
  arrival is required too. During motion, unexpected reported velocity rejects
  further positive output. No camera-LiDAR alignment/obstacle avoidance is implied.
- Browser requires recent status/decoded preview and an active page. Backend
  camera arrival age is not measured exposure or end-to-end video latency.
  Direct physical line of sight remains essential.
- Main server's only refactor is an overridable validated-operation dispatch and
  optional Handler class; its default page and endpoints still have no Publisher.
  New mode serves a separate page rather than silently making rehearsal live.

## Known limits before any actuation

Keep a clear level floor, people/objects/cables clear of the wheels/steering,
directly observe the robot and have its known normal main-power control safely
reachable without lifting. The user previously reported normal forward/self-stop;
today's floor setup is not yet confirmed. Do not grab/lift a moving robot.

Lower-controller firmware timeout, serial backlog and physical stopping after
host/serial failure are **not verified**. A dead/stalled Jetson, blocked publisher
or broken serial link may prevent zeros. Application heartbeat is not an
independent hardware watchdog. Do not intentionally disconnect links while moving.
No increase in speed/duration or continuous/reverse/steering enablement follows
automatically from success. Failure means stop/review, not repeated attempts.

## Staged deployment — wait at each evidence checkpoint

Do not change the current working viewer in place. Use a new personal directory
so its known version remains available. First inspect whether the proposed
destination exists from a ROBOT SSH shell:

```bash
ls -ld ~/fahad/remote_dashboard_web_trial
```

If it exists, inspect it before copying: do not overwrite/nest unknown contents.
If it reports no such file/directory, from LOCAL Windows PowerShell copy:

```powershell
scp -r "C:\Users\fahad\OneDrive\Documents\Bachelor Arbeit - Search and Rescue Robot Image Living Classification\Tools\remote_dashboard" wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial
```

Copying starts no ROS process and issues no motor commands. Source folder includes
tests and existing cached files; they are not needed at runtime and must not be
executed as deployment steps. Do not upgrade Python/ROS/OpenCV or install packages.

Optional first robot-side entry check (no ROS imports/server/publisher):

```bash
python -u ~/fahad/remote_dashboard_web_trial/web_crawl.py
```

Expect `OFFLINE ONLY`. Review errors before proceeding.

### Base and read-only readiness checkpoint

Only after today's clear setup/power-off conditions are confirmed and no base
driver is already running, open another robot SSH shell and use the existing
isolated launch. This opens the physical serial driver and can have hardware
side effects, even though no velocity publisher is started by the launch:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch ~/fahad/remote_dashboard/base_crawl_check.launch
```

Leave running; normal serial-open logging waits for ROS activity, not a command
prompt. In another robot shell:

```bash
source ~/wheeltec_robot/devel/setup.bash
python -u ~/fahad/remote_dashboard_web_trial/web_crawl.py --check
```

Share full readiness output before the live stage. Do not run the old CLI live
pulse as a prerequisite or start mapping/navigation/followers to create topics.

### Live stage — only after reviewed readiness and placement

Keep camera/YOLO, base and laptop tunnel running. Ctrl+C **only the old read-only
dashboard server**, wait for its robot shell prompt, then replace that process:

```bash
python -u ~/fahad/remote_dashboard_web_trial/web_crawl.py --live
```

This binds robot loopback 8765, subscribes and checks readiness first. Refuses
simulated ROS time. Requires foreground interactive exact `CRAWL` confirmation
within 30 seconds; no Publisher exists before successful checks/confirmation.
The terminal authorisation does not itself request motion. Then a queue-size-1,
nonlatched publisher must establish the expected unique controller connection.

After it prints `ONE-SHOT WEB MODE`, refresh the laptop's
`http://127.0.0.1:8765/`. This is a distinct page with a live-motor warning, NOT
the six-direction rehearsal page. Expect a recent preview and a ready state.
Only once ready to physically observe: Prepare one trial, then hold Forward.
Release can shorten the request; holding longer cannot extend the 0.4 s limit.
Stop/Space/Escape requests cancellation; if abnormal, use physical power-off.

Watch both physical movement/stopping and the terminal's outcome. A near-zero
feedback message is not independent physical-stop proof. Share output, direction,
self-stop versus intervention and approximate observation before any further step.
This mode stays spent after one attempt; do not restart merely to repeat it.

## Stop and restore viewing

If stationary, Ctrl+C the web trial and wait for its cleanup/prompt. It attempts
zeros before removing its publisher. Stop base before shutting down ROS master,
following `REMOTE_DASHBOARD_QUICK_START.md`. To restore only the old read-only
viewer once the test process releases port 8765:

```bash
python -u ~/fahad/remote_dashboard/server.py --ros
```

Do not treat browser closure/SSH loss as a physical stop. Preserve logs and vendor
software/maps/settings; no autostart service, GPS changes or firmware writes.

## Development verification

- 102 Python checks pass: 35 new web gate/lifecycle/HTTP checks plus existing
  31 dashboard and 36 crawl regressions. All ROS/actuation is fake; HTTP binds
  laptop loopback only. Initial sandbox socket failures were rerun with approved
  loopback access. A delayed-worker deadline edge found in tests was corrected
  to terminate positive output through health checking, without extending intent.
- 14 new one-shot fake-DOM checks and 12 existing frontend regressions pass.
  Holding a button leaves it enabled to receive native release/capture/key
  events; repeated press cannot request a second forward action.
- Python 3.6 grammar checked for runtime files; actual robot Python 2.7/3.6
  execution and physical browser action have not been tested.
- Non-actuating laptop preview loaded in a real browser; readiness intentionally
  refuses output (`OFFLINE UI CHECK`), controls disabled and live-mode warning
  visible. This checks page rendering, not live hold/release/sensor behaviour.

These checks support staged supervised deployment, not production safety,
independent fault stopping or unrestricted remote driving.
