# Phase 4 — PoC & Pilot

With an architecture designed in Phase 3, Phase 4 de-risks it in the smallest
possible increments before committing to production: a timeboxed proof-of-concept
answering one narrow technical question, then a controlled real-world pilot, then
a scored Go/No-Go decision on whether to scale. Each step exists to fail cheaply if
the use case doesn't hold up.

| Tool | What it does |
|------|--------------|
| [`poc-planning/`](poc-planning/) | SOP + intake scoped to a narrow, timeboxed proof-of-concept question (in scope, explicitly out of scope, success criteria, demo environment), auto-generating a technical feasibility report with a Proceed to Pilot / Iterate / Stop recommendation. |
| [`pilot-planning/`](pilot-planning/) | SOP + intake (pilot scope, objective, integration touchpoints, rollback plan) plus a checkpoint-timeline builder, auto-generating a pilot plan document for a controlled real-world deployment. |
| [`evaluation-godecision/`](evaluation-godecision/) | SOP plus a scorable evaluation matrix (criterion, evidence, 1-5 score) that computes a live overall score and a Go / Conditional Go / No-Go recommendation from task-specific evidence, auto-generating a decision report. |

All three tools follow the toolkit-wide pattern: a checkable SOP checklist, an
autosaved client intake, a live document preview, HTML/Markdown export, a
"🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting" prompt
generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work. The
`.claude/agents/use-case-evaluator.md` agent is a useful fast pre-check before
running `evaluation-godecision/` end-to-end on a real client case.
