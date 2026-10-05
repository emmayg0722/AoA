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
