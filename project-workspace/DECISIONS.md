# Decisions

## 2026-10-05 — Project covers the entire engagement

The user changed scope from a discovery-board project to a client project spanning every phase and tool. This supersedes board-only project entry as the primary project workflow. Preserve the existing tools and put a shared workspace above them.

## 2026-10-05 — One folder hierarchy and atomic multi-file saves

Store all client project records under projects/ on codex/project-data, with one project folder, then phase and tool folders. Use Git trees/commits and a non-forced ref update so metadata and tool data appear together. Do not flatten the engagement into one board session file.

## 2026-10-05 — One in-memory connection across tool navigation

Keep tools inside a same-origin workspace frame. Its parent keeps the participant token in memory and bridges existing saved-state calls. This avoids persisting a token merely to move between tools and avoids rebuilding each tool. Standalone browsing and original drafts remain available.

## 2026-10-05 — Public visibility and explicit migration

AoA is currently public. Disclose visibility before project writes and review old browser-draft imports. Keep raw profiler uploads local; save the assessment summaries that tools already persist. Do not create fake clients or project records.

## 2026-10-05 — Merge existing records by ID

The initial rule treated every competing array change as a conflict. Superseded for arrays of unique ID-based records: independent edits to existing table rows and board blocks can merge. Concurrent additions with the same ID still conflict, preventing two different new blocks from becoming one record. Primitive arrays retain the explicit conflict rule.

## 2026-10-05 — Preserve an open tool's coherent snapshot

Rendered concurrency verification exposed SOP wrappers reading newly merged fields while the form still displayed older values. Keep frame reads on their initial/write snapshot until reload; merge changes in the parent. Also treat materialized omitted blank fields as defaults rather than clears of newly populated teammate fields. Explicit clears of known values still conflict when a teammate changed them.
