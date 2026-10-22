# Remaining work and newer-YOLO feasibility

Reviewed 2026-10-14. This is a planning/research answer, not a deployment change,
promised completion date or final model selection.

Later user clarification, same date: no formal deadline; desired implementation
finish is December 2026, with four intended hours every day (28 nominal hours/week).
This supersedes 'unknown weekly hours' below. The earlier estimates remain
conditional planning bands, not measurements to scale linearly with hours. New
low-viewpoint/non-YOLO findings: `Reference Library/LOW_CAMERA_MODEL_REVIEW_2026-10-14.md`.

## User clarification

The user confirms personally clicking the box in the manual viewer. Accept that
as evidence of intended target selection; do not require another screenshot just
to establish that they clicked the box. This does not independently validate
pixel-level RGB/depth registration or absolute depth accuracy. The preceding
manual extraction milestone is complete. No new hardware measurement supplied.

## Conditional planning estimate

The user's deadline, weekly productive hours, lecturer-approved completion criteria
and available training hardware are not yet known. Therefore 'at this pace' cannot
be converted into a reliable date from chat activity. The following are rough
engineering planning ranges assuming 10-15 focused project hours/week, regular
lab access, pretrained models, a bounded indoor demonstration, and no major robot
system recovery. They exclude thesis writing and are not measured task durations:

| Cumulative outcome from current state | Rough additional calendar time |
|---|---|
| Person detection plus preliminary automatic depth output | 1-2 weeks |
| Camera-focused prototype, one alternative-model comparison and repeatable evaluation | 4-6 weeks |
| Above plus validated robot-pose/map integration and a basic labelled 2D map | 6-10 weeks |

These are alternative cumulative milestones, not durations to add together.
The person-first milestone is not completion of all intended human/animal,
hand/indoor-category or mapping work. Broader classes, custom fine-tuning/data,
robust occlusion/lighting performance, deployment troubles and missing pose/TF
can extend the schedule. Autonomous navigation and proving physiological life
are not included. Final scope/deadline requires user and lecturer agreement.

Known unfinished tasks include detection-image/depth synchronization and spatial
alignment, measured distance validation, model comparison/deployment, independent
evaluation sessions, and valid robot pose/TF for map markers. A working display
alone is not final project completion. Recorder, labels and camera/depth helpers
remain reusable; choosing another model need not restart all work.

## Current robot evidence

The uploaded October runtime report confirms L4T R32.5.2, aarch64/t210ref,
Python 2.7.17 and 3.6.9. Original Jetson Nano 4GB remains the probable board,
not a newly label-confirmed identity. Installed CUDA, TensorRT, PyTorch, free
RAM/storage and NVIDIA Docker runtime still need a bounded read-only inventory.
Do not infer those versions from another device's JetPack release.

## Official newer-model findings

1. [Ultralytics YOLO26 documentation](https://docs.ultralytics.com/models/yolo26/)
   confirms an available model family, including `yolo26n.pt` (nano/smallest scale)
   and larger scales. It documents updated architecture/training and modern
   export/inference paths. Vendor dataset/latency results are not measurements
   on this robot or a direct controlled comparison against its Darknet tiny model.
2. [Official Jetson deployment guide](https://docs.ultralytics.com/guides/nvidia-jetson/)
   explicitly lists testing on an original Nano 4GB-based reComputer J1020 v2
   with JetPack 4.6.1 and provides a JetPack 4 container route. Legacy Nano is not
   categorically excluded. Its current detailed performance tables concern newer
   Thor/Orin devices, not this robot; no expected FPS is established here.
3. [Installation requirements](https://docs.ultralytics.com/quickstart/) specify
   Python >=3.8 and PyTorch >=1.8 for the standard package route, unlike the robot's
   reported host Python 3.6.9. This blocks a blind normal install into the current
   ROS environment, not every possible deployment method.
4. [Official JetPack 4 container source](https://github.com/ultralytics/ultralytics/blob/main/docker/Dockerfile-jetson-jetpack4)
   includes YOLO26n and a separate Python 3.8 environment, CUDA 10.2 runtime,
   r32.7 repositories and TensorRT 8.2/PyTorch wheels. It is evidence of a documented
   route, not proof it works with this older host. Containers still depend on
   compatible host GPU drivers/runtime and available memory/storage.
5. [NVIDIA JetPack 4.6.1](https://developer.nvidia.com/embedded/jetpack-sdk-461)
   identifies L4T 32.7.1, newer than the robot's confirmed R32.5.2. Its TensorRT/CUDA
   versions do not establish the installed robot versions or authorize an upgrade.

The WHEELTEC brand is not the deciding model compatibility layer: compute board,
GPU/software runtime, memory, export operators, actual speed and ROS integration
are. A `.pt` file cannot simply replace a Darknet `.weights` file in the current
wrapper. A separate inference component/adapter would need to read camera images
and expose compatible class/score/box/source-image data to the existing pipeline.

## Recommendation, not yet implemented

Keep the working YOLOv3-tiny setup as a preserved baseline/fallback, not a presumed
best final model. Treat YOLO26n as one comparison candidate rather than testing
every numbered release or committing to an untested architecture. Start with
saved robot-view frames on a suitable separate computer, then assess an isolated
on-robot runtime if image quality results justify deployment effort. Compare person
recall/misses, false alarms, localization, end-to-end timing, memory and reliability
under the actual workload. Pilot annotations remain provisional; final evaluation
needs independent scenes and consistent class/reference rules.

If direct on-board deployment is impractical, laptop inference from robot images
is another architecture to evaluate, with network delay/disconnection explicitly
included. It is not an automatic equivalent to onboard deployment or a chosen
requirement. Do not reflash Ubuntu/JetPack, replace ROS's Python, pull containers,
install packages, download weights or change settings under this advice request.

Next proposed action: a small read-only compatibility audit and one controlled
saved-image comparison alongside continued person-depth integration. First clarify
the project deadline and weekly hours to convert these rough ranges into a plan.

## Verification boundary

Read the project scope/model guide and actual runtime report. Searched and opened
the five official sources above, including full container build instructions.
No newer model downloaded, installed, inferred, exported or benchmarked; no robot
connection, model accuracy claim or performance guarantee. The user has not yet
chosen a deployment route or changed final thesis scope.
