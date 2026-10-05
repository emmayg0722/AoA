# Function design

| Feature | Behavior |
| --- | --- |
| Existing workshop | Preserve typed blocks, auto-connections, inspector, workflow preview, undo/redo, fit/zoom, checklist, scoring, languages, sample loading, merge, and exports. |
| Go live | First participant seeds the session from their existing board; later participants adopt the saved session after reviewing replacement. |
| Repository save | Validate and atomically write the complete session document before reporting success; failed saves leave the authoritative board intact. |
| Live edits | Broadcast existing block, connection, intake, checklist, and whole-document operations; preserve typing/drag behavior. |
| Restart | Reload all named sessions and allocation counters from disk; a returning participant rejoins the saved session. |
| Connection settings | Optional server URL and access code connect the same public interface to a hosted relay; access code remains in memory only. |
| Offline editing | Keep existing browser autosaves; pending live edits retry while connected and must be saved before leaving. |
