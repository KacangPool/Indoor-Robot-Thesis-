# Everyday project workflow — v0.14

Implemented locally on 2026-10-22. No robot connection, update or motion request.
These additions support the existing tools; they are not a new framework or a
claim that the unresolved LiDAR issue has been fixed.

## 1. Code history: recovery points without GitHub

The project now has a **local Git repository** on branch `main`. Its first
commit, `d987a68`, records the previous modular v0.13 source before this session's
functional changes. It is a baseline snapshot, not a fully verified robot release.
The new implementation is recorded separately. There is no Git remote and no
upload. No global Git settings were changed; commits use the non-personal identity
`Local project snapshots <local-snapshot@invalid>` supplied per commit.

Tracked: authored Tools source/tests/configuration, Markdown project documents
and the two optional laptop-detector source files. Excluded: recordings, images,
model weights, private environment/key files, generated reports, vendor folders,
PDF manuals and `Sites/fieldnotes` (which has its own repository). `.gitignore`
uses a source allowlist. New source types/folders need an intentional scope review.

Git saves only recorded code history. It is **not an independent backup**, does
not include robot data, and does not automatically restore an installed robot.
Do not run destructive reset/restore commands blindly. To inspect changes safely:

```powershell
git status --short
git log --oneline -5
git diff
```

For future material code changes: inspect status, preserve unrelated edits, make
the change, run checks, update continuity notes, review the diff and record only
the task's source changes in a local snapshot. This workflow does not authorize
remote publication, credential storage or robot deployment.

## 2. Check everything with one command

In File Explorer, open the project, then `Tools`, and double-click
**Check Project.cmd**. It keeps a console open so you can read the result.

Alternatively, from PowerShell in the project folder:

```powershell
py -3.11 .\Tools\quality_check.py
```

This uses the installed laptop Python and Node. It recognizes the existing
bundled NumPy interpreter and private Hub interpreter on this laptop. On another
computer, explicitly supply existing compatible runtimes:

```text
python Tools/quality_check.py --python PATH_TO_NUMPY_PYTHON --hub-python PATH_TO_HUB_PYTHON --node PATH_TO_NODE
```

Nothing is installed automatically. The checker runs each Python suite in a
fresh process, then the JavaScript unit/syntax checks and dependency-free Python
syntax/configuration checks. Temporary HTTP and fake SSH tests use localhost,
not the robot. The old annotation browser integration test is explicitly not
included; its JavaScript syntax and scoring logic are checked, but live browser
verification is a separate workflow. No model inference, data capture or GUI starts.

Each run creates a new ignored folder under `tmp/quality_reports/` containing:

- `summary.md`: readable overall result and per-check status.
- `summary.json`: machine-readable checks, runtime paths, source commit and dirty
  state and source SHA-256 inventory; separate child reports preserve test counts,
  failures/errors and skips. A dirty tree is not misrepresented as its base commit.
- Individual logs, including tested NumPy/Paramiko/Python/Node/Git versions.

An existing output folder is refused. Command timeouts, missing runtimes, missing
test reports, empty test suites and nonzero results cannot be silently counted as passes. A suite
may pass **with documented skips**; the skip count/reasons remain visible. A
failure returns a nonzero exit code. No automatic retry or test exclusion masks
the pre-existing Windows 10053 HTTP connection-abort error.

The static checks are a useful subset, **not a full linter/type checker**. No
third-party formatter/linter was installed or mass formatting applied. Reports
are local and can include paths/test traces; they are not promised to be safe for
public sharing and are never uploaded automatically.

## 3. Hub diagnostic snapshots and structured event history

The existing **Save report** button now writes an allowlisted diagnostic report
instead of a complete raw status object. It uses the **last checked snapshot**;
it does not issue a new robot request. Snapshot age and demo status are explicit.
Click the existing Check action first if you need a newer observation.

Included: source/agent/dashboard versions, bundle hash, service registration,
RGB/YOLO freshness, scan connection/rate/age/message count, guarded-control stage,
Hub-owned process IDs, available robot Python/disk metadata and derived issues.
For example, a registered LiDAR with no delivered scans receives a distinct issue;
registration alone is not described as a healthy sensor stream.

Excluded: passwords, bootstrap keys, owner/generation tokens, raw SSH output,
full command lines, raw activity/exception text, images and raw ROS payloads.
An allowlisted report reduces disclosure risk; review it before sharing, because
process/version/time metadata can still be sensitive in some settings.

Hub structured events contain only generated run ID, time, fixed component/event
names and elapsed time. Normal application startup configures bounded files at:

```text
%LOCALAPPDATA%\FahadRobotHub\logs\events.jsonl
```

The current file is limited to approximately 256 KiB, with at most two rotated
backups; memory retains the newest 200 events. If file setup fails, the app keeps
bounded memory events instead; the exported `event_log_file_configured` flag
states whether a file handler was configured, not a guarantee of every disk write.
These are separate from the robot's existing service logs. No automatic restart,
arming, reconnection or motion recovery is introduced.

The helper's Python/disk metadata is read-only and does not import ROS or probe
serial devices. Until the updated helper is deliberately deployed, old robots
may report these fields as unavailable. No hardware identity is inferred.

## 4. Validated ordinary settings

`Tools/remote_dashboard/dashboard_config.json` now holds two profiles:

```json
{
  "schema_version": 1,
  "profiles": {
    "preview": {"port": 8765, "fps": 3.0},
    "robot": {"fps": 3.0}
  }
}
```

`fps` is the JPEG preview refresh cap (1–5), **not detector FPS**. The default
remains 3.0. Preview port is an integer from 1024 to 65535. The robot profile
retains port 8765 for the existing Hub protocol. CLI `--port`/`--fps` overrides
remain supported and bounded as before. `--ros` chooses the robot profile;
otherwise the preview profile is used. A settings file never enables ROS/driving.

Optional explicit file:

```text
python server.py --config PATH_TO_SETTINGS_JSON
```

Unknown/missing fields, duplicate keys, invalid types, unsupported schema and
oversized files are rejected before ROS/server startup. Credentials, hosts,
topics, arbitrary commands and motion parameters are not accepted. Config is
read only at startup, not hot-reloaded while driving. Existing drive limits,
freshness guards, origin/key checks and control behaviour are unchanged.

The Hub's v0.14 runtime has **17** required files, including validator and default
configuration. The existing installer verifies the complete bundle, so do not
copy the new server/configuration in isolation. It deliberately installs the
source-controlled configuration; ad-hoc robot-side edits cause a checksum mismatch
and may be replaced by the next confirmed update. Edit/review the local source
configuration and keep release records aligned instead. Original vendor code stays
untouched. Actual old-Jetson execution is not established by syntax checks.

## What remains staged, not completed

- A suitable timestamped camera/depth/CameraInfo/scan/TF dataset for offline fusion
  regression. Existing RGB/YOLO recordings are not an aligned multimodal dataset.
- Formal fusion schemas and calibration/version provenance once the association
  design is selected. Existing validation/units policies remain in force.
- Complete measured robot dependency/model inventory and tested installed-runtime
  restoration. Laptop dependency observations do not pin or upgrade the Jetson.
- CPU/GPU/bandwidth/latency benchmarks and optimization; no speed gain is claimed.
- Automated complete experiment manifests when new fusion experiments are added.

These remain part of the approved direction, not features falsely labelled live.
Restore the missing scan stream and collect suitable stationary evidence at the
lab before validating camera–LiDAR association. Saved-data tests must not publish
motion topics into the live robot.

## Verification record

Final full offline run: `tmp/quality_reports/20261022_211313_3f59ff24/summary.md`.
Tools: 57/57. Dashboard: 261/261. Hub: 53 passed, one Windows symlink-privilege
skip (54 total). All six JavaScript groups, JS/Python syntax/configuration checks,
Git whitespace and runtime inventory checks pass. Dashboard JavaScript includes
122 checks, plus four annotation-module checks and existing scoring assertions.
New tests cover checker failure/timeout/missing/invalid/empty-result handling,
source hashing, configuration bounds/precedence/protected keys, diagnostic secret
exclusion, stale/demo evidence, rotation limits, read-only inventory and Save report
without a fresh RPC. Isolated runtime-copy/bundle tests also remain in the suites.

Earlier full runs in this same session reported Windows 10053 HTTP rejection-test
errors: one in `20261022_210804_a83a0b4a`, two in `20261022_211209_6bc77e9b`.
They returned nonzero and were retained. Final reruns followed checker changes;
there is no automatic retry, exclusion or weakened assertion. A later passing run
does not diagnose/fix the intermittent host/transport issue.

Observed laptop environments: NumPy tests use Python 3.12.14/NumPy 2.3.5; Hub uses
Python 3.11.9/Paramiko 5.1.0; runner/dashboard use the installed Python 3.11.9;
Node 24.19.0, Git 2.53.0.windows.3. These are observations, not robot requirements.
No packages were installed or upgraded. Actual Python2.7/3.6/ROS/Jetson execution,
native GUI interaction, persistent real App log setup and physical robot behaviour
were not tested. Controlled tests use fake UI/SSH, synthetic data and temp files.
The CMD wrapper was inspected; checks were executed through its Python entry point.
Control/drive/browser-coordination files have no differences from the baseline.
