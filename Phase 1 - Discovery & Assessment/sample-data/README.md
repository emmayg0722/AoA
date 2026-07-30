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

## `engagement-nordkap/` — one sample engagement across all 40 tools

One consistent **fictional** engagement — *Nordkap Insurance*, real-time claims
fraud detection at FNOL — with one JSON file per deliverable tool
(`<tool-folder>.json`), each matching that tool's exact localStorage shape.
The Phase 7 files (`mlops-platform-design`, `model-monitoring`,
`retraining-strategy`, `operations-runbook`, `cost-optimization`) continue the
same engagement into production operations, so the monitoring thresholds,
retraining triggers, and incident playbooks all refer back to the same fraud
model the earlier phases scoped and built.

Phases 8–10 carry it through to handover and measurement:

| Phase | Files | How they continue the story |
|-------|-------|-----------------------------|
| 8 — Change Management & Enablement | `change-management-plan`, `training-curriculum`, `ai-coe-design`, `knowledge-transfer` | The claims analysts whose judgement the model now ranks are the stakeholder group with the sharpest impact, and the training tracks and CoE roles are sized against the same team the Phase 7 runbook puts on call. |
| 9 — Vendor Evaluation & Technology Selection | `rfp-builder`, `vendor-evaluation-matrix`, `build-vs-buy`, `platform-shortlist` | The vendors are scored on Nordkap's own imbalanced Danish-language claims history, and the deal-breakers (EU data residency, processor terms) trace back to the Phase 6 compliance assessment. |
| 10 — ROI Analysis & Cost Optimization | `roi-analysis`, `tco-analysis`, `value-tracking` | The ROI model uses the same fraud-caught-per-1000-claims measure the Phase 4 go/no-go set and Phase 7 monitors, states its confounders (a concurrent claims-process change), and leaves the unverified reinsurance benefit excluded rather than assumed. |

Every file carries a `sopDone` array, so "Load sample" restores each tool's SOP
checklist alongside its content. The state tracks how far Nordkap has actually
got: the phases it has passed through read as complete, while the Phase 6
governance tools and the Phase 7–10 operational ones are deliberately *partly*
ticked — a live engagement's checklist is rarely all-ticked, and recurring steps
(a fairness re-audit, a risk-register review) are never "done" once.
Every tool's **"🧪 Load sample"** button (in the export row) fetches its file
same-origin and restores it through the tool's normal load path, after a
confirmation (it replaces whatever is currently saved in that tool). Load
several and the hub dashboard and master engagement report light up with a
coherent end-to-end example engagement.
