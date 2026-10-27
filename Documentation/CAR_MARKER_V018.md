# v0.18 — visible car and operator-reported front preset

27 October 2026, contract before implementation. The supplied v0.17 recording
shows scan-only data, a laser-origin square and the heading-unknown message.
No manual front mark is selected in the inspected playback. The user wants the
central marker itself to be a recognisable car and forward to mean screen-up.

- Replace the fallback square in the current `laser` frame with a visible car,
  using an explicitly unverified display preset based on the user's reported
  south-facing physical nose. The preset is heading pi relative to laser +X in
  the original unrotated top view. It is NOT a measured body transform. Front-up
  rotates all scene geometry consistently, not just the car. No sensor mutation.
- Pose precedence: existing fresh body TF, explicit session mark, then the
  operator-reported `laser` display preset. Other frame IDs remain unknown until
  marked; a map still requires its own fresh body pose, never this scan preset.
- Front-up starts enabled, but free orbit/pan still exits it. Add a scan-only
  Flip front display correction for a reversed preset, disabled when TF supplies
  the pose or the scan is stale. Reset/front restores front-up. Clear mark restores
  the reported preset, not calibration. Neither command flips nor speed changes.
- Recognisable top-down car: shaped body/bonnet, cabin/windscreen, four distinct
  tyres, yellow front lamps/beams, red rear lamps and an explicit FRONT arrow.
  Keep its on-screen size bounded and readable independently of view zoom/pitch.
  Use the same glyph in scan/map and legend; do not show a second square over it.
- A centred live scan is robot-relative: the car stays centred and nearby static
  obstacles move down when approached. Do not invert physical obstacle motion to
  imitate travelling up a fixed room map. Actual map travel needs valid pose/TF.
  User clarified a fixed, growing, later-saveable room map for object labels.
  Add a preferred Fixed map display mode for existing valid /map snapshots;
  preserve world/grid orientation instead of centring/rotating with the car.
  Missing /map falls back explicitly to the current front-up scan. Actual SLAM,
  map saving and object-map association are NOT supplied by this display change.
- This is a UI-only change. No odometry integration, fake SLAM, PID, drive API,
  autonomous controller, motor limits or calibration/TF changes are in scope.

Check pure projection/sign rules, heading precedence/unknown frames, stale/reset
behaviour, screen-size bounds, glyph render paths and input isolation with fake
canvas tests plus the offline quality workflow. Real heading/preset accuracy and
appearance need stationary user validation after installation. The recording is
not a synchronized command/odometry dataset and is not published.

Verification result: `tmp/quality_reports/20261027_130622_8824ec82/summary.md`
is attention-required: Tools106pass, Dashboard263pass/one Windows10053 HTTP error,
Hub53pass/one Windows symlink skip. All JavaScript/static checks pass, including
new geometry/preset/fixed-map cases. No retry hides the historical HTTP abort.
Local synthetic native-canvas output inspected via existing @napi-rs/canvas;
no new package install, browser success or physical alignment is claimed.
