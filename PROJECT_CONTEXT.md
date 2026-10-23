# Bachelor thesis project context

## Working topic

Develop and evaluate a camera-based machine-learning system for detecting living beings during indoor search-and-rescue missions. The available robot is the deployment/test platform. User decision on 2026-10-14: use the working pretrained YOLO detector without custom training and focus implementation on camera-LiDAR association, spatial labels and evaluation, rather than a new detector architecture. Final thesis contribution/evaluation requirements still need lecturer alignment.

## Agreed implementation direction (2026-10-14)

- Main fusion work resumed2026-10-23: primary software/paper review confirms
  existing2Dlaser/camera people-fusion approaches, but no inspected package is a
  verified drop-in for this Melodic/low-camera robot. Keep existing YOLO; no new
  trained detector, custom training or third-party package installed. SPENCER/
  DR-SPAAM optional references; lightweight bearing/height-prior examples require
  caution. Research: Documentation/CAMERA_LIDAR_RESEARCH_2026-10-23.md.
- Offline fusion v0.1 now source-tested: pure3Dprojection/planar-cluster/evidence
  core; exact detector source-image keys, stationary/calibration/acquisition-age
  gates; geometric candidates stay unconfirmed, ambiguities rejected; optional
  independently confirmed registered object-depth patch can corroborate geometry.
  Marker is temporary surface observation only with timed laser-to-map TF, not
  occupancy/footprint/person persistence/SLAM or proven identity. Eight synthetic
  scenes,25fusion tests; full Tools97/dashboard261/Hub53+one skip pass. No real
  aligned recording, Jetson execution, sensor benchmark or live fusion yet.
  Existing raw-image YOLO versus rectified prototype inputs must be resolved by
  a validated later adapter, not assumed compatible. Contract/run guide:
  Documentation/FUSION_PROTOTYPE_V01.md. Existing motor/driver code unchanged.
- Current private planner source d125c32e9d9773b4b7db2c905789b9c8c17da8ba deployed
  successfully23 October (appgdep_6adb2fe627e48191b8cc6679cef03ea3); signed-in view
  confirms research/prototype progress while physical fusion remains blocked.
  Personal D1 records untouched. Shared-Wi-Fi testing remains a future lab task;
  Gazebo deferred. Occupancy-map grey is unknown, not confirmed traversable;
  existing-map geometry and separate semantic observation layer remain distinct.
- Follow-up 2026-10-23: Gazebo explicitly deferred, retained as optional future
  tool; campus Wi-Fi still parked. Copied-source inventory finds75 manifests and
  273 launch declarations (not confirmed installed/working capabilities). New
  bounded read-only robot inventory tool + shared parser and bundled-copy guide
  prepared; physical execution still pending next lab. Prioritise fresh /scan,
  sensor calibration/TF/time and validated camera–LiDAR association over demos.
- User authorizes ongoing private Fieldnotes maintenance from this chat, not robot
  control or public publication. Source-backed reviewed progress/calendar overlay
  preserves edited personal goals/notes and D1 data; new evidence panel distinguishes
  source-tested, user-observed and blocked work. Yesterday's modular/quality work
  already implemented locally, not confirmed installed on robot. Planner source
  4626cdb38231df379d77d47b228caa88517a914b privately deployed successfully
  2026-10-23 (deployment appgdep_6adb1c2f768c8191bb578bce7a4cf187); URL unchanged.
  User sign-in followed by read-only hosted-browser verification23 October:
  progress panel/calendar/notes load; next-lab goal and prerequisites expand.
  No user data edited or production test record created. Phone untested.
  Daily local thread heartbeat keep-fieldnotes-progress-current ACTIVE18:00 Berlin;
  needs running laptop/app and permissions, no unattended-run success assumed.
  Maintenance rules: Documentation/PLANNER_MAINTENANCE.md and AGENTS.md. No live
  AI/robot access. Source checks: Tools72/dashboard261/Hub53+one skip; planner25,
  TypeScript/build/API11 pass. No robot deployment or physical test from home.
- Gazebo feasibility discussed 2026-10-23, not an approved installation or new
  thesis requirement. Useful candidate for repeatable camera/planar-LiDAR height,
  occlusion and spatial-association tests in a separate PC environment. Existing
  copied simulation/Xacro and Ackermann-named URDF assets are not a verified car
  simulation. Physical ROS1 Melodic stays unchanged; modern ROS2/Gazebo integration
  requires explicit adapters/porting and cannot run the current Hub unchanged by
  assumption. Classic reached EOL January2025. PC/GPU/resources, version choice,
  model calibration and setup effort unassessed; real sensor/YOLO/Jetson/hardware
  validation remains necessary. No software installed, simulation run or deployment.
- GitHub setup COMPLETE 2026-10-22: user authenticated and pushed main to public
  KacangPool/Indoor-Robot-Thesis-. Local HEAD, origin/main and actual remote main
  independently matched f9738808104facca710ef67acf285830679a4183 before the
  documentation-completion update. Hosted Project quality run39855842652 for
  that commit completed successfully, including audit, offline checker and report
  upload. Earlier pending-authentication entries below are historical/resolved.
  Prior Windows10053 errors remain undiagnosed; Linux CI is not robot validation.
  Only reviewed source is published, not raw/private data or automatic future
  edits. Existing histories retained; no robot deployment or Wi-Fi changes.
  Current guide: Documentation/GITHUB_WORKFLOW.md.
- GitHub checkpoint 2026-10-22: origin configured and original remote README
  history merged locally atcc978be; original description retained. Committed-
  history audit covers7 commits/175 blobs with no unresolved findings and one
  exact synthetic-fixture waiver. Initial push fails because non-interactive Git
  has no credentials despite connector access; no token/password extracted. User
  given normal laptop Git push command for one-time local sign-in. Remote remains
  4ef1d77e and Actions has0 runs at checkpoint; no uploaded-source/CI-success claim.
  Latest checker64 tool passes,Hub53 passes/one skip,dashboard259 passes/two
  Windows10053 errors; JS/static pass. Upload/hosted verification pending auth.
- GitHub publication setup 2026-10-22: user explicitly authorizes reviewed source
  upload to public KacangPool/Indoor-Robot-Thesis-. HTTPS origin configured and
  original README commit fetched; local and remote histories to be retained,
  README includes user's original description. Public-history auditor + exact
  synthetic-fixture waiver/test coverage, narrow CI-file allowlist and hosted
  read-only offline quality workflow added. Wi-Fi deferred; no robot changes.
  Final audit/push/hosted run/head synchronization still pending verification;
  avoid declaring successful publication merely from repository access. Local
  latest full checker preserves one Windows10053 HTTP error, other suites/JS
  pass. Guide: Documentation/GITHUB_WORKFLOW.md. No public raw data/credentials.
- GitHub/home-network update 2026-10-22: user created PUBLIC
  KacangPool/Indoor-Robot-Thesis- and explicitly accepts visibility, superseding
  private indoor-sar-robot proposal below. Connector confirms public owner/name;
  anonymous ls-remote finds main4ef1d77e0b571cbd85d2e1507079b319e7e1be0b,
  commit fetch shows only user's introductory README. No local origin, source
  upload or remote mutation yet. Before publication review full local history
  and reconcile/preserve remote README, not force-push over it. Home PC/laptop
  connectivity demonstration is optional, not proof of robot/easyroam/campus peer
  access. Robot presence at home unknown. Recommend actual stationary robot SSH/
  tunnel/camera test on target network; campus routing and old OS/certificate
  support remain unverified. No new network/hardware measurements or settings.
- GitHub/campus follow-up 2026-10-22: user explicitly approves private destination
  KacangPool/indoor-sar-robot; no public publication. Connector login KacangPool is
  confirmed, target lookup404 is inaccessible/not proof of absence. Controlled
  browser remains signed out even after user reports sign-in; no repository-create
  connector tool/installed gh. Private creation/authenticated first push pending;
  no remote/upload yet. User's university: Hochschule Merseburg. Official Linux/
  manual WLAN guidance uses easyroam/certificates; campus peer SSH permission and
  old-Jetson compatibility unconfirmed. Same infrastructure could extend useful
  coverage beyond direct robot hotspot range, not guaranteed routing/roaming or
  out-of-sight readiness. Keep SSH/loopback and existing motion guards. First
  network switch needs local fallback; inspect assigned address/port22 while
  stationary. Hub currently accepts private IPv4 only. No network/robot changes.
  Notes: Documentation/GITHUB_AND_CAMPUS_WIFI.md and new root README.md.
- Current local source v0.14 (2026-10-22): user approves ongoing quality workflow.
  Local source-only Git repository initialized with v0.13 baseline d987a68 and a
  separate quality-foundations implementation snapshot; no remote/publication,
  private data/vendor/planner excluded, no global identity change. One-command
  Tools/quality_check.py + Check Project.cmd gives readable/JSON reports, explicit
  pass/fail/error/skip, isolated suites, syntax checks, dependency observations and
  source commit/dirty/SHA-256 provenance. No installs/robot/model startup.
  Strict dashboard_config.json preview/robot profiles retain ordinary defaults;
  unknown/protected settings fail before ROS startup, no motion/security changes.
  Hub Save report now allowlists cached diagnostic fields/issues and records age/
  demo evidence; structured event history is bounded/rotated with no raw activity,
  SSH/exception/credential payloads. Helper Python/disk metadata is read-only and
  absent until deployed. Runtime is now complete 17-file v0.14 bundle. No deployment
  or robot connection performed. AGENTS.md preserves this workflow going forward.
  Final checker: Tools57/57, dashboard261/261, Hub53 pass/one symlink skip; JS/syntax/
  inventory pass. Two earlier full runs retain one/two Windows 10053 errors, not
  fixed or hidden by final pass. Native App/old-Jetson/physical behaviour untested.
  Later staged: aligned sensor recordings/replay, fusion contracts/provenance,
  robot dependency/restore validation and measured performance. Missing scan stream
  and calibration/TF/time/association questions unchanged. Guide:
  Documentation/QUALITY_WORKFLOW.md; no thesis/detector/training scope change.
- Previous local source v0.13 (2026-10-22): user requests reuse-first modular code.
  Extracted diagnostic core in Tools/fahad_core; separate dashboard calculations,
  sensor state, ROS reader and browser sensor renderer; separate Hub setup workflow,
  SSH transport and runtime manifest. Existing entry commands/import facades and
  motion guards/limits retained. Optional laptop detector and annotation analysis
  now have explicit reusable APIs without import-time execution/model downloads.
  Shared modules must travel with scripts: diagnostic ZIP builder plus Hub's fixed
  complete 15-file runtime. New architecture/copy guide and AGENTS reuse rule.
  Vendor code, raw data, historical reports and hosted planner unchanged. No robot
  connection/deployment/motion or fusion implementation; missing /scan and physical
  integration/calibration questions remain open. Offline root tests 48/48; Hub
  46 passes/one symlink skip; latest dashboard 254/255 plus separate four new boundary
  passes (existing Windows 10053 HTTP rejection-test error); 122 dashboard JS + four
  annotation-module checks and scoring assertions pass. Python grammar checked, not
  actual Jetson 2.7/3.6 execution. Motor-free/synthetic browser preview only.
  Details: Documentation/MODULAR_CODE_ARCHITECTURE.md and CHANGELOG.md.
- Conceptual clarification 2026-10-22: user's shelf/raised-object concern is a
  genuine false-association case. Current LaserScan is planar 2D, not full-height
  sensing; approximate 14–16 cm level plane is user-estimated, not calibrated.
  Bearing/bounding-box overlap alone never proves a laser return is the RGB
  object. Preserve unmatched detections; distinguish camera-only, valid depth-
  located and laser-associated observations. Map-level camera markers over a
  LiDAR map do not prove direct object-level laser support. Existing no-training/
  physical-association scope unchanged; RGB-D remains a validation aid/optional
  position source after unresolved registration/accuracy checks. New explanatory
  note: Documentation/CAMERA_LIDAR_HEIGHT_AND_ASSOCIATION.md. No fusion code,
  new architecture commitment, hardware test or calibration performed.
- Previous source v0.12 (2026-10-22): user /map report has no publishers. The
  latest connected-Hub repeat (screenshot v0.12, SSH/web/camera/base ready) still
  registers /lsn10 but delivers no /scan messages over ~10 s; LiDAR card correctly
  WAITING FOR SCAN. Active delivery failure now observed, root cause unconfirmed;
  Hub LiDAR log subsequently shows two ended launch sessions, no explicit serial
  fault. Logs append across launches, so current node identity is not established
  by those historical PIDs. Next checks: live bounded rosnode info, process list
  and /dev/wheeltec_lidar alias; no duplicate launch/vendor change.
  Earlier /scan registered /lsn10 but no new messages during a check user says was after
  closing Hub. No active-stream/root-cause/automatic shutdown conclusion; repeat
  while connected/Prepare, no duplicate driver. Plain scan plane without radar
  rings/crosshairs/axis labels; fixed distance colours red0→blue4m, not object
  classes/material identity. Mapped points preserve sensor-relative distances
  instead of map-origin distances. Real occupancy shading retained if published;
  no /map means scan-only, no invented free floor. Camera/fusion needed for semantic
  labels as before. Driving/speed/fault guards and network/startup unchanged.
  251 dashboard Python +116 JS pass, 44 Hub pass/one skip; labelled disconnected
  synthetic preview only, no robot deployment/commands. New guide
  Documentation/REMOTE_PLAIN_LIDAR_V012.md. Actual scan/map/TF readiness and prior
  wireless/turning/physical stopping questions still open.
- Previous source v0.11 (2026-10-22): user reports good driving, estimates ~10 m
  indoor Wi-Fi reach; .40 request deferred because new recording explicitly shows
  vx=.176/yaw=.379 speed fault and later command timeout, neither diagnosed nor
  calibrated. .30 request and .32/.35/.04 feedback limits remain unchanged.
  Held A/D keyboard steering replaces desktop mouse steering in default mode;
  release or both keys centre, steering alone never starts travel, no stale/held
  replay. W/S ramp, release/B/Stop/fault checks preserved. Wider central sensor
  panels (~795px at 1280x720) and 170/245 sidebars. Optional read-only /map view
  shows real occupancy, unknown, snapshot age; map car and laser overlays require
  fresh correctly-framed planar TF (base_footprint/scan timestamp). Missing map
  means explicitly scan-only, no invented free floor. No map/nav launches, goals,
  save/overwrite or obstacle avoidance added. Input map cap 1,000,000 cells;
  conservative <=256x256 display; large default SLAM extents may need more work.
  Native Hub still Windows-only; secure phone browser access not configured.
  251 Python dashboard +114 JS pass; 44 Hub pass/one skipped. Disconnected
  synthetic-map fixture checked, no live deployment/robot commands. New guide
  Documentation/REMOTE_KEYBOARD_MAP_V011.md. Actual map/TF readiness, old-Jetson
  load, keyboard driving, turning discrepancy, stopping, wireless cause, phone
  operation and independent failure stopping unverified. Thesis perception/fusion
  scope unchanged; map visualisation is not semantic camera-LiDAR association.
- Previous source v0.10 (2026-10-22): user reports previous ramp works, renews .30
  maximum request and asks for S-like acceleration/recording HUD. Signed joystick
  ceiling now .30 m/s; default held keys/pedals smoothstep over five healthy-input
  seconds, slow/fast/level, not logarithmic. Opposite-key deceleration .08/s,
  release/B/Stop immediate-zero requests; no automatic reverse/cruise. Direct-drag
  layouts are proportional up to .30 without easing; six buttons stay .03.
  Live feedback selected explicitly at |vx|<=.32, |yaw|<=.35, |vy|<=.04 to cover
  .30 at unchanged 1/m curvature plus provisional headroom, not calibrated safe
  margins. Legacy defaults .12/.15 and other guards retained. Three-column
  single-viewport desktop cockpit: telemetry left, framed camera centre, scan
  below, controls right; details expand/side-scroll, Stop sticky, narrow screens
  stack. Full 239 Python run +107 JS pass; later repeats hit Windows 10053 in
  unchanged HTTP-denial cases, changed speed/LiDAR tests pass separately. 44 Hub
  pass/one skipped. Disconnected
  1280x720 visual fixture checked, no page overflow; no robot deployment/commands.
  New guide Documentation/REMOTE_COCKPIT_V010.md. Actual speed, stopping distance,
  turning, new feedback margins, mobile interaction and independent firmware/
  host-failure stopping remain unverified. Update at standstill, close old tabs,
  restart Hub/Prepare and load one fresh v0.10 page. Thesis scope unchanged.
- Previous source v0.9 (2026-10-22): second ~109-second recording shows generic
  heartbeat alerts and one explicit vx=-.102 speed fault above prior .100 guard;
  two console tabs visible. Contact-stopping is user-reported, not collision
  protection (none implemented). Every generic heartbeat alert is not proven
  actual timeout: HTTP rejection was mislabelled too. Added specific rejection/
  timeout messages, owner/generation-scoped automatic Stops (inactive pages no
  longer send global Stop), explicit operator Stop still global. Slider removed;
  held travel ramps 0→.10 at .04/s, opposing key decelerates .08/s to zero with
  fresh input required for reverse. Both keys brake, not cruise; release/B zero.
  Fresh travel press can Enable only when checked, healthy and stationary; no
  held/queued/cancelled input resumes. Browser Stop locks shortcut until explicit
  acknowledgement. Longitudinal feedback guard provisionally .12 (headroom, not
  physical calibration); .10 command cap, lateral/yaw/lease/other guards remain.
  Requested .30 not implemented pending diagnosis/stopping evaluation. 238 Python
  dashboard +103 JS checks and 44 hub passes/one Windows symlink skip. New guide
  Documentation/REMOTE_RAMPED_PEDALS_V09.md. Actual fault distribution, .12 margin,
  ramp/async Enable/native input and independent hardware stopping remain unverified.
  No live commands/deployment/foreground UI control by tools. Close all old tabs
  before update and use one newly loaded console. Thesis scope unchanged.
- Previous source v0.8 (2026-10-22): user supplies ~80-second screen recording,
  requests checkbox-only permission and separate keyboard travel/mouse steering.
  Visual frames show Circular mapping with low requested throttle during steering
  and repeated Stop/Enable states later; specific fault reason is below viewport,
  so cause remains unconfirmed. Implemented default Pedals + steering: held W/↑
  forward, S/↓ reverse, B brake, mouse steering only, separate on-screen touch
  pedals/steering pointer IDs. .03–.10 travel setting, default .06; normal travel
  release/B preserves healthy session and steering grip, normal steering release
  centres steering while held travel continues. Brakes/conflicts take priority,
  fresh travel input required after braking; no queued/replayed held keys. Initial
  Enable and genuine fault re-enable retained, not removed for a checkbox-only
  latch. Stop reason now visible beside Enable. Guard/lease/curvature unchanged;
  original dropout cause and real new controls still need device verification.
  235 dashboard Python +90 JS checks, 44 hub passes/one skipped Windows symlink
  test. New guide Documentation/REMOTE_PEDALS_STEERING_ROS1.md. No deployment,
  live robot commands or foreground GUI automation by tools this turn; thesis
  camera/LiDAR association goal unchanged.
- Previous source v0.7 (2026-10-21): user reports real hub works and 0.10 is useful,
  but intermittent disable/lost mouse grip requires Enable. Cause unconfirmed;
  no reports/logs yet attribute it to capture, focus, heartbeat, feedback or
  scheduling. Added working-step/elapsed indeterminate progress, explicit close/
  disconnect button, persistent separate client/backend stop reasons and bounded
  history (specific text previously could be lost), optional independent-axis
  joystick and raw intensity/distance colour views. New behaviour not robot-tested.
  Maximum stays 0.10, buttons .03, existing guards unchanged. Suggested .20 deferred
  pending fault evidence, not an agreed permanent maximum. No auto-rearm/resume.
  Driver source lsN10 publishes raw intensities, but live values/binary/device
  label remain unconfirmed. Colours are not object classes/absorption. Map layer
  requires an actual OccupancyGrid topic and frame inspection; not added here.
  234 dashboard Python, 75 JS and 44 hub tests pass; one Windows symlink case
  skipped. New guide Documentation/ROBOT_HUB_V07_OPERATING_NOTES.md. Closing hub
  attempts Stop/disconnect, leaves remote services; Ubuntu shutdown separate.
- Previous source v0.6 (2026-10-21): user requests 0.10 m/s maximum joystick
  request and a Windows hub to remove repeated manual terminal startup. Native
  Tools/robot_hub app now prepares fixed ROS services, verifies/backs up personal
  dashboard updates and opens a private SSH tunnel; existing website retained.
  No automatic arm/motion/fault restart, vendor/firmware/network/boot changes,
  hardware camera-settings controls or phone gateway. Password entered locally,
  not saved; saved SSH host identity required. Startup/physical 0.10 behaviour
  not verified on robot. Buttons stay 0.03; old feedback thresholds unchanged,
  so actual overshoot near 0.10 can fault. 227 Python dashboard tests, 69 JS
  checks and 40 passing hub tests (one further Windows symlink test skipped),
  including fake encrypted localhost SSH/tunnel; native offline demo inspected.
  New guide Documentation/ROBOT_HUB_WINDOWS.md; launcher is a source-based CMD
  launching a native app, not a standalone EXE. Thesis mapping scope unchanged.
- Latest user observation 2026-10-21: LiDAR works after activating its driver.
  This supersedes the earlier no-publisher state as the current user-reported
  outcome, without confirming scan rate/quality, device label or installed
  dashboard version. Still-reported 0.03 ceiling has no proven cause; old copy,
  button cap and joystick deflection are possibilities. Hub displays version
  and requested ceiling to make that distinction visible.
- Earlier LiDAR diagnostic checkpoint 2026-10-21: supplied rosnode list and
  /scan info both complete with exit 0. Camera/darknet, isolated base and dashboard
  reader are registered; /scan is sensor_msgs/LaserScan, Publishers: None, with
  dashboard subscriber. ROS is reachable, but no scan producer is registered;
  earlier "no output" is superseded for this checkpoint. No physical fault/model
  identification or live scanner success follows. Next: stationary device/process
  check, known sensor-only wrapper, then publisher/rate/browser verification.
  Installed dashboard version and v0.5 physical speed remain unconfirmed.
- Previous dashboard source v0.5 (2026-10-21): user reports restored webpage and
  slow driving, requests pull-dependent faster joystick and live LiDAR display.
  Prior joystick was already proportional at a 0.03 m/s ceiling; new session
  joystick ceiling 0.08 m/s, buttons/legacy profiles remain 0.03. Requested-speed
  readout distinguishes intent from physical measurement; existing reported-speed
  guards, 0.35 s lease, release/fault/enable-once behaviour unchanged. No latch,
  firmware, vendor/network/boot/model/planner change. /scan viewer now distinguishes
  connection without data, live/empty, invalid/stale and multiple-source cases;
  raw arrival rate/source/frame/counts, bounded history/plotting and valid-first
  decimation. No collision avoidance, camera alignment, labels or mapping added.
  User reported "no output" to requested /scan checks; command completion/master/
  driver status is unknown, not proof of missing LiDAR. 227 Python fake-ROS/
  loopback tests and 67 JS checks pass; actual installed version, new speed,
  current live LiDAR and physical failure stopping remain unverified. Guide:
  Documentation/REMOTE_JOYSTICK_LIDAR_ROS1.md; known sensor-only vendor wrapper
  may be used only after checking ROS and avoiding duplicate drivers. Configured
  N10/lsn10 evidence remains distinct from unconfirmed physical device label.
- Latest operator decision 2026-10-21: user reports every direction works,
  occasional no-movement presses (cause unconfirmed), and requests enable once
  plus continuous held control. Implemented source v0.4 ManualSession, selected
  by explicit --ros --drive: no fixed hold cap, normal release zeros then fresh
  post-release stationary feedback and a fresh press under the same session.
  Initial Enable retained/hidden while enabled; Stop, focus/connection/sensor/
  scheduler faults disable with explicit recovery. Same maximum |vx| 0.03 m/s,
  curvature 1/m, no spin/lateral/latch, no speed increase or firmware/network/boot
  change. Motion IDs + sequence barriers prevent released/stale/queued intents
  reviving. 208 fake-ROS/loopback Python and 60 JS checks pass; Python 3.6 grammar
  and JS syntax verified. Real v0.4 release/repeat/long hold, Python 2 runtime,
  firmware/host/serial/queue failure stopping remain untested. New guide:
  Documentation/REMOTE_DRIVING_SESSION_ROS1.md. User report supports prior v0.3
  normal direction operation only, not measured speed/turning or each stop guard.
  Hosted planner and thesis camera-LiDAR scope unchanged.
- Startup handoff 2026-10-21: after camera and remaining-client/copy/start
  instructions, user says startup "looks good" and requests proceeding. This
  is general user-reported startup success, not inspected file hashes/mode or
  physical new-direction proof. Next action is the documented brief straight
  reverse hold/release observation before steering/joystick. No new limits,
  tool-side robot connection or physical outcome reported yet.
- Operator update 2026-10-21: user reconfirms prior integrated forward operation
  is slow and controllable and explicitly requests every direction/joystick.
  Implemented locally dashboard v0.3 `ros_manual_ackermann`: six car-like
  directions and normalized pointer joystick, requested |vx| <= 0.03 m/s and
  |yaw| <= |vx| * 1/m, no lateral/in-place spin. Same two-second hold cap,
  0.35 s lease, release/health/owner/sequence guards and zero cleanup. Stop and
  explicit page re-enable before travel-sign reversal; steering changes do not
  reset hold time. New signed feedback guard does not weaken the old CLI test.
  178 Python fake-ROS/loopback tests and 45 JS checks pass; disconnected desktop
  browser layout/release/re-enable QA only. New directions, physical steering
  response, actual Python 2 runtime and firmware/host/serial failure stopping
  remain unverified; no robot connection or physical command by tools. Current
  deployment guide `Documentation/REMOTE_JOYSTICK_ROS1.md` updates six files in
  the known personal trial copy, preserves original viewer/vendor/boot/network/
  models/maps and leaves the hosted planner unchanged. Thesis fusion scope is
  unchanged; joystick is an operator enabler, not autonomous navigation.
- End-of-session update 2026-10-20: user reports the updated integrated dashboard
  moves the robot and works well, with a very short hold estimated about one
  second, then stops work for today. This supersedes the locally-only/not-yet-run
  status for integrated forward operation below. Configured command cap remains
  two seconds, not a measured physical duration. No new speed/timing setting.
  Release/physical self-stop and page re-enable in this updated mode were not
  separately reported; prior one-shot self-stop is confirmed. Next session:
  restore manual services once, inspect displayed stop reason and verify normal
  hold/release/re-enable before reverse/steering, then resume sensor fusion.
  No further actuation requested today; orderly shutdown guidance supplied,
  completion unreported. Firmware/serial/host fault stopping remains unverified.
- User's latest operator decision 2026-10-20: first one-shot browser pulse moved
  a tiny amount; user explicitly confirms normal self-stop without power-off.
  User wants actual main-dashboard hold controls and no per-action process
  restart. Implemented locally `server.py --ros --drive` + `manual_drive.py` and
  main-page live mode: repeatable explicit page Enable after release/cleanup,
  same 0.03 m/s request, new 2 s maximum hold, fresh stationary feedback and
  existing heartbeat/graph/camera/owner/no-replay protections. Default viewer
  remains motor-free. Reverse/steering are not enabled; no hardware watchdog,
  automatic resumption, boot change or unrestricted video-only driving claim.
  142 Python fake-ROS/loopback + 35 fake-DOM checks and actual simulated-browser
  hold/release/re-enable QA pass. Integrated update not yet copied/run on robot;
  guide `Documentation/REMOTE_MANUAL_FORWARD_ROS1.md` preserves original viewer
  and targets the known personal trial copy. This supersedes prior restart-per-
  attempt UX, not independent firmware/host/serial failure-stop uncertainty.
- Live-trial handoff 2026-10-20: after ROS recovery, user reports expected
  subscription-only readiness success and explicitly asks for live browser mode.
  Instructions now permit the prepared one-shot forward trial only after its
  on-site terminal/physical conditions; no actual live browser actuation or stop
  result has been supplied. Original viewer is replaced only for this deliberate
  trial, not silently made motor-capable. No continuous/reverse/steering enabled.
- Deployment checkpoint 2026-10-20: user runs copied personal trial script at
  `~/fahad/remote_dashboard_web_trial/web_crawl.py` on robot and receives its
  expected default OFFLINE output. Supersedes the earlier not-copied/default-entry
  untested status only; complete assets, ROS live mode and physical web action are
  not verified. Current viewer bind conflict is an SSH listener on robot loopback
  8765 (session PID 8307), not a matching dashboard process; inspect its command
  before targeted cleanup. No motion initiated at this checkpoint.
- Operator progress 2026-10-20: user confirms restored live browser video/YOLO.
  Separate `Tools/remote_dashboard/web_crawl.py` + dedicated page implement one
  terminal-confirmed, expiring forward-only browser trial, same fixed 0.03 m/s /
  0.4 s request as prior CLI test. Default offline, subscription-only check,
  one-use token/sequence/lease, fresh feedback/camera/graph gates and repeated
  zeros; original viewer remains read-only. 102 Python fake-ROS/loopback checks
  and 26 fake-DOM checks pass; non-actuating browser rendering verified. Not yet
  copied to/run on robot; actual Python 2/runtime and physical web action are
  untested. No continuous/reverse/steering/autonomy or independent fault-stop
  claim. Staged instructions: `Documentation/WEB_FORWARD_TRIAL_ROS1.md`.
- Use the existing working general YOLOv3-tiny pretrained weights; no detector training from scratch or fine-tuning in the current phase. Original training data are not required for live inference. Alternative models remain references, not a required comparison or deployment prerequisite.
- Prioritise camera-derived semantic labels associated with valid physical LiDAR geometry, initially while stationary and in sensor/robot-relative coordinates; add a separate basic map-marker layer only after robot pose/TF/map validity is established. Camera depth may support position estimates/validation but does not replace demonstrating requested camera-LiDAR association.
- Start with person integration and supported pretrained categories. Human/animal objectives remain; no new hand/generic-box category, fall-only scope, autonomous navigation or physiological-life claim is implied. LiDAR does not independently classify the object; some detections will have no valid laser association at the low scan height.
- Keep bounded evaluation/recordings of detection quality, association errors, timing and position accuracy. No large custom training dataset is planned, but evaluation data are still needed. Do not conflate no training with no validation.
- Decision reference: `Documentation/AGREED_PRETRAINED_FUSION_SCOPE_2026-10-14.md`. Preserve working vendor software, models and map data. This direction supersedes older 'final model open / compare alternatives first' planning below; no new fusion code or model change has yet been made.
- Priority update 2026-10-15: user explicitly asks to implement the local remote-operator interface first so the robot is not tied to a monitor/lab position. Work toward laptop camera viewing, then verified manual teleoperation and monitor-free startup; the perception/fusion thesis objectives remain. No autonomous navigation, outdoor/field readiness or automatic motion-on-boot is implied. First version is read-only plus motor-free rehearsal; live motor and boot integration require physical/controller/network verification.

## Intended users and environment

- Intended users: firefighters/search-and-rescue personnel.
- Environment: indoor buildings, potentially with poor lighting, occlusion, clutter, smoke, and unusual human poses.
- Targets: humans and household animals that may require rescue.

## Planner access boundaries (2026-10-20)

- User confirms the hosted planner works on their phone and online-only use is sufficient. Keep the planner as-is; no native app/PWA/offline enhancement is needed now. Resume robot operator/fusion work; live AI remains unconnected and is not the current task.
- Fieldnotes uses the same private hosted URL on phone and laptop, with the owning account and internet access. Browser bookmarks/home-screen or app-style shortcuts are the recommended easy-access option, not a new native app commitment. Current application source has no PWA manifest or offline implementation; phone installation/login has not been device-tested. An icon does not enable offline cloud saves. The robot's local offline dashboard remains a separate service.

## Working schedule

- User refinement 2026-10-20: aim for the beginning of December. The new private
  planner uses **7 December 2026** as an editable rough implementation target,
  not a user-confirmed exact deadline or promised completion. Baseline daily
  goals include lighter/recovery/buffer days and keep thesis writing separate.

- User clarification on 2026-10-14: no formal deadline, but wants implementation
  finished in December 2026, excluding thesis writing, and intends four hours
  every day (28 nominal project hours/week). Exact December date and agreed final
  feature/evaluation scope remain open. This is a soft planning target, not a
  promised completion date or scheduled automation.

## Current hardware evidence

- Chassis label: **WHEELTEC R PLUS**.
- Exact Chinese product description on the same label: `高配版阿克曼小车 / 常规型版本`, translated as **high-configuration Ackermann robot car / standard version**.
- ROS configuration name on the label: `senior_akm`.
- Identification boundary: the label does **not** say R550. The public R550 manual is only a related modern WHEELTEC family reference and must not be presented as this robot's exact product manual.
- Mobility: four-wheel Ackermann steering; it cannot rotate in place.
- Power-control evidence checked 2026-10-19: actual-robot photo `Picture of Robot/Documentation/photo_2026-08-17_10-03-33.jpg` has readable `主电源开关` (main power switch) above a large round metal control. User subsequently confirms it normally turns the robot off and is reachable on the floor without lifting; a short forward test then visibly stopped by itself. These are label/user-reported normal-use observations, not electrical motor-only isolation, emergency-stop certification, measured braking or verified firmware/remote-link-loss stopping. Do not reproduce unrelated credentials visible elsewhere in that photo.
- Probable compute: NVIDIA Jetson Nano 4 GB.
- Runtime report dated 2026-10-08 (`Terminal Reports/report_1638_08102026.txt`, also supplied under `D:/Bachelor Arbeit Buffer/reports/`) confirms NVIDIA L4T R32.5.2, board string `t210ref`, aarch64, Python 2.7.17 and Python 3.6.9. This does not independently establish exact compute model/RAM or installed CUDA/TensorRT/PyTorch versions. Keep robot setup separate from the Windows Python 3.11 detector-test environment; no robot upgrades have been performed.
- Confirmed camera: **Orbbec ASTRA S**, reported by the live ROS driver on 2026-09-09 with serial number **17121811539**. The user observed the camera working. Its driver supports RGB, IR, depth, registered depth, camera information, and point clouds. A readable label photograph and separate live validation of RGB, depth, rates, and recording performance remain desirable.
- User-refined sensor placement on 2026-09-10: the camera is approximately **12-13 cm above the floor** and can be tilted only by manual adjustment. The user estimates a possible tilt travel of roughly **120 degrees**, but this has not been measured and must not be treated as a calibrated angle. The LiDAR is approximately **2-3 cm higher** (therefore roughly 14-16 cm above the floor), behind the camera, and does not obstruct the camera view. Exact measurements should later use the camera lens centre and LiDAR scan-plane centre; the chosen camera pitch/roll, repeatable angle marks, tilt endpoints, and nearest visible floor point remain unmeasured.
- LiDAR evidence: the copied robot source defaults to Leishen/LS `ls_N10`, publishing a 2D `LaserScan` through `/dev/wheeltec_lidar`. The user reported visible scan points on 2026-09-09; the completed October report now confirms an actual `/scan` message from `/lsn10` in frame `laser`. The physical label/device identity, sustained rate, range quality and known-distance accuracy remain unconfirmed. The copied `lsn10` driver exposes no model/serial retrieval service; the physical label is the strongest identity evidence, while Linux USB details may identify only the CP210x/CH34x serial interface. The fixed horizontal configuration measures one plane and has no identified 3D mode. A measured mechanical sweep with calibrated pose tracking could support 3D reconstruction as a separate apparatus; changing display settings or converting the planar scan to PointCloud2 cannot add vertical measurements.
- Camera sensing principle verified against Orbbec's original-series documentation on 2026-09-16: the Astra S is a structured-light RGB-D camera (colour plus active infrared depth), not a conventional left/right stereo camera or an ordinary RGB-only monocular sensor. Distinguish it from the separately named Astra Stereo S U3 and newer Astra models. Published depth capability is 640 x 480 at up to 30 FPS over 0.4-2 m. Terminal report 2 measures `/camera/depth/image` message delivery at 29.694 Hz; the completed October report additionally confirms 640x480 float/integer depth formats and finite centre examples. Full-image valid-depth coverage, RGB registration and distance accuracy remain unverified. Manufacturer field-of-view/precision figures must not replace verified calibration and measured performance.
- Battery product-spec candidate: 22.4 V, 6000 mAh, 7S LiFePO4 with 25.55 V full-charge voltage, 3 A charging current, DC 4.0 x 1.7 mm charging socket, and XT60U-F discharge connector. This is documented in the user-supplied product image `robotspecs15.avif` and a matching WHEELTEC R5-series listing, but the physical battery label and charging-port polarity have not yet been verified.
- Closest documented export/rebrand: **Roboworks Rosbot Mini Ackermann**. JKK Research Center uses a visually matching WHEELTEC/Roboworks chassis with Jetson Nano, Orbbec depth camera, and LSN10 lidar. Its chassis photograph, wheel style, plate geometry, sensor layout, network defaults, and ROS package names closely match this robot.
- A 2023 English Roboworks Rosbot manual documents the likely chassis generation as Rosbot Mini: 445 x 358 x 125 mm chassis, 0.320 m wheelbase, 125 mm wheels, MD36N motors, HWZ020 servo, 500-line encoders, and coaxial pendulum suspension. These are high-confidence candidate specifications, but physical measurement/device labels still take priority.
- The exact WHEELTEC sales model/year and shipment configuration remain unconfirmed. Do not rename the robot R550; use **WHEELTEC R PLUS high-configuration Ackermann car (`senior_akm`)**, with **Roboworks Rosbot Mini Ackermann** noted as the closest documented equivalent.

## Current project state

- Planner publication completed 2026-10-20: https://fahad-robot-fieldnotes.crispswift256.chatgpt.site is the verified private live Fieldnotes URL. Deployment `appgdep_6ad73bfe3e908191bfa3fd3af2d334b7` succeeded for saved version `appgprj_6ad732b9b9448191ba4fba48d8f1b80f~appgver_fc9b98aa019481918fe857cc0082a910` / commit `828764251742ded0a3635b7e8654cbf9bbbc2e69`. Production page loaded in signed-in browser; temporary note save/reload/body verification/deletion passed, with only the two default context notes left afterward. This supersedes the in-progress publication wording in the build record below. Real AI is not connected: OpenAI Developers tools are now available, but no API key/call/code was configured. Credential decision/explicit secure approval is required before API-backed work; built-in guide remains explicitly non-AI. No robot-control changes.

- Separate planner built 2026-10-20 at `Sites/fieldnotes/`: Fieldnotes, a private notes/calendar/roadmap website, NOT the robot dashboard. Features 49 editable daily goals (20 Oct–7 Dec inclusive), task status/date/phase/hours, note editing/pinning/search, editable target, JSON backup/import and .ics export. Authenticated per-user D1 storage, bounded validated writes, same-origin protection and revision-conflict refusal; browser drafts are not durable until save acknowledged. Default roadmap preserves pretrained YOLO/no custom training, calibrated physical camera-LiDAR association, pose-gated map markers and evaluation. No robot command/filesystem access or automatic CHANGELOG sync. 20 core tests, 11 local API checks, TypeScript check and production build passed; desktop/phone UI checked, date-input and overflow defects fixed, temporary QA records removed from local preview. Site `appgprj_6ad732b9b9448191ba4fba48d8f1b80f`; source commit `828764251742ded0a3635b7e8654cbf9bbbc2e69`; private deployment currently building (`appgdep_6ad73bfe3e908191bfa3fd3af2d334b7`). Hosted build fallback used because local package helper requires unavailable Bash; no public-sharing change. Built-in project guide is explicitly non-AI and confirms edits; no OpenAI API calls/key configured. OpenAI Developers became available later in the session; live AI requires its credential decision/secure approval workflow, not a browser key or assumed ChatGPT-history access. Site availability requires internet; local preview DB is separate from hosted data. User's accuracy-first preference recorded in AGENTS without an infallibility promise. Robot runtime/code/settings unchanged.

- Lab planning 2026-10-20: user expects lab arrival in roughly an hour and prioritises website driving, website object identification, then return to original mapping objective. New `Documentation/LAB_PLAN_2026-10-20.md` distinguishes existing RGB/YOLO-label image viewing and motor-free rehearsal from unimplemented browser motor output/structured detection list. Plan: restore viewing; implement/test an explicit guarded opt-in bounded web forward action before later hold-to-move/release-to-stop control; confirm existing YOLO labels and optionally add fresh class/score list from detector messages; conditional stationary camera-LiDAR frame/timing/geometry check, then validated associations and later map markers. No new detector/training/autonomy/3D LiDAR scope. Continuous remote driving remains gated by failure-stop evidence; non-actuating software checks cannot prove lower-controller watchdog behavior. Planning only: runtime unchanged, no code tests or tool-side robot commands; no live browser control or automatic boot enabled, arrival/reminder not scheduled. Stable power-control summary corrected to include already-recorded user confirmation rather than older pending-switch wording.

- End-of-session request 2026-10-19: user stops for the day after the observed forward-move/self-stop milestone and asks shutdown order. Guidance: stationary robot; Ctrl+C isolated base driver first while ROS master remains, wait for shell; stop dashboard, then camera/YOLO; issue `sudo shutdown -h now` in robot SSH shell; allow Ubuntu to finish before physical main-power off, then close remaining browser/tunnel/local terminals. SSH disconnection alone is not shutdown-complete proof. No tool-side shutdown executed or user completion yet reported. Resume from guarded dashboard motor-path software/failure checks, not another basic crawl or assumed auto-start; dashboard remains motor-free and firmware/link-loss stopping unresolved.

- First observed forward actuation and normal self-stop completed 2026-10-19: after the single unchanged observed-repeat instruction, user confirms tiny physical movement, stopping by itself, then forward direction with a visual estimate of a few centimetres. This completes the basic forward-move/normal-stop observation for this trial, not measured speed/distance/braking, firmware watchdog/fault stopping or autonomy. No additional crawl repeat or second-run export is required just to accept that report. Actual speed/duration/displacement are unmeasured; exact second-run output is not supplied and first-run near-zero feedback is not a second-run trace. Dashboard motors remain disconnected and no tuning/new motion command is issued. Next software stage is separately guarded dashboard motor integration with non-actuating release/timeout/link-failure checks before enablement; these cannot prove lower-controller fault stopping. Firmware/link-loss behavior remains unresolved. Documentation-only update; executable/vendor files, settings and services unchanged.

- Observation clarification 2026-10-19: user says they did not see anything during the first pulse and asks to repeat. Record first physical outcome as inconclusive, not confirmed no movement. Next: ONE manually confirmed repeat of the unchanged gated 0.03 m/s / 0.4 s test solely with deliberate direct observation, stationary clear level placement and reachable normal power-off; no automatic retry or speed/duration increase. If still nothing visible, stop further actuation attempts and inspect evidence. This narrowly supersedes the prior immediate no-repeat instruction, not firmware/physical-stop verification or the disconnected dashboard. Second-run output/observation pending; executable/service/vendor files unchanged.

- One-shot CLI software/feedback result received 2026-10-19: user supplies full `crawl_test.py --live` output, readiness pass, typed `CRAWL`, `Pulse request finished` and recent near-zero odometry AFTER stop requests, followed by shell prompt. Supports completion of planned command/zero-attempt sequence without printed guard abort/publication error, not proof of actual physical motion, direction, distance, speed or stopping, nor delivery of every command. No during-pulse trace or direct physical observation provided yet. Immediate next step: ask whether robot visibly moved, direction and whether it stopped by itself or required power-off; do not repeat/increase request or enable dashboard motors yet. Firmware/link-loss stopping remains unverified. Guide/readiness/dashboard docs updated; executable files, services, maps and original code unchanged.

- Live no-motion readiness passed 2026-10-19: user supplies exact `READINESS: expected isolated driver + recent stationary odometry observed.` and `CHECK ONLY: no Publisher created and no movement command sent.` from personal `crawl_test.py --check`. Supports expected isolated ROS graph and fresh advancing stationary-reported odometry at that time, not quantitative rate/encoder correctness, physical calibration, stop/watchdog behavior or full driver equivalence. Robot-side check execution is demonstrated; exact Python version remains unknown. Next instruction is ONE conditional fixed 0.03 m/s / 0.4 s forward request via interactive `--live`/typed `CRAWL`, only in a clear level directly supervised area with confirmed accessible normal power-off, then repeated zeros; no actual physical duration/speed/stop guarantee. Await complete output plus direct movement/direction/stopping observation; no repeat/ramp if inconclusive. Guide updated: `Documentation/BASE_DRIVER_FIRST_CHECK.md`. No live-pulse result, dashboard motor enablement, GPS/service/vendor change or boot integration yet. Earlier check-pending notes are historical.

- Isolated-driver startup reported 2026-10-19: user says the launch stays at approximately `wheeltec_robot serial port opened`. Copied source logs this after successful serial open, then continuously reads packets and silently publishes odometry/IMU/voltage on valid data. Quiet output is compatible with normal operation but does not prove live valid packets or rule out a receive problem. This supersedes the preceding preparation-only status for driver startup, not readiness/stop/motion verification. Next: leave driver running and run personal `crawl_test.py --check` in another sourced robot SSH terminal; no movement Publisher. Actual check output, source/rate/feedback and any physical behavior remain unverified. No new live-mode command, controller modification or service change.

- Power-off confirmation / separate base-check preparation 2026-10-19: user says the normal labelled main-power control turns the robot off and is reachable on the floor without lifting. This is user-reported normal power-off fallback, not measured braking/isolation, an emergency-stop certification or firmware watchdog proof. New personal `Tools/remote_dashboard/base_crawl_check.launch` opens only the copied base driver with private test input remap (not hardware inhibition); `crawl_test.py` is offline by default and `--check` observes exclusive expected graph/source and fresh stationary odometry without a Publisher. A future separately confirmed `--live` mode contains one fixed 0.03 m/s / 0.4 s forward request and two seconds of zero attempts, with local health guards; actual speed/distance/stop are not guaranteed and no automatic retry/ramp is allowed. Current handoff is startup/check outputs FIRST, not live movement. Guide: `Documentation/BASE_DRIVER_FIRST_CHECK.md`. 36 new fake-clock/ROS/XML tests, 22 existing control/data and 12 fake-DOM checks pass; Python 3.6 grammar/default/help pass; Python 2/ROS/controller/physical behavior untested. No robot-side new code/driver/movement, dashboard motor enablement, GPS/service/vendor changes or auto-start performed by tools. Existing browser viewing remains the working milestone.

- Floor-test planning clarification 2026-10-19: user has no stand and says another student has driven robot. A stand is not categorically required; controlled crawl-speed/brief floor testing may be considered after independently accessible stopping, clear supervised setup and gated command/timeout validation. Another student's use does not validate this new interface or stopping. Initial USB checks are complete; immediate missing information is the actual normal power-off control/function and accessibility from floor without lifting/reaching into wheels. Ask for identification/normal-use confirmation, not moving test. No new motor output/driver launch or floor motion commanded.
- Port-state results 2026-10-19: ttyUSB0 target is root:dialout character device mode 0777; sudo fuser -v prints nothing; gpsd.service, gpsd.socket and gpsdctl@ttyUSB0.service all loaded/active. No process currently owning port is reported, and no Unix mode-bit access blocker or demonstrated GPSD conflict. An active unit can be idle and acquire device later; do not disable GPSD/change permissions on this evidence. Expected ROS base remains not started. Next controller/telemetry stage needs secured bench/appropriate motor-inhibited setup and verified independent stop; ask about a proper stand/all driven wheels clear, never hand-held. No base launch/motor command or physical-stop test performed.
- Corrected controller USB metadata 2026-10-19: user output identifies ttyUSB0/CP2102 USB-UART bridge, 10c4:ea60, serial-interface 0002, cp210x driver; matches copied alias rule, not motor-board model/firmware identity. Same device also has gps0 alias and SYSTEMD_WANTS gpsdctl@ttyUSB0.service. GPS-related activation metadata is a possible port-ownership/conflict lead, not proof GPSD runs/occupies port or causes an error. Next read-only target-permission, sudo fuser -v and service Id/LoadState/ActiveState checks; no serial open, GPS service change, udev rewrite, base launch or motor command. Independent stop/controller timeout still unverified.
- Controller device alias confirmed 2026-10-19: user shows `/dev/wheeltec_controller -> ttyUSB0`. Subsequent udev query used misspelled `/dev/wheeltec_conroller`, so 'device node not found' refers to the wrong path, not proof controller absent. Next rerun correct udev metadata query; target character-device permissions/USB identity, actual board function, installed driver and safe stopping remain unverified. Symlink root ownership/permissions do not establish target-device access. No serial access/base launch/motion performed.
- Live base inventory 2026-10-19: pasted rosnode list has camera/static camera-frame nodes, darknet_ros, personal dashboard reader and rosout but no expected wheeltec_robot base; /cmd_vel and /odom both Unknown topic. Confirms expected base ROS interfaces absent from current master, not broken/unpowered chassis or verified stopping. Next read-only `/dev/wheeltec_controller` symlink/udev metadata inspection, no serial open/base launch or motion. Independent stop/power-path and lower-board timeout still unverified. Source rule scripts are only references, not to run blindly.
- Self-led motion-readiness investigation 2026-10-19: user says lecturer/lab staff lack robot knowledge and requests trying movement anyway, mentioning ~20 km/h (not a measured spec). Continue independent read-only investigation rather than require a particular expert, but do not enable floor driving or use lifting as stop. Copied base callback/loop/include search shows serial forwarding, queue 100 and orderly-destructor zero packet, no explicit command-age stop identified; 2000 ms serial timeout is not a motor watchdog. Lower-controller firmware behavior/installed binary remains unknown. New `Documentation/MOTION_READINESS_2026-10-19.md` proposes bounded rosnode/cmd_vel/odom inspection, then controlled stop/controller verification before any live motion. Dashboard remains motor-free, no command published/base launched.
- Physical-stop gap 2026-10-19: user is unsure an emergency stop/motor-enable switch exists and suggests lifting robot to turn it off. Explicitly reject lifting/catching as a stopping method; keep dashboard motor output absent and no live driving test until lab staff identify/verify an independent accessible stop and controller behavior. Existing photo provides a main-power label, not a verified emergency-stop circuit. Stationary camera/LiDAR/read-only startup work can continue; no hardware modification or motion authorized/performed.
- Restart/floor-move clarification 2026-10-19: user plans to unplug equipment and place robot on floor, and assumes power-on + PowerShell suffice next time. Corrected that camera/YOLO, dashboard --ros and SSH tunnel still need manual startup; full no-monitor boot is untested, no services enabled. Added `Documentation/REMOTE_DASHBOARD_QUICK_START.md` with three-terminal manual restart and orderly shutdown, preserving sensor/power/controller cables and requiring verified motor inhibit before handling. User has not yet confirmed move/shutdown, physical stop mechanism or real driving readiness; ask lab staff if uncertain. No motion or shutdown executed by tools.
- Remote colour/YOLO viewing accepted 2026-10-19: after instructions to select YOLO labels, user reports everything working well. Treat remote camera and annotated-view workflow as user-confirmed functional milestone, not a measured accuracy/FPS/latency or independently captured annotated screenshot. Existing sensor launch + read-only dashboard + SSH tunnel are still manually started and must remain running for viewing. No live LiDAR/browser result, motor-output integration, physical stop/controller timeout or automatic boot has been demonstrated. Next mobility stage is supervised base/controller/stop verification before any live driving implementation, preserving the perception/fusion scope.
- Live browser camera milestone 2026-10-19: user pastes successful robot `server.py --ros` startup (`ros_read_only`, motor output not implemented) and explicitly reports seeing the camera in the laptop browser. This demonstrates existing robot Python/ROS/cv_bridge/OpenCV initialization and a usable colour-image path, not quantitative frame rate/latency, YOLO annotated view, LiDAR, fusion or motion. User sees no boxes; current selected source not supplied. Default Colour camera intentionally reads raw RGB; first switch View to YOLO labels before diagnosing detector/publisher failure. No model/settings/code change needed on this evidence.
- SSH/headless observation 2026-10-19: user believes camera/YOLO launch works but usual window does not appear on robot monitor; no logs/topic/image yet supplied. Copied detector disables its OpenCV window when XOpenDisplay fails and still generates/publishes detection images when subscribed, so lack of GUI is consistent with an SSH session without display access, not proven camera failure or confirmed live detection. No DISPLAY/X-forwarding/vendor-setting change. Next run dashboard `--ros` from another sourced robot SSH shell while retaining sensor launch and tunnel, then inspect colour/YOLO browser views/errors.
- ROS startup state clarified 2026-10-19: pasted shell output shows ROS_MASTER_URI `http://localhost:11311` and no output from `pgrep -af 'rosmaster|roscore|darknet_ros|astra_camera'`. Together with prior unreachable-master result, no local master/detector/Astra process is currently evident; this is not an exhaustive process or hardware audit. Next start known sensor-only `roslaunch darknet_ros yolo_v3.launch` (camera + general YOLOv3-tiny; local master normally auto-started), retain its terminal, then use another robot SSH shell to run dashboard with `--ros` while keeping laptop tunnel open. No separate camera, mapping/base, motor controller or autonomous launch needed; live camera/ROS dashboard still pending.
- ROS readiness check 2026-10-19: user reports `Unable to communicate with master` after sourced/bounded topic-list instructions. Confirms master unreachable from that shell, not that master is certainly stopped or camera is faulty; actual ROS_MASTER_URI and local process state not supplied. Next read-only URI/process inspection before camera/YOLO startup to distinguish no master from incorrect address and avoid duplicate drivers. Existing generic `darknet_ros yolo_v3.launch` includes camera (no base in copied launch); do not add separate camera/mapping/base or change ROS addressing blindly. Browser preview already demonstrated; ROS viewer remains untested.
- Browser preview milestone 2026-10-19: user screenshot displays the expected dashboard with PREVIEW ONLY, no-camera placeholder, camera-topic selector and explicit motor-output-disconnected/rehearsal-only banner after robot server/tunnel instructions. This confirms user-visible page delivery in the intended workflow, not ROS/camera/scan data, physical motion or auto-boot. 'Page hidden. Rehearsal disabled' is an expected browser lifecycle message, not a camera fault. Next: retain the tunnel, stop/restart only the personal preview server as needed, source robot ROS and inspect bounded current topics before any sensor startup to avoid duplicates.
- Robot-hosted dashboard preview confirmed 2026-10-19 by pasted terminal output: `/home/wheeltec/fahad/remote_dashboard/` contains `server.py`, `control.py`, `dist` and supporting files; `python -u ~/fahad/remote_dashboard/server.py` prints `http://127.0.0.1:8765/` and explicit preview/no-motor/loopback-only mode. This establishes remote files present and server startup, not yet browser reachability, ROS imports/streams or live driving. Exact Python version and transfer method/host-key comparison not shown. Next: keep robot server terminal running, open laptop-local SSH tunnel to the robot address, then visit laptop loopback URL. No ROS, drivers, motors or boot services started by this preview.
- Local TCP milestone 2026-10-19: user reports the Windows SSH-port test to `192.168.0.100:22` succeeded after invoking PowerShell from Command Prompt. This is user-reported laptop-to-address TCP reachability, not yet SSH host identity, login, internet or dashboard deployment. User pauses connection steps to ask about CMD versus PowerShell; no remote commands or additional access attempted. Next connection stage when resumed is host-key verification and authorized login.
- Connection report 2026-10-19: user says connected to WHEELTEC Wi-Fi but it has no internet; which device is connected and actual local reachability remain unverified. Next scoped check, if Windows laptop joined, is `Test-NetConnection 192.168.0.100 -Port 22` against the address from the live robot report. Offline internet status is not itself a failure of the local link. No successful TCP/SSH login, credential validation by tools, host-key check, program copy/start or dashboard access yet demonstrated.
- Network workflow clarification 2026-10-19: user reports recovering the Ubuntu credential; Wi-Fi credential is still only a hypothesis and must be tested locally. Do not store or repeat supplied credentials. User wants to retain internet/chat when connecting to the likely offline robot AP. Simplest option is laptop on robot Wi-Fi and phone on mobile data for chat; optional phone USB cellular tethering to laptop or robot Ethernet plus laptop internet Wi-Fi require device/adapter/policy/routing checks. Phone alone joining the robot AP does not give the laptop reachability; current loopback/SSH dashboard is not directly phone-browser accessible. No network connection, credential test or routing change performed.
- Credential constraint 2026-10-19: user also does not remember the Ubuntu account password; continued logged-in session is not confirmed. Conditional next step is the matching Wi-Fi profile's narrow local PSK query without sudo using existing account permissions. If hidden/denied/login required, involve lecturer/lab administrator; do not reset shared credentials or reboot/log out merely for this check. No password received/retrieved, account recovery or SSH key setup performed. SSH password access remains unresolved, alongside Wi-Fi connection.
- Live network report 2026-10-19 (`Terminal Reports/report_1531_19102026.txt`): `wlan0` connected through saved profile `Wi-Fi connection 1`; `docker0` connected, `eth0` unavailable; hostname addresses `192.168.0.100` and `172.17.0.1`; SSH service `active`. First address is a LAN candidate, not yet interface-mapped/reachable from laptop; second consistent with Docker. Actual SSID/AP-versus-client mode, internet and laptop login remain unverified. Next read-only SSID/mode query for this exact profile, then user may inspect matching network's saved PSK locally without sharing it. No credential retrieved, robot/network change or dashboard deployment performed.
- Local network evidence 2026-10-19: user screenshot shows a secured Wi-Fi SSID `WHEELTEC_CAR_5.5` visible on the laptop; user does not know its password. This confirms a visible candidate network name only, not that this robot is its host, internet availability, an actual connection, IP or SSH. Next read-only check is active NetworkManager profile names/types/devices on the robot; if it hosts the AP, inspect its saved password locally or ask the lab owner. No password should be sent in chat, guessed from unrelated vendor defaults, reset or changed. Dashboard remains undeployed to the robot.
- Remote dashboard v0.1 implemented locally 2026-10-15 in `Tools/remote_dashboard/`: loopback-only Python backend, local browser assets, optional ROS RGB/YOLO/2D scan reader, stale-data indicators, explicit preview mode and no-motor control rehearsal. No ROS publishers, driver/process launch, recording or boot/service/network changes. First version uses existing cv_bridge/OpenCV rather than requiring web_video_server/rosbridge. 31 offline/loopback Python tests and 12 fake-DOM frontend checks pass; embedded-browser display, source selection and enable/release-to-disable checked. Robot ROS/Python 2, live camera/scan, wireless link, controller stop, motion and no-monitor boot are untested. Copy/run/tunnel and subsequent gates: `Tools/remote_dashboard/README.md`. User's prioritisation supersedes today's earlier fusion-first schedule; actual AP/IP/SSH still needed. No custom model training or fusion implementation added.
- Remote camera-view feasibility 2026-10-15: user believes the robot broadcasts Wi-Fi and asks about replacing its attached monitor with an app. AP/SSID/IP/SSH remain unverified. Proposed local browser stream from existing RGB/YOLO image topics, using ROS 1 `web_video_server` if available; saved vendor command sheet mentions it but installation is not confirmed. Browser needs no Windows ROS or internet for local viewing after setup. Full monitor-free operation additionally needs tested remote startup and GUI-independent nodes; existing RViz/OpenCV helpers are not automatically browser apps. No dashboard/stream/headless setup installed, implemented or selected as a new thesis deliverable. Details in `Documentation/ROBOT_FILE_TRANSFER_AND_REMOTE_TERMINAL.md`.
- Local-transfer planning 2026-10-15: user does not know how to connect the robot to internet and wants to avoid SSD trips. Explained local SFTP/SSH needs device reachability, not internet. Existing `Documentation/ROBOT_FILE_TRANSFER_AND_REMOTE_TERMINAL.md` updated with read-only nmcli/interface/SSH checks and conditional approved network/AP/hotspot/Ethernet routes. Actual IP, SSH state and shared link remain unverified; no guessed manual IP, credential collection, service install, network/ROS/firewall change or direct robot access performed. WinSCP on laptop is optional preparation, not installed here. Allow a short initial network check in today's lab plan, retain SSD fallback; GUI apps remain local to robot initially.
- Planned lab session 2026-10-15, user expects approximately 13:00 arrival: `Documentation/LAB_PLAN_2026-10-15.md` provides startup/report/review and conditional first-projection steps within the pretrained camera-LiDAR scope. Reuses existing one-message sampler; no new program or completed experiment claimed. Copied sensor-only wrappers may leave camera/laser TF trees disconnected; robot-model launch contains nominal senior_akm transforms explicitly requiring measurement, not values to publish blindly. Next evidence is the focused `fusion_check_...txt` report; no model training/comparison, base/follower/navigation launch, map reset or unverified TF workaround required.
- User narrows implementation on 2026-10-14 to the existing pretrained YOLO model, no custom training/fine-tuning, camera-LiDAR association and labels; alternative-model work is not required. Focus becomes integration/evaluation with unknown association where unsupported, first local observations then validated map markers. This supersedes prior comparison-first recommendations, not unresolved calibration/timing/pose checks. No live robot changes while user is away; December soft target/four intended hours daily retained. See agreed-direction section and `Documentation/AGREED_PRETRAINED_FUSION_SCOPE_2026-10-14.md`.
- Low-camera model research refreshed 2026-10-14: Omobot is a particularly relevant human/fall-oriented reference (15 cm camera, paper reports Nano 4GB/R32.5.2/Melodic) using YOLOv8-Pose plus viewpoint processing, not a generic floor-trained non-YOLO replacement. Current robot repo asks JetPack 4.6.4, so matching paper versions do not establish drop-in compatibility. Public fall notebooks/weight filenames located but not loaded/audited. SSD-MobileNet-v2 via jetson-inference/ros_deep_learning remains the first proposed practical non-YOLO comparison with documented Nano/JetPack 4 and Melodic paths; not installed or proven superior. Legacy low-RGB-D people tracking has MATLAB/OpenNI 1.5 dependencies. Keep v3-tiny baseline and final model open; hardware inventory and saved-image comparison precede deployment changes. Research: `Reference Library/LOW_CAMERA_MODEL_REVIEW_2026-10-14.md`. No task expansion into fall-only detection, autonomy, training or installation approved.
- Planning/model discussion 2026-10-14: user confirms selecting the box manually; another screenshot is not required just to establish that click, though geometric alignment/accuracy remain unverified. Conditional schedule ranges and official YOLO26/legacy-Jetson research are recorded in `Documentation/TIMELINE_AND_MODEL_OPTIONS_2026-10-14.md`. YOLO26n is an investigation candidate, not the selected model. Official guide includes original Nano 4GB/JetPack 4.6.1 and a JetPack 4 container route, but actual robot R32.5.2/Python 3.6.9 is older; host CUDA/TensorRT/PyTorch/Docker compatibility and performance remain unmeasured. Keep v3-tiny baseline intact; propose read-only runtime audit and saved-image comparison before any isolated deployment. No install/upgrade/reflash or final scope change authorized. Deadline/hours unknown; rough cumulative ranges at 10-15 h/week: 1-2 weeks preliminary person-depth, 4-6 weeks evaluated camera prototype, 6-10 weeks including basic labelled map/valid pose. Writing/autonomy/broad custom training excluded, not a deadline promise.
- Live manual box-depth milestone demonstrated 2026-10-13 by `Terminal Reports/box_depth_20261013_131056.txt`: 10 manual selections/30 periodic rows, sampled near medians ~0.81 then ~1.08 m, farther ~2.06-2.07 m. User identifies later ~3.80-3.85 m at old pixel (232,287) as wall after the box moved right; re-click (381,304) yields 2.498 m. Fixed-pixel sampling is not object tracking. 36/40 selected patches have 100% finite-positive values; printed approximate-pair header gaps 1.3-34.6 ms. Numerical GUI workflow works, but no screenshot, measured reference, exact Python version, range accuracy or spatial registration proof supplied. Supersedes viewer-unrun status below. Next: one selected-box screenshot for preliminary correspondence, then a limited person-depth prototype with proper original-image association; no node/fusion/map change yet. Analysis: `Documentation/BOX_DEPTH_LIVE_RESULT_2026-10-13.md`.
- User's floor-level observation on 2026-10-13: YOLO detects a person but not the approximately 1 m box/chair; no current image/prediction data supplied, so angle as cause remains unverified. Copied general class list includes person/chair but no generic box. Manual box-depth viewer remains unrun and does not depend on a YOLO label: first distinguish a visible-but-unlabelled target from a target outside RGB view. Keep mounting/settings unchanged pending evidence; adjust target placement if needed. This does not establish a new model-performance metric.
- Lab work resumes 2026-10-13 with a floor-level box at user-estimated approximately 1 m and no ruler; treat the next run as plausibility/visual alignment, not accuracy validation. Prepared `Tools/box_depth_viewer.py` for manual 11x11 local-depth patches, RGB/depth panels, optional overlay, labelled historical freeze and bounded approximate pairing/age/geometry checks. Numerical availability and in-range fraction are distinguished from correctness; out-of-range readings remain visible. Thirteen offline Python 3 tests and help parsing pass; robot-side GUI/ROS/Python 2 run pending (local cv2 absent). Guide: `Documentation/BOX_DEPTH_FIRST_CHECK.md`. Does not need YOLO to recognise the box and does not alter original software, settings or motion. A measured reference, calibration/alignment and exact detection-image association still precede validated person-distance/map output.
- Full-image registered-depth monitor report uploaded 2026-10-12: `Terminal Reports/depth_check_20261012_142749.txt` contains ten snapshots of 640x480 `32FC1`, post-startup RGB/depth arrival rates 29.5-30.0/s and 58.4-60.3% finite-positive depth pixels. This establishes numerical coverage, not accuracy: the script has no physical-range check, scene medians are 3.76-4.03 m and maximum is repeatedly 9.78 m, exceeding the authoritative Astra S 0.4-2 m specification. Keep hardware identity/range unchanged pending known-distance validation. Warning at invalid-value comparison is nonfatal in this output; no script/settings fix implemented. Next: measured approximately 1 m matte target/local depth check and RGB/depth alignment/time association before person distances. Analysis: `Documentation/DEPTH_CHECK_ANALYSIS_2026-10-12.md`. AI documentation-harness discussion is conceptual only; no new runtime/API integration approved.
- Live person-filter milestone demonstrated by uploaded `Terminal Reports/report_1500_12102026.txt` on 2026-10-12: startup at trial cutoff 0.5, received-box logs, and two readable `/fahad/person_boxes` messages containing person ID 0 with scores 0.814858675003 and 0.924618005753. This supersedes live-topic verification as an outstanding first-test requirement below, but the exact Python version, paired source-field preservation and empty-output echo were not captured. Retained box counts are hypotheses, not unique people or accuracy; logs are throttled, not FPS. No model/annotation changes. Next proposed diagnostic is usable registered-depth coverage under current YOLO operation, then alignment/synchronization and known-distance checks before person-distance output. Result: `Documentation/PERSON_FILTER_LIVE_RESULT_2026-10-12.md`.
- Development proceeds at user's request on 2026-10-12 without further annotation polishing. Preserve v1/v2 as provisional references, with v2's draft still excluded; another export is not required before implementation. A separate person-only ROS postprocessor is prepared in `Tools/person_detection_filter.py`: original `/darknet_ros/bounding_boxes` -> `/fahad/person_boxes`, configurable trial cutoff 0.5, original headers/geometry/scores retained. No original detector settings, motion commands, tracking, cloud service or final-model decision introduced. Nine offline Python 3 tests and CLI help pass; live ROS/Python 2 verification remains required. Copy/run guide: `Documentation/PERSON_FILTER_FIRST_TEST.md`. Next: validate the personal topic on the stationary robot, then verify RGB/depth alignment before depth association. Chair annotations are not a blocker for this person-focused milestone; final independent evaluation and animal targets remain in scope.
- V2 export reviewed 2026-10-12: `pilot_annotations_v2.json` validates against all 31 source-image hashes and changes 17 frames, with 21 person/73 chair boxes. Thirty frames confirmed (29 regular + challenge); moving-run 0001, page position 11, remains draft. Added edge-chair coverage and expanded person boxes show progress; no ignore/occlusion metadata yet. Clarified that only confidently identifiable whole/partial targets should get class labels, one box per object; genuinely ambiguous fragments use Ignore region, not forced categories. No size-based exclusion rule introduced. Conditional metrics remain provisional; correcting person bounds exposes a localization mismatch, not deterioration of the unchanged detector. Guide: `Documentation/PILOT_ANNOTATION_V2_REVIEW_2026-10-12.md`; clarified `Documentation/ANNOTATION_WORKFLOW.md`. User annotations and camera/model settings unchanged by analysis.
- First human pilot export received 2026-10-12: `Annotation Review/pilot_annotations.json` marks all 31 images reviewed and contains 21 person/50 chair boxes; dataset identity/box geometry and all 31 raw hashes validate. Eight-image visual spot check reveals unlabelled visible foreground/edge chairs and incomplete visible-person extents; no occlusion/ignore flags exist. Results are provisional pending user corrections and a preserved `pilot_annotations_v2.json` export, not approved ground truth or final accuracy. Under current labels, regular person matched/extra/unmatched counts change from 20/14/0 at cutoff 0.3 to 20/3/0 at 0.5; chair matches drop from 34 to 23. Additional same-class suppression has no sampled effect; the separate challenge still misses a labelled person. Guide/results: `Documentation/PILOT_ANNOTATION_RESULTS_2026-10-12.md`; machine-readable analysis: `Annotation Review/pilot_evaluation_2026-10-12.json`. No labels or robot/model settings changed by analysis.
- Model-direction clarification 2026-10-09: user wants to understand YOLO before starting annotation. YOLOv3-tiny remains the unchanged baseline, not a final model selection. Proposed direction is a small human-reviewed reference, baseline/one compatible alternative comparison, then justified fine-tuning and validated depth/map integration. Filtering unwanted categories is separate from teaching new categories; do not shorten/reorder the existing 80-class label list while retaining its network/weights. Beginner concepts and primary-paper reading order: `Documentation/YOLO_BEGINNER_AND_MODEL_DIRECTION.md`. No model installation, training or annotation confirmation occurred in this discussion.
- Assisted annotation pilot ready 2026-10-09: open `Annotation Review/pilot_annotation_review.html` locally on Windows to review 30 evenly spaced raw images plus a separate known difficult case. Person/chair rectangles, optional detector suggestions, uncertain regions and reviewed-only score comparisons are implemented; labels export as `pilot_annotations.json`. Scoring and isolated Edge UI/persistence/export tests pass. No human annotations or accuracy scores exist yet. Guide: `Documentation/ANNOTATION_WORKFLOW.md`. This is a development reference for comparing settings/postprocessing and later models; final evaluation requires independently collected sessions. Annotation does not automatically retrain YOLO or alter the robot.
- Personal detector recorder implemented 2026-10-09: `Tools/record_detection_test.py` captures timed JPEG snapshots and bounding-box JSON records under `~/fahad/detection_tests` with exact image-header matching, optional drawn previews, readable reports and unique run folders. It only subscribes to already-running camera/YOLO topics; source targets Python 2.7/3. Guide: `Documentation/DETECTION_TEST_RECORDER.md`. Seven offline checks now pass locally on Python 3; three uploaded robot runs verify the live recording path. Missing detection messages are explicitly unknown; the recorder does not currently subscribe to the object-count topic, include depth/LiDAR, or establish accuracy.
- Timed pilot analysed 2026-10-09: three completed 30-second runs in `Tool reports/detection_tests/` contain 841 exact-header-matched detection records and 157 saved raw/preview pairs, with no missing references/unwritten detections. Notes distinguish empty scene, moving person and person-with-chair although all labels say `empty_room`; original metadata unchanged. Empty scene repeatedly labels chairs as traffic lights (277/278 messages), moving-person images show duplicate/background person hypotheses, and chair-run image 0030 shows a visible partly occluded person missed. Median header gaps are approximately 303-306 ms. Confidence filtering has measurable tradeoffs and has not been applied to the robot. Analysis: `Documentation/DETECTION_PILOT_ANALYSIS_2026-10-09.md`. These are descriptive baseline findings, not formal accuracy metrics or measured detection ranges; next work is object-level annotation/comparison before map association.
- Qualitative pilot reported 2026-10-09: user observes flickering chair detections and occasional traffic-light misclassification, successful person detections including seated/occluded views, and detection at an estimated approximately 4 m without a captured image or measured distance. Attached stills show person boxes, an extra person-labelled hand/arm region, multiple/overlapping chair boxes and a small unverified background person label. This is not a quantitative accuracy result, reliable maximum-range measurement, hand detector or depth-range extension. Missing chair detection with a seated person may involve occlusion/contrast but cause is unproven. Baseline remains unchanged; proposed next evaluation aid is timestamped raw-RGB/detection capture for repeatable solo tests, not yet implemented.
- Speed baseline reported 2026-10-09 via pasted `report_0908_09102026.txt`: final displayed `/camera/rgb/image_raw` rate 29.617 Hz (interval 16-50 ms, std dev 5.23 ms) and `/darknet_ros/detection_image` rate 9.249 Hz (84-132 ms, std dev 10.76 ms). Mean intervals are approximately 33.8 and 108.1 ms. These sequential short message-arrival tests do not establish unique-frame inference FPS, end-to-end latency, dropped-frame fraction or long-run stability. Next step is controlled qualitative detection testing with negative scenes and person examples, leaving baseline settings unchanged before depth/LiDAR integration.
- Numeric detector interface confirmed by `Terminal Reports/report_1715_08102026.txt` (identical to external-buffer upload): `/darknet_ros/bounding_boxes` supplies class, confidence score, class ID, pixel bounds and input-image header. One message contains three chair and two tvmonitor hypotheses, with nested same-class boxes; it does not establish five unique objects. Input frame is `camera_rgb_optical_frame`; one output-minus-image timestamp difference is 0.300077874 s, not a measured inference benchmark or FPS. No distances, unique tracked IDs or map positions are supplied. Robot timestamp date differs from report filename, so clock/acquisition date needs verification for cross-device synchronization. No parameters changed; next checks are publication rates and controlled detection evaluation before validated depth association.
- First successful user-reported live detector test, reported 2026-10-08: three annotated images in `Terminal Reports/pictures/YOLO V3_screenshot_06.10.2026*.png` show person/phone detections and false person labels on a chair, including combined `person, chair` labels. SHA-256 confirms these are the attached screenshots. Generic YOLOv3-tiny is the intended baseline from the preceding launch workflow; startup logs/model identity and GPU execution are not independently captured. This supersedes earlier untested-inference status, but is not an accuracy/speed benchmark, depth result or semantic map. Screenshot filenames have a different date (06 October), so acquisition date remains unverified. Next step is a bounded numeric bounding-box sample, followed by repeatable robot-view evaluation; no model/threshold change or final-model decision has been made.
- Follow-up `Terminal Reports/report_1659_0810_2026.txt` confirms a compiled executable at `~/wheeltec_robot/devel/lib/darknet_ros/darknet_ros` (1,525,144 bytes) and generic YOLOv3-tiny weights (34M rounded) on the robot. Live YAML selects generic CFG/weights, threshold 0.3 and 80 labels including person/chair/diningtable/cat/dog but not hand. The actual live CFG, dynamic-library compatibility, GPU use and successful inference remain unverified. Copied `yolo_v3.launch` selects that generic model and also starts the camera; first run must avoid duplicate camera startup and active motion-capable consumers. No installation/rebuild or final model selection is needed for this baseline attempt.
- Robot detector discovery, 2026-10-08: after sourcing `~/wheeltec_robot/devel/setup.bash`, `rospack find darknet_ros` resolves to `/home/wheeltec/wheeltec_robot/src/darknet_ros/darknet_ros`; `ros_deep_learning` is not discoverable in that environment. Detector execution and executable/model compatibility remain unverified; final model choice remains open. This report contains no IP/SSH checks, so network transfer is also still unverified.
- Windows off-robot SSDLite pilot: user created `Testing other Models/DetectorTest/test_detector.py` from the provided example. Screenshot diagnosis on 2026-10-07 shows Python 3.11 was not available to the user's Python manager, preventing `.venv` creation; the folder currently contains no `input.png` either. Installation/recovery instructions were provided, but no dependencies were installed or inference run by the assistant. This is not yet a successful detector experiment or a final model selection.
- Completed core report `reports/Ros topic report 22 topics.txt` (robot timestamp 2026-10-01 13:09:20 +02:00) confirms version-2 collection reached all 22 selected topics: 15 received messages, seven had no sample. The 188-topic inventory contains 39 message types and 74 configuration channels. Full analysis/index: `Documentation/ROS_CORE_REPORT_ANALYSIS_2026-10-01.md` and `Documentation/ROS_TOPIC_INVENTORY_2026-10-01.md`. Raw report preserved; this supersedes inventory-only uncertainty for the successfully sampled outputs, not their accuracy/quality limits.
- Live camera messages now confirm 640x480 `rgb8`, depth `/camera/depth/image` as `32FC1`, `/camera/depth/image_raw` as `16UC1`, and `/camera/depth_registered/image_raw` as `32FC1` despite the suffix. Centre depth examples are approximately 1.272 m / 1272 mm; eight of nine preview positions are invalid, which is not a full-frame validity percentage. Both XYZ and XYZRGB camera clouds arrived (640x480 point slots), but their first eight XYZ samples are NaN; full-cloud finite coverage remains unknown.
- Calibration pairing requires verification: registered-depth image uses `camera_rgb_optical_frame`, while registered-depth CameraInfo uses `camera_depth_optical_frame` and K/P principal points shifted -5/-4 pixels versus RGB. Copied Astra code has a plausible registration/header/offset mechanism, but live settings and processing must be checked before RGB-depth fusion; do not blindly modify calibration or assume same-sized frames align.
- The same report captures `/scan` from `/lsn10`, frame `laser`: 464 rays over approximately -pi..pi, 351 finite/in-declared-bounds (75.65%), sample range 0.571-3.915 m. Metadata scan_time implies approximately 9.77 Hz, not a measured topic rate. Declared 0-100 m limits remain unverified hardware limits; physical device identity and accuracy remain unconfirmed.
- GMapping and RTAB-Map occupancy grids were received, both 5 cm/cell, respectively 672x384 and 285x173. Their timestamps predate report start by approximately 35m19s and 34m46s; this proves available nonempty grid messages, not current updating, correct geometry, a saved map, or successful navigation. The previous empty uploaded `test.db` remains historical evidence only. `/rtabmap/info` and `/rtabmap/cloud_map` were silent in their windows.
- `/odom`, `/imu`, and `/PowerVoltage` all had `/wheeltec_robot` registered but no sample. Copied base code gates all three on valid incoming controller serial data, so the shared base telemetry path is a prioritized diagnostic hypothesis, not a confirmed fault. `/cmd_vel` had no publisher; RViz's `/move_base_simple/goal` had no subscribers. One transform each from `/tf` and `/tf_static` does not validate the full frame graph; zero model joint states do not prove measured wheel feedback.
- Read-only inspection on 2026-09-16 of uploaded `Terminal Reports/test.db` establishes that this snapshot is structurally valid but empty of map data: Node/Data/Link and feature tables have zero rows, and saved optimized grid/cloud/poses are NULL. Stored database schema version is 0.20.23. This file cannot supply a room map for the configured localization-mode navigation demo. A new protected mapping session or another valid existing map is required; see `Documentation/RTABMAP_DATABASE_INSPECTION_2026-09-16.md`. The original upload is unchanged, and no robot navigation/mapping has been started by this inspection.
- The user subsequently confirmed `rospack find amcl` resolves to `/home/wheeltec/wheeltec_robot/src/navigation-melodic/amcl` and created the personal folder on the robot. A separate mapping launch is prepared at `Tools/fahad_3d_mapping.launch`, intended to be copied to `~/fahad/launch`; it saves by default to `~/fahad/maps/lab_room.db`, never automatically deletes an existing database, and preserves the vendor source. The staged stationary/motion/clean-shutdown procedure is in `Documentation/PERSONAL_3D_MAPPING_FIRST_RUN.md`. It has not yet been run on the robot.
- After the personal launch path was not found on the robot, the user chose to use the installed vendor `3d_mapping.launch` for the first trial. This is acceptable for the empty/default database because a copy is preserved, but every vendor mapping start recreates `~/.ros/test.db`. The exact stationary checks, RViz setup, slow Ackermann teleoperation, 2D snapshot, shutdown and backup sequence is stored in `Documentation/VENDOR_3D_MAPPING_COMMAND_SEQUENCE.md`. No successful mapping launch or robot movement has yet been reported.
- The installed mapping feature is not merely storage. GMapping builds `/map` from LiDAR/odometry; RTAB-Map synchronizes RGB-D, scan and odometry into a pose graph, publishes `/rtabmap/grid_map`, refines/reconnects observations and stores the database for later localization/navigation/reconstruction. The copied grid uses LiDAR (`Grid/FromDepth=false`), and navigation's live obstacle source is `/scan`. The alternative `pure3d` files use camera depth without the physical LiDAR, but contain static camera-derived scan frames at 0.5 m and 0.1 m and a 4 m range setting that conflict with the measured mounting and Astra S range; they require recalibration. Details are in `Documentation/ROBOT_MAPPING_CAPABILITIES.md`.
- Uploaded `reports/ros_topic_report_20261001_123744.txt` inventories 188 topics and shows mapping-related publisher registrations plus `/rtabmap/rgbd_sync` as a depth subscriber. It does not establish valid maps or successful navigation. Sampling stops at the seventh topic (`/camera/depth/image/compressed/parameter_updates`); earlier readers repeatedly hit the old three-second deadline during ROS initialization. One printed sample was incorrectly labelled as no data after timeout. The precise persistent-stall mechanism remains unverified.
- The read-only topic report is now version 2: `Tools/ros_topic_report.sh` plus `Tools/ros_message_sample.py` must be copied together. It inventories all topics, defaults to sampling up to 22 core interfaces first, exposes installed message definitions and bounded actual array/pixel/cloud/range samples, and applies per-command deadlines with forced-stop fallback. `ROS_TOPIC_REPORT_MODE=all` also samples settings/transport topics. Instructions and interpretation are in `Documentation/ANALYSE_ALL_ROS_TOPICS.md` and `Documentation/ROS_TOPIC_PROGRAMMING_REFERENCE.md`. Ten offline formatting tests pass, but live ROS/Melodic Python 2 execution and Bash validation remain robot-side checks. Reports are not synchronized datasets or performance/accuracy validation.

- The copied camera/LiDAR navigation demo is explained in `Documentation/CAMERA_LIDAR_3D_NAVIGATION_EXPLAINED.md`. It loads `~/.ros/test.db` in localization mode, starts the physical base plus move_base/TEB, AMCL, camera and LiDAR, and plans on a 2D grid. Its mapping include sets `Grid/FromDepth=false` and live obstacle layers use `/scan`; viewing a 3D cloud does not prove camera-based obstacle avoidance. The companion mapping launch deletes the same database on start. `send_mark.py` can turn RViz Publish Point clicks into navigation goals. Report 2 confirms the expected depth topic is delivering messages, but TF, odometry and the controlled stop procedure remain unverified; the user has not launched 3D navigation.
- Terminal report 2 (2026-09-16), analysed in `Documentation/TERMINAL_REPORT_2_ANALYSIS.md`, confirms discoverable ROS Melodic RTAB-Map, move_base and TEB packages; a follow-up correctly spelled check confirms AMCL at `/home/wheeltec/wheeltec_robot/src/navigation-melodic/amcl`. `/lsn10` and camera nodes were running. The uploaded `/home/wheeltec/.ros/test.db` snapshot is 104K and modified March 2, 2023; subsequent read-only inspection confirmed that it has no stored map observations or optimized map. No base odometry, navigation processor or RTAB-Map grid was shown, consistent with sensor-only viewing. Goal-related topic names do not prove active navigation.

- Five robot photographs are stored in `Picture of Robot/`.
- A camera diagnostic script and initial sensor terminal measurements exist; no thesis detector implementation, labelled dataset or trained model has yet been added.
- `From Robotics Lab/` now contains the lab-session report, the approximately 1.2 GiB transfer ZIP, and its extracted four-workspace ROS source mirror. The mirror contains 4,489 files and 75 ROS packages; its detailed audit is in `From Robotics Lab/LOCAL_COPY_ANALYSIS.md`.
- The root file `ROS常用功能命令5.5.txt` is a WHEELTEC **ROS Commonly Used Function Commands 5.5** quick-reference sheet, not recorded sensor data or proof that all advertised functions are installed. An accurate annotated translation and safety classification is stored in `Documentation/ROS_COMMON_FUNCTION_COMMANDS_5_5_EN.md`. The uploaded copy differs from the extracted Chinese copy mainly by using the example network address `192.168.2.102` instead of `192.168.0.100`.
- The copied source is an analysis baseline, not a complete bootable robot image and not runtime proof. It should not be built, sourced, or launched as part of the live robot environment without a separate reviewed procedure.
- Do not publish the raw lab copy. It contains hard-coded third-party credential material, files above GitHub's normal per-file limit, nested Git histories, generated files, models/binaries, and mixed third-party licensing. Prepare a sanitized repository first and revoke/rotate exposed credentials.
- Camera recording conclusion: the Astra S does not automatically retain earlier use. The ROS driver publishes live RGB, IR, depth, registered-depth, camera-information, and point-cloud streams, and the data disappears unless Jetson-side software deliberately saves it. Prefer ROS bag recording for thesis data because it can retain synchronized sensor data and metadata. A pretrained model can perform live inference without a local image archive; training/fine-tuning and repeatable thesis evaluation require a deliberately assembled and labelled dataset. Live topic names, storage capacity, write performance, and dropped-frame behaviour remain to be measured.
- A beginner-safe camera-only activation, inspection, recording, shutdown, and troubleshooting guide is stored in `Documentation/CAMERA_QUICK_START_ROS1.md`. It uses the configured WHEELTEC camera wrapper and explicitly avoids the motion-capable visual-following demo.
- A read-only numeric camera-measurement procedure and Python ROS 1 monitor are stored in `Documentation/CAMERA_OUTPUT_DIAGNOSTICS_ROS1.md` and `Tools/camera_diagnostics_ros1.py`. They report live RGB/depth rate, encoding, resolution, exposure indicators, valid-depth percentage/range, optical frame, and calibration values without moving the robot. Recognition distance remains a detector experiment rather than a camera property reported by ROS.
- Live RGB measurements captured on 2026-09-10 confirm 640 x 480 calibration/output geometry in `camera_rgb_optical_frame`, approximately 29.60 FPS, approximately 27.4 MB/s, and approximately 0.92 MB per uncompressed image message. The raw RGB traffic alone corresponds to roughly 1.64 GB per minute before ROS-bag overhead, so storage must be checked before long recordings. The calibration reports `fx=582.795354`, `fy=584.395006`, `cx=321.415982`, `cy=245.98941`, and `plumb_bob` distortion. Report 2 adds a measured depth-message rate of 29.694 Hz, but depth-content validity/accuracy and registered-cloud performance remain unmeasured.
- Four uploaded `rqt_image_view` screenshots in `Picture of Robot/` show `/camera/rgb/image_raw` and an image area consistent with approximately 640 x 480, pending numeric `CameraInfo` confirmation. They demonstrate floor-dominant low-angle imagery, close-person truncation, furniture occlusion, strong backlighting, and decreasing target scale with distance; these conditions must be represented in robot-specific training and evaluation.
- The camera guide also documents simultaneous RViz Image and PointCloud2 viewing. A registered depth cloud is expected in the camera RGB optical frame, but its exact live topic/header must be captured. Camera PointCloud2 and LiDAR LaserScan can be overlaid only when a valid TF transform connects their frames; simultaneous sensor operation alone is not camera-LiDAR calibration.
- A beginner-safe LiDAR-only activation, `/scan` validation, RViz visualization, short recording, shutdown, and troubleshooting guide is stored in `Documentation/LIDAR_QUICK_START_ROS1.md`. It uses the configured sensor wrapper and explicitly excludes the motion-capable laser-following demo.
- A launch-verified map of direct sensor outputs and higher-level software is stored in `Documentation/CAMERA_LIDAR_SOFTWARE_CAPABILITY_MAP.md`. It distinguishes sensor-only viewing/recording, legacy TensorFlow/Darknet/AR perception, camera tracking, LiDAR mapping/navigation, camera-depth virtual scans, and combined RTAB-Map/physical-LiDAR functions from motion-capable demonstrations.
- `Documentation/SENSOR_2D_3D_EXPLORATION.md` provides a source-checked sensor comparison, camera specification boundaries, planar-versus-3D RViz experiments, driver-setting interpretation, and the distinction between one depth view and a reconstructed room. The N10 wrapper's `max_range: 100` is scan metadata, not a verified 100 m range. The shared Astra settings menu includes modes that may be unsupported by this device. The next work is stationary sensor characterization following lecturer feedback; full-room reconstruction remains a separate experiment, not a newly committed thesis requirement.
- A robot-viewpoint dataset, annotation, preprocessing, and evaluation specification is stored in `Reference Library/ROBOT_VIEWPOINT_ML_DATA_REQUIREMENTS.md`. The approximate sensor heights and relative placement are now recorded, but final model selection remains deferred until the fixed experimental camera tilt/floor coverage, real RGB/depth performance, target pixel size/range, and exact Jetson environment are measured.
- The copied source contains `xf_mic_asr_offline`, an optional Chinese offline wake-word/fixed-command system for a particular USB/HID microphone array. On 2026-09-10 Ubuntu reported `alsa_input.usb-ORBBEC_ASTRA_S-01.analog-stereo` as a 48 kHz, 16-bit stereo PulseAudio input, confirming an Astra-associated audio capture endpoint; physical/intelligible microphone capture still requires a recording test. This is not general rescue-sound recognition, and the package's `base.launch` is motion-capable; safe hardware-identification and test boundaries are documented in `Documentation/AUDIO_HARDWARE_AND_VOICE_SOFTWARE_CHECK.md`.
- Manual/capability and dataset research is documented in `RESEARCH_FOUNDATIONS.md`.
- A prioritized, evidence-graded literature review is stored in `Reference Library/LITERATURE_READING_LIST.md`.
- Battery/charger matching and safety requirements are stored in `Reference Library/BATTERY_CHARGER_REQUIREMENTS.md`.
- The AliExpress capability claim and the locations of public/private WHEELTEC materials are mapped in `Reference Library/WHEELTEC_CAPABILITY_DOCUMENTATION_MAP.md`.
- Relevant PDF references are stored in `Documentation/`.
- During the first development stage, the robot may remain stationary or be driven manually with a controller. Autonomous movement is not required.

## Documentation-distribution conclusion

- The AliExpress “Introduction to key function (full open source)” section is a family-wide capability and curriculum catalogue, not a link to one public manual and not proof that every option is installed on this robot.
- The listing advertises more than 130 video sections, matching manuals/source code and a course archive larger than 30 GB delivered through Baidu Netdisk. The saved listing pages do not expose the share URL or extraction code for that complete bundle; it must be requested from the seller or WHEELTEC using the order/item and the physical `senior_akm` identity.
- A smaller subset is public through WHEELTEC's online manual, official documentation-source repository and Bilibili playlists. Official R550/LubanCat system-image links are public, but must not be flashed onto the older R PLUS robot without a backup and compatibility confirmation.
- The pre-installed robot filesystem may be the most authoritative surviving source/configuration for the exact shipment. Inventory and back it up before upgrades.

## Important research distinction

Ordinary RGB object detection can recognize visible humans or animals, but it cannot prove that a subject is alive. The thesis must define whether the target is (a) human/animal presence detection, (b) victim detection, or (c) evidence of life using additional signals such as motion, breathing, thermal imaging, audio, or other sensors.

## Current literature conclusion

- A peer-reviewed paper explicitly uses the closest documented robot family, the WHEELTEC/Roboworks Rosbot Mini Ackermann, for ROS 2 teaching that includes perception and AI, but it does not evaluate a victim detector.
- No publication has yet been found that performs the exact visible-human/household-animal detection task on the exact WHEELTEC R PLUS `senior_akm` shipment.
- Closely transferable studies use other WHEELTEC platforms with Jetson hardware for YOLO detection, and rescue-robot studies show that lying, rotated, occluded, dimly lit, or partly buried victims are important failure cases for ordinary pretrained person detectors.
- The strongest newly found hardware/task analogue is Raghavan et al. (2026): YOLOv8 fine-tuned for visible victim body parts and deployed on a Jetson Nano camera-equipped mobile rescue vehicle. The closest current operating-mode/environment analogue is Gelfert (2022): an RGB camera on a remotely controlled mobile robot tested for victim detection in smoky indoor scenes.
- RGB-D victim literature supports evaluating partial body visibility and lying poses, and using depth as a later enhancement. Thermal and visible–infrared fusion papers reinforce that an RGB-only prototype should not claim reliable operation in dense smoke.

## Current recommended scope

### User-proposed direction, 2026-10-07

Follow-up clarification: the user explicitly agrees that camera recognition supplies the label before LiDAR association. They requested non-YOLO alternatives and references suited to floor-level indoor robot views; YOLOv3-tiny remains only an optional baseline, not a selected model. Robot-side checks are deferred to the next lab visit. The research shortlist in `Reference Library/NON_YOLO_AND_LOW_VIEWPOINT_REFERENCES.md` prioritizes SSD-MobileNet-v2 via jetson-inference/ros_deep_learning as a compatibility candidate, with SSDLite MobileNetV3 and optional off-robot RT-DETR comparison. No candidate has been installed or benchmarked. Robot@Home and THUD are relevant references but their documented camera positions do not match the user's 12-13 cm view; a robot-specific pilot/evaluation is still required.

The user now wants a reusable indoor object-detection foundation, allowing pretrained algorithms, with examples person, hand, table and chair, followed by camera-LiDAR object labelling and a labelled map. This expands the earlier detector-only/person-cat-dog proposal; semantic mapping is a planned extension, not an implemented capability or a new requirement for autonomous driving. Final thesis evaluation scope still needs lecturer alignment. The staged design is in `Documentation/INDOOR_DETECTION_AND_SEMANTIC_MAPPING_PLAN.md`.

Recommended first milestone: camera-only pretrained detection with class/score/box, then position estimates and a separate object-marker layer over validated SLAM. Camera supplies semantics; planar LiDAR supplies geometry/association only where its low scan plane actually observes the object. No requirement is adopted that the current LiDAR independently classifies every camera object. Hands remain a separate explicit task, not part of the standard COCO 80 classes; do not silently drop them or imply the existing gesture model meets the requirement.

Copied generic YOLOv3-tiny YAML, weights (35,434,956 bytes), ROS box/image outputs and `yolo_v3.launch` are present. This is a compatibility-first baseline candidate, not final selection or proof of installed/running detector. The main `darknet_ros.launch` defaults to gestures and starts the camera, so a personal detector-only launch should be prepared after read-only robot package/runtime verification. No detector code, launch or dependencies were changed/installed in this planning session.

### Earlier camera-first thesis baseline (retained as context)

Implement and evaluate a tool that detects visible humans and household animals from the robot's camera. The first prototype only needs to process the camera feed while the robot is stationary or manually controlled. Its essential outputs are the detected class, confidence, and bounding box; depth-based distance may be added if the installed camera supports it. Autonomous driving, mapping, path planning, and automatic victim approach are future extensions, not requirements for the current thesis stage. Treat physiological life-sign verification and deployment in active fire conditions as out of scope unless additional certified sensors and a separate validation plan are introduced.

The initial class proposal is `person`, `cat`, and `dog`. Robot-specific data must emphasize the measured approximately 12-13 cm camera height, lying/crouching/partly occluded targets, image-edge truncation, indoor clutter, difficult lighting, negative scenes, and actual robot motion blur. Because tilt is manual, choose and document one fixed experimental angle; changing it creates a different viewpoint domain unless angle-specific data are deliberately collected. Dataset splits must be grouped by subject/animal, room, and recording session rather than random adjacent video frames. Training should normally occur off-robot; the Jetson is the constrained deployment/evaluation target.

## Camera and LiDAR decision

- Use a camera-first workflow. RGB detection is the required baseline; registered camera depth is the first optional enhancement.
- The camera is now runtime-confirmed as Astra S. Its manufacturer-specified depth range is only 0.4-2 m, even though RGB targets may remain visible farther away. Measure this on the robot before defining the final ranging requirement.
- Include the 2D LiDAR in the detector only if the camera pilot reveals a required range/geometry gap and an explicit fusion test improves a pre-declared metric. LiDAR cannot classify a return as a human or animal and adds extrinsic calibration, TF, synchronization, association, and evaluation work.
- The copied software already contains legacy TensorFlow detection, Darknet/YOLO, AR-marker, KCF, gesture/skeleton, 2D SLAM/navigation, RTAB-Map, and depth-image-to-laserscan paths. These are reusable evidence/prototypes, not confirmed thesis solutions. In particular, the main `darknet_ros.launch` defaults to a gesture model, while a separate generic YOLOv3-tiny configuration contains person/cat/dog classes.
- The detailed physical-identification, recording, RGB, depth, and LiDAR decision procedure is stored in `Reference Library/CAMERA_LIDAR_DECISION_AND_VALIDATION_PLAN.md`.

## Current operating approach

- The researcher/operator controls the robot manually with a controller.
- The perception tool observes the live camera stream and detects visible rescue targets.
- Robot locomotion and autonomy must not be allowed to complicate or delay development and evaluation of the detection model.

## Continuity rule

Read `CHANGELOG.md` before starting new work. Update it whenever a material change, decision, research conclusion, implementation, or experiment occurs.

## Post-bachelor study intention (2026-10-13)

- User intends to pursue a master's; HTWK was an initial option, but on 2026-10-13 explicitly opened the search to other institutions near Halle, where they live. Degree/profile and admission eligibility remain undecided; no application or admission is confirmed.
- Updated interest: user specifically wants to learn more data analysis. Prior robotics-first recommendation is provisional and superseded as the first comparison priority by checking Informatik Master data-science electives and admission fit. HTWK lists statistical analysis in data science, event-time analysis, data warehousing, pattern recognition and AI; this remains a broad computer-science degree, not a confirmed dedicated Data Science master. Exact analytical interests and bachelor transcript remain unknown. Thesis scope unchanged.


- Learning goals independent of thesis: Python/programming, data analysis and hands-on creation. Regional advisory shortlist: Hochschule Anhalt Data Science (Köthen), Hochschule Merseburg Automatisierungstechnik und Informatik, Universität Leipzig Data Science, MLU Halle Informatik. No final selection; Python/project evidence strongest in the reviewed Anhalt examples, not a guarantee of beginner instruction or physical hardware projects.


- User identifies bachelor's field as electrical and automation engineering (2026-10-13); exact awarded title, institution, duration and ECTS not supplied. Relevant to admission assessment only; summer-entry comparability for Anhalt remains unconfirmed.
- Regulatory correction: Anhalt section 1(3) permits four-semester summer entry for computing/comparable 180-credit degrees too; programme overview omits this exception. Electrical/automation comparability remains subject to university assessment.
