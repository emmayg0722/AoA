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
    ├── Design Layers/                 # 18-layer agentic AI architecture reference
    │   ├── README.md                  # Overview, reshaped stack diagrams, ERP example
    │   ├── architecture-builder.html  # 14-layer comparison table + "lego" architecture selector
    │   └── layers/                    # One file per layer (01-core-intelligence.md ... 18-agent-types.md)
    ├── architecture-blueprint/        # SOP + intake + Architecture Builder import + blueprint doc (EN/DA/SV)
    ├── architecture-decision-records/ # SOP + repeatable ADR card builder + decision-log doc (EN/DA/SV)
    ├── tech-stack-selection-report/   # SOP + Architecture Builder import + selection report (EN/DA/SV)
    ├── security-architecture/         # SOP + intake (protection, encryption, access, audit, injection) (EN/DA/SV)
    └── nfr-spec/                      # SOP + repeatable requirements matrix + NFR spec doc (EN/DA/SV)
└── Phase 4 - PoC & Pilot/
    ├── poc-planning/                  # SOP + intake + feasibility report w/ Proceed/Iterate/Stop (EN/DA/SV)
    ├── pilot-planning/                # SOP + intake + checkpoint timeline + pilot plan doc (EN/DA/SV)
    └── evaluation-godecision/         # SOP + scorable matrix + live Go/Conditional/No-Go verdict (EN/DA/SV)
└── Phase 5 - Implementation & Delivery/
    ├── implementation-management/     # SOP + intake + sprint/milestone tracker + decision log (EN/DA/SV)
    ├── system-integration/            # SOP + intake + integration-points tracker (EN/DA/SV)
    ├── quality-assurance/             # SOP + intake + test-coverage tracker (EN/DA/SV)
    ├── deployment-golive/             # SOP + intake + rollout-wave tracker + rollback plan (EN/DA/SV)
    └── technical-documentation/       # SOP + documentation-inventory tracker (EN/DA/SV)
└── Phase 6 - Governance, Compliance & Security/
    ├── ai-governance-framework/       # SOP + intake (committee, policy, lifecycle, HITL) (EN/DA/SV)
    ├── compliance-assessment/         # SOP + scorable gap-analysis matrix + legal disclaimer (EN/DA/SV)
    ├── responsible-ai/                # SOP + intake + bias/fairness audit matrix (EN/DA/SV)
    └── risk-management/               # SOP + scored risk register (likelihood x impact) (EN/DA/SV)
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
  checklist. The companion **Architecture Builder** turns 14 of those layers into
  a comparison table with a "pick one per layer" selector that assembles a
  recommended stack for a specific client.
- **Architecture Blueprint** — SOP + intake (exec summary, overall/data/AI-ML/
  integration architecture, tech selections), with a one-click import of your
  Architecture Builder picks, auto-generating an architecture blueprint document.
- **Architecture Decision Records** — SOP plus a repeatable ADR card builder
  (title, status, context, decision, consequences), auto-generating a numbered
  decision-log document.
- **Tech Stack Selection Report** — SOP, an optional import of your Architecture
  Builder picks into a stack table, plus rationale/alternatives/risks intake,
  auto-generating a selection report.
- **Security Architecture** — SOP + intake covering data protection, encryption,
  access control, auditability, and prompt-injection defenses, auto-generating a
  security architecture document.
- **Non-Functional Requirements Spec** — SOP plus a repeatable requirements
  matrix (category, requirement, target, MoSCoW priority), auto-generating an
  NFR specification document.

All five new Phase 3 tools follow the established pattern (SOP card, autosaved
client intake, live document preview, HTML/Markdown export, English/Danish/
Swedish language selector).

## Phase 4 — PoC & Pilot

- **PoC Planning & Feasibility Report** — SOP + intake scoped to a narrow,
  timeboxed proof-of-concept question (in scope, explicitly out of scope,
  success criteria, demo environment), auto-generating a technical feasibility
  report with a Proceed to Pilot / Iterate / Stop recommendation.
- **Pilot Planning & Results Analysis** — SOP + intake (pilot scope, objective,
  integration touchpoints, rollback plan) plus a checkpoint-timeline builder,
  auto-generating a pilot plan document for a controlled real-world deployment.
- **Evaluation & Go/No-Go Decision** — SOP plus a scorable evaluation matrix
  (criterion, evidence, 1-5 score) that computes a live overall score and a
  Go / Conditional Go / No-Go recommendation from task-specific evidence,
  auto-generating a decision report.

All three new Phase 4 tools follow the same established pattern (SOP card,
autosaved client intake, live document preview, HTML/Markdown export,
English/Danish/Swedish language selector).

## Phase 5 — Implementation & Delivery

- **Implementation Management Plan** — SOP + intake (delivery team structure,
  agile cadence, technical decision log) plus a sprint/milestone tracker,
  auto-generating an implementation management plan.
- **System Integration Plan** — SOP + intake (API design, data migration,
  legacy-system constraints) plus an integration-points tracker (system,
  method, data flow, status), auto-generating a system integration plan.
- **Quality Assurance Test Plan** — SOP + intake plus a test-coverage tracker
  spanning model performance, integration, load, and security testing,
  auto-generating a QA test plan.
- **Deployment & Go-Live Plan** — SOP + intake (deployment strategy, production
  configuration, rollback plan, hypercare support) plus a rollout-wave
  tracker, auto-generating a go-live runbook.
- **Technical Documentation Index** — SOP plus a documentation-inventory
  tracker pre-seeded with the minimum viable set (API docs, deployment
  manual, operations runbook, test report), auto-generating a documentation
  index.

All five new Phase 5 tools follow the same established pattern (SOP card,
autosaved client intake, live document preview, HTML/Markdown export,
English/Danish/Swedish language selector).

## Phase 6 — Governance, Compliance & Security

- **AI Governance Framework** — SOP + intake (governance committee structure,
  AI usage policy, model lifecycle management, human-in-the-loop checkpoints),
  auto-generating an AI governance framework document.
- **Compliance Gap Analysis** — SOP + intake plus a scorable gap-analysis
  matrix (requirement, framework, status, notes), auto-generating a
  compliance gap analysis report. Carries an explicit disclaimer: AI
  regulation (EU AI Act, NIST AI RMF, ISO/IEC 42001, regional laws) is still
  evolving, this tool structures the assessment but is not legal advice, and
  applicability/obligations should be verified with qualified counsel.
- **Responsible AI & Bias Audit** — SOP + intake (transparency/explainability,
  privacy protection) plus a bias/fairness audit matrix (dimension, method,
  finding, status), auto-generating a bias audit report.
- **AI Risk Register** — SOP plus a scored risk register (likelihood × impact
  computed live into a Low/Medium/High/Critical severity, mitigation, owner),
  auto-generating a risk assessment report.

All four new Phase 6 tools follow the same established pattern (SOP card,
autosaved client intake, live document preview, HTML/Markdown export,
English/Danish/Swedish language selector).

Phase 7 (MLOps & Operations) follows the same folder pattern and will be
added over time.

All assessment tools run fully client-side — no data leaves the browser.
