# Sample Data

> **Everything in this folder is synthetic/demo data — fake company, fake numbers,
> fake documents.** It exists so each Phase 1 tool has a one-click "load sample"
> demo. This repo backs a public GitHub Pages site, so **only synthetic data
> belongs here — never real client or engagement data.**

| File | Used by | What it is |
|------|---------|------------|
| `ai-maturity-assessment/sample-payload.json` | AI Maturity Assessment's "🧪 View sample results" link | A fake completed assessment ("Acme Corp") in the same shape `shareResults()` produces — jumps straight to a populated results page. |
| `data-readiness-assessment-5c/sample-engagement.json` | DRA-5C console's "🧪 Load sample engagement" button | A fake engagement ("Northwind Lending" — the running example used throughout this asset's docs) covering all four steps and the final scorecard. |
| `data-readiness-assessment-5c/sample-transactions.csv` | DRA-5C profiler's "🧪 Load sample data" button | A 20-row synthetic dataset with intentional imperfections (nulls, one duplicate row, a wide date span) so the profiler demo shows a non-trivial report. |

Each tool fetches its sample file from this folder at runtime (same-origin, no
external network call) and feeds it through the tool's normal loading/restore
path — there is no separate "demo mode" code path to maintain.
