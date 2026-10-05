# Current

- Focus: publish the repository snapshot at the requested Phase 1 GitHub Pages URL; local editing remains available at `http://127.0.0.1:4317`.
- Completed: graph UI, card and connection editing, file API, atomic JSON persistence, live event stream, import/export, and toolkit links implemented.
- Blockers: none for local use; internet collaboration requires a hosted, persistent server and access control.
- Verification: all eight server tests pass; browser creation, scores, connections and label editing, dragging, reload, two-tab live synchronization, draft conflict protection, and in-page confirmation cancel/continue verified.
- Layout: rendered desktop at 1280 px and stacked layout at 815 px without document overflow; browser viewport overrides did not provide a separate phone-width render.
- Static mode: repository JSON loads read-only and write controls are disabled when no API is present.
- Cleanup: temporary verification cards and their connection removed; the user's subsequent card named `test` is preserved in repository data.
- Limitation: browser download automation timed out, so the export download was not independently read back; source wiring and complete API payload were inspected. Import payload handling is covered by the server tests.
- Next: add real use cases; host a persistent authenticated server if participants need access from different networks.
- Publication preparation: Phase 1 entry added, asset/data URLs made independent of the entry path, and existing remote workshop preserved as linked `workshop.html` with original documentation. Release is based on current remote main; unrelated local homepage work is excluded.
- Release validation: eight tests pass; the exact Phase 1 route was rendered from a static repo preview, loading the user's saved card, disabling writes, and linking the preserved workshop without console errors.
