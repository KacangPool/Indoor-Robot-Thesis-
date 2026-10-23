# Assistant-maintained Fieldnotes

Private Site: https://fahad-robot-fieldnotes.crispswift256.chatgpt.site

The user requested ongoing progress/calendar maintenance from this project chat
on 23 October 2026. The site is separate from robot control and stays private.

## Source of truth and scope

- Read `CHANGELOG.md`, `PROJECT_CONTEXT.md`, current task/user observations and
  relevant verification reports. Do not infer completion from dates, optimistic
  plans, package names or a passing laptop test.
- Keep confirmed hardware, source-tested changes, user-observed operation,
  unresolved blockers, tentative goals and deferred ideas distinct.
- Update `Sites/fieldnotes/lib/project-progress.ts` after material work. It owns
  the curated summary, evidence, next-lab focus, deferred scope and dated calendar
  overrides. Update its reviewed date/revision only when evidence was reviewed.
- Existing baseline defaults are replaced only in the displayed view when they
  are still untouched. Edited/moved/completed personal goals and personal notes
  are retained. Deleted default goals remain deleted. Old unchanged handoff text
  is superseded; no D1 user data is rewritten by publication or viewing.
- Assistant-maintained goals/notes are read-only and marked; their details expand
  in place. The real personal planner remains editable and revision-protected.
  Personal JSON backups contain personal stored data; calendar export includes
  the displayed managed roadmap. The curated source is versioned separately.
- Do not publish raw reports, credentials, photos or full conversations. No live
  chatbot, robot telemetry or autonomous sensor validation is implied.

## How updates reach the phone/laptop

Use the Sites skill with existing project ID
`appgprj_6ad732b9b9448191ba4fba48d8f1b80f`. Get current Site/access and a short-lived
source credential; open the existing source with the supported workflow before
edits. Preserve remote/user changes and owner-private access. Credentials remain
in memory and hidden stdin, never source, shell arguments or files. The user
explicitly approved that supported private publishing flow in this session;
respect any new native permission checks. Never bypass a credential rejection.

Run `node --test tests/core.test.mjs` and TypeScript checks in the Site. For UI
changes, use local preview and browser checks; API tests target localhost only.
Build/package/push with supported helpers, then native private save/deploy. If
local packaging is unavailable, preserve the pushed source and use the supported
remote-build fallback, documenting the limitation. Only claim live updates after
deployment succeeds; retain version/deployment IDs through retries.

The generated website does not read this chat or the laptop by itself. Changes
appear after the assistant updates and publishes the curated source; reload an
already-open tab to receive a new publication. No database writer/token endpoint
or cloud Site MCP integration was added for this workflow.

## Daily review

Use a local thread heartbeat, not a cloud task claiming access to laptop files.
Review daily at 18:00 Europe/Berlin and update only when material new evidence
exists or the dated plan needs an evidence-based adjustment. Stay quiet when
unchanged; report meaningful updates, publishing failures or required input.
Check existing local automation records first to avoid duplicates. A saved
schedule is not proof of an unattended successful publish. The laptop and desktop
app must be running and this project/source and Sites permissions available.
This workflow may be blocked by unattended sandbox/credential rules; report it,
not a fabricated update. Daily checks supplement maintenance during active work.

Never modify robot runtime, driving limits, networks or the public GitHub remote
as part of planner maintenance. Never mark experiments complete without evidence.
Keep continuity notes and local source snapshots; do not chase speculative new
features or rewrite the planner's storage/authentication to avoid maintenance.
