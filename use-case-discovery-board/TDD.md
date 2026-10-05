# Technical design

- Frontend: the original self-contained vanilla HTML/CSS/JS workshop, retaining its existing storage key and live operation protocol.
- Backend: Python standard-library relay in this standalone folder; the Phase 1 launcher delegates to it.
- Storage: `data/sessions.json` holds every named session and its complete board document. Atomic replacement precedes acknowledgments and broadcasts. Existing replacement-board data remains preserved in `data/board.json`.
- Concurrency: each session serializes validated operations under a lock; distinct blocks can be edited together. Whole-board actions retain the original last-writer-wins behavior. Persisted allocation counters prevent colliding IDs after restart.
- Transport: original long polling, participant roster, explicit Go live/Leave session; failed outbound requests retain their queued edits.
- Hosting: local server by default; public deployment uses HTTPS, persistent repository checkout/storage, an access code, and an explicit allowed-origin list. No credentials are committed.
- GitHub Pages: the original board remains editable in browser-local mode. Connection settings allow an external HTTPS service; static hosting does not itself perform repository writes.
- Entry generation: `publish-entry.py` copies the standalone original interface to the Phase 1 route and adjusts only toolkit/sample links.
