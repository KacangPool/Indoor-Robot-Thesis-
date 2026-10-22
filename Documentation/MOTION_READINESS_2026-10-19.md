# Motion-readiness investigation — forward movement and normal self-stop reported

2026-10-20 superseding progress: user has now observed tiny movement from the
separate browser one-shot and explicitly confirms self-stop without power-off.
This extends earlier CLI-only evidence to that browser request, not measured
speed/distance or firmware fault stopping. Repeatable main-dashboard slow forward
mode is prepared/tested locally; see `REMOTE_MANUAL_FORWARD_ROS1.md`. Its larger
two-second hold intent has not been robot-tested, reverse/steering remain off and
the copied-source watchdog/backlog limitations below still apply. Earlier browser
motor-disconnected wording refers to the default viewer/previous milestones.

## Current next step (supersedes earlier pending-switch/stand wording below)

Newest observation: user confirms forward movement, visually estimated as a few
centimetres, and stopping by itself. The basic commanded forward-motion/normal
self-stop observation is complete for this trial; no more repeats are needed
just for that milestone. This is not measured speed/distance/braking or an
independent watchdog/failure-stop test. Exact second-run output is not supplied;
do not require it to accept the direct physical report. No tuning or browser
motor enablement yet. Next software stage is guarded dashboard integration and
non-actuating release/timeout/link-failure checks before enablement, not a moving
communications-loss experiment. Firmware/link-loss physical stopping remains
unverified. Earlier pending-direction/self-stop wording below is historical.

Latest result: user supplies full `crawl_test.py --live` output after typed
`CRAWL`: pulse request finished, zero-command attempts finished, and recent
feedback reports near-zero speed after stop requests. This is a robot-side
software/feedback milestone, not proof the robot physically moved or stopped.
Await direct observation of movement, direction and stopping/any power-off
intervention. No repeat, speed increase or browser motor enablement yet. Earlier
pre-test wording below is historical; no firmware/link-loss stop test occurred.

Latest: user supplies successful `crawl_test.py --check` readiness/no-Publisher
output. This establishes fresh stationary-reported odometry and expected isolated
graph for that check, not physical motion/stop or a measured rate. The previous
startup/check gate is now met. Next is ONE conditional interactive fixed crawl
request as documented at the top of `BASE_DRIVER_FIRST_CHECK.md`, only with clear
level directly supervised placement and accessible normal power-off. No pulse
result exists yet; actual speed/duration/stop and independent watchdog remain
unverified. Browser motor output remains disconnected; no retry/speed ramp.

User now confirms the normal labelled main-power control turns the robot off and
is reachable on the floor without lifting. Record this as user-reported normal
power-off access/function, NOT emergency-stop certification, measured braking,
electrical isolation or lower-controller watchdog verification.

A separate personal launch and command-line check are prepared in
`Tools/remote_dashboard/`, with staged instructions in
`Documentation/BASE_DRIVER_FIRST_CHECK.md`. Current instruction is isolated base
driver startup followed by `crawl_test.py --check`, no velocity publisher. Serial
opening/installed-driver startup may have physical side effects; the remap is not
a motor inhibit. Use controlled clear placement and accessible normal power-off;
do not grab/lift a moving robot. Share startup/check results before any live pulse.
GPS services and vendor files remain unchanged. No actual new driver startup,
serial/telemetry/stop test or movement has been performed by this session's tools.

The separate CLI is offline by default; its future explicit `--live` mode needs
typed confirmation and healthy exclusive feedback/graph checks, and has fixed
request bounds, not guaranteed physical speed/distance/stopping. 36 offline
fake-ROS/clock/XML tests pass, plus 22 existing control/data and 12 frontend
regressions; Python 3.6 syntax checked, Python 2/live hardware not tested. Browser
motor controls remain disconnected; boot auto-start remains unimplemented.

User wants to proceed despite lab staff lacking robot knowledge. We can inspect
the system ourselves; an unverified floor-driving test or catching/lifting the
robot is not the proposed method. No specific staff member is a technical
prerequisite. A known accessible power-off fallback, suitable controlled setup
and controller behavior must be considered before physical motion; normal power
off does not establish an independent fault-stop watchdog.

The user's approximately 20 km/h statement is not a measured robot specification.
20 km/h would be approximately 5.56 m/s, not an appropriate first-test speed.
Copied keyboard software defaults to 0.2 m/s command and 0.5 rad/s turn; this is
software intent, not proof of actual hardware speed or a recommended first test.

## Copied-driver evidence

Inspected `From Robotics Lab/wheeltec_dev/wheeltec_robot_src/turn_on_wheeltec_robot/`:

- `src/wheeltec_robot.cpp`, Cmd_Vel_Callback (around line 47): accepts Twist
  components, multiplies by 1000, packs signed 16-bit quantities and writes a
  serial packet. No speed clamp, command-age or stale-command stop identified in
  this callback.
- Main Control loop (around line 416): reads sensor data, publishes odometry/IMU/
  voltage and calls spinOnce. No explicit command-age watchdog identified in the
  inspected driver/source/include search.
- Constructor uses a queue of 100 for cmd_vel and `serial::Timeout` 2000 ms.
  The serial I/O timeout is NOT evidence of a stop-on-missing-motion-command
  watchdog or a guaranteed braking response time.
- Destructor (around line 506) attempts to transmit zero velocities before
  closing serial. Normal destructor cleanup is not guaranteed after a crash,
  forced kill, stalled process or loss of computer power.
- `launch/include/base_serial.launch` normally runs `wheeltec_robot_node`,
  node `wheeltec_robot`, device `/dev/wheeltec_controller`, 115200 baud. Optional
  smoother can remap command input; inspect live endpoints rather than assume.
- Limited firmware/path search found no clearly named lower-controller firmware
  to establish the actual board watchdog. This does NOT prove firmware has no
  watchdog, nor that copied source matches the installed executable.

No controller change, firmware reading/flashing, serial packet or velocity
publication has been performed. Existing dashboard still has no motor publisher.

## Immediate read-only live check

Keep the camera launch/dashboard/tunnel unchanged. From another robot SSH shell:

```bash
source ~/wheeltec_robot/devel/setup.bash
timeout -k 2s 10s rosnode list
timeout -k 2s 10s rostopic info /cmd_vel
timeout -k 2s 10s rostopic info /odom
```

Share the full output. Unknown topics are useful evidence that the controller may
not be started; do not start mapping/navigation or publish motion to make them
appear. These checks do not issue movement commands. Inspect the actual active
controller/publishers before selecting a test path.

## Subsequent gates

### Live inventory result received

User supplied a node list containing camera nodes/static camera-frame publishers,
darknet_ros, the personal dashboard reader and rosout, with no wheeltec_robot base
node. Both `/cmd_vel` and `/odom` return Unknown topic. This establishes no expected
base command/odometry interface registered with this ROS master at that moment;
it does NOT establish a broken/unpowered motor board, no Bluetooth/firmware control
or safe physical stopping. Static `camera_base_link*` nodes are not evidence of a
running chassis controller. Camera/YOLO/dashboard remain working components.

Next inspect the expected controller device metadata, without opening serial or
starting its driver:

```bash
ls -l /dev/wheeltec_controller
udevadm info --query=property --name=/dev/wheeltec_controller
```

Send errors too. These inspect filesystem/sysfs/udev metadata, do not publish
velocity or enable the ROS base. Device presence/USB identity is not proof of
physical controller watchdog or installed binary equivalence. If absent, inspect
actual device/rule/cable state before changing anything; do not run vendor
`wheeltec_udev.sh` blindly (it writes rules under /etc with broad permissions).
No permissions, serial state, power wiring or controller setting change proposed.

Latest device result: user reports `/dev/wheeltec_controller -> ttyUSB0` from ls.
The udev command was typed with `/dev/wheeltec_conroller` (missing t), so its
'device node not found' result does not test the intended path. Rerun the correct
udevadm query above. Symlink permissions/root ownership are not target serial
device permissions or proof of board identity/firmware health. No serial open,
controller launch, power-button confirmation or motion test yet supplied.

### Corrected USB metadata received: possible GPS-service ownership to inspect

User's corrected udev output identifies `/dev/ttyUSB0`, Silicon Labs CP2102
USB-to-UART bridge, USB IDs `10c4:ea60`, interface serial `0002`, driver `cp210x`.
This matches the copied WHEELTEC controller-alias rule, but identifies the USB
adapter, not the connected microcontroller firmware, safe speed or watchdog.

The SAME device's DEVLINKS includes `/dev/gps0`, and SYSTEMD_WANTS includes
`gpsdctl@ttyUSB0.service`. This indicates GPS-related alias/activation metadata;
it does NOT prove a GPS sensor exists, gpsd currently runs, the port is occupied,
or any fault is caused by GPSD. Official GPSD docs describe udev/hotplug device
registration and gpsdctl control commands. Actual open-file ownership must be
checked before starting a second serial reader or changing services.

Next read-only checks in the robot SSH shell:

```bash
ls -l /dev/ttyUSB0
sudo fuser -v /dev/ttyUSB0
systemctl show gpsd.service gpsd.socket gpsdctl@ttyUSB0.service -p Id -p LoadState -p ActiveState
```

Enter sudo password locally. fuser -v LISTS users of the device; no kill option
is used. If missing/unavailable, report the error rather than install utilities.
No fuser output can mean no visible current owner, not that another process cannot
open it later. An active gpsd socket alone is not proof of an open serial device.
Do not stop/disable/mask/uninstall GPS services or rewrite udev rules before the
actual service/ownership result and scope are reviewed. No serial port is opened
by these metadata/process checks and no motor command is sent.

### Port ownership/service results received

User supplies target `/dev/ttyUSB0` as character device, root:dialout, mode 0777;
sudo fuser -v returns no output. gpsd.service, gpsd.socket and
gpsdctl@ttyUSB0.service all show loaded/active. Thus normal Unix read/write mode
bits are not an apparent access blocker, and no current file-user was reported
at the sampled instant. Active service/socket/activation unit is not evidence
GPSD currently holds the serial port; no actual conflict or fault is established.
GPSD can defer device opening until a client asks (depending on configuration),
so this snapshot is not proof another service can never acquire/probe the port.
Do not chmod the device, kill processes, disable GPS services or rewrite rules
based on this evidence. Runtime options and long-term ownership are not known.

Base-driver startup/telemetry is next only with an appropriate controlled test
setup and an established accessible independent stop. A proper chassis support
can reduce risk, but a stand is not the only possible test arrangement. Do not
hold the robot in hands or balance it on loose improvised objects. No instruction
to spin wheels or start the driver before placement/stop is reviewed is supplied.
If a suitable stop/setup is unavailable, continue software/mocked-interface work
without publishing to the motor controller; no unverified floor-driving test.

User says no stand is available and another student has driven the robot. This
supports that movement has been observed, not tested behavior of our new browser
controls or a verified stop. A controlled very-low-command-speed, brief floor test
can be considered after independent stopping, clear supervised area and gated
control/timeout behavior are established; no requirement for a stand or a specific
staff member should be inferred. USB/metadata checks are complete enough for this
stage; the immediate missing fact is the actual main power-off control: does the
operator normally use it to remove robot/drive power, and can it be safely reached
with the car on the floor without lifting or reaching into wheels? Ask for a
description/identification, not an experiment on a moving robot. No motor output,
driver startup or floor movement is issued on the basis of another student's use.

Primary references: [GPSD manual](https://gpsd.io/gpsd.html),
[gpsdctl manual](https://www.gpsd.io/gpsdctl.html),
[systemd device activation](https://www.freedesktop.org/software/systemd/man/247/systemd.device.html).

Earlier switch-identification request is now answered by the user's normal-use
confirmation above; circuit/fault stopping remain unmeasured. Current scoped
next step is the documented stationary driver/feedback check, not the CLI's live
pulse. A secured stand is not categorical, and unsafe improvised support/holding
is not suggested. Establish controller command-loss behavior before relying on
remote continuous driving; do not deliberately cut communications during motion
with an unverified watchdog. Process/UI checks cannot prove lower-controller
fault stopping. No live movement or particular speed has yet been tested.

If a suitable stop/setup cannot be established, continue stationary sensing and
software/simulation tests instead. No self-directed electrical modification or
reliance on picking up a moving robot.
