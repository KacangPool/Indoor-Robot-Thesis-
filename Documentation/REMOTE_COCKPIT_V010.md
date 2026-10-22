# v0.10 — recording cockpit and S-shaped travel ramp

Superseded by `REMOTE_KEYBOARD_MAP_V011.md`: A/D steering, wider sensor panels
and optional read-only occupancy map. .30 ceiling retained; .40 request deferred.

2026-10-22. Local implementation, not yet deployed or physically validated.
User reports the previous ramp works well; this is an observation, not a measured
acceleration, speed, stopping distance or fault-stop test.

## What changes

- Desktop widths of at least 1100 CSS pixels use one viewport frame: readings
  left, framed/uncropped camera centre, LiDAR below it, controls right. Details
  expand inside the panels. Side panels may scroll; Stop stays pinned near the
  bottom of the controls. Smaller screens stack, rather than shrinking controls
  beyond usability. No cloud publication or robot networking changes.
- The held W/Up and S/Down keys and on-screen travel pedals use smoothstep:
  `speed = 0.30 * (3*t*t - 2*t*t*t)`, where t advances from 0 to 1 over five
  seconds of healthy held input. This is an S-curve, not a logarithm. Approximate
  requests: .0312 m/s after 1 s, .15 after 2.5 s, .30 after 5 s. Both signs have
  the same ceiling. Scheduler deltas cap at .15 s: no long-gap catch-up.
- Opposite-key/both-key deceleration stays .08 m/s/s, never crosses zero into
  reverse automatically. From .30, that gradual deceleration takes about 3.75 s
  in request space: **use release or B for an immediate zero request**, not S
  as an instantaneous brake. Actual physical stopping may differ.
- Release, B and explicit Stop bypass the easing and request zero. All existing
  lease, camera/odometry freshness, controller uniqueness, direction, sequence,
  generation, braking/stationary confirmation and fault-recovery checks remain.
- Direct-drag Circular/Independent layouts also have a .30 m/s ceiling but map
  drag directly, without the pedal S-curve. Six direction buttons remain .03;
  historical crawl/one-shot profiles are unchanged.
- Live-session feedback now faults above |vx|=.32 m/s or |yaw|=.35 rad/s;
  lateral .04 m/s unchanged. The unchanged curvature limit 1/m can request .30
  rad/s at .30 m/s, so retaining the old .15 yaw fault ceiling would reject a
  valid full turn. Headrooms .02/.05 are provisional software values, not measured
  safe limits. The adapter explicitly selects them; historical ManualFeedback
  defaults remain .12/.15. Status and diagnostic reports expose both limits.
- A new frontend against an old speed configuration stops instead of silently
  scaling pedal requests to the wrong limit. Close all old tabs before updating:
  old already-loaded scripts are not retroactively changed by a server update.

## Update and first use

1. Release travel, press Stop and confirm actual standstill.
2. Close all old robot-console tabs and the existing Hub.
3. Reopen `Tools/robot_hub/Start Robot Hub.cmd`; connect and choose Connect & prepare.
   The existing fixed personal-folder installer handles version/checksum/backup
   checks. Do not start a second driver or dashboard manually.
4. Open one console and verify v0.10. Remain stationary while checking sensors.
5. Start with brief straight holds/release in a clear level area, directly in
   sight with the normal physical power-off reachable. Check normal stopping
   before longer holds. Do not test by deliberately hitting objects or losing
   connection while moving. No collision/scan-based stop or avoidance exists.

Only requested velocities are displayed, not verified actual speed. Acceleration,
turning, braking distance, phone interaction and independent firmware/host/serial
failure stopping at the new setting remain unverified. This is supervised manual
teleoperation, not autonomous navigation or a certified safety system.

## Verification

239 dashboard Python tests pass (fake ROS and laptop-only HTTP); 45 Hub tests
run, 44 pass and one Windows symlink-privilege case skips; 107 JS checks pass
(82 frontend, 11 geometry/ramp, 14 one-shot). Tests cover the .30 command bound,
signed turns, expanded live feedback boundaries and unchanged legacy guards,
smoothstep timing/shape, scheduler cap, braking/release/fault handling, speed
configuration mismatch, unique DOM IDs and required UI-node preservation.

One full 239-test run passed. Later final repeats encountered a Windows 10053
loopback connection abort in different unchanged origin/key rejection tests;
the 23 speed/LiDAR tests pass separately. No assertions or access checks were
weakened to hide this intermittent transport failure.

Inspected motor-free preview and a conspicuously labelled disconnected visual
fixture at 1280x720; no page overflow, all four panels and joystick/Stop visible.
No actual camera or LiDAR data in this fixture. Screenshot:
`tmp/hud_v010_review/hud_1280x720_fixture.png`. The fixture server in that directory
rejects every POST and imports no ROS, SSH or physical driver. No fresh mobile,
native Hub GUI or physical robot QA was performed. Local Python 3.6 grammar
checks are not actual Jetson Python 2.7 execution.
