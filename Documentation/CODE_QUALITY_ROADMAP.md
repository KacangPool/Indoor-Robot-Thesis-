# Long-term code quality: proposed next steps

Update 2026-10-22: user approved this direction and keeping the workflow for
future project changes. The first four foundations are implemented locally in
v0.14: local Git history, one-command checks, diagnostic/event reports and strict
ordinary configuration. See [the operating guide](QUALITY_WORKFLOW.md).
Lab-data, fusion-contract, full robot inventory/restore and measured-performance
work remain staged, not completed. No robot deployment or motion occurred.

## What "efficient" means here

Maintainability means that changes are easier to understand, test and undo.
Runtime efficiency means using less time, memory, CPU/GPU or Wi-Fi bandwidth.
Modularity mainly helps maintainability; speed improvements need measurements.

The project already has reusable modules, many focused tests, health/freshness
indicators, bounded queues, recording tools, a changelog, and checksummed Hub
updates with backups. We should extend these rather than install another parallel
framework. The latest v0.13 dashboard suite still has a Windows 10053 HTTP test
error; a future test runner must report it honestly, not ignore it.

## Recommended features

| Practice | What it would do here | Existing foundation / remaining work |
| --- | --- | --- |
| Local version control | Save named code snapshots, compare changes, return deliberately to known source | Implemented: local source-only repository, baseline d987a68 and separate implementation snapshot; no remote. Credentials, recordings, vendor archives and separate hosted app excluded. Git is not an independent backup. |
| One quality-check command | Run the relevant unit tests, import/bundle checks and suitable static checks; produce one readable result | Tests already exist but are invoked separately. Distinguish pass/fail/error/skip and missing runtimes; no robot startup or dependency installs. Add compatible lint/format tooling deliberately, without rewriting every legacy file. |
| Validated configuration | Keep ordinary tunable settings in one documented place instead of searching many scripts | Fixed settings currently exist in several modules/CLIs. Separate laptop/robot profiles; allowlist fields and reject invalid values. Preserve independent enforced motion/security ceilings; no arbitrary launch commands or secrets in config. |
| Structured logs and diagnostics | Give each run an ID and report component, time, event and reason; export a bounded support report | Hub service logs and readiness already exist. Extend with process/session identity, recent-message rate/age, disk space and version, not just node registration. Rotate/limit logs and redact credentials/tokens. No automatic motion recovery or service restart. |
| Recorded-data regression tests | Re-run perception/fusion calculations on the same saved sensor observations while at home | Recorder currently saves RGB/YOLO samples, not an aligned multimodal bag. Add a small selected stationary capture with image/depth, CameraInfo, scan and needed timestamped TF/pose. Use file readers and isolated analysis, never publish replayed motion commands to the robot. Keep storage limits and privacy in mind. |
| Clear data contracts | State what each module accepts/returns: metres, radians, frames, image time, validity and calibration version | Existing validation already rejects many malformed scan/map/pose values. Extend shared schemas at boundaries without adding incompatible Python syntax. An unmatched camera observation must not silently become a laser-associated object. |
| Reproducible dependencies and releases | Record the tested Python/ROS/library/model versions and package complete source with a release ID | Hub pins Paramiko and verifies bundles/backups. Robot package versions and restoration need inventory/validation. Keep laptop and Jetson environments separate; do not upgrade ROS/Python or claim rollback is tested merely because backups exist. |
| Performance measurement | Track processing time, end-to-end age, drops, CPU/RAM and bandwidth before optimizing | Bounded queues/image caps exist. Compare repeatable workloads; measure message/image ages and inference timings separately, since display FPS is not detector throughput or latency. Avoid processing an ever-growing backlog. |
| Experiment provenance | Save each result with code version, settings, calibration, model hash and scene notes | Existing session metadata/hash manifests are a foundation. Add a consistent record so thesis comparisons can be reproduced, while preserving original data and label caveats. |

## Suggested sequence

1. Establish a local code recovery point after an explicit version-control choice;
   no remote repository or upload is required.
2. Add one offline quality-check command and machine-readable/readable results.
3. Improve existing logs and add an explicit read-only diagnostic export.
4. Introduce validated ordinary configuration, with existing guards unchanged.
5. Capture a small suitable lab dataset and build file-based regression tests.
6. Improve data contracts, dependency/release records and measured performance as
   part of the actual camera–LiDAR implementation, not as an unrelated rewrite.

A local source snapshot does not solve installed robot rollback. A fake or saved-
data test does not establish physical calibration or stopping. Keep those results
separate. None of these additions fixes the unresolved missing live /scan stream
by itself. Heavy infrastructure, public dashboards, cloud migration, automatic
restarts and containerizing the old Jetson are not recommended as prerequisites.

## Primary references

- [ROS package quality guidance, REP-2004](https://github.com/ros-infrastructure/rep/blob/master/rep-2004.rst)
  describes version/change policies, documentation, testing, dependencies and
  platform support. Used as engineering guidance, not a claim of ROS2 migration
  or a certified quality level for this ROS1 project.
- [Git: local operations](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F)
  and [version control](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)
  explain code history and local operation; GitHub hosting is not required.
- [Python logging guidance](https://docs.python.org/3.11/howto/logging.html)
  explains component loggers, severity and configuration. Implementation must
  remain compatible with each target interpreter, not assume Python 3.11 on ROS.
- [ROS Melodic rosbag reader source](https://github.com/ros/ros_comm/blob/melodic-devel/tools/rosbag/src/rosbag/bag.py)
  provides file-based message reading; using it is distinct from publishing
  messages to a live ROS graph.
- [ROS units/coordinates, REP-103](https://github.com/ros-infrastructure/rep/blob/master/rep-0103.rst)
  and [mobile frames, REP-105](https://github.com/ros-infrastructure/rep/blob/master/rep-0105.rst)
  support explicit units and frame contracts. They do not supply this robot's
  actual calibration or measured transforms.

Original proposal verification: reviewed local module boundaries, tests, Hub
manifest/backup/log code, sensor freshness and queue settings, recorder scope,
Paramiko pin and architecture notes. Consulted the above primary references.
No new runtime tests or robot checks were needed for this documentation-only
proposal. Open choices: implementation priority, local Git scope, actual installed
robot dependency versions, approved capture topics/size and measured performance.
