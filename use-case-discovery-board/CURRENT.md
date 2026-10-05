# Current

- Focus: Create/Join projects around the original discovery board, with participant names and GitHub-backed saves.
- Completed: project chooser/list/invite links, isolated full boards and drafts, storage acknowledgment, durable member metadata, server-only GitHub Contents API commits, SHA-conflict recovery, and container startup.
- Verification: 16 tests pass. Two local browser users exchanged edits and names; new projects were empty with cleared fields/undo. Restart retained project data. A disconnected edit survived browser reload and rejoin. Outages showed a failed-save message and retained browser work. Test data is outside the repository.
- Public baseline: original page loads, but Go live has no service; `/sync/state?session=default` returns HTTP 404. No public collaboration or live GitHub save has been accepted.
- Publication: preparing a focused PR for the established Pages URL; unrelated homepage edits and user data are excluded.
- Required deployment inputs: HTTPS hosting destination and server-side GitHub Contents write credential. No AoA-linked Vercel project was found. The user has been asked for hosting context; `config.json` stays empty until a real URL is available.
- Preserve: original workshop, old browser key, legacy session JSON, and the user's earlier `test` card.
