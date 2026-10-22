# Robot file transfer and remote terminal from Windows

## Current network check: 2026-10-19

Latest user acceptance: after selecting-view instructions, user reports everything
working well. Remote colour and YOLO annotated viewing workflow is user-confirmed;
no new annotated screenshot/quantitative benchmark supplied. Keep the camera/YOLO
launch, robot dashboard --ros and laptop SSH tunnel running while using the page.
This is a completed manual remote-viewing milestone, not boot automation, tested
live laser display, physical driving, collision avoidance or validated safety.
Motor controls remain rehearsal-only. For mobility, next verify live base health,
competing command sources, independent physical stop and lower-controller timeout
before introducing an actual command path or supervised movement.

Live ROS viewer success: user supplies `server.py --ros` startup in ros_read_only
mode and reports seeing the camera in the laptop browser. Robot-side ROS/image
dependencies and a usable live colour path are now demonstrated by user report.
No quantitative FPS/latency or annotated YOLO/LiDAR/motion result inferred.

User initially sees camera without boxes; selected source unknown. Default View
is Colour camera (`/camera/rgb/image_raw`), deliberately unannotated. First select
YOLO labels (`/darknet_ros/detection_image`) above the image, and use a clearly
visible person as a supported class while robot remains stationary. If boxes are
still absent, distinguish live unannotated image from no recent image and inspect
selected-view screenshot/publisher state before changing anything. No duplicate
camera/YOLO launch or model/configuration change on this observation alone.

User reports camera/YOLO seems to run over SSH but its usual robot-monitor window
does not open. This is consistent with an SSH environment lacking desktop display
access; not by itself proof of live streams or failure. Copied detector checks
XOpenDisplay, disables viewImage when unavailable, and still generates/publishes
annotated images when subscribed. No forced DISPLAY/X-forwarding or vendor edit
needed just for browser viewing. Keep sensor launch and laptop tunnel running;
use another robot SSH session to source ROS and start personal server with --ros,
then refresh colour/YOLO views and inspect output. Do not start duplicate camera.

Latest pasted diagnostics show `ROS_MASTER_URI=http://localhost:11311` and no
matches for the requested master/core/YOLO/Astra process query. Together with the
failed master query, consistent with those ROS programs not started, not a stale
remote master address. No configuration change required by this evidence.

In the existing robot SSH terminal, source workspace and start the known general
YOLO wrapper (includes camera, not base in copied launch):

```bash
source ~/wheeltec_robot/devel/setup.bash
roslaunch darknet_ros yolo_v3.launch
```

Keep it running; roslaunch normally starts its local master when absent. No
separate roscore, second camera driver, mapping/navigation or motor launch needed.
Copied detector has GUI-disable/no-X handling, but actual installed headless path
is not yet validated. Send errors rather than enabling X forwarding/GUI or editing
the original configuration blindly.

Once camera/detector startup appears healthy, use another robot SSH shell (open
from a fresh local PowerShell with `ssh wheeltec@192.168.0.100`), leaving the
existing laptop tunnel intact. Run:

```bash
source ~/wheeltec_robot/devel/setup.bash
python -u ~/fahad/remote_dashboard/server.py --ros
```

Only one dashboard process may use 8765; the earlier preview should already be
stopped. Refresh laptop browser at `http://127.0.0.1:8765/` and expect ROS viewer
read-only mode, then select colour/YOLO. No live stream success is established
until new output/screenshot. LiDAR remains optional later; no scan is expected if
its driver is not started. All dashboard driving controls remain motor-free.

ROS inventory result: user reports `Unable to communicate with master`. Sourcing
the workspace sets the shell environment; it does not start ROS master or drivers.
Error means the configured master is unreachable from that shell, with no proof
yet whether stopped, wrong address or another issue. In the robot shell inspect:

```bash
echo "$ROS_MASTER_URI"
pgrep -af 'rosmaster|roscore|darknet_ros|astra_camera'
```

No output from pgrep is useful evidence, not a need to reset software. Compare URI
with actual local configuration before launch/environment edits. Once absent
master/drivers and correct local URI are established, the known general YOLO
wrapper can start camera/detector (and roslaunch can start a local master). Do not
use bare default darknet_ros.launch (gesture configuration), launch a second camera,
or start mapping/base/navigation just to fix this error. Keep tunnel available;
starting the ROS viewer before a reachable master can wait at initialization.

User screenshot now confirms the dashboard preview is visible in the laptop
browser: PREVIEW ONLY/no-camera and motor-disconnected banner match the expected
NO-ROS mode. This is not a camera/scan failure; no actual sensor data were requested.
Page-hidden rehearsal-disable message is expected. Do not start a second server
on the same port, duplicate drivers or enable motors to obtain a picture.

Next inspect existing ROS streams on the robot. Keep the laptop tunnel terminal
open. In the robot terminal running the personal preview, Ctrl+C stops that
server (not other robot controllers); the webpage may temporarily disconnect.
Then run these read-only checks:

```bash
source ~/wheeltec_robot/devel/setup.bash
timeout -k 2s 10s rostopic list
```

Share the topic list or error before selecting an existing camera/YOLO publisher
or starting the appropriate sensor-only wrapper. If no master, `--ros` server
startup may wait; do not start mapping/base/navigation just to create a master.
ROS viewer/sensor operation remains unverified at this milestone.

Confirmed latest milestone: user supplies robot terminal listing of
`~/fahad/remote_dashboard/` with server/control/browser asset directory and
successful NO-ROS startup output on `127.0.0.1:8765`. Program is now present and
running on robot in preview/no-motor mode; browser and ROS operation still pending.
Exact Python version, transfer method and host-key comparison not captured.

Keep that server terminal open. In a SEPARATE laptop-local PowerShell tab (not
inside the robot shell), open:

```powershell
ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 -o ExitOnForwardFailure=yes -o ServerAliveInterval=5 -o ServerAliveCountMax=3 wheeltec@192.168.0.100
```

Enter Ubuntu login credentials locally if prompted; do not bypass unexpected
host-key warnings. A quiet/no-prompt terminal after login is normal with `-N`;
leave it running, then visit `http://127.0.0.1:8765/` on the laptop. Expect preview
mode with no camera/scan yet. Do not use `192.168.0.100:8765` directly: robot server
is loopback-only. Address-in-use, connection or key errors should be reported,
not handled by disabling firewall/authentication or exposing a public listener.

Next deployment instructions prepared on user's request to continue: finish SSH
host-key/login check, keep robot SSH and local PowerShell tabs distinct, check
for an existing personal dashboard directory before copying with scp from the
Windows project, then first test the robot-hosted NO-ROS preview over an SSH
tunnel. This isolates Python/page/network problems before sensor imports. Exact
commands in `Tools/remote_dashboard/README.md` under Lab restart. No successful
SSH-login output, actual copy, robot-hosted server or webpage has been supplied;
do not treat issued instructions as a completed deployment. No motor/boot changes.

Latest result: user reports TCP test to `192.168.0.100:22` succeeded after running
the PowerShell command from CMD. Laptop local reachability to an SSH-port listener
is now user-confirmed; host identity/login and dashboard copy/start remain pending.
User requests an explanation of shells before continuing, not further access.
`Test-NetConnection` is a PowerShell cmdlet, not a built-in CMD command; use a
PowerShell window or invoke `powershell -NoProfile -Command "Test-NetConnection
192.168.0.100 -Port 22"` as one line from CMD. The initial CMD error did not test
robot connectivity. No remote login, new service or configuration change occurred.

User now reports being connected to WHEELTEC Wi-Fi with no internet; connecting
device and SSID/IP route are not independently confirmed. An offline AP may still
provide the required local link. If the WINDOWS LAPTOP is connected, run a scoped
read-only TCP check in its PowerShell:

```powershell
Test-NetConnection 192.168.0.100 -Port 22
```

This address comes from the supplied robot report, not a guessed factory default.
`TcpTestSucceeded: True` establishes a reachable SSH-port listener at that address,
not verified robot host identity/login/internet or an active dashboard. Inspect
the result before SSH host-key verification/login. If only the phone is connected,
the laptop is not thereby connected. No dashboard webpage is available until the
program is copied/started and its SSH tunnel is opened. Do not switch OS/ROS/network
settings or launch motion while checking connectivity.

Latest clarification: user reports recovering the Ubuntu credential, but only
suspects the Wi-Fi credential matches; verify locally and do not record either
credential in project files. Earlier forgotten-password status below is historical.

For keeping internet while using the robot AP, the simplest initial arrangement
is laptop connected to the robot Wi-Fi for SSH/dashboard and phone using mobile
data for chat. Do not join the phone to an offline robot AP if relying on it for
internet. Only connecting the phone to robot Wi-Fi does not make the laptop able
to reach the robot; current dashboard is loopback-only with an SSH tunnel, not
direct phone-browser LAN access.

If internet must remain on the laptop too, assess phone USB cellular tethering
while laptop Wi-Fi reaches the robot (device/carrier/data-policy/drivers/routing
dependent), or robot Ethernet plus laptop internet Wi-Fi if ports/adapters and
addressing permit. Simultaneous links are not a guarantee of correct default-route
selection; inspect failures before changing routes/metrics or enabling sharing.
No tethering, Internet Connection Sharing, network/route or firewall change made.

User subsequently reports also forgetting the Ubuntu account password. If the
existing desktop session is still logged in, retain it during setup; no logout,
reboot, password reset or account/network change is needed for the next read-only
attempt. After matching the profile SSID, the same narrow saved-PSK query can be
tried without sudo under the current account's existing permissions:

```bash
nmcli --show-secrets -f 802-11-wireless-security.psk connection show "Wi-Fi connection 1"
```

This may show the key or remain hidden/deny access. It is not a permission bypass
or a guaranteed recovery method. Keep output local. If authorization/login is
required, ask the lecturer/lab administrator for the authorized account/network
access procedure; do not guess credentials or reset a shared lab account.
SSH password login also remains unresolved unless an already-authorized working
key exists; no key has been identified or created. No account recovery performed.

Live report `Terminal Reports/report_1531_19102026.txt` confirms `wlan0` connected
using profile `Wi-Fi connection 1`, `docker0` connected, Ethernet unavailable and
SSH service `active`. `hostname -I` lists `192.168.0.100` and `172.17.0.1`. The first
is a candidate robot LAN address; the second is consistent with Docker but the
report does not explicitly map addresses to interfaces. SSH active does not prove
laptop reachability or successful login; no internet or AP-host confirmation.

Identify the actual SSID and operating mode without printing secrets:

```bash
nmcli -f 802-11-wireless.ssid,802-11-wireless.mode connection show "Wi-Fi connection 1"
```

If the SSID matches the intended authorized `WHEELTEC_CAR_5.5` network, the operator
can inspect its saved PSK locally on the robot:

```bash
sudo nmcli --show-secrets -f 802-11-wireless-security.psk connection show "Wi-Fi connection 1"
```

This is read-only and reveals only that profile's PSK, not all saved secrets.
Any sudo prompt asks for the robot Ubuntu account password, not the unknown Wi-Fi
password. Enter it locally; ask lab staff if that login/permission is unavailable.
Do not upload this command's output or screenshots to chat or a shared report.
If empty/hidden, access-denied, non-PSK authentication or a different SSID, inspect
the error/network identity or ask the lab owner rather than reset/change settings.
`ap` mode means this Wi-Fi interface hosts an AP; `infrastructure` means it joins
an AP (possibly an onboard separate router). Either can support the local link;
neither proves internet. Match identity before selecting the laptop network.

User screenshot shows the secured SSID `WHEELTEC_CAR_5.5` on the laptop, but the
password is unknown. This is a candidate robot Wi-Fi name, not proof of AP host
identity, internet, successful association, usable IP or SSH availability.

On the stationary robot, inspect active profiles without printing secrets:

```bash
nmcli -f NAME,TYPE,DEVICE connection show --active
```

Saved connection profile names can differ from the SSID. If the active AP profile
is identified as the robot-hosted network, its saved Wi-Fi security settings may
allow the authorized operator to view the existing password locally through the
connection editor. Ask the lab owner if credentials are managed externally or
unavailable. Do not send password output/screenshots to chat, guess unrelated
factory defaults, edit/reset the password, or change networking during motion.
No credential recovery or robot configuration change has been performed here.

## Implementation started: 2026-10-15 (supersedes feasibility-only status below)

User explicitly prioritises programming the remote interface before the next
fusion experiment so the robot can operate without a tethered monitor in approved
indoor test areas. First local prototype is in `Tools/remote_dashboard/`; follow
its `README.md` for the exact copy/run/SSH-tunnel workflow and limits.

It provides a browser UI, optional read-only ROS RGB/YOLO/scan subscriptions and
motor-free driving rehearsal. There is deliberately NO motor publisher, process
launcher or boot configuration. ROS viewing/live robot performance remain untested;
physical driving and power-on-to-browser startup are not complete. Earlier
feasibility candidates web_video_server/rosbridge are not prerequisites for this
implementation: it uses existing ROS/cv_bridge/OpenCV plus Python's local HTTP
server. Loopback-only access over an SSH tunnel avoids a public HTTP/control port;
SSH/local-link confirmation is still the first deployment prerequisite.

31 Python and 12 fake-DOM frontend tests passed locally; browser display/source
selection/enable/release-to-disable checked. See changelog for verification scope.
Stable thesis perception/fusion scope remains; operator-interface work is now the
current implementation priority. This is not adoption of autonomous navigation,
outdoor/field readiness, model training or a new detector.

## Power-on-to-browser operation: proposed workflow, 2026-10-15

User asks whether the final workflow can be power on, join the robot network and
open the website, without first attaching a monitor. Yes in principle: headless
operation with boot-managed services can provide this. This is not evidence that
the current robot already boots a working AP, ROS stack or website; no startup
change is authorized by the feasibility question.

Proposed behavior after a one-time setup and validation:

1. Robot boots, makes the approved local network available and starts the dashboard
   backend plus the chosen ROS/camera/LiDAR/detector services without a desktop
   login. Service ordering must account for real sensor/serial/network readiness,
   permissions and ROS environment, not rely solely on a fixed delay.
2. Laptop joins the verified network and opens a bookmarked, stable local address.
   Choose addressing/name resolution after checking the existing AP, not by
   applying an unverified static IP. No internet/cloud dependency is required.
3. Authenticated/authorized operator sees live status (starting/ready/error and
   fresh/stale data) and video. Startup and reconnect leave driving disarmed;
   a deliberate enable plus hold-to-drive are required after health/stop checks.
4. Lost commands/connections, app restart or controller fault must return to the
   verified stopped/disarmed state. Automatic service restarts must not replay
   motion commands or restore a previously armed state. Retain independent physical
   stopping and SSH/monitor recovery; provide an orderly shutdown route.

An Ubuntu system service (typically systemd) is a candidate for boot supervision,
logs and controlled restart. A per-user desktop Startup Applications entry alone
does not demonstrate startup without login. Inspect existing boot services and
vendor launch behavior before adding anything, to avoid duplicate drivers/base
controllers and launches that reset mapping data. Initial boot tests should be
read-only/perception-only with motion inhibited through a verified method.

Copied `darknet_ros/config/ros.yaml` defaults `image_view/enable_opencv` true;
`darknet_ros/src/YoloObjectDetector.cpp` reads that parameter and turns off its
window when XOpenDisplay fails. This supports a candidate headless route, not
proof that the installed binary and complete launch work without a monitor.
Explicit personal GUI-disabled configuration and no-monitor reboot verification
remain necessary. No boot-time/latency estimate is established.

First validate manual remote operation, then automate only the validated launch
set. Repeat power-on/no-monitor, unavailable sensor, Wi-Fi loss and recovery tests
before calling this a reliable workflow. No service/unit/script or dashboard has
been created, enabled or run on the robot.

Primary reference: [Ubuntu systemctl manual](https://manpages.ubuntu.com/manpages/jammy/man1/systemctl.1.html)
describes service enablement; exact directives must match the robot's installed
systemd version, not be copied from a newer distribution without review.

## Movement controls in the same interface: feasibility only, 2026-10-15

User asks whether the proposed camera interface could also control movement.
Technically feasible, but no driving, motion launch, command publication or
dashboard implementation is authorized by this question. Manual remote driving
(teleoperation) is separate from autonomous navigation and object avoidance.

Evidence: saved October topic inventory identifies `/cmd_vel` as
`geometry_msgs/Twist`, with `/wheeltec_robot` subscribing. Copied
`turn_on_wheeltec_robot/src/wheeltec_robot.cpp` subscribes to `cmd_vel` and forwards
linear/angular commands over serial to the lower controller. Copied
`wheeltec_robot_rc/launch/keyboard_teleop.launch` remaps its keyboard output to
`/cmd_vel`. These establish an existing command interface in the copied software,
not a tested current base/motor connection or confirmed stopping behavior.

A future browser interface could combine video with forward/reverse, steering
and stop controls. Use Ackermann-compatible controls: this chassis turns in arcs,
not sideways or by spinning in place. Browser-to-ROS communication can use a
version-compatible ROS 1 bridge or a narrowly scoped backend; the robot must
enforce command validation, speed limits, a single active controller and stale
command rejection. Do not expose unrestricted ROS publishing publicly.

Before any supervised movement test, establish an independent physical stop
method and clear test area. Proposed requirements are hold-to-drive/release-to-
stop, low robot-enforced speed limits, explicit enable state and no automatic
resumption on reconnect. A robot-side watchdog must stop on lost/stale commands
even if the browser crashes or Wi-Fi disappears; browser release/close events
and Ctrl+C are not sufficient. Verify lower-controller timeout behavior too:
the inspected serial callback alone does not establish a firmware watchdog.
A normal screen Stop button is not a certified physical emergency stop.

Check current base health and competing publishers first; earlier missing
odometry/serial evidence remains unresolved. Test command gating/timeouts without
motion using an appropriate verified motor-inhibited setup, then low-speed,
line-of-sight operation with a nearby supervisor/physical stop. Delayed/frozen
camera video must not be the sole safety feedback. Camera/LiDAR display or person
detection does not itself add automatic collision avoidance.

Suggested sequence remains local networking, read-only video, then a separately
approved teleoperation test/interface. No new autonomous-navigation requirement
or change to the agreed perception/fusion thesis scope has been adopted.

Primary reference: [ROS 1 rosbridge README](https://github.com/RobotWebTools/rosbridge_suite/tree/ros1)
documents browser-compatible ROS communication, not built-in motion safety or
confirmed installed availability on this robot.

## Camera on the laptop: feasibility discussion, 2026-10-15

User believes the robot broadcasts its own Wi-Fi (SSID, mode and reachability
remain unverified) and asks whether an app could display the camera instead of
requiring a monitor attached to the robot. This is a feasibility discussion, not
authorization to implement a dashboard, install services or change startup.

A local browser viewer is the proposed first approach: the existing Astra/YOLO
nodes stay on the robot, an image-streaming service subscribes to an existing ROS
image topic, and a laptop browser receives the stream over the local link. This
does not require internet once the necessary software is present. It does not
require installing ROS on the Windows laptop or moving inference to the laptop.

The user's saved command sheet already mentions `web_video_server`; see section
13 of `ROS_COMMON_FUNCTION_COMMANDS_5_5_EN.md`. Its example starts `usb_cam`, which
must NOT be copied for the active Astra setup. Documentation mentioning a package
does not establish that it is installed on this robot. The project's upstream
`ros1` branch provides an HTTP image-topic viewer and MJPEG streaming; the current
default branch is ROS 2, so do not blindly install/build the latest branch on
Melodic. Installed version, dependencies and legacy compatibility need checking.

Candidate first views are `/camera/rgb/image_raw` and
`/darknet_ros/detection_image`, already demonstrated in earlier reports. An
illustrative route is `http://<actual-robot-IP>:8080/`; the address is a placeholder,
not an actual tested endpoint. Plain raw depth needs a meaningful visualization
and units/range legend; LiDAR/map displays need a separate integration layer.
Showing camera video does not automatically provide RViz, calibrated fusion,
recording or robot driving controls.

After confirming the local link and SSH, inspect package presence on the robot:

```bash
source ~/wheeltec_robot/devel/setup.bash
rospack find web_video_server
```

If missing, retain the error and review an isolated setup rather than installing
or upgrading the robot OS. Start with one modest-rate/resolution stream; measure
added CPU/network load and detector responsiveness before adding panels. Wi-Fi
video can lag or freeze, so it is an observation aid, not safe driving feedback.
Use a trusted local link or reviewed SSH tunnel; do not expose an unprotected
HTTP camera server publicly or disable firewall protections.

Removing the external monitor also requires starting/stopping the required ROS
nodes remotely and checking that their graphical windows can be disabled or are
not required. Plain SSH does not display RViz/OpenCV windows. Existing desktop
helpers are not automatically converted into browser apps; a remote-desktop route
could be evaluated separately if full desktop access is desired. Keep the monitor
available until a reboot-to-connected-view workflow is actually tested. No
streaming/app/headless runtime has yet been implemented or verified.

Primary sources checked: [upstream ROS 1 README](https://github.com/RobotWebTools/web_video_server/tree/ros1),
[ROS 1 server source](https://github.com/RobotWebTools/web_video_server/blob/ros1/src/web_video_server.cpp),
[Melodic API documentation](https://docs.ros.org/en/melodic/api/web_video_server/html/web__video__server_8cpp.html).

## Current restart point: 2026-10-15

User reports the robot has no known internet connection and asks for an alternative
to repeated SSD transfers. No local network/IP/SSH connectivity has yet been
demonstrated. Internet access and local device-to-device connectivity are different:
files/terminal sessions can use a reachable local link without an internet uplink.

Prepare WinSCP on the Windows laptop from its official site while laptop internet
is available, if desired. This laptop is the client; a Windows SSH **server** is
not needed for the proposed laptop-to-Ubuntu connection. Do not install/enable any
robot service or change network settings before inspecting the current state.

First checks on the robot desktop, while stationary:

```bash
nmcli device status
ip -br address
systemctl is-active ssh
```

These inspect interfaces, link/IP state and service status without exposing saved
Wi-Fi passwords, enabling SSH or changing connections. If nmcli is unavailable,
share that error and inspect the desktop network menu; do not install a new
network manager. Select the actual shared-network address, not loopback/Docker
addresses. The manual's 192.168.2.102/192.168.0.100 examples are not a verified IP.

Possible routes, selected only after inspecting the network and lab policy:

- Existing robot access point, if it actually exists: laptop joins that local
  Wi-Fi. Do not assume its SSID/password from another WHEELTEC model. Joining an
  offline robot AP may disconnect laptop Wi-Fi internet, affecting this chat;
  plan a permitted second connection if needed.
- Approved lab/private router Wi-Fi or Ethernet: both devices obtain a reachable
  local address. Campus/guest Wi-Fi may isolate clients even on the same SSID.
  Ask lab IT rather than disabling firewalls, certificate checks or isolation.
- Personal hotspot, only if lab rules permit and the hotspot allows clients to
  communicate: can provide a shared link, with internet only if its uplink works.
  Device-to-device reachability is not guaranteed for every hotspot configuration.
- Direct Ethernet cable: no internet uplink required, but addresses may need an
  agreed configuration; it is not guaranteed plug-and-play DHCP. Laptop Wi-Fi can
  potentially remain on the university internet while Ethernet reaches the robot.
  Check actual ports/adapters, routes and addressing before making changes.

Prefer a trusted local link and existing SSH over exposing an old robot OS to the
public internet. No public port forwarding or unreviewed initssh/network scripts.
Changing interfaces/IP can affect ROS connectivity; preserve current settings
and review ROS network assumptions before modifying them. Do not assume existing
remote ROS nodes survive a connection change or loss.

Once reachability/service are confirmed, use SFTP/WinSCP with the actual robot
IP, account and normal SSH port (usually 22). Enter credentials locally, not in
chat. Verify the host-key fingerprint as described below. Transfer explicit files
between the laptop project folders and `~/fahad/tools`/`~/fahad/reports`; avoid
delete/mirror synchronization and vendor directories. Standard SSH gives a remote
terminal, not automatic RViz/OpenCV graphical forwarding. Keep GUI work on the
robot desktop initially; file transfer does not give this assistant direct robot
control or visibility into uncopied remote files.

For today's session, try an approved local connection first for approximately
15-20 minutes; if it needs IT/configuration work, SSD remains the fallback so the
sensor experiment can proceed. No connection, installation or firewall/network
change has been performed by preparing this guidance.

Primary references refreshed: [WinSCP connection guide](https://winscp.net/eng/docs/guide_connect),
[host-key verification](https://winscp.net/eng/docs/ssh_verifying_the_host_key),
[Ubuntu OpenSSH](https://documentation.ubuntu.com/server/how-to/security/openssh-server/),
[Microsoft terminal SSH](https://learn.microsoft.com/en-us/windows/terminal/tutorials/ssh).

Proposed 2026-10-08 to replace repeated external-SSD transfers for small reports/scripts. Connection not tested; no software installed, services enabled, firewall rules changed or credentials collected.

## Recommended arrangement

Use WinSCP with SFTP for graphical file transfer and Windows OpenSSH for the robot terminal. Both use the robot's SSH service. Internet is not required for local transfers after setup, but the two devices must be able to reach each other on the local network. Being on the same campus Wi-Fi does not guarantee connectivity: client isolation or separate networks can block it. Use an approved lab network or ask lab IT; do not disable security controls or expose SSH through public router forwarding.

The external SSD remains useful for large raw datasets or backups. GitHub is not needed for this workflow and the unsanitized robot source should not be uploaded publicly.

## First: read-only checks on the robot

```bash
hostname -I
whoami
systemctl is-active ssh
```

`hostname -I` can list more than one address; select the address on the network shared with the Windows computer, not an arbitrary Docker/private bridge. `whoami` provides the login account name. `active` indicates the service is running, not that Windows can necessarily reach it. If inactive/missing, inspect the result before installing or enabling anything. Do not change the network during robot motion.

## File transfer using WinSCP

Install WinSCP on Windows from its official site if desired. Configure a new connection with SFTP, the verified robot address, SSH port (normally 22), robot username and its existing login password. Never paste the password or private SSH keys into chat.

On first connection, compare the presented SSH host-key fingerprint with the corresponding public host key displayed locally on the robot; do not blindly accept an unknown/mismatched host. For example, if the connection offers ED25519 and that key exists:

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

After verification, browse `/home/wheeltec/fahad/reports/` to copy reports to the Windows project `reports` folder. Upload personal scripts into `/home/wheeltec/fahad/tools/`. Adjust these paths if the actual robot username/home differs. Start with explicit copy operations; avoid delete/mirror synchronization and accidental overwrites of vendor files. Files copied to Windows become available to this workspace only when placed inside its project folders.

## Remote terminal

In Windows PowerShell, replace the placeholders below with the observed account and address:

```powershell
ssh ROBOT_USERNAME@ROBOT_IP
```

After logging in, commands run ON THE ROBOT even though the window is on Windows. Terminal output can then be copied directly into chat. Source the robot workspace when ROS commands require it. Plain SSH is a terminal, not automatic graphical forwarding of RViz/camera windows. Use `exit` to return to the Windows shell; do not assume remote processes survive disconnection.

## Sources

- [WinSCP quick start](https://winscp.net/eng/docs/getting_started)
- [SSH host-key verification](https://winscp.net/eng/docs/ssh_verifying_the_host_key)
- [Microsoft Windows Terminal SSH](https://learn.microsoft.com/en-us/windows/terminal/tutorials/ssh)
- [Ubuntu OpenSSH server](https://documentation.ubuntu.com/server/how-to/security/openssh-server/)
