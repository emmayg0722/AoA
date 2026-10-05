# Function design

| Feature | Inputs | Behavior and edge cases |
| --- | --- | --- |
| Add/edit | Title, problem, owner, type, status, optional 1–5 scores | Explicit save; blank titles rejected; incomplete scores remain unscored. |
| Move | Pointer drag or inspector X/Y coordinates | Save card position on drop; keyboard users can edit coordinates. |
| Connect | Source, target, label | Directed connection; reject self-links, duplicate pairs, or missing endpoints. |
| Remove | Selected card/connection | Confirm card deletion; remove incident connections with the card. |
| Navigate | Search, card selection, pan, zoom, fit | Sidebar and inspector provide alternatives to canvas interactions; responsive stacked layout on mobile. |
| Live updates | Server-sent saved snapshots | Other browsers update; unsaved inspector drafts stay intact and conflicts require review. |
| Persistence | Revision and operation | Success only after disk save; failures and stale edits leave the persisted board intact. |
| Import/export | Board JSON or existing prioritization export | Export complete board; validate imports before writing; no synthetic seed data. |
| Static view | No writable API | Load checked-in JSON, disable writes, and show the command to start the server. |
| Confirmation | Delete, import, discard, or edit-label action | Accessible in-page dialog with Cancel/Continue; preserve the initiating revision while the dialog is open. |
| Public Phase 1 route | GitHub Pages URL | Loads the shared standalone assets and repository JSON; previous workflow workshop remains accessible through the header link. |
