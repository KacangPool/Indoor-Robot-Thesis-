# v0.9 · ramped held travel, fresh-press Enable and clearer faults

Superseded by `REMOTE_COCKPIT_V010.md`: current source has a .30 m/s ceiling,
five-second S-curve and recording cockpit. This file records historical v0.9.

Prepared 2026-10-22. Local source only; no robot deployment or physical testing
by tools. This supersedes v0.8 fixed-speed/slider and always-separate Enable
instructions in `REMOTE_PEDALS_STEERING_ROS1.md`.

## Findings from the second recording

`C:/Users/fahad/Videos/20261022_094909.mp4` is about 109.27 seconds, 1920×1080.
Twelve sampled large frames and one-per-second control-panel contact sheets were
extracted without modifying the original MP4. Visual samples confirm separate
pedal/steering use, 0.06 and later 0.10 speed settings, and the generic message
**Heartbeat failed or expired. Session disabled.** A later sample clearly shows:

`Unexpected reported speed (vx=-0.102 m/s, vy=0.000 m/s, yaw=-0.038 rad/s); stop`

The previous longitudinal feedback guard was |vx|>0.100. This establishes one
guard-triggered disable. The slider shows .08 in that frame and earlier .10;
the image does not prove matching command/odometry timestamps, calibrated wheel
speed or why the reported overshoot occurred. Generic heartbeat text still does
not identify the cause of every other stop. Contact is user-reported, not proof
of a collision sensor or contact-triggered protective algorithm. No audio analysis.

Two console tabs are visible. Source inspection also found automatic `stop()`
could send a global Stop while the page owned no session, including inactive
blur/connection events. This is a real cross-page interference possibility, not
proof it caused this recording's individual stops. Close old tabs for the update.

## What changed

- Slider removed. A held travel key/pedal ramps its **requested speed** from zero
  at 0.04 m/s per second, capped at **0.10 m/s** (about 2.5 s ideal time to ceiling).
  Per-update elapsed time is capped at .15 s, so a delayed browser does not jump
  ahead/catch up. Normal non-split joystick layouts and .03 buttons remain.
- From rest, hold W/↑ to ramp forward or S/↓ to ramp reverse. Mouse remains
  steering only. Touch held pedals also ramp; phone connection is unchanged.
- Press the opposite key during keyboard travel to decelerate the existing
  direction at 0.08 m/s per second. If the original key is released while the
  opposite remains held, that input continues braking, **not reverse**. At zero,
  retire the motion, request neutral and await existing stationary feedback.
  Release and press afresh for reverse. If the braking key is released while the
  original travel key remains held before zero, the valid original input can
  accelerate again. Both W+S mean deceleration, **not cruise/latched speed**.
- Releasing all travel inputs or pressing B/on-screen Brake requests immediate
  zero; it does not ramp slowly through an emergency. Physical braking still is
  not guaranteed. A held Brake blocks new travel. Normal steering release centres
  steering while a held travel input can continue; travel release requests stop.
- With the physical acknowledgement checked and the existing status/image/
  stationary readiness satisfied, a **fresh travel press can explicitly Enable**
  and begin a new ramp. This is deliberate input, not automatic recovery. A held
  key across a fault, key repeat, an early press while unready, stale/hidden page,
  released/cancelled pending press or brake cannot queue later motion. Releasing
  during the asynchronous Enable cancels it and performs scoped cleanup.
- Browser Stop/Space/Escape explicitly disables and locks this shortcut. Deliberate
  Enable or untick/re-tick unlocks it; ticking alone never starts movement. The
  separate Enable button remains available for manual use/legacy layouts. A fault
  still disables, but once healthy/stationary it can be acknowledged by releasing
  and making a fresh travel press rather than hunting for the button.
- Command ceiling is **not raised to .30**. Longitudinal reported-speed fault
  threshold is provisionally **.12 m/s**, separate from .10 command ceiling, to
  provide bounded headroom for the observed -.102 report. This is an intentional
  .02 software-tolerance increase, not measured/calibrated safe speed. Lateral
  .04, yaw .15, curvature 1/m, lease .35 s, freshness, ownership, publication and
  worker/feedback checks remain. .121 longitudinal reports still fault.
- Authenticated HTTP 400 command rejections include a current control snapshot;
  frontend distinguishes backend rejection, timeout and connection failure. It
  no longer describes every rejection as an expired heartbeat. Origin/key/Host
  checks still reject before providing this payload. No secrets/generation are
  added to snapshots. Keep the detailed report after a recurrence.
- Automatic browser stops send only when this page has an active/pending session,
  and include owner/generation. Stale/different-owner cleanup cannot stop a newer
  session. Explicit browser/Hub operator Stop remains global. Pending-arm owner-only
  cleanup is supported without allowing another owner to stop a different session.
  Old v0.8 tabs still run old JavaScript until closed/reloaded: close them all.

## Update and first supervised test

1. Release travel, click Stop and verify actual standstill. Keep wheels clear,
   direct sight and normal physical power-off reachable. Do not bump objects as
   a stop test. Never lift a moving robot.
2. Close **all** old console tabs and close/reopen Robot Hub. Connect & prepare
   using the established safe-update/backup procedure; do not bypass a refusal.
3. Open one fresh browser console and confirm **v0.9**, Pedals + steering, no slider.
   Tick acknowledgement. When it says ready, a fresh W/S press can enable without
   a separate button. Release quickly for the first low-speed straight stop test.
4. Only after observing normal stop, try a somewhat longer hold/ramp, steering,
   and reverse from stationary with fresh input. B requests zero; Space/Escape
   disables/locks. Watch actual motion, not only the requested-speed number.
5. If it stops unexpectedly, release inputs, read/copy the visible reason and
   Why did driving stop details; save a Hub report. Do not repeatedly re-enable
   against contact or suppress an unresolved speed/connection/feedback fault.

This dashboard does **not** implement collision detection, obstacle avoidance,
costmaps, autonomous navigation or calibrated braking. LiDAR scan display is not
a motor interlock. A heartbeat/rejected-command stop after contact is not proof
of protection. Higher-speed/autonomous work needs separate stopping/obstacle
evaluation, not removal of failure checks. Independent firmware/host/serial
failure stopping and command queuing remain unverified. .30 m/s is deferred,
not installed as a hidden setting or accepted as a confirmed operating limit.

## Verification

238 fake-ROS/laptop-loopback dashboard Python tests pass; 103 JS checks (80 main
fake-DOM, nine geometry/ramp, 14 historical one-shot) pass. 45 hub tests run, 44
pass and one Windows symlink-privilege case skipped. Cases cover ramp bounds/no
catch-up, gradual opposing-key braking/no reverse or replay, release/brake priority,
fresh healthy input Enable, async keyup/touch cancel/Brake/Stop during Enable,
unready/held-key blocking, explicit Stop lock, specific HTTP rejection/timeout,
inactive-tab no-stop and owner/generation Stop enforcement, .102 acceptance and
.121 rejection with unchanged .10 request cap. Python 3.6 grammar/JS syntax checked.
These are not live browser pointer, actual Jetson Python 2, physical acceleration,
braking distance or reliable contact/failure-stop tests. No foreground UI control
used, to avoid interrupting an active robot page; no preview server left running.

Reference frames are in `tmp/drive_video_20261022_second_review/`, not a training
dataset. Original MP4 is unchanged. No vendor/firmware/boot/network/model/map/
planner changes; personal trial runtime remains the same ten allowlisted files.
