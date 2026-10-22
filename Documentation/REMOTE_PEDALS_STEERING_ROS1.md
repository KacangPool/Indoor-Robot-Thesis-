# v0.8 · held travel keys/pedals and separate steering

Superseded by `REMOTE_RAMPED_PEDALS_V09.md` (2026-10-22): slider removed,
ramped held travel, fresh-press Enable and provisional .12 reported-speed guard
with unchanged .10 command ceiling. The v0.8 description below is historical.

Prepared 2026-10-22. Local implementation; no live robot login, deployment or
motion by tools. Original viewer and previous circular/independent layouts remain.
Use the new **Pedals + steering** layout, selected by default on a fresh v0.8 page.

## What the recording establishes

User's `C:/Users/fahad/Videos/20261022_092317.mp4` is about 80 seconds, 1920×1080.
Visual samples show Circular selected, e.g. throttle about 25%, steering 97%,
requested travel 0.015 m/s. Circular axis coupling explains that low request while
turning. Later samples show repeated stopping/Enable transitions. The diagnostic
reason is below the recorded viewport; the images do not establish whether the
actual cause is lost capture/focus, heartbeat/network, camera/odometry, speed
guard or worker timing. A browser zoom change is also visible, not proof of cause.
Requested speed and camera motion are not measured wheel speed/steering calibration.

The old source already retained a healthy session after ordinary release.
Therefore removing the Enable button alone would not diagnose these fault stops.
This update makes travel independent of joystick vertical/zero crossings and
puts the first browser stop reason beside Enable, without suppressing faults.

## Install and first test

1. Release all keys/pedals, click Stop, and verify the robot is stationary.
2. Close/reopen **Start Robot Hub.cmd**, Connect & prepare and confirm **v0.8**.
   The hub uses its established disabled/ready update checks and backups. A running
   old app does not reload new files automatically. Do not bypass an update refusal.
3. Reload the browser while stationary. Confirm v0.8 and **Pedals + steering**.
   Keep just one driving page enabled and watch the robot directly with the normal
   physical power-off reachable. Tick the setup acknowledgement, then Enable once.
4. Start with a brief low-speed straight hold/release. Confirm physical stop before
   steering or reverse. Collect the displayed reason if controls disable; do not
   repeatedly re-enable and guess. Do not test link loss with an unattended robot.

## Controls

| Input | Requested action |
| --- | --- |
| Hold W or ↑ | Forward at the selected travel speed |
| Hold S or ↓ | Reverse at the selected travel speed |
| Release travel key/pedal | Zero/brake request and stationary-feedback check; retains healthy idle session |
| Hold/press B or on-screen Brake | Zero/brake request; blocks travel while brake held; requires a fresh travel press afterward |
| Drag steering pad left/right | Steering curvature only; vertical drag ignored, no throttle change |
| Release steering normally | Centres steering; **a still-held travel key/pedal continues requesting travel** |
| Space or Escape / Stop | Full software stop/disable; deliberate Enable required after readiness returns |

The speed slider selects **0.03–0.10 m/s request**, default 0.06. It cannot change
while a travel pedal is held. This is a held speed setpoint, not a latched cruise
control, physical accelerator ramp, active mechanical brake or measured speed.
Steering keeps that requested speed instead of reducing it near a circular corner.
At rest the pad sets a steering request for subsequent travel; this does not add
a standalone stationary wheel-angle command. Existing curvature <=1/m remains,
so no promise of a tighter physical turning radius. No sideways/in-place spin.

Choose the speed while stationary, then hold travel and steer. After travel
release, steering grip may remain held through normal braking, but travel requires
fresh input after stationary feedback. A press made during braking is discarded,
not queued. Changing forward/reverse while held or pressing conflicting travel
inputs brakes first; release them and press again after feedback. Repeated keys
and keys still held through a fault/re-enable do not restart travel.

### Phone / touch

Hold an on-screen Forward or Reverse pedal with one finger, and steer with a
second finger. The touch IDs are separate. Release the travel finger to request
stop; normal steering release centres the request without ending a still-held
pedal. A cancelled/lost captured input disables the session. Held Brake takes
priority. Phone connectivity still needs its own trusted connection: this update
does not expose a LAN/public server or make laptop localhost reachable by phone.
Actual multi-touch behaviour on the user's device still needs testing.

## Enable, checkbox and diagnostics

Initial Enable and re-enable after a genuine fault remain. A checked box can stay
checked after focus, input or network loss; it is not a dead-man control. Unticking
always requests Stop. Ordinary travel release/B brake preserve healthy permission,
not an old held intention; no automatic re-arm or reconnect/resume is added.

Lost focus/capture, stale camera/status/odometry, graph/connection/sequence faults,
expired heartbeat and worker scheduling still disable. The first browser reason
now stays in a visible alert beside Enable; backend reason/history remain under
**Why did driving stop?** and in the hub status export. Copy both after a recurrence.
Enable clears the alert deliberately; generic status text does not erase it.

The recording confirms symptoms, not a root-cause fix. The 0.10 m/s request ceiling
and existing reported-velocity guards/lease/freshness/cleanup are unchanged.
Independent firmware/host/serial-fault stopping is still unverified. Software
Stop is not a physical emergency stop; use reachable physical power-off if abnormal.
Do not lift a moving robot. Shutdown/disconnection remains as documented in
`ROBOT_HUB_V07_OPERATING_NOTES.md`; closing the hub leaves remote ROS services.

## Verification and limits

- 235 dashboard Python fake-ROS/loopback tests pass, including constant travel
  across steering and brake/new-motion reversal checks.
- 90 JavaScript checks: 69 main fake-DOM, seven geometry and 14 historical
  one-shot. New cases cover simultaneous keys/steering, independent touch travel,
  preserved steering through normal braking, release semantics, held/opposite/
  modified/editing keys, brake priority, cancellation, visible alert and no replay.
- 45 hub tests run, 44 pass and one Windows symlink-privilege case skipped.
  Includes encrypted localhost fake SSH/tunnel and deployment/ownership guards.
- JS syntax and Python 3.6 grammar checked. Actual Jetson Python 2 execution,
  native browser pointer/keyboard/touch behaviour, new physical response and the
  user's dropout cause are not verified. No fresh foreground GUI automation was
  used, to avoid interfering with a potentially active robot-control page.

Temporary visual-analysis frames/contact sheets are under
`tmp/drive_video_20261022_review/`; the original MP4 was not changed. Frames are
diagnostic artifacts, not new training labels or a training dataset.
