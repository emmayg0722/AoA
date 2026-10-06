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

- 2026-10-06 focus: whole-project example loading. Sourced catalog planned for Nordkap (42 tools / ten phases), Nordvik Furniture and Grønhøj Foods (one discovery board each). Examples will work without authentication, use the original tools, and keep edits temporary.

- Implemented and checked: three example projects, honest phase/tool coverage, temporary scoped edits, original board/forms/report, reset and refresh. All 45 tools opened without runtime errors or GitHub API requests; old drafts and recovery storage remained unchanged. Adding the explicit starting-project copy before publication.

- Ready to publish: example loading/reset/report, no-login browsing, optional explicit starting-project copy, provenance and source failure retention implemented. 20 workspace tests and 26 original board tests pass. All 45 tool pages, report, temporary edits, reset/refresh, legacy-draft isolation and mobile layout passed in the browser. The isolated API fixture also verified atomic copy, updated identity headers, a clean subsequent project and unchanged source samples.
- Production acceptance for this change: publish the focused change, then verify example entry, populated original tools, report and reset on GitHub Pages. Real authenticated project-copy writes still require the participant to enter their own token.

- 2026-10-06: example projects published in PR #58, merged as 6be3472db2c24b1d3e42e3106ee71b5e1fdc9163. Pages build/deploy/report all succeeded (run 37421880144). Actual public verification loaded Nordkap, Nordvik and Grønhøj without a token; Nordkap’s original board has 20 nodes and its master report has 42 tools across ten phases. A temporary strategy edit appeared in the report and reset restored its exact source value. The copy-entry form disclosed fictional contents and still required connection; actual authenticated copying remains participant-owned. 20 workspace tests and 26 board tests pass; rendered all-tool, isolation, reset/report, source-failure and isolated copy checks passed. Live screenshot: example-projects-live.png in the task visualization directory. Source remains /private/tmp/aoa-project-workspace; primary unrelated edits preserved.

- 2026-10-06 current focus: move examples into Join existing, default the entry to that list, remove standalone connection/example cards, and defer required GitHub access to writable client-project actions. Preserve source examples, existing tools and public storage disclosure for real writes.

- Browser verification found a newly created client missing from the selector after forgetting its connection. The verified loaded manifest now supplies its list entry immediately; the next index refresh still uses GitHub. This preserves rejoin access with the deferred connection flow.

- Verified current entry: all three examples loaded from Join existing with no identity or credential, including client-index failure. The isolated browser verified modal cancellation, invalid token clearing, canceled in-flight connection, resumed create/join, saved client-state restoration, reconnect cancellation and 390px entry layout. Workspace domain/storage tests: 20 pass. Publishing the focused chooser change next; actual public verification follows deployment.

- The updated example-copy browser scenario also passed through the deferred access dialog, including source failure retention, copied identity/phase data, clean subsequent creation and source preservation.

- 2026-10-06 focus: the user confirmed GitHub-only hosting and token-free project-ID access for viewing. Implement anonymous saved-project loading, protected tool state and explicit view-only notices; retain authenticated creation/editing and examples. Verify no authentication, membership writes or recovery-journal changes during viewing.

- Implemented token-free ID/list viewing, immutable raw file loading and explicit refresh. All 45 tool frames and report passed the isolated browser checks with protected storage and unchanged membership/journals; 22 workspace tests pass. Board zoom is retained while node movement is blocked. Added an explicit editor return path so existing-project editing remains available after reload.

- Ready to publish: 22 workspace tests pass. Isolated browser checks opened all 45 view-only tools and report, blocked board-node dragging while retaining zoom, refreshed a saved owner edit, rejected invalid/missing IDs without access prompts, preserved membership/recovery/legacy drafts, and retained examples/authenticated creation and explicit existing-editor return. No production fixture projects were written.

- 2026-10-06 completed: PR #60 merged as ff2798113efd881dbaf0de655724eaa5e4f6e4b9; Pages build/deploy/report succeeded (run 37429142025). Actual public verification opened the existing Test client project from the list and directly by ID without a token, loaded its original discovery board and master report, confirmed protected fields/hidden save controls, and refreshed saved work. No fixture client records or application writes were sent to production. Twenty-two workspace tests and isolated all-45-tool, report/refresh, board zoom/drag protection, draft/membership isolation, invalid-ID, example/create and returning-editor checks passed. Live proof: token-free-project-viewing-live.png in the task visualization directory.
