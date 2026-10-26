# Fahad robot dashboard — first version

## Latest source v0.15 — sensor-first layout and honest beam shading (2026-10-26)

Large camera left; LiDAR above controls; compact readings right. Desktop preview
stretches to fill without changing source pixels. Scan-only grey unknown cells
and individual valid-beam sectors are not a saved occupancy map or driving
clearance. No guessed car heading in laser coordinates; map car still requires
fresh body TF. Same 17-file runtime, no new dependencies or motor changes; limit
remains 0.30 m/s, not the requested 0.50. See
`Documentation/REMOTE_SENSOR_LAYOUT_V015.md` for update steps, evidence and limits.

## Previous source v0.14 — validated ordinary settings (2026-10-22)

`dashboard_config.json` separates preview/robot JPEG refresh settings; a strict
size/type/schema/key validator rejects invalid input before ROS/server startup.
Defaults remain 3 FPS, loopback and port 8765; no settings can enable ROS/driving,
alter motion limits or provide arbitrary commands. Existing explicit CLI overrides
remain bounded. Keep all **17** runtime dependencies together through the Hub.
No robot deployment or live compatibility claim. See
`Documentation/QUALITY_WORKFLOW.md` for configuration, one-command checks and
the continuing Windows HTTP-test limitation. Driving logic is unchanged.

## Previous source v0.13 — reusable modules (2026-10-22)

Sensor calculations, state, ROS subscriptions and browser scan/map drawing now
have separate modules. Existing `server.py` commands/imports and HTTP routes are
preserved; motion profiles, limits and guards are unchanged. Copying just the new
server is insufficient: keep all runtime dependencies together. The Hub's fixed
15-file installer includes them. No robot installation was performed here.

See `Documentation/MODULAR_CODE_ARCHITECTURE.md` for the layout and full checks,
including the latest 254/255 dashboard result (one existing Windows HTTP abort),
122 dashboard JS checks and the outstanding live-robot/Python-version limits.
The actual connected-Hub /scan check still received no messages; refactoring the
display does not fix that stream. No /map publisher or fusion implementation added.

## Previous source v0.12 — plain coloured LiDAR plane (2026-10-22)

See `Documentation/REMOTE_PLAIN_LIDAR_V012.md`. Scan-only view has no decorative
radar rings/crosshairs/axis labels. Fixed point colours show distance from laser:
red 0 m → blue 4 m, not object types. Map overlays carry source ranges so colours
do not depend on map origin. Actual occupancy shading retained when `/map` exists;
no map still means labelled scan-only. User reports no /map publishers; /scan has
/lsn10 registered but no messages during a Hub-closed check. Recheck while connected
before diagnosing or launching another driver. Controls/speed/guards unchanged.
251 Python +116 JS checks pass, 44 Hub pass/one skip; disconnected visual QA only.

## Previous source v0.11 — A/D steering and read-only map view (2026-10-22)

See `Documentation/REMOTE_KEYBOARD_MAP_V011.md`. W/S travel; A/D held steering,
release centres, A+D centres, steering alone never starts travel. Desktop mouse
steering disconnected; no selectable legacy layouts/scan colour modes. Sidebars
narrower, camera/map centre wider. `/map` OccupancyGrid is read-only and optional;
map car/scan overlays require valid fresh TF. No map => labelled scan-only fallback,
not fabricated free floor. No mapping/navigation stack is launched automatically.
Input capped at 1,000,000 map cells and conservative 256x256 display.
Requested .40 speed deferred: new video shows yaw=.379 at vx=.176 and a later
command timeout. .30 ceiling and all feedback/failure limits remain unchanged.
Local tests/visual fixture only; robot integration and actual map publication
must be checked. Native Hub remains Windows-only; phone secure access unconfigured.

## Previous source v0.10 — recording HUD and 0.30 m/s S-curve (2026-10-22)

See `Documentation/REMOTE_COCKPIT_V010.md`. Desktop: readings left, framed camera
centre with LiDAR beneath it, controls right, in one viewport workspace. Details
expand/scroll inside side panels; narrow screens stack. Held pedals/keys now
request a five-second smoothstep ramp to .30 m/s (not a logarithm); opposing-key
deceleration remains .08 m/s/s. Release/B/Stop request zero without easing. Direct
drag layouts also have a .30 ceiling, but no S-curve. Six buttons stay .03.
Live-session feedback envelope is now |vx|<=.32, |yaw|<=.35, |vy|<=.04, with
provisional headroom, not calibrated safety limits. Historical feedback defaults
stay .12/.15. Other freshness/lease/owner/release/recovery checks retained.
One full 239-test fake-ROS Python run and 107 JS checks pass; later repeats show
an intermittent Windows loopback abort in unchanged HTTP-denial tests (details
in the v0.10 guide); changed speed/LiDAR checks pass separately. A visual fixture was
inspected at 1280x720: no page overflow, visible camera, scan, steering and Stop.
No robot deployment or new-speed/stopping validation performed. Close old tabs
before updating through Hub; verify one new v0.10 console while stationary.

## Previous source v0.9 — ramped travel and fresh-press Enable (2026-10-22)

See `Documentation/REMOTE_RAMPED_PEDALS_V09.md`. No slider: held travel ramps
0→.10 request, opposite key decelerates to zero with no automatic reversal or
cruise. Fresh held press can Enable when checked/healthy/stationary; cancelled,
stale, held-through-fault and pre-readiness inputs cannot queue/resume. Browser
Stop/Space/Escape locks this shortcut; explicit Enable/tick cycle unlocks without
starting motion. Command cap .10 retained; reported longitudinal guard .12 with
explicit headroom after recorded -.102. .30 not implemented. Backend rejection,
timeout and network errors distinguished. Inactive pages no longer automatically
issue global Stop; automatic cleanup owner/generation-scoped, operator Stop global.
238 fake-ROS Python +103 JS checks pass; no robot deployment/physical proof.

## Previous source v0.8 — separate held travel and steering (2026-10-22)

See `Documentation/REMOTE_PEDALS_STEERING_ROS1.md`. Fresh page defaults to
Pedals + steering: hold W/↑ or S/↓, mouse steers only; held touch pedals plus
second-finger steering also supported. B/on-screen Brake requests zero and blocks
travel until released and a fresh press; Space/Escape disable. Normal travel
release preserves healthy session/steering grip. Normal steering release centres
it while a valid held travel pedal continues. No automatic fault re-enable or
checkbox-only latch. Prominent retained stop reason beside Enable. Speed setting
.03–.10 m/s (default .06), guard/curvature/lease unchanged. 235 fake-ROS Python
and 90 JS checks pass; actual dropouts not diagnosed or physically fixed by proof.
No robot deployment/live motion or new GUI focus changes by tools. Sites local
workflow retained; vendor software, LiDAR/map scope and hosted planner untouched.

## Previous source v0.7 — working indicator, diagnostics, independent axes, intensity

See `Documentation/ROBOT_HUB_V07_OPERATING_NOTES.md`. Hub activity is visible
with an indeterminate bar, step and elapsed time. The browser retains separate
last local/backend disable reasons with bounded history; generic polls/Stop do
not erase those records. Independent-axis layout is optional and configuration
changes stop the session. LiDAR preserves optional raw intensities with honest
availability/scaling; no object classes/absorption/map are inferred. Ceiling
stays 0.10, buttons 0.03, existing guards unchanged; 0.20 suggestion deferred.
234 Python and 75 JS checks pass; live deployment/dropout cause/new behaviour
not verified. Read-only/default and original rollback remain. Hosted planner
unchanged. v0.6 entry below is historical.

## Latest source — Windows hub and 0.10 m/s joystick (2026-10-21, v0.6)

`Tools/robot_hub/Start Robot Hub.cmd` opens the new native setup/status hub.
See `Tools/robot_hub/README.md` and `Documentation/ROBOT_HUB_WINDOWS.md`.
The hub checks/reuses/starts the established services, updates only the personal
trial dashboard with backups/checksums and sets up an SSH tunnel. Browser views
remain; no hardware camera settings, public hosting or automatic movement added.
Joystick maximum request is now 0.10 m/s; buttons stay 0.03. Feedback guards
remain unchanged. Source tested offline, not deployed/physically tested by tools.
227 Python and 69 JS checks pass. Older entries below describe historical versions.

This is the first local operator-interface prototype, created 2026-10-15.
It is separate from WHEELTEC's original software. It is **not yet a complete
remote-driving or power-on-to-browser system**.

## Previous update — joystick speed + live LiDAR diagnostics (2026-10-21, v0.5)

Session joystick now scales to 0.08 m/s maximum request instead of 0.03; small
pulls remain slow and six buttons remain 0.03 m/s. Requested-speed readouts are
not physical measurements. Existing feedback thresholds/lease/release/Stop and
enable-once session retained; no speed boost at the dead zone or latched motion.
LiDAR panel already reads /scan; it now distinguishes local connection, waiting,
live/no-valid-ranges, invalid/stale and multiple-source states, with raw arrival
rate, source/frame/counts and bounded plotting. Sensor display only: no driver
launch from browser, obstacle avoidance, alignment, object labels or map.

See `Documentation/REMOTE_JOYSTICK_LIDAR_ROS1.md` for six-file copy/start and
stationary LiDAR diagnostics. User's "no output" report is inconclusive, not
proof of absent LiDAR. 227 fake-ROS/loopback Python and 67 JS checks pass; new
physical speed/LiDAR/runtime not verified. Sites guidance keeps this robot-local;
vendor/firmware/network/planner unchanged. Default viewer is still motor-free.

## Previous update — enable-once held driving (2026-10-21, v0.4)

User reports every direction works and requests continuous held driving without
re-enabling between presses. Explicit `--ros --drive` now selects ManualSession:
Enable once, hold to drive, release to zero/brief stationary-feedback check,
then a fresh press. Enable is hidden during that session. No fixed two-second
hold cap; maximum absolute request remains 0.03 m/s. Stop/fault/focus/connection
loss disables and requires Enable again. No latched motion, speed boost,
sideways/spin or independent firmware failure-stop claim. New behaviour is
locally tested, not robot-tested/deployed by tools.

See `Documentation/REMOTE_DRIVING_SESSION_ROS1.md` for copy/start, exact behaviour
and first release/repeat checks. 208 Python fake-ROS/loopback and 60 JS checks
pass. v0.3 below is the historical bounded-hold version. Sites guidance keeps
this robot-local; Fieldnotes/vendor/boot/network/models/maps are unchanged.

## Previous update — six directions and joystick (2026-10-21, v0.3)

The main page now offers six slow car-like directions and a pointer joystick in
explicit `server.py --ros --drive` mode (`ros_manual_ackermann`, page v0.3).
Same maximum absolute speed request 0.03 m/s, two-second hold cap, command lease,
release-to-stop, stationary feedback and page re-enable without terminal restart.
No sideways/spin, auto-resume or verified firmware failure-stop claim. Reverse/
steering are locally tested, not yet physically verified. Default viewer remains
motor-free. Sites guidance kept this in the robot-local dashboard; the hosted
Fieldnotes planner and vendor software are unchanged.

See `Documentation/REMOTE_JOYSTICK_ROS1.md` in the Windows project for the six-file
copy into the existing personal trial folder, startup and first direction checks.
178 Python fake-ROS/loopback tests and 45 JavaScript checks pass. Desktop browser
rendering/release/re-enable checked in a disconnected simulation, not real ROS.

## Previous update — repeatable main-dashboard forward control (2026-10-20)

User confirms first one-shot browser movement and normal self-stop and requests
removing per-action terminal restarts. The main page now supports an explicit
`server.py --ros --drive` mode: acknowledgement + Enable + hold Forward, then
release/Stop. Same 0.03 m/s request, new two-second hold cap, two-second zero
cleanup and fresh stationary feedback before re-enabling on the page. No terminal
countdown or restart between normal holds. No reverse/steering/continuous latch,
automatic resume, firmware/boot changes or verified hardware fault-stop claim.
Without `--drive`, `server.py --ros` remains motor-free/read-only.

142 Python fake-ROS/loopback and 35 fake-DOM checks pass; actual simulated-browser
hold/release/re-enable QA passes. Updated integrated version not yet robot-tested.
See `Documentation/REMOTE_MANUAL_FORWARD_ROS1.md` for the four-file update into
the known personal trial copy, first-version verification, operation and rollback.
The previous one-shot workflow below is historical; it is retained, not the
normal integrated workflow. The original robot viewer remains untouched until
the user explicitly copies the reviewed update into its separate trial folder.

## 2026-10-20: separate supervised web-forward trial prepared

User has restored live camera/YOLO viewing today. The normal `server.py --ros`
remains read-only and the original six directions are still rehearsal-only.
New `web_crawl.py` is default OFFLINE; `--check` delegates the subscription-only
readiness check. Its separately opted-in `--live` mode offers exactly one gated,
terminal-confirmed forward hold (fixed 0.03 m/s / at most 0.4 s intent) per launch,
then zero attempts. No reverse/steering/continuous mode, auto-rearm or replay.
See `Documentation/WEB_FORWARD_TRIAL_ROS1.md` in the Windows project for staged
copy, readiness, physical conditions, operating limits and recovery.

Prepared/tested locally, **not deployed or robot-tested**. 102 Python fake-ROS/
loopback checks and 26 fake-DOM checks pass. Actual Python 2 execution, robot
browser action and firmware/host/serial fault stopping remain unverified.
Do not use live mode until the documented readiness and placement checkpoints.
Earlier claims below refer to the original viewer and prior CLI test milestones.

## Current tested status and next-time checklist

On 2026-10-19 the user demonstrated robot preview startup and accepted live
colour/YOLO browser viewing. This supersedes initial robot-viewer-unrun notes
below; no performance, LiDAR, real driving or automatic-boot test is implied.
For the current three-terminal manual restart and safe shutdown/floor-move
checklist, see `Documentation/REMOTE_DASHBOARD_QUICK_START.md` in the Windows
project. Opening PowerShell alone is not sufficient. Keep original vendor files
unchanged and retain monitor access for recovery until a complete no-monitor boot
is verified.

### Separate base-driver check prepared 2026-10-19

Latest physical observation: user now confirms a tiny visible movement after
the single unchanged observed-repeat instruction and confirms it stopped by
itself, then confirms FORWARD direction and estimates a few centimetres. This
completes the basic observed forward-move/self-stop trial, not measured
speed/distance/braking or firmware/link-loss stopping. No additional repeat is
needed for this milestone. Browser motor output remains disconnected; next
software work is a separately guarded motor path with non-actuating failure/
release/timeout tests before enablement. This supersedes physical-movement/
direction/self-stop-pending notes below, not fault-stop verification or autonomy.

Newest result: user supplies completed CLI `--live` output after typed `CRAWL`:
pulse request finished and feedback reports near-zero speed after zero attempts.
Physical movement/direction/stopping observations are still pending. Do not repeat
or increase the test yet; no firmware fault-stop validation or browser driving
is established. This supersedes live-test-pending wording below.

Latest live result: user supplies successful `crawl_test.py --check` output
(expected driver/recent stationary odometry; no Publisher or movement command).
This supersedes check-pending notes below, not physical motion/stop validation.
Next conditional single-pulse instruction and physical conditions are at the top
of `Documentation/BASE_DRIVER_FIRST_CHECK.md`. Dashboard driving remains disabled.

User confirms normal main-power-off is reachable on the floor; this is not a
certified emergency stop or verified firmware watchdog. New personal files
`base_crawl_check.launch` and `crawl_test.py` are NOT connected to the dashboard.
The server/browser remain motor-free. Current deployment step is isolated driver
startup then `crawl_test.py --check`, with no velocity publisher. Full staged
instructions and limitations: `Documentation/BASE_DRIVER_FIRST_CHECK.md` in the
Windows project. Do not use the separate CLI's `--live` mode before those actual
results are reviewed. No driver, telemetry or physical movement test of the new
files has yet been performed on the robot; copying files alone starts nothing.

The CLI contains a future gated fixed 0.03 m/s / 0.4 s request and repeated-zero
cleanup, not a reliable hardware stopping guarantee. It is offline by default.
36 new fake-clock/fake-ROS/XML checks, 22 existing control/data regression tests,
and 12 fake-DOM checks pass locally; Python 3.6 grammar passes. No actual Python 2
run or robot-side crawl test is implied. The new test file itself uses Python 3
unittest.mock and is for the development laptop, not the robot's default Python.

## Lab restart: 2026-10-19

User reports successful laptop TCP access to `192.168.0.100:22`; SSH login was
guided but no final login output/host-key comparison has been supplied. Continue
only after completing that identity check and reaching the robot shell. No copy
or live dashboard test has yet been confirmed.

Keep two distinct terminal tabs: A is the robot SSH shell
(`wheeltec@wheeltec:~$`), B is local Windows PowerShell (`PS C:\...>`).

1. In A, prepare the personal parent and check for an existing dashboard:

   ```bash
   mkdir -p ~/fahad
   ls -ld ~/fahad/remote_dashboard
   ```

   If it says no such file/directory, proceed. If a folder/file already exists,
   inspect it before copying; do not overwrite an unknown existing version.
2. In B, copy this project folder (password entered locally if prompted):

   ```powershell
   scp -r "C:\Users\fahad\OneDrive\Documents\Bachelor Arbeit - Search and Rescue Robot Image Living Classification\Tools\remote_dashboard" wheeltec@192.168.0.100:/home/wheeltec/fahad/
   ```

   This is a Windows-local command, not a command for the robot shell. No SSD
   needed. If a new/unexpected host-key warning appears, stop and verify rather
   than bypass it. Copying the whole small folder includes optional tests/cache;
   these are not required by the robot but do not launch anything.
3. Once the copy succeeds, use A to start a NO-ROS preview first:

   ```bash
   python -u ~/fahad/remote_dashboard/server.py
   ```

   Leave it running. This isolates interpreter/network/page checks from ROS
   dependencies. No camera is expected and no motors can run from this program.
4. In B, after scp returns to its prompt, open the tunnel:

   ```powershell
   ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 -o ExitOnForwardFailure=yes -o ServerAliveInterval=5 -o ServerAliveCountMax=3 wheeltec@192.168.0.100
   ```

   Keep this quiet terminal open; visit `http://127.0.0.1:8765/` in the laptop
   browser. Expect **Interface preview · no robot**. Send screenshot/errors.
5. Only after the preview is confirmed, Ctrl+C in A, source the ROS workspace and
   restart with `--ros` as described below after checking existing sensor nodes.
   Do not start duplicate drivers or assume GUI/headless/ROS compatibility. This
   is still a motor-free viewer, not live teleoperation or automatic boot.

## What works in this version

- A browser page with colour/YOLO view selection, connection status and 2D scan
  visualization in the original laser frame.
- Optional ROS subscriptions to existing `/camera/rgb/image_raw`,
  `/darknet_ros/detection_image` and `/scan` topics. No drivers are launched.
- JPEG camera previews, capped at 3 refreshes/s per source by default (configurable
  1–5). This is deliberately modest for first testing, not measured robot speed
  and not a low-latency driving video system.
- Hold-to-rehearse direction controls, explicit enable, stop, one browser owner,
  a 0.5 s rehearsal heartbeat timeout and a maximum 30 s enable period. Release,
  blur, hidden page or connection failure disables the rehearsal. Re-enable for
  another direction. No automatic resumption after reconnect.
- Frames/scan display marked unavailable after 2 s without recent received data.
  Message arrival age is not exposure age, inference timing or accuracy.

**The dashboard server has NO ROS publisher, motor endpoint, navigation goal, process launcher,
recording, shutdown action or boot installer.** The driving controls only display
intended actions. Their timeout is NOT a verified physical motor watchdog.
They cannot stop a robot driven by some other program.

No cloud hosting, account, CDN, external fonts, analytics, training or model change.
Existing NumPy/OpenCV/cv_bridge/rospy are used only in ROS mode; no new web package,
web_video_server or rosbridge is required for this first viewer. Those tools were
feasibility candidates, not dependencies selected for this implementation.

## First: confirm the laptop can reach the robot

Keep the car stationary with the normal physical stop method available. Initially
retain the monitor for setup. On the robot, run:

```bash
nmcli device status
hostname -I
systemctl is-active ssh
```

Share the output, not passwords. The robot AP/SSID, usable IP and SSH service are
not confirmed yet. Do not guess manual defaults or change the robot's networking.
Follow `Documentation/ROBOT_FILE_TRANSFER_AND_REMOTE_TERMINAL.md` for the shared
local link, WinSCP and first SSH host-key verification. Internet is unnecessary
after setup, but joining an offline robot Wi-Fi can disconnect laptop internet.

## Copy the complete folder once

Copy `Tools/remote_dashboard/` from the Windows project to:

```text
/home/wheeltec/fahad/remote_dashboard/
    server.py
    control.py
    dist/
        index.html
        app.js
        style.css
```

Use WinSCP once connected, or the SSD for this initial copy. Tests and this README
are optional on the robot; generated `__pycache__` files are unnecessary. Preserve
the folder structure, including `dist`. Do not put files into vendor directories
or edit the robot's original launch/configuration files.

## Start the viewer on the robot

For the first test, camera/YOLO/LiDAR should already be running through the known
sensor-only launch paths. The viewer does not start them. Do not launch duplicate
camera drivers, base, navigation, followers or mapping merely to see the page.
The working general `darknet_ros yolo_v3.launch` wrapper includes the Astra camera;
the default `darknet_ros.launch` is not the same general-model entry point.

In a robot terminal (or an established SSH terminal):

```bash
source ~/wheeltec_robot/devel/setup.bash
python -u ~/fahad/remote_dashboard/server.py --ros
```

The camera stream does not require a desktop window. However, any camera/YOLO
nodes you start separately still need their GUI/headless configuration checked.
This command does not turn on the base or make movement possible.

The code targets Python 2.7 and Python 3.6+ syntax. Melodic's current ROS Python
environment is the right choice; the local checks used Python 3 only. If imports
fail, share the error. Do not upgrade ROS/Python, install packages or select a
different interpreter blindly. If ROS master initialization waits, confirm that
the existing ROS nodes/master are running; Ctrl+C can stop this startup attempt.

## Open it from Windows securely

The service listens **only on 127.0.0.1 on the robot**, not the public network.
For this prototype, SSH supplies the remote login/encrypted connection. There is
no separate website password or public network listener. Other local processes
and people with access to the SSH forwarding endpoint are inside this trust
boundary; this is not a production-hardened multi-user server.

After confirming the actual robot IP, account and host key, open a Windows
PowerShell terminal. Replace `ROBOT_IP` below with the verified address; do not
type the placeholder literally. If the account is not `wheeltec`, use the actual
account too.

```powershell
ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 -o ExitOnForwardFailure=yes -o ServerAliveInterval=5 -o ServerAliveCountMax=3 wheeltec@ROBOT_IP
```

Enter the existing robot login password locally if asked. The terminal may remain
quiet: this is normal for a tunnel. Keep it open, then open this address in your
laptop's Chrome/Edge browser:

```text
http://127.0.0.1:8765/
```

The browser's local address is forwarded securely to the robot. Use the same port
on both ends: this version checks the Host/Origin port. If 8765 is occupied, choose
another unprivileged port in BOTH the server `--port` and the tunnel's two port
positions. Do not disable browser/security warnings or firewall protections.
No router forwarding or exposed ROS/HTTP server is needed.

This initial version therefore needs a started viewer and an SSH tunnel, **not
yet just power on + a bookmark**. After this workflow succeeds, we can automate
the reviewed boot services and connection in a separate step. Do not enable a
boot service yet or paste a generic vendor autostart script.

## What to check and send back

1. Page says **ROS viewer · read-only**, not **Interface preview · no robot**.
2. Colour camera appears; switch to YOLO labels and verify that view if YOLO is
   running. It is normal for a missing topic to show no recent image rather than
   invent data. No numeric depth view is implemented yet.
3. If LiDAR is active, points appear. These are sensor-frame returns, not a map or
   camera-calibrated fusion. The minimum distance is anywhere in the scan; it is
   not automatically an object's distance or a front bumper clearance.
4. With the car stationary, try the motor-free rehearsal. Enable it, hold a
   direction, release. It should disable. Switch tabs while enabled and verify
   disable. This only checks interface logic, not physical braking.
5. Send a screenshot plus terminal errors if any. A slow preview, ROS import error
   or absent stream is diagnostic information, not a reason to change the model.

Stop the dashboard with Ctrl+C in its terminal; close the SSH tunnel with Ctrl+C
in the Windows tunnel terminal. This does not stop independently running drivers
or other robot controllers. Do not interpret it as an emergency stop.

## Windows preview without a robot

No ROS or camera is needed. From the project folder in PowerShell, use a Python 3
interpreter already installed on your laptop:

```powershell
python .\Tools\remote_dashboard\server.py
```

If `python` is unavailable, use a known installed interpreter; do not reinstall
Python just for this. In this Codex workspace the bundled interpreter is also
available (no installation):

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\Tools\remote_dashboard\server.py
```

Open `http://127.0.0.1:8765/`. It explicitly shows preview/no robot and no sensor
data. Opening `dist/index.html` directly is insufficient: the page needs its local
backend. Stop with Ctrl+C. Saved screenshot: `tmp/remote_dashboard_preview_2026-10-15.jpg`.

## Before real driving and automatic boot

Next implementation stages, not completed features:

- Inspect live base/serial/odometry health and existing command publishers.
- Establish the independent physical stop and verify the lower controller's
  communication-loss timeout using a suitable motor-inhibited setup.
- Build a separately gated command path with robot-enforced speed/steering limits,
  fresh-command rejection, single operator, deliberate enable, and robot-side
  timeout. Browser checks alone cannot guarantee a stop if the computer or motor
  process fails. A software screen Stop is not a certified emergency stop.
- Test low-speed line-of-sight motion in an approved clear indoor area with a
  nearby supervisor. Video delay/dropouts prohibit relying on the image alone.
- After manual operation works, review existing boot services, create a separate
  personal startup configuration with GUI-free perception, and test no-monitor
  power-on, missing sensors, restart and reconnect. Motion must stay disabled at
  every boot/reconnect and never replay an old command. Preserve vendor maps.

Mobility between approved indoor test areas does not mean outdoor readiness,
autonomous navigation, collision avoidance or deployment in fire/smoke.

## Local verification

From this folder, using the laptop's existing Python 3:

```text
python -m unittest -v test_dashboard
node test_frontend.js
node --check dist/app.js
```

31 Python tests and 12 fake-DOM JavaScript tests initially passed. Python HTTP
tests use a temporary loopback port and need local network permission. Browser
checks confirmed display, camera-source switching, explicit enable and release-
to-disable. No live ROS, camera/scan, Python 2.7, Jetson resource, wireless range,
motor, firmware timeout, no-monitor reboot or automatic startup test has occurred.
The Python standard-library HTTP server is intentionally limited to this local
prototype, not suitable as a public production server.

Primary references: [Python HTTP-server limitations](https://docs.python.org/3/library/http.server.html),
[ROS LaserScan definition](https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/msg/LaserScan.msg).
