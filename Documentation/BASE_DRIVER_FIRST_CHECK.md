# Base-driver check and one-shot crawl test

## Current milestone: forward movement and normal self-stop reported

After the single unchanged observed-repeat instruction, user reports: "it did
move, just a tiny bit". This is the first user-confirmed visible movement during
this test sequence, superseding physical-motion-pending notes below. User then
confirms it "moved by itself, and it stopped by itself". Record normal self-stop
without user intervention in this trial, not a measured braking time, independent
watchdog or fault-stop result. This is commanded motion, not autonomous navigation.
User additionally confirms forward direction and estimates "a few centimetres".
The basic forward-motion/normal-self-stop observation is complete; no additional
repeat is needed for that milestone. Distance is a visual estimate, not a
measured calibration, and does not establish actual speed or pulse duration.
Exact second-run terminal output is not supplied, but another terminal export
is not a prerequisite just to accept the direct physical observation. No speed
increase or dashboard motor enablement yet; firmware/link-loss stopping remains
unverified. Next software stage is a separately reviewed guarded dashboard
motor path, with release/timeout/link-failure behavior tested without actuation
before any enablement. Such software tests do not prove lower-controller fault
stopping. Earlier direction/repeat/stopping-pending instructions below are
historical, not new retries.

## Latest clarification: one identical, deliberately observed repeat

User says they honestly did not see anything and asks to repeat. Treat the first
run as physically inconclusive, not confirmed no actuation. Permit ONE manually
initiated repeat of the unchanged gated `--live` test solely for direct
observation. This supersedes the immediate no-repeat instruction below for this
one attempt only; it is not automatic retry, permission to raise speed/duration,
or a general driving clearance.

Before repeating: robot stationary on clear level floor, directly visible,
people/objects away from wheels/path, away from edges/stairs, and normal power-off
immediately reachable without lifting/reaching into wheels. Keep the base driver
running, use the same robot SSH shell and existing `--live` command, and type
`CRAWL` only after the conditions are met. Watch the wheels/body from a safe
position (or use a stationary side-view recording), not just the dashboard.
Settings remain 0.03 m/s / 0.4 s followed by zero attempts; actual physical motion
and stopping are not guaranteed. Use accessible power-off for abnormal behavior.
If still no visible movement, stop further attempts and share full output plus
that observation. Do not increase speed/duration; inspect evidence before further
actuation changes. No second-run result is yet available.

## Latest result: command sequence completed; physical observation pending

User supplied the full `--live` output on 2026-10-19, including typed `CRAWL`,
`Requesting ONE pulse`, `Zero-command attempts finished: Pulse request finished`
and `Recent feedback reports near-zero speed AFTER stop requests.` The script
returned to the robot shell without a reported guard abort/publication error.
This supports execution of the planned request/zero-attempt sequence and fresh
near-zero odometry afterward, not actual motor motion or controller receipt of
every request. No during-pulse speed trace or physical observation was supplied.

Do not repeat or increase the request yet. Next ask whether the user directly
saw movement, its direction, and whether it stopped by itself or needed power-off.
If no movement was seen, the result remains inconclusive for actuation; do not
assume friction is the cause. Physical stop and firmware/link-loss stopping are
not validated by the printed near-zero feedback. Browser driving stays disabled.
The launch/check/one-shot instructions below describe the completed sequence,
not an instruction to rerun it before reviewing the physical observation.

Prepared 2026-10-19. The camera/dashboard/tunnel already work by user report.
This is a separate personal test path, not an upgrade that enables web driving.
User reports the isolated driver reaches `wheeltec_robot serial port opened`
and supplies the successful `--check` result below. Fresh stationary odometry
and the expected ROS graph passed the script's checks at that time. This does
not establish actual motion calibration, physical stopping or fault behavior.
The subsequent script result is recorded above; physical movement remains unknown.

## Readiness passed; next conditional one-shot test

User supplied on 2026-10-19:

```text
READINESS: expected isolated driver + recent stationary odometry observed.
CHECK ONLY: no Publisher created and no movement command sent.
```

This resolves whether the driver is merely displaying a quiet terminal: fresh
feedback was available to the checker. No quantitative rate, physical movement,
encoder calibration, IMU/voltage accuracy or watchdog test is established.

Next is ONE conditional test, not continuous/browser driving. Keep the base
launch running. Only proceed on clear level floor, robot directly in sight,
people/objects clear of wheels/steering and path, away from edges/stairs, with
the user-confirmed normal power-off immediately reachable without lifting or
reaching into moving parts. Otherwise do not proceed. No other driving program.
In the same robot SSH shell that just ran `--check`:

```bash
python -u ~/fahad/remote_dashboard/crawl_test.py --live
```

It rechecks readiness, displays the conditions and asks for exact `CRAWL` within
30 seconds. Type it only if those conditions are met; otherwise cancel with
Ctrl+C. It requests forward 0.03 m/s for up to 0.4 seconds, then repeated zero
requests for two seconds and exits. Those are software request bounds, not a
guaranteed physical speed/duration/distance or stopping time. A small nudge or no
movement due to friction is possible. Do not change speed, repeat an inconclusive
test or run a continuous publisher to compensate.

Observe the robot directly, not just the delayed camera. If behavior is abnormal,
use the accessible power-off; never grab/lift the robot. Ctrl+C in the test
terminal requests a software stop, not a guaranteed independent stop. Do not
disconnect SSH/browser as a stopping method or deliberately test link loss yet.
Share the complete output AND whether it physically moved, in which direction,
and stopped. Near-zero feedback is not proof of actual physical stopping or
that any motion occurred. Browser motor controls remain disconnected.

### Why the driver terminal can stay quiet

The launch is a persistent background connection, not a program that finishes,
opens a window or drives automatically. In the copied source, `serial port
opened` is logged after the operating system opens the device. The driver then
loops reading controller packets; valid packets cause `/odom`, `/imu` and
`/PowerVoltage` publication, without a regular success/progress log. A quiet
terminal alone cannot distinguish healthy streaming from missing/invalid data.
Opening a port does not prove the controller is sending valid data.

Leave that launch running. The `--check` command in step 3 observes ROS feedback
and sends no movement commands; the user has now supplied its successful result.
Do not start a second base driver to make the quiet terminal progress. The
conditional one-shot instruction above supersedes the initial check-only gate.

User confirms the labelled main power switch turns the robot off and can be
reached on the floor without lifting. That is a normal power-off fallback, not
a certified emergency stop, verified braking response or independent firmware
watchdog. We have not verified drive-power isolation electrically.

## Today's step: driver and feedback, no requested movement

Use a clear, level area, robot in sight, people/objects clear of wheels and
steering, power-off immediately reachable without reaching into moving parts.
Do not hold/lift a moving robot. Do not start navigation, followers, keyboard
driving or another base driver alongside this test. Stop if placement or cutoff
access is unsuitable. An accessible switch is not proof of stopping distance.

Keep the existing camera, dashboard and SSH-tunnel windows running.

### 1. Copy two new files — laptop's Windows PowerShell, NOT inside SSH

```powershell
$crawlFolder = 'C:\Users\fahad\OneDrive\Documents\Bachelor Arbeit - Search and Rescue Robot Image Living Classification\Tools\remote_dashboard'
scp "$crawlFolder\base_crawl_check.launch" "$crawlFolder\crawl_test.py" wheeltec@192.168.0.100:/home/wheeltec/fahad/remote_dashboard/
```

This copies over local Wi-Fi; internet is not required. It leaves the working
server, browser files, vendor code, maps and services unchanged. Existing
`~/fahad/remote_dashboard/control.py` supplies the monotonic clock helper. Enter
the SSH password locally; do not post it. If scp fails, share the error and stop.

### 2. New robot SSH terminal — isolated base driver

Open another Windows PowerShell tab and connect:

```powershell
ssh wheeltec@192.168.0.100
```

Then, INSIDE that robot terminal:

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch /home/wheeltec/fahad/remote_dashboard/base_crawl_check.launch
```

Leave it running and inspect the startup output. This launch opens the physical
serial controller at the copied driver's 115200-baud setting. It does not
intentionally publish movement commands, start mapping, or launch other sensors.
Its node is `/fahad_base_crawl_check`; the command input is remapped from ordinary
`/cmd_vel` to `/fahad/crawl_test/cmd_vel`. This software separation is NOT a
hardware motor inhibit. Serial opening/installed-driver startup effects have not
been tested; if unexpected movement occurs, use the accessible power-off control,
not the camera window or lifting. If there is a port/error/crash, stop and share
the output; do not launch another reader or automatically change GPS services.

### 3. Another robot SSH terminal — inspect feedback only

Connect as above, then:

```bash
source ~/wheeltec_robot/devel/setup.bash
python -u ~/fahad/remote_dashboard/crawl_test.py --check
```

Expected successful final lines:

```text
READINESS: expected isolated driver + recent stationary odometry observed.
CHECK ONLY: no Publisher created and no movement command sent.
```

Share BOTH driver startup output and the complete check output before moving on.
`NOT READY` is a reason to inspect the result, not bypass a check. `--check`
creates no ROS Publisher and sends no velocity commands. It requires the exact
expected subscriber, exclusive `/odom` source, no competing velocity publisher,
advancing recent odometry, stationary reported velocity and fresh graph checks.
It does not validate actual motion calibration, encoder correctness or a physical
stop. Driver telemetry may be wrong even when well-formed and fresh.

The check exits after approximately ten seconds if not ready after ROS init;
ROS initialisation itself may wait for a master. Ctrl+C cancels the check. To
finish today's stationary check, Ctrl+C in the base-driver launch terminal too.
Normal driver shutdown attempts zeros, but cleanup alone is not a guaranteed
physical stop. Dashboard and camera may remain running for stationary viewing.

## One-shot implementation and limitations

The tool's `--live` mode is conditional on the reviewed readiness result and
physical setup above. It requires a foreground interactive
terminal and exact typed `CRAWL` within 30 seconds. No piped approval, speed,
duration or topic override is supported. Default invocation only prints an
offline plan and does not import/connect to ROS.

The fixed forward request is 0.03 m/s for up to 0.4 seconds, zero steering and
lateral components, followed by repeated zero requests for at least two seconds.
Nominal travel would be 1.2 cm ONLY with correct speed tracking; actual speed,
distance and stopping time are unverified. Friction may prevent any movement;
do not automatically increase speed or repeat a failed/inconclusive pulse.

Readiness is checked again after confirmation. An asynchronous publisher uses a
one-message queue, not a latched command. Fresh odometry, graph snapshots and a
single connection are monitored. Interrupts, anomalous reported speed/direction,
stale feedback, competing publishers or a scheduling gap end further nonzero
requests and attempt zeros. No automatic retry/re-arm. Graph monitoring is on a
separate thread so a blocked graph query cannot hold the pulse loop; stale
snapshots fail closed. Detection of a change is not instantaneous.

This is best-effort process-level control, NOT a real-time or independent motor
watchdog. The installed driver may queue commands. Crash, forced kill, host
failure, USB loss or lower-controller fault can prevent zeros taking effect.
Closing the browser/tunnel is not a physical stop. Ctrl+C in the crawl-test
terminal requests zeros but is also not an independent stop. The accessible
normal power-off remains the fallback if abnormal; no grabbing wheels/lifting.
Near-zero odometry after the test is feedback evidence, not proof of fault
stopping, or proof that the robot actually moved. Do not deliberately disconnect
communications during motion to test a still-unverified watchdog.

Do not enable browser motor output or boot-time motion from this test. Those
need a separately reviewed controller/stop path, command-loss behavior and
operator-link failure handling. Boot auto-start is still unimplemented.

## Local software verification

`Tools/remote_dashboard/test_crawl_test.py` uses fake clocks, fake ROS objects and
XML inspection. It opens no network socket, serial port or physical controller.
It checks bounded request ordering, stale/source/graph guards, exact confirmation,
no-publisher check/cancel/failure paths and repeated-zero attempts on exceptions.
Python 3.6 grammar compatibility is checked separately. The user-provided result
now demonstrates the robot's ROS `--check` path, not the exact Python version or
the `--live` path/physical behavior. Tests run on the laptop are not evidence of
successful actuation or motor stopping.
