# Current

- Focus: restore the original discovery workshop at its existing public URL and add durable live sessions to it.
- Confirmed: the user wants the original board and all its features preserved; the replacement UI was incorrect.
- Data: preserve existing browser storage and the user's `test` card in `data/board.json`.
- Completed: original interface restored; existing live protocol now saves full sessions atomically in repository JSON.
- Verification: eight tests pass; two browser tabs synchronized all five block types, automatic connections, scores, intake fields, and checklist updates. Restart retained the session and live editing resumed.
- Publication: preparing a focused PR against current remote main, excluding unrelated homepage work.
- Hosting: awaiting the user's existing HTTPS hosting context for internet-wide shared editing. Local/network collaboration can be verified independently.
