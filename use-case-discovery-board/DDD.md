# Dictionary

| Term / function / concept | File | One-line purpose |
| --- | --- | --- |
| Original workshop interface | `index.html` | Existing canvas, five block types, intake, checklist, exports, scoring, and live-session client. |
| Durable live relay | `relay.py` | Validates operations, atomically saves named sessions, allocates IDs, and long-polls updates. |
| Session data | `data/sessions.json` | Repository source of truth for saved original workshop documents. |
| Preserved replacement-board data | `data/board.json` | Retains the user's data from the earlier replacement interface. |
| Publication entry generator | `publish-entry.py` | Copies the original interface to the Phase 1 URL with adjusted relative links. |
| Relay verification | `test/test_relay.py` | Checks persistence, concurrent edits, failure handling, validation, and HTTP collaboration. |
| Commands | `package.json` | Starts the restored workshop and runs its checks. |
| Usage and hosting | `README.md` | Explains local shared editing, repository storage, and public connection settings. |
| Design and status | `PDD.md`, `TDD.md`, `FDD.md`, `CURRENT.md`, `DECISIONS.md` | Scope, implementation, behavior, progress, and decisions. |
| Public entry | `../Phase 1 - Discovery & Assessment/use-case-discovery-board/index.html` | Publishes the original workshop at its established URL. |
| Compatibility launcher | `../Phase 1 - Discovery & Assessment/use-case-discovery-board/workshop-relay.py` | Keeps the original Python launch command working. |
| Earlier relay implementation | `server.mjs`, `board.mjs`, `app.js`, `styles.css`, `test/board.test.mjs` | Retained implementation of the superseded replacement interface; no longer the default UI. |
