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
