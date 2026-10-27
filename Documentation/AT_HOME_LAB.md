# At-home perception and simulation lab

Contract recorded before implementation, 27 October 2026. User authorizes all
three proposed home-development tasks and preparation of a separate laptop
simulation environment later. No robot deployment or large OS/ROS installation
in this step. Read-only local check reports WSL not installed; gz/ros2 not found.

## Deliverables and honest boundaries

1. Interactive loopback-only workbench reusing semantic_snapshot/fuse_snapshot,
   existing ten fixtures and projection/depth helpers. Synthetic height, object
   distance and background range are adjustable. Exact reasons and source mode
   remain visible. File import is bounded normalized JSON, not arbitrary code,
   URLs or server filesystem paths. Imported data is evaluated at its recorded
   reference timestamp, not falsely presented as a current live scene.
2. Passive ROS1 capture adapter: fixed sensor-topic allowlist, explicit recording
   opt-in, new output directory, finite time/message/byte limits, and no Publisher,
   launch, serial read or movement topics. Raw bags/images stay private. Raw capture
   does not establish calibration/registration or automatically become validated
   fusion input. Normalized-session replay is offline and never rosbag play.
3. Versioned saved object layer with run/map/calibration/source-image provenance,
   detector score, evidence type and historical observation time. Preserve unknown
   positions; static spatial grouping is provisional and never object-identity
   proof. Dynamic classes (person/animals) remain time-stamped observations, not
   permanent occupancy. Never mix synthetic/recorded evidence or map/calibration
   identities. No mutation of occupancy, tracking truth or navigation commands.
4. Reproducible ideal bicycle/pure-pursuit route exercise and seeded Gazebo world
   generator: known-route, seeded obstacle world, mapping world. Generic Ackermann
   dimensions/inertia/sensor poses are TOY assumptions, not a Wheeltec digital twin.
   Simulation outputs and commands use /home_lab_sim only; no adapter to the
   physical ROS1 dashboard/base. Generated world geometry is evaluator truth,
   not a map supplied to a robot in an unknown-map experiment. No actual Gazebo,
   Nav2, unknown-world navigation, exploration or SLAM success without those runs.

## Units, coordinates and validity

Fusion retains existing exact YOLO source-image identity, stationary-snapshot,
rectified image/intrinsic, calibrated full3D transform, scan-duration, timestamp,
foreground-depth and ambiguity gates. Optical +Z forward/+X right/+Y down; laser
+X/+Y in its physical scan plane; all positions metres, angles radians and source
timestamps seconds. UI display presets are NEVER calibration. No estimated
"table/floating/free to drive" conclusion from missing LiDAR returns.

Normalized sessions contain at most100 snapshots, <=2MiB input, strict JSON and
one run/map/mode identity, <=20000 scan rays/1000 boxes/2000000 association-work
units across the session. Split longer recordings into independently reviewed
sessions. Stored object layers are historical, not current/live
obstacles. Save to new paths/directories and preserve input hashes. Capture raw
arrival/source time and TF; no inferred time synchronization or hardware accuracy.

## Autonomy progression

| Stage | Required demonstration | What it does NOT prove |
| --- | --- | --- |
| Ideal known route | bounded steering/speed, endpoint and cross-track error | dynamics, friction, braking, hardware control |
| Gazebo known route | actual physics/sensor/odometry route tracking | transfer to real car |
| Known-map navigation | collision-aware car-feasible paths, localization, recovery | exploration of unknown space |
| Unknown-world exploration | sensor-limited mapping, frontier choice, feasible replans | omniscient goal routing from evaluator truth |
| Save/reload + semantic layer | real map identity/pose graph with object provenance | static certainty about moving people |
| Robot validation | calibrated mounting/time, feedback/control and bounded tests | autonomy certified safe |

Reuse established navigation/SLAM packages later; do not grow a bespoke full
navigation stack merely to create a demo. Candidate separate stack: Ubuntu24.04,
ROS2 Jazzy, Gazebo Harmonic (supported pair), subject to laptop/GPU/WSLg setup.
Robot ROS1 Melodic and firmware remain unchanged. A new ROS2 adapter is not a
drop-in Melodic package. Source preparation does not claim simulator execution.

Primary references reviewed27October:
- https://gazebosim.org/docs/harmonic/ros_installation/
- https://gazebosim.org/docs/harmonic/ros2_integration/
- https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1AckermannSteering.html
- https://gazebosim.org/docs/harmonic/sensors/
- https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/planners_plugins/smac/
- https://get.gazebosim.org/tutorials?cat=connect_ros&tut=ros_installing

Gazebo Classic reached end of life in January2025. Do not install an unsupported
legacy stack on the Jetson to satisfy laptop simulation preparation.

## Still needed for the thesis

Real aligned capture, RGB-depth registration/rectification validation, measured
extrinsics and body/laser/map TF, clock provenance, reliable scans, persistent map
identity/localization, real association ground truth, precision/recall and false
association/unknown rates, measured latency/resource use, failure handling and
hardware validation. Pretrained YOLO stays; custom training is not a prerequisite.

## Use at home

Windows: double-click `Tools/Start Home Lab.cmd`, then open
http://127.0.0.1:8878/ in the laptop browser. It uses the existing bundled NumPy
Python when available, or the installed Python3.11 (which must already have
NumPy). No automatic dependency install. This loopback app is not the private
online planner and is not remotely accessible from the phone by default.

Laptop commands, from the project root with an existing Python3.11+ and NumPy:

```text
python Tools/home_lab.py --serve
python Tools/home_lab.py --demo --output tmp/my_home_run
python Tools/home_lab.py --replay tmp/my_home_run --output tmp/my_replayed_run
python Tools/prepare_simulation.py --output tmp/my_simulation --seed 7
```

Each output directory must be NEW. The demo writes a three-frame normalized
synthetic session, hash manifest, historical semantic_layer.json and replay.json.
Load session.json in the browser, select frames, inspect source/evidence/reasons,
or download session/layer JSON. Unknown positions remain null. Hash checks prove
local file consistency, not authenticated data origin or physical correctness.
Repeated static surface observations can form one provisional group; person
observations remain separate historical events, never permanent occupied cells.

The two displays are image/projection geometry (NOT image pixels or real YOLO
inference) and map-frame surface samples (NOT a SLAM occupancy grid). Existing
ten scenarios can be selected; the virtual-scene controls independently create
synthetic chair samples at adjustable height/distance/background. Calibration
and independent-depth flags are synthetic test inputs, never robot validation.

## Next-lab capture preparation — not run at home

`record_fusion_session.py` defaults to printing its fixed topic plan without ROS.
After deliberate copying of the complete diagnostic bundle into the personal
tools folder, an operator may later run it in the EXISTING ROS1 Python environment:

```text
python ~/fahad/tools/record_fusion_session.py --record --seconds 10 --max-mib 512 --output ~/fahad/reports/capture_NEW
```

No drivers start. No Publisher or movement topic is used. The capture may stop
BEFORE10seconds at the serialized-byte/message cap; cameras can produce large
raw streams. Counts, missing topics, stop reason, bag hash and ROS simulated-time
flag are recorded. ROS1 Python2 uses the existing recorder's wall-time fallback
when monotonic is unavailable and stops on clock regression; no clock is changed.
This is not a hard real-time duration guarantee or a lossless capture guarantee.
Topic absence, callback queue drops and CPU/storage throughput require lab checks.
The adapter has fake-ROS tests, not actual Jetson/ROS1/Python2 execution proof.

Raw sensors.bag contains private images, scans/TF/odometry/detections/calibration
metadata. Do NOT upload it publicly. Raw bag → normalized fusion snapshot is not
automated or certified here: a future offline converter must use exact source
image identity, real rectification, verified RGB-depth object patches and full
acquisition-timed transforms. Do not rename a bag into JSON or use rosbag play
against the physical robot. No real synchronized dataset has been validated yet.

## Gazebo preparation, not installation

The generator writes known_route.sdf, seeded_unknown.sdf, mapping.sdf, a scoped
ROS2/Gazebo bridge JSON (valid YAML subset), evaluator_truth.json, ideal_route.json
and simulation_manifest.json. All are synthetic. Changing seed reproducibly
changes obstacles; random worlds are not guaranteed connected/traversable.
The ideal trace is generated by bicycle kinematics/pure pursuit with no collision,
motor lag or dynamics. It does not command a simulator or physical car.

Later, only in the separate Linux environment, a manual preview would use:

```text
gz sim known_route.sdf
```

No install or `gz sim` was performed. Before any ROS2 controller is connected,
isolate its discovery/domain from other robots, use only /home_lab_sim topics,
inspect actual generated camera topic names, validate joints/sensor axes/physics,
and test simulated stopping. The prepared bridge covers scan/odom/TF/simulated
cmd_vel only; camera bridge, simulated clock/use_sim_time wiring, Nav2 parameters,
mapping/localization/exploration launches remain pending actual Gazebo setup.
They are not implemented live integrations. Do not bridge to the ROS1 robot.

Observed verification:22new focused tests,128root Tools tests,264dashboard tests,
53Hub passes/one Windows symlink skip, all JS/static/configuration checks pass in
release run `tmp/quality_reports/20261027_235756_ec49022e/summary.md`. Earlier full
runs `20261027_234724_838bad9b` and `20261027_234326_28380091` also passed before
the last privacy-safe recorder error handling/source-message refinement.
Initial focused run found an XML helper argument collision; corrected and tested.
The historical Windows10053 issue is not declared fixed by these passing runs.
Own synthetic run saved/replayed (3observations/1provisional static group);30file
diagnostic bundle generated. Browser checked raised-object and blocked-calibration
cases after normal loopback permissions; initial sandbox socket10013/CIM denial
and preview timeout retained as environment limitations, not hidden code passes.
The inspected monitor/table screenshot contains only synthetic geometry. Actual
ROS1/Python2/Jetson capture, simulator physics/Nav2/SLAM and hardware remain unrun.
Final browser check also imported the own synthetic three-frame session, selected
frame3/3 and downloaded a valid historical layer (3events/1provisional static
group). Owned preview servers were stopped; use Start Home Lab.cmd to run locally.

## Files and dependencies

- `fahad_core/experiment.py`: bounded strict session IO, replay and hash checks.
- `fahad_core/semantic_memory.py`: historical evidence/provisional static groups.
- `fahad_core/capture.py`: fixed topic and budget policy, no ROS.
- `home_lab_scenes.py`: existing fixture/geometry reuse, synthetic inputs only.
- `home_lab.py` + `home_lab.html`: local adapter/UI; no arbitrary file-serving API.
- `record_fusion_session.py`: explicit ROS1-only subscriber/bag writer adapter,
  reusing record_detection_test.wall_time and shared recording helpers.
- `fahad_core/simulation.py` + `prepare_simulation.py`: ideal kinematics, seeded
  world generation and XML/files; no network, installation or publication.

The diagnostic ZIP now includes30source files; the robot Hub/dashboard stays
v0.18 with22fixed runtime files and no new motion code. New calculations are not
silently installed into the running dashboard or represented as live fusion.
