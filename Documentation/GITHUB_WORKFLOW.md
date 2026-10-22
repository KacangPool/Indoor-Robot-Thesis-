# GitHub: project source and checks

Public repository: [KacangPool/Indoor-Robot-Thesis-](https://github.com/KacangPool/Indoor-Robot-Thesis-).
The user explicitly authorized uploading the reviewed project source here on
2026-10-22. This is not permission to publish credentials, recordings or all future
private files. Wi-Fi work is deferred; no robot/network changes are part of setup.

## What belongs on GitHub

Authored code, tests, ordinary configuration, project Markdown notes and the
GitHub quality workflow. Excluded: images/video, captured ROS data, raw reports,
private profiles/keys, model weights, vendor archives/PDF manuals and the separate
hosted planner. These stay on the computer and require separate backup decisions.

The publication audit checks all reachable committed versions against a source
path allowlist and selected high-confidence credential patterns. It prints only
locations/categories, never matching values. It is best-effort, not a guarantee
of confidentiality. One reviewed synthetic redaction-test marker is explicitly
reported with a waiver pinned to its exact path, Git blob, line and category;
it is not a blanket exclusion of test files or password findings. It is not proof
that all secrets/private information were detected. Review files/history as well:
`.gitignore` does not erase previously committed content.

```text
python Tools/publication_audit.py
```

The local history and original GitHub README commit are combined without a
force-push. The README retains the user's original project description and adds
accurate status/entry points. No history or unrelated user changes are discarded.

## Everyday use

1. Work in the existing project folder. Check `git status --short` first.
2. Make a focused change, run `Tools/Check Project.cmd`, review errors/skips and
   update the project continuity notes.
3. Review/stage only intended source changes and record a local commit.
4. Run the publication audit before the first upload and whenever adding data,
   dependencies, source scope or potentially sensitive material.
5. Push deliberately to `origin/main`; inspect the GitHub Actions result. Nothing
   pushes automatically merely because a file was saved or this chat was used.

The coding assistant can use the existing GitHub connection to inspect this
repository. That connection does not give Git in PowerShell automatic credentials.
Normal Git pushes may use Git Credential Manager's sign-in flow; complete it
locally if prompted, never paste a token or password into chat. No credential is
embedded in the remote URL, source, CI configuration or documentation.

Useful read-only checks:

```text
git status --short
git remote -v
git log --oneline --graph -8
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Matching local/remote commit hashes after a successful push establish that the
recorded source was synchronized at that moment, not that untracked files were
uploaded or the robot was updated. Avoid force-push/reset commands. If GitHub has
new changes, fetch and review/reconcile them before pushing; preserve user edits.

## Automatic quality checks

[Actions](https://github.com/KacangPool/Indoor-Robot-Thesis-/actions) runs
`.github/workflows/quality.yml` on main pushes, pull requests and manual dispatch.
It uses Ubuntu24.04, Python3.11, Node24 and the pinned **hosted-test** requirements
in `.github/ci-requirements.txt`. This does not install or upgrade anything on the
Jetson. Direct dependencies are pinned; the complete transitive environment is
not a fully locked robot release.

Official checkout/setup/artifact actions are pinned to exact v7 revision SHAs.
The job token is `contents: read`; checkout credentials are not persisted. It
audits source history and calls the same offline checker used locally. Reports
are retained as an artifact for seven days, including on failures. These contain
synthetic test output and hosted-runner metadata, not captured robot data.

Local tests and hosted CI are different evidence. A workflow file existing does
not prove a successful hosted run; inspect the run for the actual commit. Existing
Windows HTTP10053 flakiness is not hidden or declared fixed by a passing Linux run.
No ROS/hardware/old-Jetson environment, physical stopping, fusion accuracy, live
browser or native GUI is validated by this CI. There are no deployment actions,
auto-fix commits, remote robot credentials or autonomous motion.

GitHub Actions configuration follows the official
[workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
and the respective official checkout/setup/artifact action documentation. Changing
the workflow, dependencies or permissions needs normal review and verification.
