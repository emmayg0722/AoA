# Phase 9 — Vendor Evaluation & Technology Selection

Phase 3 decided the architecture. This phase decides who and what actually
supplies it — deliberately, rather than by whoever gave the most convincing demo.

The distinction that matters here: vendor demos are run on the vendor's data, and
AI products differ from ordinary software in how far that gap can stretch. A model
that scores well on a curated benchmark can fall apart on a client's messy,
imbalanced, Danish-language claims history. So every tool in this phase pushes the
evaluation onto the client's own data and writes down the deal-breakers *before*
anyone sees a price.

| Tool | What it does |
|------|--------------|
| [`rfp-builder/`](rfp-builder/) | SOP + intake covering the requirement and scope statement, the evaluation approach and scoring model, process, timeline and vendor communication rules, and constraints, must-haves and deal-breakers, plus a weighted evaluation-criteria tracker, auto-generating an RFP/RFI document. |
| [`vendor-evaluation-matrix/`](vendor-evaluation-matrix/) | SOP + intake covering the shortlist and how it was arrived at, technical capability findings tested on the client's own data, implementation and ongoing support, and company stability, roadmap and lock-in risk, plus a per-vendor scoring matrix. |
| [`build-vs-buy/`](build-vs-buy/) | SOP + intake covering the options being compared and the horizon, cost comparison over that horizon, technical debt and maintenance burden, and strategic flexibility versus lock-in, plus a decision-factor tracker weighing each option, auto-generating a build-vs-buy analysis. |
| [`platform-shortlist/`](platform-shortlist/) | SOP + intake covering ML platform and MLOps tooling, model selection (LLM, embeddings) and the evaluation basis, data platform and vector store, and observability and evaluation tooling, plus a per-category selection tracker. |

All four tools follow the toolkit-wide pattern: a checkable SOP checklist, an
autosaved client intake, a tracker matrix, a live document preview, HTML/Markdown
export, a "🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting"
prompt generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work.

## Where this phase connects

- **Phase 3 `tech-stack-selection-report`** records what was chosen and why.
  This phase is the evidence behind it — run `platform-shortlist` and
  `vendor-evaluation-matrix` first, then let the Phase 3 report cite them rather
  than restating conclusions with no working shown.
- **Phase 3 `nfr-spec`** holds the latency, availability and throughput numbers
  that belong verbatim in the RFP. A vendor cannot be held to a requirement that
  was never written down.
- **Phase 10 `tco-analysis`** consumes this phase's pricing directly. A build-vs-buy
  case that uses different numbers from the TCO model means one of them is wrong.
- **Phase 6 `compliance-assessment`** determines which vendors are eligible at all
  — data residency and processor terms are deal-breakers, not scored criteria.
