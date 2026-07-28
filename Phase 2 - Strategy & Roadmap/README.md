# Phase 2 — Strategy & Roadmap

Once Phase 1 has identified and prioritized a use case, Phase 2 turns it into a
funded, sequenced plan: the strategy document that justifies the investment, the
business case that quantifies it, and the roadmaps (technology and organizational)
that sequence the work. This is the hand-off between "should we do this" and
"how do we actually build it."

| Tool | What it does |
|------|--------------|
| [`ai-strategy-planning/`](ai-strategy-planning/) | SOP + intake covering vision/mission, strategic alignment, and success metrics, plus a 3-5 year milestone-roadmap builder, auto-generating an AI strategy document. |
| [`business-case-development/`](business-case-development/) | SOP + intake with a **live ROI model** (payback period, net benefit over horizon, ROI%) that computes as you type, auto-generating a business case document with the computed figures embedded. |
| [`technology-roadmap/`](technology-roadmap/) | SOP + platform-strategy intake (cloud-first / hybrid / private / multi-cloud) and a milestone timeline with dependencies, auto-generating the technology roadmap Phase 3 architecture work designs against. |
| [`organizational-roadmap/`](organizational-roadmap/) | SOP + intake covering AI CoE design, talent acquisition/development, structure changes, and partner ecosystem, auto-generating an organizational change roadmap. |

All four tools follow the toolkit-wide pattern: a checkable SOP checklist, an
autosaved client intake, a live document preview, HTML/Markdown export, a
"🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting" prompt
generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work, and
[`sample-data/`](../Phase%201%20-%20Discovery%20%26%20Assessment/sample-data/)
for the sample engagement each tool's "Load sample" button pulls from.
