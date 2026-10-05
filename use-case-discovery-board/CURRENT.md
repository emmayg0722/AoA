# Current

- Focus: Create/Join projects around the original discovery board, with participant names and GitHub-backed saves.
- Completed: project chooser/list/invite links, isolated full boards and drafts, storage acknowledgment, durable member metadata, server-only GitHub Contents API commits, SHA-conflict recovery, and container startup.
- Verification: 17 tests pass. Two local browser users exchanged edits and names; new projects were empty with cleared fields/undo. Restart retained project data. A disconnected edit survived browser reload and rejoin. Outages showed a failed-save message and retained browser work. Test data is outside the repository.
- Public baseline: original page loads, but Go live has no service; `/sync/state?session=default` returns HTTP 404. No public collaboration or live GitHub save has been accepted.
- Publication: PR #52 merged as `f2e543c0ba85f2e10c3da3b6731230774941c3a3`; Public HTTP and browser checks confirm Create/Join, the unavailable-service message, and access to the original workshop. No JavaScript errors were reported. Unrelated homepage edits and user data are excluded.
- Required deployment inputs: HTTPS hosting destination and server-side GitHub Contents write credential. No AoA-linked Vercel project was found. The user has been asked for hosting context; `config.json` stays empty until a real URL is available.
- Preserve: original workshop, old browser key, legacy session JSON, and the user's earlier `test` card.
- Hosting preparation: project commits use `codex/discovery-data` so data writes do not rebuild the site.
- Storage preparation: PR #53 merged as `3ad29ca6200ae509d9b42d811069491a4bca3d87`; data branch created and storage notice includes its branch/path. Invalid remote data is rejected without advancing the write SHA.
- Live acceptance found cached project JavaScript after publication; the entry now versions that asset so normal reloads receive the fixed connection warning.
