# Decisions

## 2026-10-05 — Standalone repository-backed board

The user requested a live board with all its data stored in the repository. Keep the feature in `use-case-discovery-board/`, with a small local server writing `data/board.json`. This supersedes the earlier proposed cloud-database approach for this implementation.

## 2026-10-05 — Empty board and explicit migration

Start with no fabricated use cases. Import existing prioritization exports explicitly rather than silently copying private browser data. Preserve the complete original import payload.

## 2026-10-05 — Saved snapshots and optimistic concurrency

Broadcast only successfully persisted snapshots. Reject stale mutations to protect other participants' changes. Leave Git commits and pushes under the user's control.

## 2026-10-05 — Workshop working surface

Architects use this board during a daytime workshop on laptops. Use the toolkit's light working surface, indigo actions, system font, a spacious canvas, and familiar list/editor panels.

## 2026-10-05 — In-page confirmations

Use accessible HTML dialogs for destructive imports, deletion, draft discard, and connection-label edits. Native confirm/prompt dialogs stalled the in-app browser during verification; the in-page alternative was verified with both Cancel and Continue.

## 2026-10-05 — Publish at the requested Phase 1 URL

The user requested publication at `/AoA/Phase%201%20-%20Discovery%20%26%20Assessment/use-case-discovery-board/`. Keep the standalone implementation and JSON at the repository root, with a Phase 1 entry loading those assets. Current remote main already contains a different workflow workshop, so preserve it as linked `workshop.html` and retain its original documentation and assets. Publish against current remote main rather than overwriting it with the older local checkout or unrelated homepage edits.

## 2026-10-05 — Restore the original workshop (supersedes replacement UI and publication facade)

The user explicitly corrected the scope: retain the original discovery board and apply live repository-backed saving to it. The earlier new interface and read-only public facade are superseded. Reuse the original workshop and relay protocol; preserve its browser storage and the replacement interface's saved data.

## 2026-10-05 — Project entry and actual GitHub persistence

The user requested Create/Join projects with named participants and all project data stored on GitHub. Keep the original board after the entry screen. Server-generated IDs isolate projects, and Join never creates missing projects. This supersedes the earlier manual-commit decision for configured project mode: successful saves are committed by the server. Local development remains clearly labeled and does not claim GitHub saving.

## 2026-10-05 — Repository visibility disclosed before entry

The current AoA repository is public. Participants acknowledge that project names, display names, and board content will be visible there before creating or joining a GitHub-backed project. The server determines the actual storage mode and repository visibility; the frontend cannot assert a GitHub save on its own.

## 2026-10-05 — Separate project-data branch

Keep project records at the same standalone-folder path on `codex/discovery-data` in the AoA repository. This supersedes main as the default data branch: board edits must not trigger repeated Pages website builds. The code remains on main; storage notices include the actual data branch and path. Serialize GitHub write attempts to keep save traffic bounded.
