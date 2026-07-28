# Phase 5 — Implementation & Delivery

With a Go decision from Phase 4, Phase 5 covers the actual build-out: managing
delivery, integrating with existing systems, testing, deploying, and documenting
it all so the solution is operable by someone other than the person who built it.

| Tool | What it does |
|------|--------------|
| [`implementation-management/`](implementation-management/) | SOP + intake (delivery team structure, agile cadence, technical decision log) plus a sprint/milestone tracker, auto-generating an implementation management plan. |
| [`system-integration/`](system-integration/) | SOP + intake (API design, data migration, legacy-system constraints) plus an integration-points tracker (system, method, data flow, status), auto-generating a system integration plan. |
| [`quality-assurance/`](quality-assurance/) | SOP + intake plus a test-coverage tracker spanning model performance, integration, load, and security testing, auto-generating a QA test plan. |
| [`deployment-golive/`](deployment-golive/) | SOP + intake (deployment strategy, production configuration, rollback plan, hypercare support) plus a rollout-wave tracker, auto-generating a go-live runbook. |
| [`technical-documentation/`](technical-documentation/) | SOP plus a documentation-inventory tracker pre-seeded with the minimum viable set (API docs, deployment manual, operations runbook, test report), auto-generating a documentation index. |

All five tools follow the toolkit-wide pattern: a checkable SOP checklist, an
autosaved client intake, a live document preview, HTML/Markdown export, a
"🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting" prompt
generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work.
