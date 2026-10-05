# Use Case Discovery Board

The original workshop is retained: workflow steps, pain points, systems, candidate use cases, notes, scoring, document preview, SOP, languages, merge, and exports. The entry screen offers **Create a project**, **Join an existing project**, and **Open browser-only board**.

## Collaborate entirely on GitHub

The published board now uses GitHub Pages and GitHub's API directly. It needs no Azure, Vercel, or separate server. The existing original board is unchanged after the project entry screen.

1. Open the published board and expand **Connection settings**.
2. Connect your own GitHub token. The repository owner can use a fine-grained token restricted to `AoA` with **Contents: read and write**. Other repository collaborators may need a classic token with `public_repo` scope because GitHub currently limits fine-grained tokens for outside/repository collaborators. Classic tokens can also access other public repositories available to their owner; give them an expiry. Never share the owner's token.
3. Enter your display name, choose Create or Join, and acknowledge the public storage notice.
4. Share the invite link with collaborators who have repository write access. Each connects their own token and enters their own display name.

The token is sent only to `https://api.github.com`, held in memory, cleared from the input after connection, and excluded from localStorage/sessionStorage, repository records, invite links, and exports. Reloading requires reconnection. **Forget GitHub token** ends the connection after saving pending edits. If a save fails, pending operations remain in the browser and the failure is visible.

Project names, member display names, full boards, fields, and checklist are committed to `use-case-discovery-board/data/sessions.json` on `codex/discovery-data`. AoA is public, so everyone can read those records and their Git history. The UI reads actual repository visibility before entry. Display names are labels; GitHub permissions authorize writes.

Edits are batched for 5 seconds, then committed using the current file SHA. A conflicting save re-reads the latest data and reapplies individual operations, preserving changes in other projects. Teammates' saved changes are checked every 12 seconds. The roster shows project members, without claiming active presence. Whole-board imports/undo replacements retain the original replacement behavior. This is suitable for a small workshop; GitHub's API limits and commit history make it unsuitable for high-volume instant collaboration.

Public projects can be listed without a token. Create/Join require a connected GitHub identity and a token that permits writes. An empty list means no projects have been committed; the application never creates demo projects automatically.

References: [GitHub Contents API](https://docs.github.com/en/rest/repos/contents), [GitHub cross-origin API support](https://docs.github.com/en/rest/using-the-rest-api/using-cors-and-jsonp-to-make-cross-origin-requests), [token permissions and collaborator limitations](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

## Optional local relay

```sh
cd use-case-discovery-board
npm start
```

Open `http://localhost:4317/use-case-discovery-board/?backend=relay` for the retained Python relay. Give the project a name, enter your display name, acknowledge the storage notice, and create it. Copy its invite link; collaborators open that link and enter their own names. Join also lists projects on the connected service. Each project has a separate board, engagement fields, checklist, browser draft, and undo history.

Names are participant labels, not authenticated accounts. An access code protects the service when hosted. All participants with that code can list and join its projects.

Local mode writes `data/sessions.json` atomically in this repository checkout. Its status says **Saved on server disk**; it does not claim a GitHub commit. `data/board.json` preserves the user's earlier replacement-board data. Browser-only mode retains the original `aoa_usecase_board_v1` draft.

## Optional server-based GitHub saves

Run one Python relay process behind HTTPS. Configure these values in the hosting service's settings:

| Setting | Value |
| --- | --- |
| `AOA_GITHUB_TOKEN` | Server-only GitHub credential with Contents read/write for the selected repository. |
| `AOA_GITHUB_REPOSITORY` | `emmayg0722/AoA` (default). |
| `AOA_GITHUB_BRANCH` | `codex/discovery-data` (default); the credential must be allowed to write this branch. |
| `AOA_GITHUB_DATA_PATH` | `use-case-discovery-board/data/sessions.json` (default). |
| `AOA_RELAY_TOKEN` | Service access code shared with collaborators; required beyond localhost. |
| `PORT` | Host-provided listening port, or `4317`. |

Never put the GitHub credential in HTML, configuration JSON, browser storage, or the repository. Enter it directly in the host's secret settings. The service access code stays in browser memory and is excluded from invite links and board exports.

```sh
python3 relay.py --host 0.0.0.0 \
  --allow-origin https://emmayg0722.github.io
```

A Dockerfile is included for hosts accepting a container with this folder as its build context. It serves the API; GitHub Pages serves the original board UI. Without a GitHub credential, a hosted relay needs persistent disk and remains explicitly in local mode. With GitHub configured, the relay reads the repository on startup, commits changes before acknowledgment/broadcast, and uses disk only as a secondary mirror. SHA conflicts refresh repository state and preserve pending client operations for retry. Use one relay instance; concurrent instances are not supported.

Project data uses a separate branch in the same repository, so board edits do not rebuild the Pages website. This data branch is created from published main; its initial session file is empty. Repository writes are serialized with at least two seconds between attempts; live changes are broadcast after the save completes.

Set `relayUrl` in `config.json` to the service's HTTPS URL, run `npm run publish-entry`, and publish both configuration files. Participants can also use **Connection settings** to connect an existing service. The Phase 1 URL remains:

https://emmayg0722.github.io/AoA/Phase%201%20-%20Discovery%20%26%20Assessment/use-case-discovery-board/

GitHub Pages cannot run this optional Python API. The default public configuration uses direct GitHub access instead, so no externally hosted relay is required.

## Storage and recovery

Project metadata contains its ID, name, creator name, timestamps, and member display names. Each record contains the full original board document. Active presence is temporary; participant names remain in the saved metadata. GitHub mode discloses the repository and its actual visibility before entry. In the public AoA repository, anyone can read committed data and history.

Autosave and pending operations have project-specific keys; each browser tab has its own pending journal. Failed writes are not acknowledged or broadcast. Pending operations survive reload and are retried after the participant rejoins that project. Changing projects never copies a browser-only board into a new project. The browser-only board can still export JSON for an explicit import into a project.

## Verify and publish

```sh
npm test
npm run publish-entry
```

The tests cover original board persistence, concurrent edits, project isolation, missing projects, required names/storage acknowledgment, authentication/origin restrictions, restart recovery, and simulated GitHub failures/conflicts. The browser adapter adds two-participant commits, conflict rebasing, Unicode data, isolation, corrupted data protection, failed/ambiguous saves, and credential boundaries. Live browser write acceptance requires the participant to connect their own credential; mocked API tests are not proof of an authenticated public save.

`index.html` is the canonical original workshop; `projects.js` owns the project flow. `publish-entry.py` generates the Phase 1 HTML and configuration with corrected toolkit/sample/script links. The Phase 1 `workshop-relay.py` command delegates to this relay.
