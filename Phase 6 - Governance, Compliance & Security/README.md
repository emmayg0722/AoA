# Phase 6 — Governance, Compliance & Security

Governance runs alongside every other phase in a real engagement, but this
phase's tools are where it gets formalized: who oversees the AI system, how it's
checked against relevant regulatory frameworks, whether it treats people fairly,
and what could go wrong and how it's mitigated.

| Tool | What it does |
|------|--------------|
| [`ai-governance-framework/`](ai-governance-framework/) | SOP + intake (governance committee structure, AI usage policy, model lifecycle management, human-in-the-loop checkpoints), auto-generating an AI governance framework document. |
| [`compliance-assessment/`](compliance-assessment/) | SOP + intake plus a scorable gap-analysis matrix (requirement, framework, status, notes), auto-generating a compliance gap analysis report. Pre-seeded with 11 requirement rows spanning EU AI Act, NIST AI RMF, and ISO/IEC 42001. |
| [`responsible-ai/`](responsible-ai/) | SOP + intake (transparency/explainability, privacy protection) plus a bias/fairness audit matrix (dimension, method, finding, status), auto-generating a bias audit report. |
| [`risk-management/`](risk-management/) | SOP plus a scored risk register (likelihood × impact computed live into a Low/Medium/High/Critical severity, mitigation, owner) with a canvas heatmap, auto-generating a risk assessment report. |

All four tools follow the toolkit-wide pattern: a checkable SOP checklist, an
autosaved client intake, a live document preview, HTML/Markdown export, a
"🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting" prompt
generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work.

> **Not legal advice.** `compliance-assessment/` carries an explicit disclaimer:
> AI regulation (EU AI Act, NIST AI RMF, ISO/IEC 42001, regional laws) is still
> evolving. This tool structures the assessment but applicability and
> obligations should be verified with qualified counsel.
