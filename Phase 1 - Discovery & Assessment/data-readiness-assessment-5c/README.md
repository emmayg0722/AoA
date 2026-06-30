# Data Readiness Assessment (5C)

Phase 1 (Discovery & Assessment) asset. Judges whether a client's data is ready for
a **specific** AI use case, scored across five dimensions: **Context, Clarity,
Coverage, Credibility, Capacity**.

## What's here

| File | Purpose |
|------|---------|
| `methodology.md` | The 5C method — what each C means, how each is actually assessed, scoring scale, privacy posture. |
| `profiler.html` | **Browser-local data profiler.** Drop in a CSV/JSON sample; it computes fill rate, duplicates, type consistency, distributions, and freshness entirely in-browser and emits an aggregate summary. **Raw data never leaves the machine.** |
| `templates/` | Fill-in markdown for each deliverable: interview guide, document-review checklist, validation plan, scorecard. |

The orchestrating agent lives at `.claude/agents/dra-5c.md` (Claude Code requires
agents in `.claude/agents/`); it reads this folder's methodology and templates.

## How the pieces fit

1. Run the **`dra-5c` agent** with a client's AI use-case plan.
2. It generates the **interview guide** (Step A) and **doc-review checklist** (Step B).
3. The architect runs **`profiler.html`** on a representative data sample and pastes
   the aggregate summary back into the agent (Step C — Coverage & Credibility).
4. The agent produces the **validation plan** and the filled **5C scorecard** (Step D).

## Why a separate browser tool for the data step

The generative steps (interviews, checklists, validation plans) are an LLM's
strength. But the actual-data spot-check must respect that **raw client data cannot
leave their environment** — so it runs fully client-side in `profiler.html`, and only
non-sensitive aggregates flow back to the agent.
