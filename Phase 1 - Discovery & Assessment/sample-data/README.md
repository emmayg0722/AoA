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

## `engagement-nordkap/` — one sample engagement across all 24 tools

One consistent **fictional** engagement — *Nordkap Insurance*, real-time claims
fraud detection at FNOL — with one JSON file per deliverable tool
(`<tool-folder>.json`), each matching that tool's exact localStorage shape.
Every tool's **"🧪 Load sample"** button (in the export row) fetches its file
same-origin and restores it through the tool's normal load path, after a
confirmation (it replaces whatever is currently saved in that tool). Load
several and the hub dashboard and master engagement report light up with a
coherent end-to-end example engagement.
