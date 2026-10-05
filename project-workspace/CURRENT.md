# Current

- Focus: toolkit-wide client projects, phase navigation, and GitHub folder storage around the existing tools.
- Confirmed: GitHub-only hosting; preserve original tool pages and browser drafts.
- Source: current published main in an isolated checkout; primary checkout has unrelated homepage edits that must be preserved.
- Implemented: all 45 saved tools across ten phases, atomic project folder creation/saves, scoped tool storage, shared header/report, public-storage consent, conflict review and recovery.
- Verified: 15 domain/storage/API tests and 26 original board tests pass. Browser checks opened all 45 tools and verified Phase 1/2/10 saves, report/header scoping, second-client isolation, failed-save recovery, explicit draft import, conflict resolution and two-browser collaboration. Credentials stay out of browser stores.
- Fixed from browser evidence: preserve coherent open-frame snapshots during SOP double-saves; materialized omitted blank fields cannot overwrite newly populated teammate fields.
- Published: PR #56 merged as a311e72cd31a4f658377c16c1160a85bef5254d0. Pages build, deploy and reporting succeeded. The live homepage opens /AoA/project-workspace/.
- Actual public verification: the workspace loaded the empty index on codex/project-data; invalid authentication was rejected, its input cleared, and project writes remained disabled. No test client records were created on GitHub.
- Remaining acceptance: a participant enters their own GitHub token on the page and performs a real authenticated project save. Implementation and isolated rendered checks are complete.
- Live writes require each participant to enter their own GitHub credential; no managed connector credential is copied to the app.
