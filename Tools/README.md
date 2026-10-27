# Project code: where to start

Current console source is **v0.16**: equal camera/LiDAR panes, bounded view-only
zoom/orbit/pan and camera-only observation snapshots. Shared semantic_scene builds
offline supported laser labels and camera-depth-only surface observations; neither
is a verified live fusion system. See
[the v0.16 contract](../Documentation/SEMANTIC_VIEW_V016.md). Hub runtime22files;
diagnostic bundle21source files. Keep sibling shared modules when copying source.

Current quality foundations: **v0.14**, not yet deployed to the robot. Double-click
`Tools/Check Project.cmd` for the consolidated offline checks. The Hub's existing
Save report now creates an allowlisted diagnostic snapshot; the dashboard reads
validated ordinary settings. Reviewed source was published to GitHub on22 October;
later local commits are not automatically uploaded. Raw/private data remains excluded.
Read [the everyday workflow](../Documentation/QUALITY_WORKFLOW.md) before copying
updates. No deployment, motion-limit change or live LiDAR fix was performed.

The main user-authored tools now share reusable modules. The original command
names still work; the pieces underneath them have been separated by purpose.
This is a local v0.13 source refactor, not a robot installation.

Read [the plain-language architecture guide](../Documentation/MODULAR_CODE_ARCHITECTURE.md)
for the complete layout, verification results and deployment limits.

| Folder or file | Responsibility |
| --- | --- |
| `fahad_core/` | Shared depth, detection, recording, message and camera-summary functions |
| `fusion_prototype.py`, `fusion_fixtures.py`, `fusion_demo_template.html` | Explicit offline camera–planar-LiDAR regression report; no live inference or robot connection |
| `box_depth_viewer.py`, `camera_diagnostics_ros1.py` | ROS/camera adapters using those shared functions |
| `person_detection_filter.py`, `record_detection_test.py` | ROS detection filtering and recording entry points |
| `ros_message_sample.py`, `ros_topic_report.sh` | Bounded ROS inspection entry points |
| `remote_dashboard/` | Browser console, sensor state, ROS reader and separate guarded motion adapters |
| `robot_hub/` | Windows interface, setup workflow, SSH transport and complete runtime installer |
| `annotation_review_core.js` | Existing shared annotation matching/scoring rules |
| `analyse_pilot_annotations.js` | Reusable evaluation builder plus explicit report-writing command |
| `build_robot_tool_bundle.py` | Packages the diagnostic scripts with their shared dependencies |

## Important: copy the dependencies too

For the updated diagnostic scripts, copying just one `.py` file is no longer
enough. The robot needs the `fahad_core` folder beside it:

```text
/home/wheeltec/fahad/tools/
  box_depth_viewer.py
  person_detection_filter.py
  record_detection_test.py
  camera_diagnostics_ros1.py
  ros_message_sample.py
  ros_topic_report.sh
  fahad_core/
    __init__.py
    depth.py
    detections.py
    recording.py
    message_samples.py
    camera_metrics.py
```

The laptop can prepare that complete set without ROS or an internet connection:

```powershell
py -3.11 .\Tools\build_robot_tool_bundle.py --output .\robot_tools_v013.zip
```

The output name must not already exist. The builder includes a SHA-256 file
manifest and refuses to overwrite an existing ZIP. It does not upload, install,
launch or move anything. Later, extract it into the personal robot tools folder,
preserving any existing files first; it is not an automatic rollback installer.
Existing copies on the robot are unchanged until deliberately updated.

The Hub has its own complete dashboard installer. Keep the **entire** local
`robot_hub` folder beside `remote_dashboard`; do not copy just its launcher or
individual runtime files. The Hub's fixed 17-file runtime list includes the new
dashboard modules and browser renderer.

## Reusing a piece

From another script beside `fahad_core`, use a function instead of copying it:

```python
from fahad_core.depth import depth_metres, patch_stats

# image_array and encoding come from the caller's camera/ROS adapter.
metres = depth_metres(image_array, encoding)
```

This import does not start a camera or ROS node. Calling the adapter's explicit
start/main function is still required. The depth/camera numeric modules need
the existing NumPy installation; this refactor does not install dependencies.

## Offline checks

Camera–LiDAR research shortlist: [reviewed sources](../Documentation/CAMERA_LIDAR_RESEARCH_2026-10-23.md).
The new [offline fusion prototype](../Documentation/FUSION_PROTOTYPE_V01.md) reuses
the shared code and keeps geometric candidates separate from supported labels.
It does not implement live ROS fusion or create the room map. Use a new output
directory with `python Tools/fusion_prototype.py --demo --output tmp/fusion_new`.

New read-only feature discovery: `robot_inventory.py` uses the sibling
`fahad_core/inventory.py` to catalogue explicit source trees. `--robot` adds fixed,
bounded installed/registered observations; no launch, echo payload, sudo or motion.
See [the software catalogue and next-lab commands](../Documentation/ROBOT_SOFTWARE_CATALOGUE.md).
The diagnostic bundle includes both files. Source presence is not working hardware.

Use an existing Python environment with NumPy for the root tools suite, the
existing Hub environment for its SSH tests, and Node for JavaScript tests:

```text
python -m unittest discover -s Tools -p "test*.py"
python -m unittest discover -s Tools/remote_dashboard -p "test*.py"
python -m unittest discover -s Tools/robot_hub -p "test*.py"
node Tools/remote_dashboard/test_frontend.js
node Tools/remote_dashboard/test_sensor_view.js
node Tools/remote_dashboard/test_joystick.js
node Tools/remote_dashboard/test_web_frontend.js
node Tools/test_analysis_modules.js
node Tools/test_annotation_review_core.js
```

These are local checks, not evidence of physical robot operation. HTTP/fake SSH
tests use localhost; bundle tests use temporary folders. See the architecture
guide for the observed Windows HTTP-test error and the Python-version limits.
