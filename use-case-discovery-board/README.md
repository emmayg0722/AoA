# Use Case Discovery Board

The original workshop interface is retained: workflow steps, pain points, systems, candidate use cases, notes, scoring, document preview, SOP, languages, merge, and exports.

## Start a shared workshop

```sh
cd use-case-discovery-board
npm start
```

Open `http://localhost:4317/use-case-discovery-board/`, enter your name and a session name, then press **Go live**. Participants using the same server and session edit one board. The first participant seeds it from their existing browser board; later participants review adopting the saved session. Browser editing remains available offline.

## Repository storage

`data/sessions.json` stores every named live session and its complete original board document. Writes are validated and atomic; the server confirms a save and publishes it only after disk persistence succeeds. Sessions and ID allocations survive a restart. Pending failed edits retry and remain in browser autosave.

`data/board.json` preserves the user's data from the superseded replacement interface. It is not silently substituted for an existing workshop. The earlier Node implementation remains available in source, but `npm start` launches the original workshop's durable Python relay.

Disk saves update the repository checkout on the **server**. They are not automatic Git commits or pushes. Commit and push the JSON when you want it in GitHub history. This repository is public; only publish content you intend to make public.

## Public GitHub Pages connection

The original board is published at its existing Phase 1 URL. GitHub Pages serves static files; shared repository writes need a separate running service. In the board's **Connection settings**, enter that service's HTTPS URL and access code, then use the same session name as other participants. The access code stays in memory and is never placed in board exports or committed configuration.

A hosted relay needs Python, one server process, a persistent checkout/disk, and HTTPS at a reverse proxy. Set `AOA_RELAY_TOKEN` through the host's secret settings and launch:

```sh
python3 relay.py --host 0.0.0.0 --port 4317 \
  --allow-origin https://emmayg0722.github.io
```

For a trusted LAN, the same command can be used with the machine's LAN address. No service has been provisioned by this change. Named-session files are excluded from the relay's static file serving; API access requires the configured access code.

## Verify and publish the entry

```sh
npm test
npm run publish-entry
```

`index.html` is the canonical original workshop. `publish-entry.py` generates the Phase 1 entry and adjusts only toolkit/sample links. The existing Phase 1 `workshop-relay.py` command delegates to this relay.
