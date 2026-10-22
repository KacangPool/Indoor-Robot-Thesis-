# Remote dashboard: manual start, stop and moving to the floor

Current source v0.6 (2026-10-21): see `ROBOT_HUB_WINDOWS.md` and
`Tools/robot_hub/README.md` for the native Windows setup hub and 0.10 m/s
joystick request ceiling (buttons remain 0.03). New implementation is not yet
physically tested. The manual version-specific notes below are historical.

Latest source v0.5 (2026-10-21): `REMOTE_JOYSTICK_LIDAR_ROS1.md` adds proportional
joystick requests up to 0.08 m/s (buttons still 0.03), requested-speed readout
and detailed /scan connectivity/data diagnostics. Same enable-once held session,
release/Stop/fault guards. New speed and LiDAR connection not physically verified.
Use that guide for update and bounded stationary ROS checks; do not duplicate
drivers merely because no points appear. Older version notes below are historical.

Latest source (2026-10-21, v0.4): `REMOTE_DRIVING_SESSION_ROS1.md` supersedes
the bounded v0.3 workflow below. Enable once, continuously drive only while held,
release/brief stationary-feedback check then fresh press; no re-enable per normal
hold and no fixed two-second hold cap. Stop/fault disables. Same 0.03 m/s maximum
request. Update only the personal trial copy; new behaviour not physically tested.

Current source update (2026-10-21): v0.3 adds six slow car-like directions and a
joystick in explicit `--ros --drive` mode. See `REMOTE_JOYSTICK_ROS1.md` for the
six-file update into the existing personal trial copy and current startup steps.
The user confirmed the prior integrated forward control moves slowly; the new
reverse/steering directions are not physically tested. Same two-second maximum
hold, 0.03 m/s maximum absolute request, release/cleanup/page re-enable; no
sideways/spin or auto-start. Older forward-only instructions below are historical.

Latest operator update: user confirms first browser one-shot movement/self-stop
on 2026-10-20. Repeatable main-dashboard forward control is now prepared in the
Windows source; `REMOTE_MANUAL_FORWARD_ROS1.md` gives its staged four-file update
and explicit `--ros --drive` startup. No terminal restart between normal holds.
Until that update is copied/run, robot still has the earlier version. Default
`server.py --ros` below remains read-only, not live driving. Do not silently add
the drive flag for a viewing-only session. Boot auto-start is still unconfigured.

## Everyday restart reminder — 2026-10-20

User confirms live colour/YOLO viewing today, but later says the website was
turned off. Exactly which process/window was closed is not established. The
original robot server subsequently reports Errno 98 (port already in use), so
do not assume that it stopped just because the browser no longer opens.

Latest listener evidence: user reports no matching viewer/trial process, and
`ss` shows robot loopback 8765 owned by `ssh`, PID 8307. The original dashboard
still cannot bind. Inspect `ps -p 8307 -o pid,ppid,args` before stopping it. This
is consistent with a forwarding client started on the wrong computer, not a
running dashboard. PID is session-specific, not a reusable everyday kill target.
Separately, copied trial script's default OFFLINE entry now runs on robot; live
mode/ROS and browser actuation remain untested.

Follow-up: user supplied `ps` showing PID 8307 / PPID 8083 is exactly the robot-side
`ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 ...` client. For this identified session,
request normal `kill -TERM 8307`, verify the robot listener is gone with `ss`,
then restart the original `server.py --ros`. This is a single known misplaced
forwarder, not SSH daemon termination or a permanent startup step. Keep the
camera running and create/reuse the actual tunnel only in Windows-local PowerShell.
Cleanup and restored viewing are not yet confirmed.

The three separate pieces below are required: robot camera/YOLO, robot dashboard
server and laptop SSH tunnel. Closing a browser tab stops none of these by
itself. A real computer shutdown stops its processes; reopening PowerShell does
not restart them. A lost SSH connection does not prove its remote process exited.

For this CURRENT bind-error case, from a robot SSH shell first inspect:

```bash
pgrep -af 'remote_dashboard/server.py|remote_dashboard_web_trial/web_crawl.py'
ss -ltnp 'sport = :8765'
```

These do not start/stop programs or issue motion. Read the process/listener
output before choosing reuse versus stopping a specific known process. Do not
kill all Python/ROS processes or reboot merely to free the port. Do not start
camera/base duplicates. A listener on the robot and the laptop-local SSH tunnel
can both use 8765 because they are on different computers; two listeners on the
same local address/port cannot.

For a normal fresh robot boot with no matching processes, follow Terminal A/B/C
below. Start the camera/YOLO wrapper once, the original `server.py --ros` once,
then the tunnel directly in a Windows-local tab. If one piece is already running,
reuse it after checking its identity instead of starting it again. Keep all three
tabs open. On the laptop open `http://127.0.0.1:8765/`, then View → YOLO labels.
This starts viewing only, not the separate base driver or web movement trial.

If just the browser was closed, reopen that link. If just the tunnel was stopped,
restart Terminal C. If the dashboard server was stopped and its port is actually
free, restart Terminal B. After full robot shutdown/reboot, check and restore all
three. Current listener conflict must be resolved by evidence, not assumed away.

Current status, 2026-10-19: user has demonstrated robot-hosted colour and YOLO
viewing in a laptop browser. Driving is rehearsal-only. **Automatic boot is NOT
configured. Opening PowerShell alone does not start camera/YOLO or the dashboard.**
No full power-on-without-monitor test has been completed. Keep monitor/keyboard
available as a recovery option for the first such test.

## Before unplugging or lifting

- Monitor/video cable and an external keyboard/mouse are display/input
  peripherals, not the camera or computer power connections. Do not treat all
  cables as removable. Leave camera, LiDAR, motor/controller and computer/battery
  connections intact unless a specific powered-down lab procedure requires it.
- Before lifting/repositioning, use the verified motor-inhibit/physical-stop
  procedure; if uncertain, ask lab staff. This project has not identified or
  tested that mechanism. Dashboard Stop/Ctrl+C/Wi-Fi loss are NOT physical stops.
- For a powered-down move: Ctrl+C the camera/YOLO launch and dashboard in their
  respective robot SSH terminals. In a remaining robot shell, request orderly
  computer shutdown with `sudo shutdown -h now` and enter credentials locally.
  SSH will disconnect. Wait for the computer to finish shutting down using the
  lab's normal confirmation procedure, then switch robot power off before lifting.
  Do not abruptly pull computer power while Ubuntu is running. No shutdown is
  executed by preparing these instructions.
- Place securely on a clear level floor, do not move the camera mounting/tilt,
  and check cable slack before powering up. Moving it to the floor is not approval
  for live driving or a substitute for verifying motor/controller safeguards.

## After power-on: manual startup currently required

Keep robot stationary. Join the established WHEELTEC Wi-Fi from the laptop.
No internet is needed for this local connection. Use the separate permitted
internet/chat connection if required. Address below was observed in the robot
report and used for successful manual viewing; if it changes, inspect actual
network state rather than guessing a new address or editing network settings.
Use the already-verified SSH identity; stop on unexpected host-key changes.

### Terminal A: camera + YOLO

In LOCAL Windows PowerShell:

```powershell
ssh wheeltec@192.168.0.100
```

Once the prompt is `wheeltec@wheeltec:~$`, commands run on the robot:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch darknet_ros yolo_v3.launch
```

Leave running. This known wrapper includes the camera and normally creates its
local ROS master if absent. Don't start another camera, roscore, base, mapping,
navigation or follower launch. If services are already running after boot, inspect
before duplicating them. No desktop camera window is required for browser viewing.

### Terminal B: dashboard

In a NEW local PowerShell tab:

```powershell
ssh wheeltec@192.168.0.100
```

Then, in that robot shell:

```bash
source ~/wheeltec_robot/devel/setup.bash
python -u ~/fahad/remote_dashboard/server.py --ros
```

Leave running. Expect `Mode: ros_read_only` and motor output not implemented.
Only one dashboard may occupy port 8765; don't start a second preview copy.

### Terminal C: secure webpage tunnel

In another LOCAL PowerShell tab (not inside SSH):

```powershell
ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 -o ExitOnForwardFailure=yes -o ServerAliveInterval=5 -o ServerAliveCountMax=3 wheeltec@192.168.0.100
```

Leave the quiet tunnel running, then open `http://127.0.0.1:8765/` in the laptop
browser. Select Colour camera or YOLO labels. Enter all login credentials locally;
do not send passwords in chat or store them in scripts. Files remain on the robot
after shutdown, but the running programs and tunnel do not automatically return.

## Stop and shutdown

### End of the 2026-10-19 base-test session

User is stopping for the day after reporting a tiny forward movement followed
by self-stop. Dashboard remains motor-free, but the separate base-driver launch
may still be running. No more movement tests are needed for shutdown.

1. Confirm robot is stationary. In the terminal showing the base launch / serial
   port opened, press Ctrl+C ONCE and wait for the robot shell prompt to return.
   Stop this driver before the camera/YOLO launch that may own the ROS master.
   Normal driver cleanup attempts zeros; this is not a guaranteed emergency stop.
   If robot is moving abnormally, use the accessible power-off fallback instead
   of relying on terminal cleanup or lifting it.
2. Ctrl+C in the dashboard/server terminal; wait for its prompt.
3. Ctrl+C in the camera/YOLO launch terminal; wait for its prompt.
4. In a ROBOT SSH shell (prompt `wheeltec@wheeltec:~$`), request orderly Ubuntu
   shutdown with `sudo shutdown -h now`. Enter password locally. Do not run that
   command in a Windows-local prompt or assume closing the SSH window shuts down
   Ubuntu. If the command reports an error, inspect it before removing power.
5. SSH disconnection is expected, not proof the computer has finished halting.
   Allow roughly a minute for shutdown and confirm completion using the robot's
   normal local procedure before switching main power off. If completion is in
   doubt, retain power and check locally; do not equate a dropped Wi-Fi link with
   completed shutdown. Do not lift/reposition before computer shutdown and power
   removal. Then close browser/tunnel/remaining PowerShell tabs (Ctrl+C in the
   quiet tunnel tab if it has not exited).

This is an instruction for the user, not a tool-executed shutdown. No boot service
is configured: next time requires the manual camera/dashboard/tunnel start. Start
the isolated base only when the next reviewed test requires it; do not rerun the
crawl merely to restore viewing. Files remain saved across shutdown.

For viewing-only sessions without the base launch, omit step 1's driver stop.
Do not assume a remote process always exits cleanly on network/terminal loss;
check state before restarting. Closing a browser/tunnel is not a motor stop.

## Before actual movement

Latest update 2026-10-19: user confirms the normal main-power control turns the
robot off and is reachable on the floor without lifting. This answers the normal
use/access question, not circuit isolation, emergency-stop certification or a
firmware watchdog. A stand/specific staff member is not categorically required.
Current next step is the separate isolated driver startup and no-publisher
feedback check in `BASE_DRIVER_FIRST_CHECK.md`, with clear controlled placement
and reachable power-off. Review actual outputs before any live pulse. The
dashboard itself remains motor-free; new CLI default is offline, not automatic
driving. No physical/ROS test of the new files or automatic boot has occurred.

Update after user says staff are unfamiliar: we can investigate the driver/live
interfaces ourselves. See `MOTION_READINESS_2026-10-19.md` for copied-code findings
and read-only controller/node/topic checks. Verified stopping and an appropriate
controlled test setup remain required; staff availability does not justify a
floor-driving experiment with unknown command-loss behavior.

Earlier user proposed picking up the robot before turning it off; the latest
normal power-off/access answer supersedes that proposed method. Do NOT use lifting/catching
a moving or powered-drive robot as the stopping procedure: wheels/steering can
continue moving while handled. No live motion test until a safe independent stop
and supervised lab procedure are established.

Existing actual-robot photo
`Picture of Robot/Documentation/photo_2026-08-17_10-03-33.jpg` shows a readable
label `主电源开关` (main power switch) above a large round metal control. This is
evidence of a labelled main-power control, not verified motor-only isolation,
circuit behavior or a safety-rated emergency stop. The user's normal-use answer
is now recorded, while fault stopping still needs verification;
do not guess the functions of neighbouring buttons or alter wiring. The photo
also contains unrelated credentials: do not copy those into reports or reproduce
the full image merely to discuss the switch.

Need to identify and verify the physical stop/motor inhibit, live base/serial
health, competing command publishers and lower-controller stale-command timeout.
Then implement and test a separate gated low-speed control path in a supervised
clear indoor area. Existing page cannot send motor commands. Neither YOLO nor the
laser display automatically prevents collisions.

Automatic boot is a later reviewed configuration/test stage: network + selected
perception/dashboard services may start, but motion must stay disabled after boot,
disconnect and restart. No autostart service has been written or enabled.
