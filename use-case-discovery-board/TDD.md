# Technical design

- Stack: Node.js 22+ standard library; vanilla HTML/CSS/JavaScript; no build step or external runtime dependencies.
- Components: browser graph/editor, HTTP API, server-sent event stream, validated board model, and JSON file store.
- Flow: browser operation + expected revision → validate → atomically replace `data/board.json` → publish saved snapshot to connected browsers.
- Concurrency: one server process serializes writes; stale revisions return 409 and never overwrite newer data.
- Storage: metadata, cards, scores, owners, positions, and connection labels live in `data/board.json`; the initial graph is empty. View pan/zoom is session-only presentation state.
- Import: a JSON board replaces the graph after explicit confirmation; legacy prioritization JSON appends candidates and retains its original payload in repository data.
- Hosting: loopback by default; configurable bind address for trusted networks. Host/origin checks protect local write endpoints. Public hosting requires authentication, HTTPS, persistent disk, and a single writer process.
- Static hosting: display the checked-in JSON read-only when the API is unavailable; never claim a browser-only change was saved to the repo.
- Public route: `Phase 1 - Discovery & Assessment/use-case-discovery-board/index.html` loads the standalone assets using relative paths; data/API URLs resolve from `app.js`, so both entry points use the same saved JSON. The previous remote board is preserved as `workshop.html`.
