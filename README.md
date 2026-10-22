# Indoor search-and-rescue robot perception

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

The user created public [KacangPool/Indoor-Robot-Thesis-](https://github.com/KacangPool/Indoor-Robot-Thesis-)
and accepts that visibility. It currently contains only the user's initial README;
local remote configuration and first source upload are pending. Preserve that
remote history and review local files/history for private material before upload.
The local repository remains independent until the connection is completed.
No cloud CI/deployment or live robot/network change is configured by this README.
