# v0.17 — front-up display, not a mounting calibration

Contract recorded before implementation, 27 October 2026. User reports installing
v0.16 in the lab and observing physical front towards screen bottom. The supplied
scan-only screenshot has no body TF and shows the laser origin, not a body pose.
This observation does not establish a numerical laser-to-body transform.

- Front means the vehicle nose, not instantaneous velocity: reversing must not
  rotate the view 180 degrees. Front-up is a display-only camera rotation/centring.
- Prefer the existing fresh body pose: acquisition-time body-in-laser pose in
  scan mode, or existing fresh map-frame body pose in occupancy mode. Rotate all
  points, ray sketches, map cells and the glyph together. Preserve metric geometry.
- With no body TF, the user may click the physical front direction on a fresh
  scan-only top view. Store only a tab-session, scan-frame-bound display heading.
  Draw its illustrative car at the laser origin, explicitly not a body position,
  footprint or measured mounting calibration. Never export it as TF or fusion data.
- Manual marks expire on disconnect/reset of sensor state or scan-frame change;
  no local storage, ROS parameters, motion inputs or server state are modified.
  TF takes priority over a mark. A manual scan heading cannot orient a map.
- Front-up follows each available body pose without velocity/steering-command
  inference. Missing/stale pose or scan must not retain a claimed current heading.
  Free orbit/pan exits follow; zoom preserves it; reset returns to front-up when
  a heading exists. Marking front never starts or steers the robot.
- Make headlights, rear lights and a labelled FRONT arrow visually distinct.
  Unknown heading remains explicit until a pose or operator mark is available.

Verification: pure inverse/projection and follow tests, fake-canvas renderer and
input-isolation/freshness tests, existing frontend/Hub/bundle tests and the offline
quality command. Laptop checks cannot verify physical orientation, installed
Jetson behaviour, visual appearance or stopping. Lab check: driving disabled,
mark the nose direction once, verify a known obstacle relative to physical front,
and check zoom/orbit/reset. Actual mounting TF/calibration remains separate work.

Results: full offline report `tmp/quality_reports/20261027_124239_b2b44a74/summary.md`
passes (Tools106, Dashboard264, Hub53pass/one Windows symlink skip; frontend92 and
renderer/geometry checks). Earlier report `20261027_124108_77c3c9fc` retains two
outdated release-version assertions, subsequently corrected. Historical Windows
HTTP10053 remains unresolved, not fixed by this run. No physical/browser visual
validation of this release; user-observed installation applies tov0.16 only.
