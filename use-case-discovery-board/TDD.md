# Technical design

- UI: original self-contained workshop plus a project entry screen. Every project has a server-generated ID; browser drafts use a project-specific storage key. Existing offline browser data retains its original key.
- API: info/configuration, list/create projects, join an existing project, and the original node/edge/field/checklist/whole-document live operations. A missing project is never silently created by Join.
- Metadata: project ID/name, created/updated timestamps, creator display name, member display names, and complete board document. Display names are labels, not authenticated identities.
- Local persistence: existing atomic `data/sessions.json` file; project records coexist with legacy sessions.
- GitHub persistence: server-only token, configured repository/branch/path (default data branch `codex/discovery-data`), Contents API reads and SHA-checked commits. The authoritative save completes before acknowledgment and live broadcast; local mirrors are secondary in GitHub mode.
- Concurrency: one relay process serializes writes, with at least two seconds between GitHub write attempts. A remote SHA conflict never overwrites newer repository data; the session refreshes and client operations retry against the current document. GitHub failures remain visible and preserve pending browser work.
- Hosting: persistent Python HTTP service behind HTTPS with explicit allowed origin and access code. The public Pages frontend reads `config.json` for the live service URL. No credentials enter frontend configuration or exports.
- Availability: the project screen checks the service and shows an explicit unavailable state if it is missing. It never claims an offline browser draft is committed on GitHub.
- Publication: `publish-entry.py` generates the established Phase 1 entry and its public configuration from this standalone folder.

- GitHub-only production (supersedes hosted relay requirement): a browser adapter uses the fixed GitHub REST origin and selected repository/data branch. Each participant supplies a personal repository-scoped credential; no shared credential is published. SHA-checked commits reapply individual operations after conflicts. Poll saved snapshots every 12 seconds, and batch edits for 5 seconds. Member names describe project membership, not online presence. The Python relay remains an optional local workflow.
