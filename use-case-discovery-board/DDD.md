# Dictionary

| Term / function / concept | File | One-line purpose |
| --- | --- | --- |
| Board interface and confirmations | `index.html` | Toolbar, graph canvas, card list, editor forms, and accessible review dialog. |
| Board styles | `styles.css` | AoA tokens, responsive layout, canvas and interaction states. |
| Browser controller | `app.js` | Rendering, drafts, mutations, drag/pan/zoom, imports, and event stream. |
| Board validation and operations | `board.mjs` | Validates the schema and applies revision-checked graph operations. |
| HTTP server and file store | `server.mjs` | Serves assets, serializes atomic JSON saves, and broadcasts snapshots. |
| Saved graph | `data/board.json` | Repository source of truth for all durable board data. |
| Persistence verification | `test/board.test.mjs` | Model, API, concurrency, live stream, and restart checks using temporary data. |
| Commands | `package.json` | Dependency-free start and test commands. |
| Usage and hosting | `README.md` | Setup, storage, import/export, and collaboration boundaries. |
| Current work | `CURRENT.md` | Focus, verification, blockers, and next steps. |
| Product scope | `PDD.md` | Users, purpose, scope, and success criteria. |
| Technical design | `TDD.md` | Architecture, persistence, and hosting decisions. |
| Function behavior | `FDD.md` | Inputs, outcomes, and edge cases. |
| Decisions | `DECISIONS.md` | Confirmed choices and their reasons. |
| Published Phase 1 entry | `../Phase 1 - Discovery & Assessment/use-case-discovery-board/index.html` | Loads this standalone app at the requested GitHub Pages URL. |
| Previous workflow workshop | `../Phase 1 - Discovery & Assessment/use-case-discovery-board/workshop.html` | Preserves the remote workshop board and its browser-local data. |
