# Dictionary
| Term / function / concept | File | One-line purpose |
| --- | --- | --- |
| Workspace interface | index.html, workspace.css, workspace.js | Create/join client projects, navigate phases/tools, disclose storage, and show save/recovery state. |
| Toolkit landing entry and storage notice | ../index.html | Links to client projects and distinguishes standalone drafts from GitHub project storage. |
| Operation and verification guide | README.md | Explains project entry, storage, recovery, limitations and reproducible checks. |
| Tool registry | registry.json | Maps each existing tool, route, storage key, phase, and repository folder. |
| Registry and page integration | integrate.py | Builds the sourced registry and adds the early storage bridge to original tool pages. |
| GitHub repository transport | repository.js | Holds the in-memory credential and commits multiple JSON files through a non-forced Git branch update. |
| Project domain and merging | projects.js | Owns project folder creation/join, tool files, three-way field merging, and durable metadata. |
| Tool storage bridge | tool-storage.js | Routes known storage keys into the active workspace while preserving standalone browser drafts. |
| Project-aware master report | ../engagement-report.html | Uses the bridge's AoaProjectTool flag for project-specific report, import and export wording. |
| Discovery project entry | ../use-case-discovery-board/index.html, ../use-case-discovery-board/publish-entry.py | Sends new engagements to the toolkit workspace while retaining previous board sessions and drafts. |
| Domain and API verification | test/projects.test.mjs, test/fake-github.mjs | Tests atomic commits, concurrent fields, project isolation, credentials, and registry coverage. |
| Isolated browser API fixture | test/mock-server.mjs | Loopback test gateway used only for rendered verification; never a production backend. |
| All-tool rendered smoke | test/browser-smoke.js | Playwright CLI scenario opens all 45 original tools and checks early project storage integration. |
| Storage snapshot regression | test/storage.test.mjs | Verifies SOP double-saves cannot erase unseen remote edits or touch legacy browser drafts. |
| Rendered concurrency regression | test/browser-concurrency.js | Exercises remote independent edits and explicit same-field conflict resolution in a real tool. |
| Two-browser collaboration | test/browser-collaborators.js | Tests two named GitHub participants joining the same project and saving independent fields. |
| Project index and folder policy | ../projects/index.json, ../projects/README.md | Defines the empty repository index and data folder hierarchy. |
| Public configuration | config.json | Selects the GitHub repository and data branch with no credential. |
| Example project catalog | examples/catalog.json | Maps existing synthetic sample files to project identities and registry keys. |
| Example loader and coverage | examples.js | Validates same-origin source mappings and assembles isolated project state with honest coverage counts. |
| Example verification | test/examples.test.mjs, test/browser-examples.js | Verifies sourced coverage, failure atomicity and editable examples without GitHub writes or legacy-draft changes. |
| Example-to-project copy | workspace.js, projects.js | Holds a temporary seed for explicit new-project creation and commits copied tool states atomically. |
| Rendered example copy and failure check | test/browser-example-copy.js | Verifies explicit authenticated copying, source-load failure retention, reset, and clean subsequent project creation. |
| Combined existing project selector | workspace.js: renderProjectList, selectedExample, mode | Lists source examples and real clients and selects the appropriate no-login or shared-project entry flow. |
| Deferred access dialog | index.html: connectionDialog, workspace.js: connectionForm | Requests GitHub access only for creation or an editor reconnect action, and resumes the pending form on success. |
| Join-list and access verification | test/browser-entry.js | Checks example selection, client index failure, deferred access, cancel/invalid connection, create, reconnect and join. |

| Token-free project viewing | workspace.js: mode, enter, projectForm; index.html: viewNotice | Opens saved public projects by list or ID without registering a participant or requesting a credential. |
| View-only original tools | tool-storage.js | Protects project storage and disables editing controls in anonymous saved-project frames. |
| Anonymous snapshot reads | repository.js: read | Reads public JSON from an immutable raw GitHub commit without using per-file REST quota. |
| Project-view browser verification | test/browser-viewer.js | Verifies ID/list access, all original tools/report, refresh, missing IDs and no credentials/writes/journals. |

| Resume existing-project editing | workspace.js: editProject, connectionForm | Explicit editor action connects, then requires the normal name/visibility join before enabling changes. |
