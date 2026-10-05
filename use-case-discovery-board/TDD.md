# Technical design

- UI: original self-contained workshop plus a project entry screen. Every project has a server-generated ID; browser drafts use a project-specific storage key. Existing offline browser data retains its original key.
- API: info/configuration, list/create projects, join an existing project, and the original node/edge/field/checklist/whole-document live operations. A missing project is never silently created by Join.
- Metadata: project ID/name, created/updated timestamps, creator display name, member display names, and complete board document. Display names are labels, not authenticated identities.
- Local persistence: existing atomic `data/sessions.json` file; project records coexist with legacy sessions.
- GitHub persistence: server-only token, configured repository/branch/path, Contents API reads and SHA-checked commits. The authoritative save completes before acknowledgment and live broadcast; local mirrors are secondary in GitHub mode.
- Concurrency: one relay process serializes writes. A remote SHA conflict never overwrites newer repository data; the session refreshes and client operations retry against the current document. GitHub failures remain visible and preserve pending browser work.
- Hosting: persistent Python HTTP service behind HTTPS with explicit allowed origin and access code. The public Pages frontend reads `config.json` for the live service URL. No credentials enter frontend configuration or exports.
- Availability: the project screen checks the service and shows an explicit unavailable state if it is missing. It never claims an offline browser draft is committed on GitHub.
- Publication: `publish-entry.py` generates the established Phase 1 entry and its public configuration from this standalone folder.
