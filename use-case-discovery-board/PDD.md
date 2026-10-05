# Product design

- Users: workshop participants collaborating on use-case discovery projects.
- Entry: opening the discovery card presents Create project or Join project, then a required display name.
- Scope: retain the original board and add isolated projects, an existing-project list, share links, named participants, and explicit storage disclosure before joining.
- Storage: configured production service commits complete project metadata and board content into the selected GitHub repository; local development clearly reports local-file storage.
- Success: create a project, join from another browser, see shared edits and names, reload/restart without data loss, and verify GitHub commits when production credentials are configured.
- Non-goals: redesigning the original workshop, invented project records, verified user accounts, or silently provisioning a hosting account.

- Confirmed hosting constraint: GitHub Pages and GitHub repository only. The public board connects directly to GitHub; participants need repository write access as well as a display name. Public repository data is disclosed before entry. Tokens stay in memory for the current page session.
