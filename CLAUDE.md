# CLAUDE.md

Guidance for AI assistants (Claude Code and others) working in this repository.

## What this is

**AoA — AI Architect Toolkit.** A working portfolio of tools and deliverables for
AI-architecture *consulting engagements*, organized by delivery phase. It is
published as a static site via **GitHub Pages** at
https://emmayg0722.github.io/AoA/ (see `.nojekyll` — Jekyll processing is
disabled so folders/files are served as-is).

This is **not** a conventional application. There is no root build system, no root
package manager, and no server. Almost everything is a **self-contained static
HTML file** that runs entirely in the browser. The one exception is an optional
Python/Streamlit implementation of the maturity assessment (see below).

The overarching goal: mirror how an AI architect actually moves a client from
discovery to production, one phase at a time. The canonical reference for the
phases and deliverables is `AI-Architect-Consulting-Work-Research.md` — consult it
when adding new phases or tools so terminology stays consistent.

## Repository layout

```
.
├── index.html                    # Portfolio hub — links to every phase's tools, plus a
│                                  # cross-tool "engagement dashboard" (TOOL_REGISTRY)
├── engagement-report.html        # Master engagement report — reads every tool's saved
│                                  # localStorage state in this browser and assembles one
│                                  # combined document (REGISTRY); supports export/import
│                                  # of a full engagement as one JSON file
├── og-image.png                  # Social/link preview image
├── .nojekyll                     # Serve files as-is on GitHub Pages (do not delete)
├── README.md                     # Human-facing overview (kept in sync with actual tools)
├── AI-Architect-Consulting-Work-Research.md   # Phase 1–10 reference this toolkit follows
├── .claude/agents/               # Claude Code agents (MUST live here to be loadable)
│   ├── dra-5c.md                 # Data Readiness Assessment (5C) orchestrating agent
│   └── use-case-evaluator.md     # Use-case evaluation mentor (scores against Phase 1/4 rubrics)
├── skills/                       # Portable agent skills — SKILL.md files, not browser tools
│   ├── index.html                # Skills library + per-agent install guide (EN/DA/SV)
│   ├── install.py                # Cross-platform installer (Claude/Codex/Cursor, stdlib only)
│   ├── business-problem-sharpener/      # SKILL.md + references/taxonomy.md
│   ├── eval-harness-designer/           # SKILL.md + scripts/eval_report.py + references/
│   ├── architecture-tradeoff-analyst/   # SKILL.md + references/common-decisions.md
│   ├── architecture-red-team/           # SKILL.md + references/attack-axes.md
│   ├── context-architecture-designer/   # SKILL.md + scripts/context_budget.py + references/
│   └── roi-scenario-model/       # SKILL.md + scripts/roi_model.py + references/
├── Phase 1 - Discovery & Assessment/    # ai-maturity-assessment, data-readiness-assessment-5c,
│                                        # infrastructure-audit, organizational-readiness,
│                                        # use-case-prioritization, sample-data/
├── Phase 2 - Strategy & Roadmap/        # ai-strategy-planning, business-case-development,
│                                        # organizational-roadmap, technology-roadmap
├── Phase 3 - Architecture Design/       # Design Layers (architecture-builder.html + an
│                                        # 18-layer markdown reference), architecture-blueprint,
│                                        # architecture-decision-records, nfr-spec,
│                                        # security-architecture, tech-stack-selection-report
├── Phase 4 - PoC & Pilot/               # evaluation-godecision, pilot-planning, poc-planning
├── Phase 5 - Implementation & Delivery/ # deployment-golive, implementation-management,
│                                        # quality-assurance, system-integration,
│                                        # technical-documentation
├── Phase 6 - Governance, Compliance & Security/  # ai-governance-framework,
│                                                   # compliance-assessment, responsible-ai,
│                                                   # risk-management
├── Phase 7 - MLOps & Operations/        # mlops-platform-design, model-monitoring,
│                                        # retraining-strategy, operations-runbook,
│                                        # cost-optimization
├── Phase 8 - Change Management & Enablement/     # change-management-plan,
│                                                 # training-curriculum, ai-coe-design,
│                                                 # knowledge-transfer
├── Phase 9 - Vendor Evaluation & Technology Selection/  # rfp-builder,
│                                                        # vendor-evaluation-matrix,
│                                                        # build-vs-buy, platform-shortlist
└── Phase 10 - ROI Analysis & Cost Optimization/  # roi-analysis, tco-analysis,
                                                  # value-tracking
```

The hub presents each phase as a **stage**, not a bucket of tools: a `.stage`
block under every `phase-head` states what you decide there, what you produce,
the stack decisions it forces (phases 3, 4 and 7), and the gate to clear before
the next stage is worth starting. Below the skills section sits a **Reference
Architecture** section rendered from the `LAYERS` array in `index.html` — the 18
capability layers lifted out of `Phase 3 - Architecture Design/Design Layers/`
with the tools each is built with, so the stack vocabulary (LangGraph, MCP,
Ragas, Lakera, Helicone…) is visible on the hub instead of three levels down.
Both sections are `is-aux`, so they stay out of the numbered path and out of the
"43 tools / 10 phases" counts; layer rows are `a.layer`, which the visibility
pass counts alongside `a.card`.

Stage `Stack` lines carry `<code>` markup, so they use `data-i18n-html` rather
than `data-i18n` — `applyI18n` writes `textContent` for the former and
`innerHTML` only for the latter, keeping the safe path the default.

**All 10 phases above are fully built** — every subfolder listed is a real, working tool,
not a placeholder, and the delivery lifecycle this toolkit follows is now complete end to
end (43 stateful tools). Almost every tool folder is `index.html`; the two
exceptions are `data-readiness-assessment-5c/` (`console.html` + `profiler.html`) and
`Design Layers/` (`architecture-builder.html`) — the hub's cards link to those files
directly. **Folder names contain spaces and `&`** (e.g. `Phase 1 - Discovery & Assessment`)
— always quote paths in shell commands and URL-encode them in HTML links
(`Phase%201%20-%20Discovery%20%26%20Assessment/…`).

## Core conventions

### 1. Structure by phase, then by deliverable
Each consulting phase gets a top-level `Phase N - <Name>/` folder. Within it, each
tool/deliverable gets its own subfolder. New assets follow this same pattern. When
you add a user-facing tool, **also add a card for it to the root `index.html`** so
it's reachable from the hub.

### 2. Client-side only — privacy is a hard requirement
All assessment tools run **fully in the browser; no data leaves the machine** and
there are no backend/API calls. This is a load-bearing selling point, not an
accident. In particular the DRA-5C `profiler.html` processes raw client data
locally and emits only non-sensitive *aggregate summaries*. **Never** introduce a
step that uploads, POSTs, or otherwise transmits client data, and never route raw
data through an LLM. If you add a tool that touches client data, keep the
processing in-browser.

### 3. Only synthetic data in the repo
This repo backs a **public** site. Only fake/demo data belongs in
`Phase 1 - Discovery & Assessment/sample-data/` — never real client or engagement
data. Each tool fetches its sample file same-origin at runtime and feeds it through
its normal load path (no separate "demo mode" code path). If you add a "load
sample" affordance, follow that pattern and add a row to the sample-data README.

### 4. Vanilla, self-contained front-ends
The HTML tools are plain HTML/CSS/JS with **no framework and no build step**.
Third-party libraries (e.g. charting) are loaded from a CDN when needed; app logic
lives inline in the file. Keep each tool self-contained and openable directly in a
browser. Prefer editing the single HTML file over introducing a bundler or
dependency graph.

### 5. Shared visual language
The hub and tools share a design system: navy primary `#1B1474` (dark
`#120D52`), periwinkle accents (`#DCDDF6` / `#EEEEFA`), **Fraunces** for headings
and **Inter** for body (Google Fonts). Reuse these CSS variables and the card/hero
patterns from `index.html` for new pages so the toolkit reads as one product.

### 6. Language conventions vary by asset — match what's already there
The **Python** maturity-assessment implementation (`ai-maturity-assessment/python/`) is
**English + 中文** throughout — questions, options, reports. Preserve both languages when
editing it. The **browser** tools (including the HTML `ai-maturity-assessment/index.html`)
use an **English / Dansk / Svenska** language selector instead — this is the pattern for
every HTML tool in the repo, not just the newer ones. When adding a language to an HTML
tool, add it to all three; when editing the Python impl, keep EN/中文 in sync.

## The portable agent skills

`skills/` is the one part of the toolkit that does **not** run in a browser. Each
subfolder is a `SKILL.md` (YAML frontmatter + markdown) that an agent loads and
follows, with `skills/index.html` as the library and install guide. Five exist:
`business-problem-sharpener` (Phase 1), `eval-harness-designer` (Phase 4),
`architecture-tradeoff-analyst`, `architecture-red-team` and
`context-architecture-designer` (Phase 3/5), and `roi-scenario-model` (Phase 10).

The set is spread deliberately across five verbs — **interrogate, design,
decide, critique, quantify**. Skills whose descriptions overlap compete
for the same request and mis-trigger, so keep new ones in a distinct lane.

These differ from the `.claude/agents/` subagents in one load-bearing way, and it
must be preserved if you edit them: **the agents read methodology out of this
repo's tool files; the skills carry their own.** A skill is copied out and
installed elsewhere — on Claude, Codex, Cursor — so it can never read a sibling
file here. Keep the invariants:

- **Self-contained.** No skill reads another file in this repository. Cross-
  reference toolkit phases by name where useful, never by path.
- **No agent-specific assumptions.** Frontmatter stays at `name` and
  `description`; no named tools or vendor APIs in the body.
- **Scripts are stdlib-only and optional.** `roi_model.py` imports nothing
  outside the standard library, and the skill says what to do without Python.
- **Nothing is uploaded**, same as every tool here.

`skills/install.py` copies the skills to the right place per agent and OS, and
for Codex/Cursor writes the wiring file that points at them. It inserts a block
between `<!-- ai-architect-skills:start -->` / `:end` markers so re-running is
idempotent and never clobbers a user's existing `AGENTS.md`. It lists whatever
is actually present in the destination, not just what the run touched, so
installing one skill at a time does not drop the others from the wiring. If you
add a skill, add a line to its `WHEN` map so the generated wiring describes it.

When you add a skill: create the folder under `skills/`, keep `SKILL.md` under
~500 lines with detail pushed into `references/`, then update `skills/README.md`,
`skills/index.html` (all three languages), the root `index.html` card, and this
file. The hub counts skills separately from the 43 tools — the skills card grid
carries `class="cards is-aux"` and its section heading `class="phase-head is-aux"`,
which is what keeps the "43 tools / 10 delivery phases" stats honest.

## The Claude Code agents

`.claude/agents/` holds two orchestrating subagents. Both are Read/Write/Glob/Grep only —
no code execution — and both refuse to invent methodology, instead reading it from the
tool files/docs already in the repo.

### `dra-5c`

`.claude/agents/dra-5c.md` defines a Claude Code subagent (model: sonnet; tools:
Read, Write, Glob, Grep) that orchestrates the 5C Data Readiness Assessment. It
runs a four-step workflow (interviews → doc review → browser-local data spot-check
→ validation plan + scorecard) and **reads the methodology and templates** in
`Phase 1 - Discovery & Assessment/data-readiness-assessment-5c/` rather than
inventing formats. Two invariants baked into the agent, keep them if you edit it:
- Readiness is always assessed **relative to a specific use case**.
- The agent **never ingests raw client data** — only aggregate output from
  `profiler.html`.

Claude Code requires agents to live in `.claude/agents/`; don't move it.

### `use-case-evaluator`

`.claude/agents/use-case-evaluator.md` defines a subagent (model: sonnet; tools:
Read, Write, Glob, Grep) that interviews the architect about a proposed client use case
and scores it against rubrics that already exist in this repo — the ROI/Feasibility/
Impact matrix in `use-case-prioritization/index.html`, the technical/user-acceptance/
business-impact criteria in `evaluation-godecision/index.html`, and a DRA-5C scorecard if
one exists for the engagement — rather than inventing new criteria. It ends in a Pursue /
Pursue-with-conditions / Don't-pursue verdict plus paste-ready JSON matching those two
tools' localStorage shapes. Meant to double as both a learning tool (it explains its
reasoning) and a fast pre-check before running the full client-facing tools.

## The Python maturity-assessment implementation

`Phase 1 - Discovery & Assessment/ai-maturity-assessment/python/` is the only part
with a real toolchain. It's a Streamlit web app plus a CLI, sharing an
`assessment/` package (`model`, `questions`, `scoring`, `engine`, `report`).

```bash
cd "Phase 1 - Discovery & Assessment/ai-maturity-assessment/python"
pip install -r requirements.txt        # streamlit, pandas

streamlit run app.py                   # web app on :8501
python main.py                         # interactive CLI assessment
python main.py demo                    # generate a demo report
python main.py questions --format json # export the question bank
python main.py batch answers.json --company "Acme" --industry "Finance"
```

Generated reports/data land in `output/` (gitignored, along with `__pycache__/`).
There is no test suite; validate changes by running the CLI/web app. The
standalone `index.html` in the parent folder is the browser version of the same
assessment and is what the hub links to.

## Working in this repo

- **No build/lint/test at the repo root.** For HTML tools, verify by opening the
  file in a browser (or a static server: `python3 -m http.server` from the repo
  root, then browse to the phase path). For the Python tool, run it as above.
- **Git workflow:** work happens on feature branches merged via PR. Commit
  messages are short and imperative and reference the PR number, e.g.
  `Add interactive Architecture Builder: comparison table + lego-style selector (#18)`.
  Match that style.
- **When you add a tool:** create it under the right `Phase N - …/` folder, keep it
  self-contained and client-side, add a card to `index.html`, and update the
  relevant README(s). If it consumes sample data, add synthetic data under
  `sample-data/` and document it there.
- **Keep docs in sync.** READMEs and `methodology.md` describe behavior users rely
  on; update them alongside code changes.
