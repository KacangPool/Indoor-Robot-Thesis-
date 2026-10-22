# Indoor search-and-rescue robot perception

## Original project description

Wheeltec Ackerman robot car project for my thesis. Creating the connection and communication between the Camera and 2D Lidar from the robot to visualise and identify objects from the camera then to save them as a map through the Lidar.

The description above is preserved from the original GitHub README. The sections
below distinguish the intended goal from what has actually been demonstrated.

Bachelor-thesis project: evaluate pretrained camera-based detection of living
beings on an indoor WHEELTEC robot, then develop and evaluate appropriately
validated camera–LiDAR association and spatial labels.

## Source status

Current local source: **v0.14**. The robot's installed version and live sensor
state must be checked separately. This source snapshot does not establish a
working LiDAR stream, calibrated fusion, autonomous navigation or physical safety.
The existing YOLO detector is retained; no custom training is currently planned.

## Start here

- [Project context](PROJECT_CONTEXT.md): confirmed results, scope and open issues.
- [Tool catalogue](Tools/README.md): entry points and shared libraries.
- [Quality workflow](Documentation/QUALITY_WORKFLOW.md): tests, local history,
  configuration and diagnostic reports.
- [Module architecture](Documentation/MODULAR_CODE_ARCHITECTURE.md).
- [GitHub and campus Wi-Fi plan](Documentation/GITHUB_AND_CAMPUS_WIFI.md).
- [Changelog](CHANGELOG.md).

## Offline checks on the laptop

Double-click `Tools/Check Project.cmd`, or use an existing Python 3.11+:

```text
python Tools/quality_check.py
```

The checker uses existing runtimes, makes no robot connection and installs
nothing. Fake HTTP/SSH tests use localhost. Reports retain errors/skips and live
under ignored `tmp/quality_reports/`. Passing laptop tests are not ROS/Jetson or
physical validation. See the workflow for dependencies and Windows HTTP flakiness.

## Repository boundaries

Only authored source, tests, ordinary configuration and project Markdown notes
are tracked. Recordings, images, private profiles/keys, model weights, vendor
archives/manuals, generated reports and the separately hosted planner are excluded.
Do not add passwords, easyroam certificate/private-key files or diagnostic dumps.

Public source repository: [KacangPool/Indoor-Robot-Thesis-](https://github.com/KacangPool/Indoor-Robot-Thesis-).
Its original README commit and local source history are retained, not overwritten.
See [the GitHub workflow guide](Documentation/GITHUB_WORKFLOW.md) for upload
verification, everyday synchronization, test results and limitations.

GitHub Actions runs the existing offline checks on pushes/pull requests to main.
The hosted test job has read-only repository permissions and no robot credentials;
it does not deploy software or operate hardware. Tests/reports are not a live
integration claim. Do not treat the intended fusion/map goal as a completed feature.
