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
├── index.html                    # Portfolio hub — links to every phase's tools
├── og-image.png                  # Social/link preview image
├── .nojekyll                     # Serve files as-is on GitHub Pages (do not delete)
├── README.md                     # Human-facing overview
├── AI-Architect-Consulting-Work-Research.md   # Phase 1–10 reference this toolkit follows
├── .claude/agents/               # Claude Code agents (MUST live here to be loadable)
│   └── dra-5c.md                 # Data Readiness Assessment (5C) orchestrating agent
├── Phase 1 - Discovery & Assessment/
│   ├── ai-maturity-assessment/
│   │   ├── index.html            # Browser tool: 6-dimension maturity scoring
│   │   └── python/               # Optional Streamlit + CLI implementation
│   ├── data-readiness-assessment-5c/
│   │   ├── console.html          # Front-end that walks the 4-step 5C assessment
│   │   ├── profiler.html         # Browser-local data profiler (raw data stays local)
│   │   ├── methodology.md        # The 5C method
│   │   ├── copilot-prompt-pack.md, m365-copilot-integration.md
│   │   └── templates/            # Fill-in markdown deliverables
│   └── sample-data/              # SYNTHETIC demo data only (see its README)
└── Phase 3 - Architecture Design/
    └── Design Layers/
        ├── architecture-builder.html   # Interactive 14-layer "pick one per layer" builder
        ├── README.md                   # 18-layer agentic architecture reference
        └── layers/                     # One markdown file per layer (01…18)
```

Phases 2, 4–7 are scaffolded conceptually (listed on `index.html`) and will be
filled in over time. **Folder names contain spaces and `&`** (e.g.
`Phase 1 - Discovery & Assessment`) — always quote paths in shell commands and
URL-encode them in HTML links (`Phase%201%20-%20Discovery%20%26%20Assessment/…`).

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

### 6. Bilingual where it started bilingual
The AI Maturity Assessment (and its Python impl) is **English + 中文** throughout —
questions, options, reports. Preserve both languages when editing those assets.
Other assets are English-only; match whatever the file already uses.

## The `dra-5c` agent

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
