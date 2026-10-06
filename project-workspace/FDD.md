# Function design

| Feature | Input | Behavior |
| --- | --- | --- |
| Create | Client, project, display name, GitHub connection, public-storage acknowledgment | Commit an isolated project manifest, shared header, and all empty phase/tool folders in one commit. |
| Join | Existing project or invite ID, display name, acknowledgment | Load only that project and record its participant name; missing IDs never create projects. |
| Phase workspace | Phase and tool selection | Show the phase toolkit and open the original tool with project-scoped state. |
| Autosave | Existing tool localStorage writes | Update that project tool file and shared header atomically; claim GitHub save only after the branch update succeeds. |
| Conflicts | Competing saved edits | Merge independent fields and existing ID-based records; surface same-field edits, colliding new IDs or other competing arrays, and retain pending work. |
| Switch | Another tool/project | Flush changes before switching; fail visibly without discarding unsaved work. |
| Master report | Current project | Assemble/export only its tool state using the existing report page. |
| Browser migration | Explicit import review | Show matching saved tools before copying; do not import raw profiler files or unknown storage keys. |
| Recovery | Reload and reconnect | Reapply the same project/tab journal to current repository state and preserve failed saves. |

| Load example project | Committed example ID | Load all mapped samples and one shared header without a token; show populated-tool and phase counts. Unknown IDs or failed source loads leave the current workspace intact. |
| Explore example | Existing phase/tool/report UI | Keep edits in the tab across tool navigation, label the project synthetic and show absent samples as empty tools. Never write GitHub or replace standalone drafts. |
| Reset example | Explicit reset button | Discard temporary edits and reload the original committed example; refresh has the same result. |
| Leave example | Switch project | Discard temporary values and return to create/join/example entry without a client-data write. |

| Use example as starting project | Explicit example action, create form and GitHub connection | Copy current temporary tool state into a new isolated project; show the fictional-content notice, require normal consent, and allow canceling the seed. Copy identity headers from the form; do not rewrite fictional narratives. |

| Join-list examples | Existing-project selection | Display all committed examples in the shared existing-project list, show sourced coverage, and load without a name, consent checkbox or credential. |
| Deferred project access | Create or real Join submit while disconnected | Open an access dialog after form validation; resume the requested operation on successful connection, retain inputs on cancellation or failure. No standalone connection card. |
