# Product design

- Users: AI architects and teammates working through an entire client engagement.
- Problem: each tool saves one browser-wide draft, so clients and projects cannot be isolated or shared reliably.
- Scope: Create/Join a client project; retain all existing tools; group work by ten phases; save project, shared client header, and tool state in GitHub folders; show durable save status and member names.
- Storage: projects/<client-project-id>/<phase>/<tool>/state.json on a data branch in AoA. The current repository is public; disclose this before sending names or work.
- Migration: review and explicitly copy old browser drafts into a selected project. Raw uploaded profiler datasets remain local; only the saved assessment/deliverable state is eligible for repository storage.
- Non-goals: redesigning tools, automatic client-data migration, anonymous repository writes, or external hosting.
