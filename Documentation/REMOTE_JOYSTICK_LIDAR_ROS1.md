# Dashboard v0.5: proportional joystick speed and live LiDAR diagnostics

Superseded for current startup/deployment by `ROBOT_HUB_WINDOWS.md` and
`Tools/robot_hub/README.md`: v0.6 adds a native Windows setup hub and raises the
joystick maximum request to 0.10 m/s (buttons remain 0.03). This file records
the earlier v0.5 manual procedure and 0.08 limit, not the current ceiling.

Prepared 2026-10-21. Source update only: not copied to or physically tested on
the robot by tools. User reports restored dashboard access and slow driving;
installed version/exact file hashes and v0.4 release/repeat remain uninspected.

## Joystick speed

The joystick was already proportional, but v0.4 capped every request at 0.03 m/s.
v0.5 raises the **session joystick ceiling to 0.08 m/s** (8 cm/s request), while
all six buttons remain at **0.03 m/s** for precise movement. Small/medium/full
vertical deflections request increasing speeds after the unchanged 12% dead
zone; there is no minimum-speed boost. Approximately 45% forward input requests
0.03 m/s; full vertical input requests 0.08 m/s. Diagonal input is circularly
clamped, so its travel component is smaller than straight full-up/down input.

Speed and heading rate remain coupled by requested curvature <= 1/m; no lateral
travel or zero-speed spin. Existing 0.10 m/s reported-speed and 0.15 rad/s yaw
guards are **not raised**. The separate CLI and legacy bounded profiles retain
their old speeds. The new readout labels requested signed travel and joystick
maximum explicitly, not measured physical speed. Actual tracking, stopping and
turning at the new request remain unverified.

Enable-once/continuous-held session behaviour remains: release to zero/brief
stationary-feedback check, then fresh press without another Enable. Stop/fault/
lease/focus/connection loss disables. No latch, automatic resume or arbitrary
speed/ROS-topic tuning endpoint. Independent controller/host/serial/queue failure
stopping remains unverified; screen Stop is not a physical emergency stop.

## LiDAR panel

The dashboard already subscribed to the fixed `/scan` LaserScan topic. This
update makes its connection/data state explicit rather than starting a scanner
from the browser:

| Display | Meaning |
| --- | --- |
| CHECKING ROS | No local connection observation or first message yet |
| NO ROS CONNECTION | Subscriber currently reports zero publisher connections |
| CONNECTED · WAITING | A connection exists but no scan message has arrived |
| LIVE SCAN | A recent valid scan is available |
| LIVE · NO VALID RANGES | Messages arrive, but none of the ranges are finite/in bounds |
| INVALID SCAN | Processed LaserScan geometry/ranges are invalid |
| STALE SCAN | No recent valid scan; old points are hidden |
| MULTIPLE ROS SOURCES | More than one connection; points hidden rather than mixed |
| UNKNOWN | Dashboard disconnected; robot-side state unknown |

Panel shows fixed topic, local ROS connection count, message caller/source,
frame, raw callback arrival rate, arrival age, received-message count, valid
ranges and minimum range. Arrival rate is not necessarily sensor rotation rate;
arrival age is not end-to-end latency. Messages/connection do not identify the
physical scanner, prove calibration or guarantee useful ranges.

Geometry is processed at most 5 Hz, at most 240 displayed points, with a 4 m
display radius. Raw arrivals are counted independently of plotting throttling;
arrival history is bounded to 80 timestamps. Valid returns are selected before
display decimation, so isolated valid measurements are not lost merely because
invalid ranges occupied the old sampled indices. Nothing records a map or
assigns object labels. Sensor +X is up, +Y left; no camera/base/map alignment or
obstacle avoidance. LiDAR display does not become a collision-stop interlock.

## Copy and restart

Release controls, confirm stationary, then Ctrl+C **only the live dashboard**
and wait for its cleanup/prompt. Keep camera, isolated base and laptop SSH tunnel
running; do not copy into a running dashboard. If its terminal was lost, identify
the current personal dashboard PID and listener first, and use normal TERM on
that exact process. Never reuse an old session PID or confuse port 8765 with PID.

In **local Windows PowerShell**, not robot SSH:

```powershell
Set-Location -LiteralPath 'C:\Users\fahad\OneDrive\Documents\Bachelor Arbeit - Search and Rescue Robot Image Living Classification\Tools\remote_dashboard'
scp .\server.py .\manual_drive.py wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial/
scp .\dist\index.html .\dist\app.js .\dist\joystick.js .\dist\controls.css wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard_web_trial/dist/
```

After both transfers succeed, in the **robot dashboard SSH terminal**:

```bash
source ~/wheeltec_robot/devel/setup.bash
python -u ~/fahad/remote_dashboard_web_trial/server.py --ros --drive
```

Refresh laptop `http://127.0.0.1:8765/` with Ctrl+F5; look for **v0.5**. Same
loopback/SSH-only network, explicit drive opt-in; default `--ros` is motor-free.
Original `~/fahad/remote_dashboard/` viewer, vendor drivers, firmware, Wi-Fi,
models, maps and hosted planner remain unchanged. No ROS/Python upgrade needed.

## Check ROS/LiDAR while stationary

User reported "no output" from earlier commands; this is inconclusive. Was the
command waiting, or did the prompt return? Do not start another driver solely
because the plot is blank. In a spare **robot SSH terminal**:

```bash
source ~/wheeltec_robot/devel/setup.bash
timeout -k 2s 8s rosnode list
echo $?
timeout -k 2s 8s rostopic info /scan
echo $?
```

`0` means normal command completion; `124` means timeout. Preserve any other
code/error. If ROS graph inspection times out, diagnose that first; no duplicate
master/base/camera launch or broad process kill. If graph responds but /scan
has no publisher, inspect existing driver nodes/processes and serial alias:

```bash
pgrep -af 'lsn10|lslidar|rplidar|ldlidar|wheeltec_lidar.launch'
ls -l /dev/wheeltec_lidar
```

Only when no LiDAR driver is already running and the configured device exists,
start the known **sensor-only** wrapper in that terminal:

```bash
roslaunch turn_on_wheeltec_robot wheeltec_lidar.launch
```

Leave it running. Copied source selects `ls_N10` and includes the `lsn10` driver
publishing `/scan`, frame `laser`, through `/dev/wheeltec_lidar`; it does not
include the base, follower, navigation or mapping. This is configuration
evidence, not physical-model confirmation. Existing October report showed actual
/scan from /lsn10 historically, not proof of today's connection. If serial or
package errors occur, send them; do not change permissions/device rules blindly.

In another robot shell, check:

```bash
source ~/wheeltec_robot/devel/setup.bash
timeout -k 2s 8s rostopic info /scan
timeout -k 2s 10s rostopic hz /scan
```

The second command intentionally ends after its observation window. A live
publisher should produce arrival statistics and the page should show LIVE SCAN
with changing planar points; a connection alone is insufficient. No driver
duplicates or laser-follower/mapping launches. For stationary plotting, dashboard
can run without `--drive`.

## Verification boundary and first physical check

227 Python fake-ROS/laptop-loopback tests and 67 JS checks pass (49 main-page,
four joystick geometry, 14 legacy one-shot), plus JS syntax/Python 3.6 grammar.
New tests cover proportional/signed bounds, unchanged button speeds and feedback
guards, release zero, source/frame/stamp/rate, empty/invalid/stale/multiple-source
scans, bounded history/plotting and sparse returns. No real robot publication,
phone testing or new physical speed/LiDAR validation by tools. Motor-free local
preview returned HTTP 200; native handoff was queued, not confirmed opened.

First physical check: directly visible clear level floor, wheels/cables/people
clear, known physical power-off safely reachable. Start with a small straight
joystick deflection and release; confirm actual stop before gradually trying
larger pulls. Speed is a request, not a calibrated guarantee. If abnormal,
physical power-off takes precedence; do not lift a moving robot or test moving
link loss. Normal shutdown remains dashboard cleanup, base, LiDAR/camera/master,
orderly Ubuntu halt then main power-off. No live map/fusion/autonomy is added.
