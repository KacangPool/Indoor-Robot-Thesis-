# Fahad Robot Hub · Windows

## Latest source v0.18 — visible central car / fixed-map preference (2026-10-27)

Same22file runtime and unchanged motion guards/limits. A shaped car replaces the
central square for the currentlaser frame using an explicitly unverified reported
front display preset, with Flip front correction. Fixed-map mode displays real
/map when available; otherwise the current-scan fallback is explicit. No SLAM,
map-saving, fake pose or motor/PID change. Contract: CAR_MARKER_V018.md. Stationary
with driving disabled: reopen Hub, Connect & prepare, verifyv0.18 and reload.
No tool-side robot update occurred; validate physical orientation after install.

## Previous source v0.17 — front-up viewer (2026-10-27)

Same22file runtime, unchanged motion limits/guards. Adds Front-up, an explicit
FRONT arrow and a session-only Mark front tool when body TF is missing. Marking
is a display convention, NOT mounting calibration or body position. Map follow
requires body TF. See Documentation/FRONT_UP_VIEW_V017.md and the dashboard README.
Stop, confirm stationary, close/reopen the Hub, Connect & prepare, verifyv0.17 and
reload the console. No tools have installed this version on the robot.

## Previous source v0.16 — view controls and shared observation dependency (2026-10-27)

Fixed runtime now22files: equal camera/LiDAR panels, view-only zoom/pan/orbit,
uniform keyboard control styling and bounded camera-only detection snapshots.
Four allowlisted shared fahad_core files are read from the sibling source folder
and installed inside the runtime. Keep Tools/robot_hub, remote_dashboard and
fahad_core together; manifests/upload/import tests cover the new dependency path.
No robot deployment, speed/guard change or autonomous function. Actual fused
positions remain blocked by missing calibration/TF. Details and explicit limits:
Documentation/SEMANTIC_VIEW_V016.md. Stop and confirm stationary before updating
through the existing Hub; reopen it, Connect & prepare, verifyv0.16, reload one
console. Runtime originals remain subject to the existing ownership/backup rules.

## Previous source v0.15 — sensor-first console (2026-10-26)

Installs the same 17-file runtime contract with a large left camera, LiDAR above
controls and compact right readings. Scan-only shading distinguishes unknown
from individual observed beam sectors, not guaranteed clearance or saved SLAM.
An unverified laser-frame car heading is no longer shown. See
`Documentation/REMOTE_SENSOR_LAYOUT_V015.md`. Keep the sibling source folders
together; Stop, confirm stationary and close old controllers/Hub before preparing
the update. Speed remains 0.30 m/s and all motion guards are unchanged. New source
is not proof of installation, physical direction or Jetson compatibility.

## Previous source v0.14 — diagnostics and quality foundations (2026-10-22)

The existing Save report button now writes a bounded allowlisted diagnostic
snapshot with explicit age/demo evidence and sensor-stream issue codes. It does
not probe again, include raw SSH commands/logs/keys, or start/restart anything.
Bounded structured session events are configured at application startup; no raw
activity or exception text is persisted. Normal location:
`%LOCALAPPDATA%\FahadRobotHub\logs\events.jsonl` (256 KiB, two rotated backups).

Robot helper adds read-only Python-version/disk metadata, missing until updated.
The fixed v0.14 runtime has **17** files, including strict ordinary configuration.
Existing launch/control/ownership/guards unchanged. No actual GUI/robot deployment
was performed; offline tests use fake UI/SSH and temporary files. Read
`Documentation/QUALITY_WORKFLOW.md` for the local-only source history, one-command
checker, settings rules, report limits and staged lab work.

## Previous source v0.13 — modular source/runtime (2026-10-22)

The setup workflow is now in `hub_controller.py`, transport stays in
`connection.py`, and checksum preparation is in `runtime_bundle.py`. Keep the
whole Hub source folder together; old import paths remain compatible. The
standalone robot bootstrap stays self-contained. Its fixed dashboard runtime
list now has 15 files, including the new sensor modules and browser renderer.

The interface/commands and robot behaviour are unchanged. Nothing was connected,
uploaded or installed on the robot during this at-home refactor. Offline Hub
tests: 46 passed, one Windows symlink-privilege skip; isolated runtime dependency
checks included. See `Documentation/MODULAR_CODE_ARCHITECTURE.md` for complete
verification, update requirements and remaining Windows HTTP/live-robot limits.

## Previous source v0.12 (2026-10-22)

Plain LiDAR plane: removed decorative radar rings/crosshairs, fixed distance
colours (red 0 m to blue 4 m), never object-type labels. Existing read-only map
layer retained if actually published. No control/speed/driver-startup changes.
See `Documentation/REMOTE_PLAIN_LIDAR_V012.md`. Repeat /scan rate check while Hub
is connected; closing Hub does not necessarily shut down background ROS nodes.

## Previous source v0.11 (2026-10-22)

Installs A/D keyboard steering, wider central camera/map panels and a read-only
`/map` view with TF-validated car/scan overlays. Missing map falls back honestly
to scan-only. No mapping stack starts automatically, no map/goal writes, no new
network exposure. .30 speed remains; .40 request deferred after explicit yaw
fault in new video. See `Documentation/REMOTE_KEYBOARD_MAP_V011.md` for limits,
verification, update and stationary `/map` inspection. Phone Hub is not implemented.

## Previous source v0.10 (2026-10-22)

Installs the three-column recording HUD and a five-second held-pedal/key S-curve
to .30 m/s command ceiling. Readings left, framed camera centre, LiDAR below,
controls right. Expandable details and side-panel scrolling retain diagnostics;
narrow screens stack. Release/B/Stop do not use easing. Command/feedback limits
are distinct; actual speed and stopping distance at .30 remain unmeasured.
See `Documentation/REMOTE_COCKPIT_V010.md`. Stop and confirm standstill, close
all old console tabs and Hub, reopen Hub, Connect & prepare, open one v0.10 page.
No remote deployment or movement was performed by tools for this change.

## Previous source v0.9 (2026-10-22)

Slider replaced by held-input acceleration (0→0.10 m/s request). Opposite key
decelerates to zero; reverse requires fresh input, both keys are not cruise.
Fresh healthy/stationary travel press can Enable without a separate click;
held/early/cancelled inputs never resume automatically. Browser Stop locks the
shortcut until deliberate acknowledgement. Owner-scoped automatic stops prevent
inactive/stale pages issuing global Stop; explicit Stop remains global. Feedback
headroom .12 m/s is distinct from unchanged .10 command cap. .30 is not enabled.
See `Documentation/REMOTE_RAMPED_PEDALS_V09.md` for evidence and first test. Close
all old console tabs, restart Hub, Prepare and use one new v0.9 page while stationary.

## Previous source v0.8 (2026-10-22)

Default browser layout is now held **W/↑ forward, S/↓ reverse**, separate mouse
steering, **B brake**, Space/Escape stop/disable; touch pedals support a second
steering finger. Normal travel release/braking preserves healthy permission and
steering grip; faults still disable. A prominent stop-reason alert sits beside
Enable. Travel setting .03–.10 m/s, default .06; no maximum/guard increase.
See `Documentation/REMOTE_PEDALS_STEERING_ROS1.md` for update and first-test steps.
Close/reopen the hub and reload the browser while stationary. Do not treat the
checkbox as a dead-man control. New native input/physical behaviour unverified.

## Previous source v0.7 (2026-10-21)

Adds animated step/elapsed-time progress, explicit **Disconnect & close**,
persistent backend stop diagnostics, an optional independent throttle/steering
joystick layout, and labelled raw-intensity/distance LiDAR colour views. Maximum
joystick request stays 0.10 m/s; suggested 0.20 is deferred pending unexplained
disable diagnosis, with existing guards unchanged. See
`Documentation/ROBOT_HUB_V07_OPERATING_NOTES.md` in the project root for update,
fault collection, colour meaning and full-shutdown steps. Close/reopen the hub
before Prepare, and reload the browser while stationary. New robot behaviour
and actual dropout cause remain unverified. Earlier first-use notes below apply.

A native Windows app that prepares the existing robot dashboard. This is a
source-based app launched with `Start Robot Hub.cmd`, not a packaged EXE installer.
Keep this folder beside `../remote_dashboard`; do not copy the launcher alone.

## First use

1. With laptop internet available, double-click **Start Robot Hub.cmd**. Its first
   run creates a private laptop environment and installs the SSH library. Normal
   later runs do not need internet. Python 3.11 with Tkinter must be installed;
   the launcher recognises this laptop's existing Python installation.
2. Join the robot's Wi-Fi. Keep the robot stationary, directly visible, with
   wheels clear and its normal power-off immediately reachable. If the old web
   controller is open, release it and click **Stop** before updating.
3. In the hub, leave `192.168.0.100`, enter the robot login password locally,
   tick the stationary-setup acknowledgement, and click **Connect & prepare**.
   Do not send passwords to the chat. The password field clears on submission;
   the hub does not save it to files or logs.
4. Wait for the service cards. Click **YOLO detections** or **Driving + LiDAR**
   to open the existing website. Startup itself never enables driving or sends
   a movement command. The website retains its initial Enable and held-input
   controls. Begin with a small, brief joystick input while watching the robot.

The app verifies an already-saved SSH host identity using
[Paramiko's rejecting host-key policy](https://docs.paramiko.org/en/stable/api/client.html).
If no identity is saved, verify the robot's SSH fingerprint through a trusted
source and connect once using normal Windows SSH. It will not silently accept
unknown/changed identities. Existing Windows SSH use may already have saved it.

## What Prepare does

- Reuses registered camera/YOLO, LiDAR and the expected isolated base when healthy.
- Starts missing services with fixed launch commands, not arbitrary user commands.
- Updates the **personal trial dashboard** to v0.16, with checksums and backups.
- Opens a private, laptop-loopback SSH tunnel and shows running version/speed.
- Shows freshness/readiness separately from merely registered ROS nodes.
- Offers service logs, status-report export, check-only and software Stop.

The normal sequence is camera/ROS, verified personal runtime, LiDAR, isolated
base, dashboard, tunnel. Camera startup may take about a minute. A partial or
conflicting existing setup is reported; it is not blindly killed or duplicated.
Existing active/faulted driving sessions cannot be automatically replaced. Release
and Stop first, then inspect any remaining readiness error. A temporary image or
LiDAR view in the browser is not permission to assume the base is healthy.

**Connect / reconnect** connects and installs/checks the personal helper, without
starting ROS services. When reconnecting it first attempts software Stop on the
old connection. **Check now** only reads status. Monitoring reads status every
four seconds; it never automatically restarts or re-arms after a fault.

## Speed update

Direct-drag joystick layouts request up to **0.30 m/s** forward/reverse at full vertical
joystick pull. Small pulls remain proportional; circular diagonal inputs have a
smaller travel component. Six direction buttons and legacy test profiles stay
at **0.03 m/s**. This is a requested velocity, not measured speed or a guarantee.
Curvature remains at most 1/m, with no sideways motion or in-place spinning.

Default Pedals + steering uses a five-second S-curve from zero to .30 m/s;
pressing the opposite travel key decelerates at .08 m/s/s to zero, without auto
reverse. Release/B request immediate zero, not a gradual easing to rest.
v0.10 live-session reported-velocity guards are |vx| above .32 m/s, lateral speed
above .04 m/s, or yaw above .35 rad/s. The yaw ceiling accommodates .30 m/s at
unchanged 1/m curvature. These headrooms are provisional, not calibrated safety
margins. Historical crawl feedback defaults remain .12/.15. Release and inspect
feedback/logs on any fault. Do not assume collision protection or a stopping distance.
Lease, camera/odometry freshness, unique-controller, release/braking, Stop and
explicit recovery guards remain in place. Independent firmware/serial/host-fault
stopping is still unverified. Software Stop is not a physical emergency stop.

## Existing terminals and ports

On this first transition, healthy services started in old terminals are reused;
their old terminals may still be needed. Do not close unknown active driver
terminals while operating. After a normal fresh robot boot, the hub can start
services detached from SSH and write personal background logs, so separate
PowerShell windows are not needed. No boot auto-start has been installed.

If a verified existing laptop tunnel reaches the same dashboard boot identity,
the hub may reuse it. That old tunnel terminal must then remain open. To migrate
fully, remain stationary and click Stop, close **only the known old laptop
tunnel** with Ctrl+C, then Prepare again so the hub creates its own tunnel.
Never kill a process using its port number. An unrelated listener on 8765 is
reported and is not killed. No real-robot transition has been verified yet.

Closing the hub attempts software Stop and closes its own SSH/tunnel. Sensor,
ROS and base processes remain running on the robot. Closing is **not Ubuntu
shutdown**, and neither the app nor its connection is a physical motor inhibit.
Cancel setup stops future setup steps; already-started services remain. A fault
or dropped connection requires deliberate recovery; nothing resumes motion.

## Files and boundaries

Robot writes stay inside `/home/wheeltec/fahad/`:

- `robot_hub/agent.py`, `services.json`, `logs/`, `staging/`, `backups/`;
- the seventeen allowlisted runtime files and manifest in `remote_dashboard_web_trial/`.

Existing matching trial files are backed up before replacement; unrelated files
are preserved. Interrupted/hash-mismatched updates prevent managed base/dashboard
startup until corrected. The original `remote_dashboard/` viewer and vendor ROS
source, firmware, Wi-Fi, boot setup and permissions are not modified. An already
running external isolated base is checked/reused, not restarted for the update.

Camera buttons select the existing colour/YOLO browser views, **not** hardware
exposure/gain/calibration controls. Manual tilt stays physical. The app is a
setup/status hub, not a new embedded camera viewer. LiDAR is a live 2D scan view,
not mapping, object association or collision avoidance.

The website is retained. Phone access still needs its own trusted connection:
phone `localhost` is not the laptop's SSH tunnel. No public hosting or unauthenticated
LAN listener is added. Laptop network selection/tethering is not automated.

## Development verification, 2026-10-22

- 45 hub tests run: 44 pass, one Windows symlink-privilege test skipped. Includes
  encrypted SSH/RPC/tunnelling to a generated fake localhost peer, rejecting
  unknown/changed keys, simulated fixed detached launches, interrupted updates,
  checksum/backup/path/ownership guards, conflicts, cancellation and no arming.
- 239 dashboard fake-ROS/loopback Python tests and 107 JavaScript checks pass.
  A full run passed, but later repeats hit intermittent Windows 10053 loopback
  aborts in unchanged HTTP-denial tests; 23 speed/LiDAR tests pass separately.
- Earlier v0.6 disconnected demo visually inspected, simulated Prepare reached
  SIMULATED cards. No fresh v0.10 native Hub GUI QA or live credentials used by
  tools; user reports prior real hub works and 0.1 is useful, not measured speed.
- New cockpit inspected in motor-disconnected browser fixture at 1280x720;
  no page overflow; camera/scan/steering/Stop visible. No live data or mobile QA.
- Robot helper targets Python 2.7/3.6 syntax; actual v0.10 Jetson execution,
  update/startup, UI layout/timing, dropout diagnosis, new axes/intensity and
  independent hardware failure stopping remain unverified on the robot.

Offline demo: `Start Robot Hub.cmd --demo`. It does not connect to a robot,
open a tunnel, upload files, or open the live website. All cards are simulated.
For development, run `python -m unittest discover -s Tools/robot_hub -p "test*.py"`
from the project root with the SSH dependency installed on the laptop.
