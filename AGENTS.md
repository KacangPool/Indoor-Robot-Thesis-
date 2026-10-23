# Project continuity instructions

This workspace contains a bachelor-thesis project about vision-based detection of living beings for an indoor search-and-rescue robot.

For every material change to files, research conclusions, project scope, experiments, model choices, datasets, hardware assumptions, or decisions:

1. Update `CHANGELOG.md` in the same work session.
2. Add the newest entry at the top of the relevant date section.
3. Record what changed, why it changed, files affected, verification performed, and any open questions.
4. Update `PROJECT_CONTEXT.md` when the stable project scope, confirmed hardware, constraints, or key decisions change.
5. Do not present preliminary hardware identification as confirmed unless supported by a readable device label or authoritative documentation.

Preserve user-authored files and unrelated changes.

## Accuracy-first preference

The user explicitly asks for careful, mistake-avoiding work in subsequent prompts.
Verify material changes with appropriate checks, distinguish observed results
from assumptions/plans, and disclose untested behavior or missing connections.
Do not promise infallibility or describe a mock feature as a live integration.

## Reuse-first modularity

For new or changed user-authored code, reuse the existing shared modules before
copying an algorithm into another script. Keep sensor/data calculations separate
from ROS, network, GUI, model-loading and motion adapters. Imports of shared code
must not start services, connect to the robot or download model weights.

Preserve existing entry points and behaviour where practical. When extracting a
module, update its callers, tests, runtime/bundle dependency lists and copying
instructions together. Keep distinct guarded motion profiles separate. Do not
rewrite vendor packages, historical reports/data or unrelated apps to satisfy a
blanket modularity request. See Documentation/MODULAR_CODE_ARCHITECTURE.md.

## Ongoing quality workflow

The user approved maintaining this workflow for future work on this project:

- Inspect local Git status before editing. Preserve unrelated changes; use local,
  source-only snapshots for meaningful task changes. Never add credentials,
  recordings, vendor archives or the separate hosted app. No remote publication
  is authorized by this workflow. Local snapshot identity is non-personal and
  supplied per commit; do not alter the user's global Git identity.
- Reuse Tools/quality_check.py after material code changes, alongside focused
  tests appropriate to risk. Report failures, errors, missing dependencies and
  skips honestly. Never hide the Windows HTTP abort with retries or exclusions.
- Keep ordinary settings validated and separate from enforced motion/security
  limits. Configuration must not launch ROS, arm driving or accept shell commands.
- Use bounded structured events and allowlisted diagnostic exports. Do not log
  passwords, bootstrap keys, command payloads, images or raw exception/SSH text.
  Mark cached/demo evidence clearly and preserve snapshot age.
- Keep runtime bundles, dependency/version records, tests and usage docs aligned.
  Do not upgrade or claim compatibility with the old Jetson from laptop tests.
- Before changing live perception/fusion, define units, coordinate frames,
  timestamps, validity/association rules and experiment provenance. Prefer saved-
  data regression tests where suitable data exists; never replay motion commands
  into the live robot. Measure performance before claiming an optimization.

See Documentation/QUALITY_WORKFLOW.md for the implemented foundations and staged
lab-dependent work. CHANGELOG.md and PROJECT_CONTEXT.md still require updates as
specified above. Keep code changes separate from robot deployment authority.

## Assistant-maintained planning website

The user requested ongoing progress/calendar maintenance on 2026-10-23. After
material work, update the private Fieldnotes project summary and dated roadmap
using verified project records, in addition to CHANGELOG/PROJECT_CONTEXT. Reuse
Sites/fieldnotes/lib/project-progress.ts and the Sites skill; preserve private
access, personal notes/goals and source history. Separate source-tested,
user-observed, blocked and planned states. Do not mark hardware work complete
from elapsed dates or code tests. No robot telemetry or live chatbot is implied.
Publish through supported Sites tools and verify deployment before claiming live
updates; disclose blockers. Never expose source credentials or raw/private data,
or treat planner maintenance as robot/deployment/public-GitHub authorization.
See Documentation/PLANNER_MAINTENANCE.md. A local daily review supplements active
work; it does not guarantee updates while the laptop/app are off.

## Public repository scope

The user explicitly authorized the initial reviewed source upload to
KacangPool/Indoor-Robot-Thesis- on 2026-10-22. Keep a public-safe source allowlist;
this is not blanket permission to publish private data or every future edit.
Before publication, run Tools/publication_audit.py against committed history,
review any findings and preserve existing remote changes. Never print secret
values or force-push over unrelated history. GitHub CI is read-only/offline with
no robot deployment or credentials. Do not claim a push or hosted check succeeded
until actual remote commit/run state confirms it.
