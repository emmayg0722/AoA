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
    ├── infrastructure-audit/          # SOP + intake + auto-generated current-state doc (EN/DA/SV)
    ├── organizational-readiness/      # SOP + intake + auto-generated readiness doc (EN/DA/SV)
    ├── use-case-prioritization/       # SOP + ROI/feasibility/impact matrix + priority doc (EN/DA/SV)
    └── sample-data/                   # Synthetic demo data only — see its README
        ├── ai-maturity-assessment/
        └── data-readiness-assessment-5c/
└── Phase 2 - Strategy & Roadmap/
    ├── ai-strategy-planning/          # SOP + intake + milestone roadmap + auto-generated doc (EN/DA/SV)
    ├── business-case-development/     # SOP + intake + live ROI/payback model + auto-generated doc (EN/DA/SV)
    ├── technology-roadmap/            # SOP + platform-strategy intake + milestone timeline (EN/DA/SV)
    └── organizational-roadmap/        # SOP + intake (CoE, talent, structure, partners) (EN/DA/SV)
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
- **Infrastructure Audit** — SOP for the interview → document review → technical
  inspection → capacity/cost → use-case scoring workflow, with client intake that
  auto-generates a customized current-state document.
- **Organizational Readiness Assessment** — SOP + intake covering team capability,
  culture/change readiness, process maturity, and stakeholder analysis, auto-
  generating a customized readiness document.
- **Use Case Identification & Prioritization** — SOP plus a live, scorable ROI /
  feasibility / impact matrix that ranks candidate AI use cases, flags quick wins,
  and auto-generates a priority document.

All three new Phase 1 tools follow the same pattern: an SOP card, a client-intake
form (autosaved locally), a live document preview built from a `{{field}}` template,
HTML/Markdown export, and an English/Danish/Swedish language selector — the pattern
now used across the toolkit.

## Phase 2 — Strategy & Roadmap

- **AI Strategy Planning** — SOP + intake covering vision/mission, strategic
  alignment, and success metrics, plus a 3-5 year milestone-roadmap builder,
  auto-generating an AI strategy document.
- **Business Case Development** — SOP + intake with a **live ROI model**
  (payback period, net benefit over horizon, ROI%) that computes as you type,
  auto-generating a business case document with the computed figures embedded.
- **Technology Roadmap** — SOP + platform-strategy intake (cloud-first / hybrid /
  private / multi-cloud) and a milestone timeline with dependencies, auto-
  generating the technology roadmap Phase 3 architecture work designs against.
- **Organizational Roadmap** — SOP + intake covering AI CoE design, talent
  acquisition/development, structure changes, and partner ecosystem, auto-
  generating an organizational change roadmap.

## Phase 3 — Architecture Design

- **Design Layers** — reframes "which tools should I use?" into a capability-stack
  view: 18 layers covering how an agent understands, decides, acts, remembers,
  verifies, and improves inside a business system (core intelligence, orchestration,
  tools/actions, RAG, memory, planning, human-in-the-loop, evaluation, observability,
  guardrails, security/governance, deployment, business integration, data, prompts,
  workflow, cost, and agent types), plus a worked ERP example and an architect's
  checklist.

Further phases (PoC/Pilot, Implementation, Governance, MLOps) follow the same
folder pattern and will be added over time.

All assessment tools run fully client-side — no data leaves the browser.
