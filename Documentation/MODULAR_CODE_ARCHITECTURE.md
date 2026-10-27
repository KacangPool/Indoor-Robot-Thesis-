# Reusable project code — v0.13, 2026-10-22

v0.18: pure projected-marker geometry keeps glyph screen size independent of
zoom/pitch. The same shaped-car renderer serves scan/map/key; fixed-map preference
and the reported-direction display preset remain browser-local and isolated from
TF/fusion/motion. No added runtime files/packages. See CAR_MARKER_V018.md.

v0.17 follow-up: scene_geometry.js owns inverse display-point selection and
front-up centring/rotation; sensor_view.js owns only the frame-bound tab-session
operator mark and existing fresh TF preference. No new runtime dependency or
server parameter. The mark never becomes body TF, sensor data or motion input.
The Hub remains22fixed files. See FRONT_UP_VIEW_V017.md.

Latest source follow-up27October: v0.16 adds pure scene_geometry view projection,
shared observations/semantic_scene modules and a read-only detection adapter.
Hub22file runtime now includes4allowlisted shared modules through one validated
source resolver; diagnostic bundle21source files. Historical counts below refer
to earlier extraction versions. See SEMANTIC_VIEW_V016.md for current contracts,
copy instructions, verification limits and pending real positional fusion.

Current follow-up: v0.14 adds validated ordinary configuration, consolidated
checks, local source history and allowlisted Hub diagnostics. The runtime now
has 17 files; the 15-file references below describe the original v0.13 extraction.
See [the current quality workflow](QUALITY_WORKFLOW.md). No robot deployment.

## What changed, in plain language

Previously, some scripts contained both the calculation and everything needed to
run it: ROS connections, image windows, files or a website. We have separated
the reusable calculation from the part that operates the program.

For example, converting depth values into metres is now one shared function.
The depth-viewing program calls it. A future camera–LiDAR experiment can call
the same function without launching the viewer or copying its code.

Modular does **not** mean every future feature needs no new code. It means new
features can be assembled from tested pieces, with new logic added only where
needed. It also does not automatically improve detection, calibration, speed or
LiDAR reliability.

## The boundaries

```text
User commands / windows / browser
        |
        +-- ROS adapters ---- shared sensor/data functions
        |
        +-- Windows Hub ---- setup workflow ---- SSH transport
        |
        +-- Dashboard ---- sensor state ---- ROS reader
                    |         |
                    |         +---- shared scan/map summaries
                    +---- read-only browser renderer
                    +---- existing separate guarded motion adapters
```

### 1. Robot diagnostic library: Tools/fahad_core

| Module | Reusable work | Deliberate boundary |
| --- | --- | --- |
| `depth.py` | Depth-unit conversion, selected-patch statistics, pair checks | Strict accepted encodings preserved; no camera/ROS startup |
| `detections.py` | Detection serialization and person-only box selection | Existing score/label policy preserved; no inference or publisher |
| `recording.py` | Header/frame IDs, bounded image cache, explicit JSON/disk helpers | Writes happen only when a write function is called |
| `message_samples.py` | Bounded readable summaries of message payloads | PointCloud2 decoding imports its existing ROS helper only when called |
| `camera_metrics.py` | Brightness, valid depth statistics and camera-info summary | Legacy diagnostic depth fallback preserved, not calibration validation |

`fahad_core/__init__.py` intentionally loads no submodules. Numeric depth/image
functions need NumPy; basic detection/recording helpers do not. These modules
start no ROS node, model, window, network connection or background worker on
import. They are not all mathematically pure: explicit disk helpers do write
files when called, and PointCloud2 decoding needs ROS when used.

The original scripts remain the entry points. They import these functions rather
than keeping second copies. Existing imports such as
`box_depth_viewer.depth_metres` remain compatibility exports of the same function.
The camera diagnostics adapter itself still imports ROS, as before; use its
shared numeric module for offline work, not the ROS adapter.

### 2. Dashboard: Tools/remote_dashboard

| Module | Owns |
| --- | --- |
| `settings.py` | Fixed version, read-only topic names and static asset allowlist |
| `sensor_models.py` | Scan/map/pose validation and summary calculations |
| `sensor_state.py` | Latest sensor state, locks, freshness and API snapshots |
| `ros_reader.py` | Explicit ROS subscriptions, image conversion, map/TF work |
| `server.py` | Existing HTTP routes, command-line startup and compatibility exports |
| `dist/sensor_view.js` | Scan/map rendering and colour scale, with injected UI/canvas access |
| `dist/app.js` | Browser networking and UI coordination, calling the renderer |
| Existing control/drive modules | Their existing separate rehearsal, one-shot and guarded live profiles |

Importing the read-only modules does not start ROS, a server or a motor
publisher. Constructing `RosReader` explicitly is a live adapter operation.
The renderer has no network requests, timers or driving endpoints. Its canvas
cache is private to each renderer and cleared on disconnect.

No driving limits, watchdog/lease, enable/release rules, HTTP origin checks,
topic paths, map policy or keyboard logic were intentionally changed. The HUD
appearance is retained apart from the v0.13 label. Compatibility exports mean
existing test/program imports through `server` still resolve to the real modules.

### 3. Windows Hub: Tools/robot_hub

- `hub.py` remains the native interface.
- `hub_controller.py` owns the setup workflow and accepts a connection object.
  Tests can supply a fake connection instead of contacting the robot.
- `connection.py` owns real SSH, SFTP and the private local tunnel. Old imports
  of `HubController` and `local_manifest` still work through compatibility exports.
- `runtime_bundle.py` builds the checksummed fixed-file runtime manifest.
- `agent.py` remains a self-contained robot-side bootstrap. It is deliberately
  **not** dependent on files that have not yet been installed.

The runtime is now 15 allowlisted files, including the four new Python modules
and `dist/sensor_view.js`. Isolated-copy tests check that this set is complete.
Existing checksum, backup and manifest-last installation rules are preserved.
No startup, reconnect, shutdown or background-service ownership policy changed.

### 4. Optional laptop detector and annotation evaluation

The separate SSDLite experiment in `Testing other Models/DetectorTest` now has
`detector_model.py` for explicit model loading, prediction and drawing. Its old
`test_detector.py` command remains a thin entry point. Importing it no longer
downloads weights, reads an image or runs inference. Calling `load_detector()`
can still download the unchanged pretrained weights if they are not cached.
This does not replace the robot's installed YOLO or confirm Jetson compatibility.

`Tools/analyse_pilot_annotations.js` exports `buildPilotEvaluation(projectRoot)`.
Calling it reads the supplied project inputs and returns the report/summary;
importing it does no evaluation or file I/O. The explicit CLI `main()` retains
its existing report-writing behaviour and historical output path. It can overwrite
that report when deliberately run, as before. No real annotations were evaluated
or rewritten during this refactor. Matching rules and historical caveats remain.

## Copying and later installation

Updated standalone tools now require their sibling `fahad_core` package. Use the
complete diagnostic bundle builder described in [Tools/README.md](../Tools/README.md),
not the old single-file copying steps on their own. It packages source and a hash
manifest; extraction is manual, not an automatic backup/rollback system.

Keep all local Hub source files together beside the dashboard source. The Hub
installer handles its complete dashboard runtime; do not partially copy the new
server or renderer to the robot. Original entry-point commands are unchanged
**when their complete dependencies are present**.

Nothing was uploaded or installed on the robot in this session. Existing installed
tools remain as they were. There is nothing you need to run on the robot at home.
At the next lab update, confirm standstill, stop driving, close old console tabs
and Hub, then reopen the local Hub and use its existing Prepare workflow. Check
one fresh v0.13 page before any supervised movement. Do not remove existing guards.

## What was deliberately left alone

- Copied vendor/WHEELTEC ROS source, firmware, archives, model weights and raw data.
- Existing historical reports, labels, images, maps and scratch prototypes.
- The separately hosted planner under `Sites/fieldnotes`, which already has
  component/library boundaries; no rebuild, deployment or publication.
- Existing annotation scoring/reviewer modules, already shared, apart from making
  the analysis entry point reusable. The reviewer UI was not changed.
- Small ROS launch/shell compositions and distinct motion safety profiles. They
  should not be merged merely to reduce the number of files.

## Verification and remaining limits

Offline checks on this Windows laptop:

- Root tools suite: **48/48 passed**, including depth/filter regressions, import
  boundaries, injected detector tests and complete ZIP dependency/hash checks.
- Hub suite: **46 passed, one Windows symlink-privilege test skipped** (47 total).
  Includes an isolated copied-runtime import and fake connections, not real SSH.
- Dashboard: one post-extraction **251/251** run passed before adding four new
  boundary tests. The latest complete **255-test** run had **254 passes and one
  WinError 10053 connection-abort error** in the existing origin/host/key rejection
  HTTP test. All four new boundary tests also pass separately. The Windows abort
  was observed in earlier versions; it is not dismissed as a pass or corrected
  by weakening checks. Its exact host/transport cause remains unresolved.
- JavaScript: **91 browser-coordination + 6 renderer + 11 joystick + 14 one-shot**
  checks passed (122), plus **4 annotation-module checks** and the existing
  annotation scoring assertions. Fake-DOM checks are not physical/browser proof.
- Browser preview: actual v0.13 page loads without reported console errors in
  motor-free mode; a separately labelled synthetic-map fixture exercises the
  extracted canvas raster. No real image/scan/map/TF data involved.
- Robot-targeted Python grammar and changed JavaScript syntax checked locally.
  Actual old-Jetson Python 2.7/3.6 runtimes, old NumPy/OpenCV and ROS were **not**
  executed. Syntax/import checks cannot establish physical integration.

No motion was requested; there is no new stopping, wireless, detection, mapping
or performance measurement. The missing live `/scan` stream, calibration/time/TF
questions and camera–LiDAR height-association problem remain unresolved. This
refactor prepares reusable pieces; it does not implement or validate sensor fusion.

## Rules for the next feature

1. Look for an existing shared function before copying code.
2. Keep calculations separate from ROS/network/UI/model startup.
3. Keep entry points and data formats stable unless a change is explicitly needed.
4. Add a focused test and update the relevant bundle/dependency list together.
5. Keep vendor code, user data and unrelated apps outside the refactor.
6. Log material changes and distinguish offline checks from live robot results.
