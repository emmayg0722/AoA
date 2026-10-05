# Function design

| Feature | Inputs | Behavior / edge cases |
| --- | --- | --- |
| Create project | Project name, display name, storage acknowledgment | Create a new isolated empty board with a generated ID; reject blank inputs and missing acknowledgment. |
| Join project | Existing selection or project ID/share URL, display name, acknowledgment | Join only an existing project; show its saved board and current participants. |
| Project discovery | Connected service | List real saved projects; distinguish no projects from service unavailable. |
| Disclosure | Service storage mode/repository | State GitHub visibility before sending project content; local development explicitly says GitHub sync is not configured. |
| Share | Active project | Generate a same-board URL with project ID and configured service URL; never include access codes. |
| Isolation | Project ID | Browser drafts, board data, peers, and undo history remain separate between projects. |
| Switch / leave | User action | Save pending operations before leaving; refuse to discard a failed repository write silently. |
| Live editing | Original operations | Preserve all original workshop features and participant names; acknowledge only durable saves. |
| GitHub save | Server token and current blob SHA | Commit complete project data; conflicts refresh without overwriting and failures keep edits pending. |
| Recovery | Reload / server restart | Rejoin the existing project using the participant name; protect project-specific browser drafts. |
| Offline board | Explicit local-board action | Retain the original local workshop and its browser key; never imply project collaboration or GitHub saving. |

| GitHub-only connection | Participant token | Verify GitHub identity, read actual repository visibility and saved projects; hold credential only in memory and never include it in drafts, exports, URLs, or configuration. |
| Repository collaboration | Original operations | Commit changes to the data branch, retry conflicts against the latest saved state, and poll every 12 seconds; show project members without claiming active presence. |
| Missing credential | Public entry | Read public projects, explain required write access, and disable create/join until the participant connects; browser-only workshop remains available. |
