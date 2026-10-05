# Use Case Discovery Board

The original workshop is retained: workflow steps, pain points, systems, candidate use cases, notes, scoring, document preview, SOP, languages, merge, and exports. The entry screen offers **Create a project**, **Join an existing project**, and **Open browser-only board**.

## Try shared projects locally

```sh
cd use-case-discovery-board
npm start
```

Open `http://localhost:4317/use-case-discovery-board/`. Give the project a name, enter your display name, acknowledge the storage notice, and create it. Copy its invite link; collaborators open that link and enter their own names. Join also lists projects on the connected service. Each project has a separate board, engagement fields, checklist, browser draft, and undo history.

Names are participant labels, not authenticated accounts. An access code protects the service when hosted. All participants with that code can list and join its projects.

Local mode writes `data/sessions.json` atomically in this repository checkout. Its status says **Saved on server disk**; it does not claim a GitHub commit. `data/board.json` preserves the user's earlier replacement-board data. Browser-only mode retains the original `aoa_usecase_board_v1` draft.

## Enable automatic GitHub saves

Run one Python relay process behind HTTPS. Configure these values in the hosting service's settings:

| Setting | Value |
| --- | --- |
| `AOA_GITHUB_TOKEN` | Server-only GitHub credential with Contents read/write for the selected repository. |
| `AOA_GITHUB_REPOSITORY` | `emmayg0722/AoA` (default). |
| `AOA_GITHUB_BRANCH` | `main` (default); the credential must be allowed to write this branch. |
| `AOA_GITHUB_DATA_PATH` | `use-case-discovery-board/data/sessions.json` (default). |
| `AOA_RELAY_TOKEN` | Service access code shared with collaborators; required beyond localhost. |
| `PORT` | Host-provided listening port, or `4317`. |

Never put the GitHub credential in HTML, configuration JSON, browser storage, or the repository. Enter it directly in the host's secret settings. The service access code stays in browser memory and is excluded from invite links and board exports.

```sh
python3 relay.py --host 0.0.0.0 \
  --allow-origin https://emmayg0722.github.io
```

A Dockerfile is included for hosts accepting a container with this folder as its build context. It serves the API; GitHub Pages serves the original board UI. Without a GitHub credential, a hosted relay needs persistent disk and remains explicitly in local mode. With GitHub configured, the relay reads the repository on startup, commits changes before acknowledgment/broadcast, and uses disk only as a secondary mirror. SHA conflicts refresh repository state and preserve pending client operations for retry. Use one relay instance; concurrent instances are not supported.

Set `relayUrl` in `config.json` to the service's HTTPS URL, run `npm run publish-entry`, and publish both configuration files. Participants can also use **Connection settings** to connect an existing service. The Phase 1 URL remains:

https://emmayg0722.github.io/AoA/Phase%201%20-%20Discovery%20%26%20Assessment/use-case-discovery-board/

GitHub Pages alone cannot run this API. No live hosting target or GitHub server credential is currently configured. The public entry therefore shows a connection-required state and disables project submission until a service responds.

## Storage and recovery

Project metadata contains its ID, name, creator name, timestamps, and member display names. Each record contains the full original board document. Active presence is temporary; participant names remain in the saved metadata. GitHub mode discloses the repository and its actual visibility before entry. In the public AoA repository, anyone can read committed data and history.

Autosave and pending operations have project-specific keys; each browser tab has its own pending journal. Failed writes are not acknowledged or broadcast. Pending operations survive reload and are retried after the participant rejoins that project. Changing projects never copies a browser-only board into a new project. The browser-only board can still export JSON for an explicit import into a project.

## Verify and publish

```sh
npm test
npm run publish-entry
```

The tests cover original board persistence, concurrent edits, project isolation, missing projects, required names/storage acknowledgment, authentication/origin restrictions, restart recovery, and simulated GitHub failures/conflicts. Mocked GitHub tests validate the save contract; live GitHub acceptance still requires the hosted service and credential.

`index.html` is the canonical original workshop; `projects.js` owns the project flow. `publish-entry.py` generates the Phase 1 HTML and configuration with corrected toolkit/sample/script links. The Phase 1 `workshop-relay.py` command delegates to this relay.
