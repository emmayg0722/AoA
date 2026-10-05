# Toolkit client projects

Open `/project-workspace/` from the toolkit home page. Connect your own GitHub account, acknowledge repository visibility, then create or join a client project. The repository owner can use a fine-grained token restricted to AoA with Contents read/write. Outside collaborators currently need GitHub write access and a classic `public_repo` token. Credentials stay in the tab's memory.

Each client project spans ten phases and all 45 existing saved tools. The tools retain their original interfaces inside the workspace. The shared header, master report, cross-tool inputs and exports use only the selected project. Standalone tool pages retain their previous browser drafts. Use **Project options → Review browser drafts** to explicitly import selected drafts.

Data lives in `projects/<project-uuid>/<phase>/<tool>/state.json` on `codex/project-data`. Project creation commits the manifest, header and all tool folders atomically. Autosave waits eight seconds; **Save now** saves immediately. GitHub changes are checked every fifteen seconds and offered for reload. Member names describe durable membership, not online presence. This is collaboration through saved GitHub commits, without a separate server or live cursor service.

Independent fields and existing ID-based rows/blocks merge. Same-field edits, colliding new record IDs and other competing arrays require review. Failed saves retain a project/tab recovery journal in this browser. Reload, reconnect, and join the same project to recover it. A quota failure is reported; keep that tab open and use a pending-work download. **Forget token and leave** clears the credential even when the service is unavailable.

AoA is public: client names, saved tool data, membership and commit history are readable by anyone. Raw profiler datasets remain in the browser; only saved assessment summaries can be imported/saved. Do not enter credentials or confidential client information into tool fields.

## Verification

Run `npm test` here. Run `npm test` in `../use-case-discovery-board` for the existing 26 board checks. `python3 integrate.py` rebuilds the registry and early bridge imports from the real report registry. After changing the canonical board, run its `publish-entry.py` before `integrate.py`.

| Check | Evidence |
| --- | --- |
| Domain, atomic Git API, Unicode, isolation, merge and credential failures | 15 Node tests pass. |
| Original board regressions | 17 Python and 9 Node tests pass. |
| Original interfaces and bridge coverage | Playwright CLI opened all 45 tools without page runtime errors. |
| Rendered project workflow | Isolated API fixture verified create/join, Phase 1 board, Phase 2 strategy, Phase 10 ROI, shared header/report, second-client isolation, failed-save recovery and explicit draft import. |
| Rendered collaboration | Two browser participants retained both members and independent fields; same-field conflicts required an explicit choice. |
| Actual authenticated GitHub writes from the public application | Require a participant to enter their own token on the page; the managed connector credential is never copied into the application. |

The disposable `test/mock-server.mjs` gateway runs only on loopback port 4323 and never sends fixtures to GitHub. For browser verification, serve this checkout on port 4321 and route `https://api.github.com/**` in Playwright to the gateway `/gateway` endpoint, supplying the intercepted request URL and options. The CLI scenarios `browser-smoke.js`, `browser-concurrency.js` and `browser-collaborators.js` require that route and a joined fixture project. They are verification code, not a production service.
