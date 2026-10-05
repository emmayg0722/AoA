# Use Case Discovery Board

The original discovery workshop remains the primary page at this URL, with its canvas, five block types, intake, SOP, scoring, languages, document preview, merge, and exports.

Create/Join projects wrap the original board, with participant display names, storage acknowledgment, and invite links. The published workflow runs entirely on GitHub: each participant connects their own repository token; boards and member names are committed on `codex/discovery-data` and saved edits are checked every 12 seconds. See the standalone [`use-case-discovery-board/`](../../use-case-discovery-board/) [README](../../use-case-discovery-board/README.md) for access, token permissions, and public storage. Offline browser autosave retains the original `aoa_usecase_board_v1` key. The Python relay remains available for optional local use.

`workshop-relay.py` is a compatibility launcher. `workshop.html` preserves the unmodified original source; `WORKSHOP.md` retains its earlier documentation, including the superseded in-memory relay behavior.
