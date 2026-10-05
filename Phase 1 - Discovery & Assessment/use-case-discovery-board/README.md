# Use Case Discovery Board

The original discovery workshop remains the primary page at this URL, with its canvas, five block types, intake, SOP, scoring, languages, document preview, merge, and exports.

Create/Join projects wrap the original board, with participant display names, storage acknowledgment, invite links, and an explicit service connection state. Shared projects use a durable relay and repository JSON in the standalone [`use-case-discovery-board/`](../../use-case-discovery-board/) folder. See its [README](../../use-case-discovery-board/README.md) for setup, storage, and public HTTPS connection settings. Offline browser autosave retains the original `aoa_usecase_board_v1` key.

`workshop-relay.py` is a compatibility launcher. `workshop.html` preserves the unmodified original source; `WORKSHOP.md` retains its earlier documentation, including the superseded in-memory relay behavior.
