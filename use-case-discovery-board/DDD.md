# Dictionary

| Term / function / concept | File | One-line purpose |
| --- | --- | --- |
| Original workshop interface | `index.html` | Existing canvas, five block types, intake, checklist, exports, scoring, and live-session client. |
| Durable live relay | `relay.py` | Validates operations, atomically saves named sessions, allocates IDs, and long-polls updates. |
| Saved-state validation | `relay.py` (`validate_saved`) | Validates disk/repository records before loading or accepting a remote conflict refresh. |
| Session data | `data/sessions.json` | Full workshop records; hosted GitHub mode uses this path on `codex/discovery-data`. |
| Preserved replacement-board data | `data/board.json` | Retains the user's data from the earlier replacement interface. |
| Publication entry generator | `publish-entry.py` | Copies the original interface to the Phase 1 URL with adjusted relative links. |
| Relay verification | `test/test_relay.py` | Checks persistence, concurrent edits, failure handling, validation, and HTTP collaboration. |
| Commands | `package.json` | Starts the restored workshop and runs its checks. |
| Usage and hosting | `README.md` | Explains local shared editing, repository storage, and public connection settings. |
| Design and status | `PDD.md`, `TDD.md`, `FDD.md`, `CURRENT.md`, `DECISIONS.md` | Scope, implementation, behavior, progress, and decisions. |
| Public entry | `../Phase 1 - Discovery & Assessment/use-case-discovery-board/index.html` | Publishes the original workshop at its established URL. |
| Compatibility launcher | `../Phase 1 - Discovery & Assessment/use-case-discovery-board/workshop-relay.py` | Keeps the original Python launch command working. |
| Earlier relay implementation | `server.mjs`, `board.mjs`, `app.js`, `styles.css`, `test/board.test.mjs` | Retained implementation of the superseded replacement interface; no longer the default UI. |

| Project entry and isolation | `index.html`, `projects.js` | Create/join forms, project lists/share links, names, storage notice, and per-project browser drafts. |
| Project API and metadata | `relay.py` | Creates/list/joins isolated project records and persists participant display names. |
| GitHub persistence adapter | `github_store.py` | Reads and SHA-checks repository commits using a server-only credential. |
| Public service configuration | `config.json` | Non-secret live-service URL and repository label for the Pages frontend. |
| Container service | `Dockerfile` | Runs the Python API on a host-provided port with server-only configuration. |
| Project verification | `test/test_projects.py` | Checks project creation/join, isolation, recovery, notice enforcement, and GitHub failures/conflicts. |

| GitHub-only browser adapter | `github-projects.js` | Authenticates directly to GitHub, loads/projects, applies operations, SHA-checks commits, and polls shared snapshots. |
| Browser adapter verification | `test/github-projects.test.mjs` | Exercises conflict recovery, isolation, real commit acknowledgment, failures, and credential boundaries with a simulated API. |

| Shared status and transport selection | `index.html` (`syncFetch`, `sharedStatus`), `projects.js` (`initProjects`) | Selects direct GitHub versus optional relay and reports polling/member semantics accurately. |
| Forget participant credential | `projects.js` (`forgetGithubConnection`) | Flushes pending work before clearing the in-memory GitHub connection. |
