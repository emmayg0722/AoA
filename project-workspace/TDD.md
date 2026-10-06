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

- examples/catalog.json indexes existing same-origin sample JSON by registry key. examples.js validates and loads all source files before entering an example; missing files fail visibly rather than showing a partial project. No sample data is duplicated or mixed across clients.
- Example mode uses the same scoped tool bridge with in-memory values, but skips repository saves, recovery journals and GitHub polling. The mode also changes tool/report storage notices. A URL example ID supports direct loading after refresh.

- A requested example copy retains a cloned state seed only in the tab. Projects.create validates all seed keys, copies known tool data into its atomic folder commit, and sets shared/client/assessor header fields from the creation form. The example catalog and existing client projects are untouched.

- The project selector renders separate example/client optgroups, preserving example entries even when the public client index fails. An example-prefixed selection invokes the existing temporary example loader.
- A deferred connection dialog retains the creation form and resumes its submit only after successful authentication. Cancel keeps the form and performs no project write. Reconnect uses the same dialog without leaving the open tool.

- Anonymous project sessions use immutable public GitHub snapshots without a credential. Public file reads use raw.githubusercontent.com at the resolved commit to avoid a separate REST request per tool. View sessions skip mutation, recovery journals and background API polling; an explicit refresh reloads saved work. The tool bridge exposes view-only state, protects storage and disables editing controls while retaining readable forms and workspace navigation.

- The optional editor action from a viewed project reconnects in memory, then requires normal participant/visibility confirmation before loading a writable session. Anonymous opening remains independent of that action.
