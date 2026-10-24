# Project handover — indoor search-and-rescue robot

Last reviewed: **24 October 2026**. This is a documentation snapshot, not a claim that the robot was tested on this date. Source baseline before this handover: local commit `00ffa9f99240dca3e7264e450673995bea2971bc`.

## 1. Start here

The camera, existing YOLO detector, remote viewing and manual driving have worked in user-reported lab sessions. A conservative camera–2D LiDAR fusion prototype now exists and passes offline tests, but it has **not** been validated on synchronized real sensor recordings or run as live fusion on the robot.

The immediate dependency is fresh LiDAR data. In the latest reported checks, `/lsn10` was registered as the publisher of `/scan`, but `rostopic hz /scan` received no messages. `/map` also had no publisher. A registered node, a spinning sensor, a dashboard connection and a valid room map are different things.

Do not begin by replacing YOLO, increasing driving limits or starting navigation. First restore sensor delivery, verify calibration and timing, then record a stationary real example and replay it offline.

Evidence labels used below:

- **Source-tested:** laptop tests checked code, not physical operation.
- **Synthetic:** generated toy inputs, not detector or sensor performance evidence.
- **User-observed:** reported lab behavior, not independently instrumented validation.
- **Planned/blocked:** not completed merely because its calendar date has passed.

## 2. Goals and agreed scope

The bachelor-thesis topic is camera-based machine-learning detection of living beings for an indoor search-and-rescue robot. The practical first target is **person detection**; available indoor furniture classes provide useful association examples. Visual recognition of a person does not establish physiological signs of life, and general animal detection is not yet demonstrated.

The intended pipeline is:

1. Use the existing pretrained detector to label objects in camera images.
2. Associate a detection with actual LiDAR returns only when geometry, timing and foreground evidence support the association.
3. Express supported observations in a validated common/map frame.
4. Display temporary semantic observations separately from the existing occupancy map.
5. Evaluate detection, association errors, position estimates and runtime limitations using reproducible experiments.

On 14 October the user chose to continue with the working pretrained YOLO model, without making custom training or a new detector architecture a prerequisite. Current copied configuration points to YOLOv3-tiny; the exact running weights/configuration still need inventory confirmation before comparative benchmarking. A launch file named `yolo_v3.launch` alone does not prove which weights were loaded.

New SLAM development, autonomous navigation, conversion of the physical LiDAR to 3D, thermal/sound detection and a new learned fusion model are not required for this first implementation. Gazebo is deferred, not rejected permanently. Final thesis contribution and evaluation requirements still need lecturer alignment.

The working aim is implementation completion around early December 2026, separate from thesis writing. The planner's 7 December target is a movable planning default, not a confirmed hard deadline or completion guarantee.

## 3. Hardware and platform: evidence versus assumptions

| Component | Evidence and limitations |
| --- | --- |
| Chassis | Readable-label evidence recorded for WHEELTEC R PLUS, high-configuration Ackermann/standard variant; configuration `senior_akm`. Do not substitute an unconfirmed R550 identity. Car-like steering is not rotation in place. |
| Camera | Driver-reported Orbbec ASTRA S; working colour and depth streams observed. Structured-light RGB-D, not ordinary passive stereo or a colour-only camera. Keep driver identification distinct from physical-label confirmation. |
| Mounting | User estimates camera about 12–13 cm above the floor, LiDAR about 2–3 cm higher and behind it without blocking the view. Camera tilt is manual and unmeasured. These are not calibrated extrinsics. |
| LiDAR | Source/default driver and `/lsn10` suggest the LS/Leishen N10 family; exact physical model and specifications remain unconfirmed without a readable label/authoritative match. It measures ranges in a plane, not a volumetric 3D room. |
| Computer | Legacy NVIDIA Jetson-class, aarch64, L4T 32.5.2 and ROS 1 Melodic reported, with Python 2.7.17/3.6.9 environments. Nano/4 GB identification is still provisional; exact RAM, board and acceleration stack need inventory. |

Do not upgrade the robot's ROS, Python or operating system to match laptop tooling. Laptop tests and Python grammar compatibility are not Jetson runtime compatibility tests.

Published Astra S planning specifications cited in earlier records include depth 640 × 480 up to 30 Hz and approximately 0.4–2 m operating range. These are not measurements of this installed unit's accuracy. Existing reports contain unexplained positive depth values beyond that range; do not declare them accurate extended-range measurements or silently rescale them.

## 4. Decisions that must survive a handover

### Height and identity are the central fusion problem

The camera sees objects at many heights; the LiDAR samples one scan plane. A camera detection on a shelf may have no corresponding laser return, while a return projected inside its image box may belong to the wall behind it. A bounding box, angular overlap or a guessed object height does not prove common identity.

Use calibrated full 3D transforms of real planar points, correct camera intrinsics and the correct source image. Preserve unmatched/ambiguous results. Independently verified registered object-depth evidence can support an association, but is not infallible ground truth. A depth reading on the wall must not become the detected object's range.

### Map and display semantics

Typical occupancy-map colours are white/free, black/occupied and grey/unknown. **Grey is not confirmed traversable.** Even a free cell at the laser plane does not guarantee full robot clearance: overhangs, low obstacles, drops, footprint and motion constraints matter.

Laser colours depend on the renderer's chosen channel and scale, such as intensity or distance. They are not object classes and do not by themselves identify materials or absorption. A dashboard should state the actual colour channel rather than imply semantic recognition.

Keep the occupancy map and expiring labelled observations separate. Missing map transforms must not cause an invented origin or a permanent object marker. No current prototype updates the occupancy map or performs SLAM.

### Modularity, safety and authority

Reuse `Tools/fahad_core` for calculations; keep ROS, transport, UI, model loading and motion adapters separate. Imports must not connect, launch services, download weights or arm driving. Preserve distinct guarded motion profiles and existing entry points; do not rewrite vendor packages or historical records.

Ordinary settings cannot relax enforced motion/security limits. The maintained dashboard source requests at most **0.30 m/s**; the later request for 0.40 m/s was not enabled. Feedback guard thresholds are separate from requested speed. Do not resolve faults by raising thresholds or removing stale-feedback/lease protections.

Software Stop and successful release-to-stop observations are not proof of an independent firmware timeout or certified emergency stopping. A normal physical power cutoff has been user-confirmed, not certified as an emergency-stop system. A heartbeat stop after contact is not evidence of collision detection.

Source editing, robot deployment, public GitHub publication and private planner maintenance are separate authorizations.

## 5. Completed work and its evidence

| Work | Actual status |
| --- | --- |
| Camera and YOLO viewing | User-observed colour images and labelled detections. Chairs flicker/misclassify; low viewpoint, dark surfaces and occlusion remain difficult. |
| Topic delivery baseline | Provided terminal results show RGB about 29.6 Hz and detection-image output about 9.25 Hz. These are message rates, not unique inference FPS, latency or accuracy. |
| Person filtering | Live reported `/fahad/person_boxes` filtering from `/darknet_ros/bounding_boxes`, threshold 0.5, preserving the detector's source-image header. Filtering is not training or a new detector. |
| Detection recording/review | Three short runs produced 157 sampled images and 841 detector records with source-image keys. A 31-image pilot included a separate challenge image; v2 had 30 confirmed and one draft. This is not a final held-out benchmark or a training dataset. |
| Depth diagnostics | Registered depth stream reported as 640 × 480 `32FC1`, near 30 Hz. About 59% finite-positive coverage in one sample means coverage, not 59% accuracy. |
| Manual depth experiment | User clicked and moved a floor box. A fixed patch later sampled the wall until reselected. No measured reference distance established absolute accuracy; close timestamps alone do not prove spatial registration. |
| Remote operation | SSH, local tunnelling, file transfer and camera/detection web viewing worked by user report. Manual low-speed forward/self-stop and subsequent directional/ramped controls were observed. Fault stopping and Wi-Fi range are not validated. |
| Dashboard/Hub | Source implements guarded controls, camera/YOLO viewing, scan/map display and Windows SSH/service orchestration. Recent source versions are not confirmed installed on the Jetson. No proven power-on-to-ready unattended startup. |
| Software inventory | Copied source contains 75 package manifests and 273 launch declarations. A bounded read-only inventory tool is prepared; vendor packages and launch files do not prove installed hardware or successful functions. |
| Fusion prototype | Eight synthetic cases and 25 focused tests pass; no real synchronized data validation, live ROS fusion, navigation or room-map creation. |
| Quality/Git/planner | Shared modules, validated settings, diagnostics, source-bundle checks, local snapshots, reviewed initial public source and a separate private planner are established. See verification boundaries below. |

The user's approximate four-metre person observation is qualitative, not a calibrated maximum recognition distance. Pilot labels include partial/occluded chair interpretations; resolve a consistent annotation policy before drawing final precision/recall conclusions.

## 6. Code and documentation map

| Location | Responsibility |
| --- | --- |
| `Tools/fahad_core/` | Reusable depth, message, detection, recording, evaluation, inventory and fusion calculations. |
| `Tools/remote_dashboard/` | Sensor/motion adapters and browser interface; preview/read-only/live modes are distinct. |
| `Tools/robot_hub/` | Windows connection, tunnel, managed service status, diagnostics and runtime installation workflow. |
| `Tools/robot_inventory.py` | Explicit read-only inventory of selected source/runtime capabilities, not a full-disk scan. |
| `Tools/fusion_prototype.py` | Offline normalized-input evaluator and synthetic demo/report entry point. |
| `Tools/fusion_fixtures.py`, `Tools/fusion_demo_template.html` | Synthetic scenes and standalone report rendering. |
| `Tools/test_fusion.py`, `Tools/quality_check.py` | Focused fusion tests and the broader offline quality workflow. |
| `Sites/fieldnotes/` | Separate private planning app/repository; not the robot dashboard or part of public robot source. |

Runtime copying matters: standalone tools depend on the sibling shared package. The diagnostic source bundle currently has 19 files; the Hub's dashboard runtime bundle has a distinct 17-file contract. Keep manifests, tests, usage docs and copying instructions aligned rather than copying only the visible entry script.

Read these next:

- [Agreed scope](AGREED_PRETRAINED_FUSION_SCOPE_2026-10-14.md)
- [Height and association reasoning](CAMERA_LIDAR_HEIGHT_AND_ASSOCIATION.md)
- [Primary-source software/paper review](CAMERA_LIDAR_RESEARCH_2026-10-23.md)
- [Fusion v0.1 contract and usage](FUSION_PROTOTYPE_V01.md)
- [Robot software catalogue](ROBOT_SOFTWARE_CATALOGUE.md)
- [Modular architecture](MODULAR_CODE_ARCHITECTURE.md) and [quality workflow](QUALITY_WORKFLOW.md)
- [Current keyboard/map decisions](REMOTE_KEYBOARD_MAP_V011.md) and [plain LiDAR display](REMOTE_PLAIN_LIDAR_V012.md)
- [Hub operating guide](../Tools/robot_hub/README.md) and [dashboard guide](../Tools/remote_dashboard/README.md)
- [Depth evidence](DEPTH_CHECK_ANALYSIS_2026-10-12.md), [box experiment](BOX_DEPTH_LIVE_RESULT_2026-10-13.md) and [annotation review limitations](PILOT_ANNOTATION_V2_REVIEW_2026-10-12.md)
- [GitHub workflow](GITHUB_WORKFLOW.md) and [planner maintenance](PLANNER_MAINTENANCE.md)

Older guides may describe rehearsal-only controls or earlier speed caps. Inspect the actual version, entry point and guarded profile before operating; do not combine historical startup commands blindly.

## 7. Fusion prototype: exact boundary

The implementation is an original small offline prototype, not installed third-party fusion software. It accepts bounded normalized JSON with explicit synthetic/recorded provenance, sensor timestamps and exact detector source-image keys. It validates calibration, frames, stationary state, whole-scan timing and age before considering associations.

Actual laser-plane points are transformed using a full rigid camera–laser transform and projected with matching **rectified** camera intrinsics. Adjacent valid rays form clusters. Projection alone yields `candidate_only`; it never becomes a confirmed map label. Overlapping detections, multiple possible clusters or shared clusters remain ambiguous. Missing/invalid evidence remains unavailable or camera-only rather than receiving a guessed distance.

Optional independently confirmed registered depth patches reuse the shared depth calculations to corroborate optical-Z agreement and reject background/mixed/invalid patches. `depth_supported` is conditional evidence, not proven object identity. Any map output is an expiring **surface observation from a real ray**, transformed at the relevant time, not a centroid, footprint, permanent person or occupancy update.

The eight toy scenes cover supported geometry, a raised object, background wall, projection-only evidence, overlap ambiguity, stale data, absent map TF and unvalidated calibration. Thresholds are provisional. There is no live ROS adapter yet. Existing YOLO raw-image boxes cannot be treated as rectified coordinates without a validated conversion/projection path. Conservative clustering can also reject a person's separated legs; this is an evaluation issue, not justification to hide ambiguity.

Research found relevant precedents: SPENCER multimodal people tracking, DROW/DR-SPAAM 2D-laser person detection and lightweight ROS2 fusion examples. None inspected is verified drop-in software for this legacy, low-mounted robot. Bearing-only association and configured centroid heights do not solve unobserved foreground height. No external package, model weights or ROS upgrade was installed for that review. Primary links and inspection limitations are in the research document above.

## 8. Verification record and limits

The latest complete recorded offline run is **23 October**, in local ignored report `tmp/quality_reports/20261023_115506_9cd03745/summary.md`:

- Tools: **97/97 passed**, including **25 fusion tests**.
- Dashboard: **261/261 passed**.
- Hub: **54 run, 53 passed, one Windows symlink skip**.
- JavaScript/static/configuration/environment checks passed.
- Initial restricted-temp focused-test execution encountered Windows access denial; permission-correct execution passed. This was an environment failure, not an omitted test.

Earlier intermittent Windows HTTP abort `10053` remains undiagnosed. A subsequent passing run is not a demonstrated fix; do not add retries/exclusions to conceal it. Syntax/grammar checks do not execute ROS or the robot's legacy Python environment.

Planner core tests (25), TypeScript and production build passed in the preceding work. Earlier local API checks covered authorization and revision behavior; private publication and signed-in read verification succeeded on 23 October without rewriting personal records. These checks do not imply a live chatbot, robot telemetry or guaranteed unattended future updates.

Public source CI last verified successful for commit `32abfce6c7018573bdba3758242892eb68e1caa8`, run `39856347465`. It does **not** cover later local inventory/fusion changes. The pre-handover local HEAD is newer than cached `origin/main`; no public push is part of this handover request.

No physical sensor test, calibration, mapping run, Wi-Fi peer test or motion test was performed while writing this document. Documentation-specific checks for this handover belong in the 24 October changelog entry.

## 9. Unresolved problems

1. **LiDAR delivery:** registered `/lsn10` but no new `/scan` messages. Existing logs show normal launch/shutdown sequences, not a proven root cause. Serial ownership, aliases, actual driver/device and current process state still require bounded checks.
2. **No current map publisher:** a dashboard subscription does not create `/map`. SLAM/map server and valid pose/TF are separate prerequisites.
3. **Calibration:** sensor centres, full extrinsics, camera tilt, optical axes, intrinsics, distortion and actual RGB-depth registration are not validated sufficiently for reliable fusion.
4. **Timing:** detector source image, scan acquisition interval, depth and TF must be matched. Topic names and reception timestamps are insufficient; clock/report dates have differed.
5. **Real evidence:** no aligned real recording has passed through the fusion prototype. No physical association accuracy, map error or end-to-end runtime benchmark exists.
6. **Detection limitations:** low camera angle, partial objects, occlusion, dark chairs and false classes. A pretrained model need not recognize an arbitrary cardboard box.
7. **Control faults/network:** heartbeat/feedback stops and UI re-enable events are not fully diagnosed. Infrastructure Wi-Fi peer connectivity and reliability remain untested; sharing an SSID does not ensure device-to-device reachability.
8. **Installation gap:** new source, copied vendor source, installed binaries and currently running software must be distinguished. Optional packages may target other robot variants or unavailable hardware.
9. **Evaluation/schedule:** finalize label policy, held-out protocol and lecturer-approved contribution before expanding scope.

## 10. Next steps, in dependency order

### Next lab session — stationary, read-only first

1. Confirm current process ownership and source the existing ROS environment. Avoid duplicate drivers/controllers and broad process-killing commands.
2. Run the prepared read-only inventory and verify exact installed model/configuration and hardware labels. Save reviewed results locally, not into public source.
3. Diagnose missing scans until fresh `/scan` messages are measured. A publisher entry alone is not the pass criterion.
4. Check colour/depth topics, encodings, units, `CameraInfo`, source-image headers and TF. Use measured reference distances and multiple surfaces; do not trust invalid/far depth automatically.
5. Measure/fix camera tilt and sensor centres; validate full transforms and a raw-versus-rectified image path.
6. Record a small stationary aligned sample with acquisition timestamps, scan timing, calibration provenance and independent reference measurements. Include raised objects, background walls, occlusion and negative examples. Keep raw human imagery private.

Useful bounded checks, **in a sourced robot terminal**, do not request motion:

```bash
timeout -k 2s 8s rosnode list
timeout -k 2s 8s rostopic info /scan
timeout -k 2s 10s rostopic hz /scan
timeout -k 2s 8s rostopic info /map
```

A timeout intentionally ends observation; report whether messages arrived, not just the exit code. Existing operating guides govern startup/shutdown. A port number is not a process ID; inspect the actual owning process before stopping it.

### After usable real evidence

7. Normalize and replay saved sensor data into the existing pure core. Never replay motion commands into the live robot. Evaluate correct, incorrect, unmatched and ambiguous associations without converting uncertainty into success.
8. Add a subscribe-only ROS 1 adapter after recorded-data geometry checks pass. Do not make it launch drivers, arm controls or start navigation implicitly.
9. Validate an existing occupancy-map/pose/TF workflow, then overlay expiring semantic surface markers separately. Preserve existing maps/databases; never delete them on startup.
10. Evaluate on independent held-out scenes: detection false positives/misses, association errors, correct rejection, reference position error, latency, dropouts and CPU/GPU/resource load. Moving tests come later with appropriate supervision.
11. Test shared infrastructure Wi-Fi while stationary, keeping console/fallback access. University peer isolation or authentication may prevent communication. Do not expose ROS or the dashboard publicly to bypass it.
12. Review scope/results with the lecturer, stabilize the demonstration and freeze features before the soft December implementation target.

### At home

Read the fusion contract and research shortlist; inspect the synthetic examples. Safe local entry points are:

```powershell
git status --short
python Tools/quality_check.py
python Tools/fusion_prototype.py --demo --output tmp/fusion_handover_demo_new
```

Use the already configured Python/NumPy, Node and Hub environments from the quality guide. A new output directory avoids overwriting evidence. Do not install modern robot dependencies or infer Jetson support from a laptop success.

## 11. Continuity, privacy and publication

Before material work, inspect Git status and preserve unrelated changes. Update `CHANGELOG.md`; update `PROJECT_CONTEXT.md` for stable decisions/hardware changes. Use source-only local snapshots with per-commit non-personal identity. Run the appropriate focused checks and the shared quality checker after code changes, honestly recording errors and skips.

The initial reviewed public source upload was authorized; future public pushes are not automatically authorized. Before any authorized publication, run `Tools/publication_audit.py` against committed history, review its findings and preserve remote history. Pattern auditing is best-effort, not a guarantee that private information is absent.

Do not commit credentials, raw human images/videos, terminal dumps, private annotations, vendor archives/weights, generated reports or the separate private planner. Source Git is not a complete backup of excluded experiment data; retain that evidence separately under appropriate access controls.

Maintain the private Fieldnotes summary/dated roadmap through `Sites/fieldnotes/lib/project-progress.ts` and the supported Sites workflow. Preserve personal notes/goals, private audience and source history. Mark source-tested, observed, blocked and planned work distinctly. The daily local review depends on the laptop/app being available and does not guarantee unattended publication. No live chatbot or robot telemetry is implied.

This handover deliberately excludes credentials, device identifiers, private network addresses, personal notes, private hosting identifiers and raw participant data. It records technical aggregates and project conclusions only. Use [PROJECT_CONTEXT](../PROJECT_CONTEXT.md) and [CHANGELOG](../CHANGELOG.md) for evolving source records; do not copy their unrelated/private material into public documentation.
