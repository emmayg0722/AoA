# Phase 1 — Discovery & Assessment

Where an engagement starts, and where most of them are quietly decided. Before any
architecture can be drawn, four things have to be established: how mature the
client's AI practice actually is, whether their data can support the use case they
have in mind, what their infrastructure can carry, and whether the organization can
absorb the change. Then, and only then, which use case to start with.

The distinction that matters here: readiness is never absolute. Data that is
hopeless for real-time fraud scoring may be perfectly adequate for monthly churn
reporting, so every assessment in this phase is scored **relative to a specific
use case** rather than in general.

| Tool | What it does |
|------|--------------|
| [`ai-maturity-assessment/`](ai-maturity-assessment/) | A 24-question assessment across six dimensions producing a maturity level, per-dimension scores and a prioritized recommendation set. Browser version (`index.html`) plus an optional Python/Streamlit + CLI implementation in [`python/`](ai-maturity-assessment/python/) (English + 中文). |
| [`data-readiness-assessment-5c/`](data-readiness-assessment-5c/) | The 5C assessment (Context, Clarity, Coverage, Credibility, Capacity) as a two-part asset: [`console.html`](data-readiness-assessment-5c/console.html) runs the four-step workflow and scorecard, and [`profiler.html`](data-readiness-assessment-5c/profiler.html) profiles a real client CSV **entirely in the browser**, emitting only non-sensitive aggregate summaries. See its [README](data-readiness-assessment-5c/README.md) and `methodology.md`. |
| [`infrastructure-audit/`](infrastructure-audit/) | SOP + a scored rubric across compute, storage, networking, MLOps tooling and integration surface, auto-generating an infrastructure audit with a gap list. |
| [`organizational-readiness/`](organizational-readiness/) | SOP + a scored rubric across sponsorship, skills, culture, governance and change capacity, auto-generating a readiness assessment. |
| [`use-case-prioritization/`](use-case-prioritization/) | SOP + a repeatable use-case matrix scored on ROI, feasibility and impact, ranking candidates so the engagement starts on the one most likely to succeed. |
| [`sample-data/`](sample-data/) | Synthetic sample data for every tool in the toolkit, including the [Nordkap engagement](sample-data/README.md) that each tool's "🧪 Load sample" button pulls from. **Only fake data belongs here** — this repo backs a public site. |

All five assessment tools follow the toolkit-wide pattern: a checkable SOP
checklist, an autosaved client intake, a live document preview, HTML/Markdown
export, a "🧪 Load sample" button, an "Agent drafting" prompt generator, and an
English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work.

## The agents that work alongside this phase

Two Claude Code subagents in [`.claude/agents/`](../.claude/agents/) read their
methodology out of this phase's tool files rather than inventing it:

- **`dra-5c`** orchestrates the 5C assessment end to end — interviews, document
  review, a browser-local data spot-check, then a validation plan and scorecard. It
  never ingests raw client data, only `profiler.html`'s aggregate output.
- **`use-case-evaluator`** interviews you about a proposed use case and scores it
  against `use-case-prioritization`'s ROI/feasibility/impact matrix, a DRA-5C
  scorecard if one exists, and Phase 4's go/no-go criteria — ending in a
  Pursue / Pursue-with-conditions / Don't-pursue verdict.

## Where this phase connects

- **Phase 2** turns the prioritized use case into a funded plan. A business case
  built on a use case this phase scored as low-feasibility is where engagements go
  wrong before any code is written.
- **Phase 3 `nfr-spec`** inherits the constraints `infrastructure-audit` found;
  requirements the client's platform cannot meet belong in the gap list, not the
  spec.
- **Phase 8 `training-curriculum`** should address the specific gaps
  `organizational-readiness` scored, otherwise one of the two documents is
  decorative.
