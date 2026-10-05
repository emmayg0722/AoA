# Technical design

- Static workspace shell on GitHub Pages retains one in-memory participant token while users switch existing tools in a same-origin iframe.
- registry.json indexes actual tool routes, storage keys, phase names, and folder ownership.
- tool-storage.js runs before a tool initializes: project keys use the parent workspace cache, while language/preferences and standalone pages keep normal browser storage. The original browser draft is never replaced.
- Each open frame reads its own coherent initial/write snapshot until reloaded. The parent merges that snapshot's changes into the project cache; unseen merged fields cannot be copied into a tool's SOP save wrapper and then overwritten by a stale form.
- GitHub Git Data API commits metadata, engagement header, and tool files atomically, with a non-forced branch update. Re-read immutable commit snapshots and reapply edits after competing commits. Never replace the branch with a stale tree.
- Generic tools merge disjoint object fields and existing ID-based table rows/board blocks. Same-field edits, colliding new record IDs, and competing edits to other arrays show a conflict that retains browser work for review. Names show project membership, not active presence.
- Debounce saves for eight seconds. Poll the branch every fifteen seconds and offer refresh when newer saved work is available; do not reload a form with pending work.
- Recovery journal stores project-scoped pending values/baselines per tab. Credentials stay out of every persistent store, URL, export, and repository file.
- Default data branch codex/project-data holds projects/index.json and per-client project folders, so project commits do not rebuild the Pages site.
