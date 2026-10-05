# Use case discovery board

A standalone workshop board for adding, arranging, connecting, and reviewing AI use cases. All durable board data is saved in this folder's `data/board.json`.

Published entry: [Phase 1 discovery board](https://emmayg0722.github.io/AoA/Phase%201%20-%20Discovery%20%26%20Assessment/use-case-discovery-board/). The previous workflow workshop is retained through the header link. GitHub Pages shows the repository snapshot read-only; the server below enables edits and live updates.

## Run

Requires Node.js 22 or newer. No dependency installation or build step is needed.

```sh
cd use-case-discovery-board
npm start
```

Open **http://127.0.0.1:4317**. To choose another port: `PORT=4318 npm start`.

## Use

- Add a use case or note, enter its title and context, and select **Save card**.
- Drag saved cards to arrange them. The card position fields provide a keyboard alternative.
- Select a saved card and use **Connect to** to add a labeled, directed connection.
- Set an owner, review status, and optional ROI, feasibility, and impact scores. No scores are filled in automatically.
- Search the card list, pan the canvas, or use **Fit board**.
- **Export JSON** downloads the complete saved board. **Import JSON** accepts a board export or the existing prioritization tool's JSON export. Board imports replace after confirmation; prioritization imports append and preserve the entire source payload.

## Data and Git

| Data | Location |
| --- | --- |
| Board name, saved revision, timestamp | `data/board.json` |
| Cards, notes, owners, statuses, and scores | `data/board.json` → `nodes` |
| Card positions | `data/board.json` → `nodes` → `x`, `y` |
| Directed connections and labels | `data/board.json` → `edges` |
| Original prioritization import payloads | `data/board.json` → `imports` |

Changes are written atomically before success is shown. They survive reloads and server restarts and appear in `git diff`. Git commits and pushes remain explicit actions; the server never commits or pushes. Pan, zoom, search, and unsaved drafts are session-only UI state. Export contains saved data, so save a draft before exporting it.

The board was initialized empty; its checked-in JSON contains the user's saved content at publication time. No existing browser data is silently imported.

## Live collaboration

Open the same server in two browser windows: saved edits appear in both through server-sent events. Concurrent stale edits are rejected instead of overwriting a newer graph. Unsaved card drafts are retained when another browser edits the card; use **Review saved card** to resolve the conflict.

For participants on a trusted private network:

```sh
HOST=0.0.0.0 npm start
```

Share `http://<this-computer-private-IP>:4317`. All participants edit the same repo file on the server computer. This mode permits anyone who can reach that server to edit the board; use it only on a trusted network. The default binds only to this computer.

People on different networks need a hosted server with persistent storage, HTTPS, and authentication. Run one writer process for this JSON file. Cloud provisioning and public access control are outside this implementation.

GitHub Pages serves the checked-in board as a **read-only snapshot**. It cannot save files back to this repository or provide live edits. Private workshop data should only be committed when its repository visibility is appropriate.

## Verify

```sh
npm test
```

Tests use temporary JSON files, never the real board. They cover durable saves, restart readback, simultaneous writes, live events, invalid input, origin checks, and deletion of incident connections.
