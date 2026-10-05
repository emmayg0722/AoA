# Current

- Focus: toolkit-wide client projects, phase navigation, and GitHub folder storage around the existing tools.
- Confirmed: GitHub-only hosting; preserve original tool pages and browser drafts.
- Source: current published main in an isolated checkout; primary checkout has unrelated homepage edits that must be preserved.
- Implemented: all 45 saved tools across ten phases, atomic project folder creation/saves, scoped tool storage, shared header/report, public-storage consent, conflict review and recovery.
- Verified: 15 domain/storage/API tests and 26 original board tests pass. Browser checks opened all 45 tools and verified Phase 1/2/10 saves, report/header scoping, second-client isolation, failed-save recovery, explicit draft import, conflict resolution and two-browser collaboration. Credentials stay out of browser stores.
- Fixed from browser evidence: preserve coherent open-frame snapshots during SOP double-saves; materialized omitted blank fields cannot overwrite newly populated teammate fields.
- Next: prepare the empty GitHub project data branch, publish the focused workspace change, and verify the actual Pages route and public repository connection.
- Live writes require each participant to enter their own GitHub credential; no managed connector credential is copied to the app.
