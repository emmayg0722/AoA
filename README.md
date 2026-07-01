# AoA — AI Architect Toolkit

A working toolkit for AI-architecture consulting engagements, organized by delivery
phase. Live site: https://emmayg0722.github.io/AoA/

Each consulting phase has its own folder; within a phase, each deliverable/tool has
its own subfolder. New phases and assets follow the same structure.

## Structure

```
.
├── index.html                         # Portfolio hub (links to every phase tool)
├── og-image.png                       # Social/link preview image
├── AI-Architect-Consulting-Work-Research.md   # The Phase 1–10 reference this toolkit follows
├── .claude/agents/                    # Claude Code agents (must live here to be loadable)
│   └── dra-5c.md                      # Data Readiness Assessment (5C) agent
└── Phase 1 - Discovery & Assessment/
    ├── ai-maturity-assessment/        # Browser tool: 6-dimension AI maturity scoring
    │   ├── index.html
    │   └── python/                    # Streamlit/Python implementation
    ├── data-readiness-assessment-5c/  # 5C data-readiness assessment
    │   ├── methodology.md
    │   ├── console.html               # Workspace front-end for the 4-step assessment
    │   ├── profiler.html              # Browser-local data profiler (data stays local)
    │   ├── templates/
    │   └── README.md
    └── sample-data/                   # Synthetic demo data only — see its README
        ├── ai-maturity-assessment/
        └── data-readiness-assessment-5c/
└── Phase 3 - Architecture Design/
    └── Design Layers/                 # 18-layer agentic AI architecture reference
        ├── README.md                  # Overview, reshaped stack diagrams, ERP example
        └── layers/                    # One file per layer (01-core-intelligence.md ... 18-agent-types.md)
```

## Phase 1 — Discovery & Assessment

- **AI Maturity Assessment** — score an organization across strategy, data,
  technology, governance, talent, and operations, with instant results and a
  downloadable report.
- **Data Readiness Assessment (5C)** — an agent + browser-local profiler that judge
  whether a client's data is ready for a specific AI use case (Context, Clarity,
  Coverage, Credibility, Capacity).

## Phase 3 — Architecture Design

- **Design Layers** — reframes "which tools should I use?" into a capability-stack
  view: 18 layers covering how an agent understands, decides, acts, remembers,
  verifies, and improves inside a business system (core intelligence, orchestration,
  tools/actions, RAG, memory, planning, human-in-the-loop, evaluation, observability,
  guardrails, security/governance, deployment, business integration, data, prompts,
  workflow, cost, and agent types), plus a worked ERP example and an architect's
  checklist.

Further phases (Strategy & Roadmap, PoC/Pilot, Implementation, Governance, MLOps)
follow the same folder pattern and will be added over time.

All assessment tools run fully client-side — no data leaves the browser.
