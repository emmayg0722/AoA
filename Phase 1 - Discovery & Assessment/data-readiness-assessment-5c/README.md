# Data Readiness Assessment (5C)

Phase 1 (Discovery & Assessment) asset. Judges whether a client's data is ready for
a **specific** AI use case, scored across five dimensions: **Context, Clarity,
Coverage, Credibility, Capacity**.

## What's here

| File | Purpose |
|------|---------|
| `console.html` | **The front door.** A workspace that walks all four steps end-to-end: it generates a paste-ready prompt for the `dra-5c` agent at each step, takes the agent's output back, embeds the profiler for Step C, and assembles the final 5C report. No API calls; work autosaves locally and exports as a file. |
| `profiler.html` | **Browser-local data profiler.** Drop in a CSV/JSON sample; it computes fill rate, duplicates, type consistency, distributions, and freshness entirely in-browser and emits an aggregate summary. **Raw data never leaves the machine.** |
| `methodology.md` | The 5C method — what each C means, how each is actually assessed, scoring scale, privacy posture. |
| `templates/` | Fill-in markdown for each deliverable: interview guide, document-review checklist, validation plan, scorecard. |

The orchestrating agent lives at `.claude/agents/dra-5c.md` (Claude Code requires
agents in `.claude/agents/`); it reads this folder's methodology and templates.

## How the pieces fit

Open **`console.html`** and work top to bottom. For each step it gives you a
tailored prompt to run through the `dra-5c` agent (or any Claude), and you paste the
result back:

1. **Setup** — enter the client and the AI use case (everything is judged against it).
2. **Step A / B** — generate prompts for the interview guide and doc-review checklist.
3. **Step C** — run **`profiler.html`** on a sample, paste its aggregate summary in, generate the Coverage/Credibility interpretation.
4. **Step D** — generate the validation plan + 5C scorecard, set the final scores, and export the combined report.

You can also drive the `dra-5c` agent directly in Claude Code without the console —
the console is just a human-friendly front-end that keeps everything in one place.

## Why a separate browser tool for the data step

The generative steps (interviews, checklists, validation plans) are an LLM's
strength. But the actual-data spot-check must respect that **raw client data cannot
leave their environment** — so it runs fully client-side in `profiler.html`, and only
non-sensitive aggregates flow back to the agent.

## Integrations

- `m365-copilot-integration.md` — feasibility & architecture comparison for leveraging
  Microsoft 365 Copilot / Graph to accelerate data-gathering. Recommends a staged path;
  the local profiler stays in every option.
- `copilot-prompt-pack.md` + **console buttons** — Option A (built): on Steps A & B the
  console's "🤖 Generate M365 Copilot prompts" button produces tailored prompts to run in
  the client's *own* Copilot; paste the findings into "Copilot findings" and they fold into
  the dra-5c prompt as source evidence. Zero infrastructure; raw data stays in the client tenant.

## Try it without a real engagement

Both `console.html` ("🧪 Load sample engagement") and `profiler.html` ("🧪 Load sample data")
have a one-click demo using the fake "Northwind Lending" engagement in
`../sample-data/data-readiness-assessment-5c/` — see that folder's README for what's synthetic
vs. what real client data should never be committed here.
