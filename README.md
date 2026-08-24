# AoA — AI Architect Toolkit

A working toolkit for AI-architecture consulting engagements, organized by delivery
phase. Live site: https://emmayg0722.github.io/AoA/

Each consulting phase has its own folder; within a phase, each deliverable/tool has
its own subfolder. New phases and assets follow the same structure.

All **ten phases** of the delivery lifecycle are built — 43 browser-local tools
from first discovery interview through to the quarterly value review after go-live.
Alongside them sit **agent skills**: portable instructions that give Claude, Codex
or any other agent the same reasoning, installable outside this repository.

## Structure

```
.
├── index.html                         # Portfolio hub (links to every phase tool)
├── og-image.png                       # Social/link preview image
├── AI-Architect-Consulting-Work-Research.md   # The Phase 1–10 reference this toolkit follows
├── .claude/agents/                    # Claude Code agents (must live here to be loadable)
│   ├── dra-5c.md                      # Data Readiness Assessment (5C) agent
│   └── use-case-evaluator.md          # Use-case evaluation mentor (scores against Phase 1/4 rubrics)
├── skills/                            # Portable agent skills — run inside an agent, not the browser
│   ├── index.html                     # Skills library & per-agent install guide (EN/DA/SV)
│   ├── business-problem-sharpener/    # Sharpen + classify a business problem
│   └── roi-scenario-model/            # Scenario ROI with NPV, sensitivity, breakeven
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
└── Phase 7 - MLOps & Operations/
    ├── mlops-platform-design/         # SOP + intake (CI/CD, registry, feature store, tracking) + component tracker (EN/DA/SV)
    ├── model-monitoring/              # SOP + intake (drift, decay, hallucination) + monitored-signal tracker (EN/DA/SV)
    ├── retraining-strategy/           # SOP + intake (triggers, canary, rollback) + trigger tracker (EN/DA/SV)
    ├── operations-runbook/            # SOP + intake (rotation, escalation, incidents) + playbook tracker (EN/DA/SV)
    └── cost-optimization/             # SOP + intake (attribution, utilization, caching) + lever tracker (EN/DA/SV)
└── Phase 8 - Change Management & Enablement/
    ├── change-management-plan/        # SOP + intake (impact, comms, resistance, adoption) + stakeholder tracker (EN/DA/SV)
    ├── training-curriculum/           # SOP + intake (literacy, technical, tool, leadership tracks) + module tracker (EN/DA/SV)
    ├── ai-coe-design/                 # SOP + intake (mandate, roles, processes, KPIs) + responsibilities tracker (EN/DA/SV)
    └── knowledge-transfer/            # SOP + intake (approach, docs, best practice, community) + handover tracker (EN/DA/SV)
└── Phase 9 - Vendor Evaluation & Technology Selection/
    ├── rfp-builder/                   # SOP + intake (scope, scoring model, process, deal-breakers) + weighted criteria (EN/DA/SV)
    ├── vendor-evaluation-matrix/      # SOP + intake (shortlist, capability, support, stability) + per-vendor scoring (EN/DA/SV)
    ├── build-vs-buy/                  # SOP + intake (options, cost, technical debt, lock-in) + decision-factor tracker (EN/DA/SV)
    └── platform-shortlist/            # SOP + intake (ML platform, model, data, observability) + per-category selections (EN/DA/SV)
└── Phase 10 - ROI Analysis & Cost Optimization/
    ├── roi-analysis/                  # SOP + intake (quantification, model, attribution, sensitivity) + value drivers (EN/DA/SV)
    ├── tco-analysis/                  # SOP + intake (scope, run costs, people costs, levers) + cost-line tracker (EN/DA/SV)
    └── value-tracking/                # SOP + intake (KPIs, dashboard, review cadence, actions) + KPI tracker (EN/DA/SV)
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

## Phase 7 — MLOps & Operations

Phase 5 ships the solution; this phase keeps it working. A model does not fail
like ordinary software — it keeps returning confident answers while quietly
getting worse — so these tools are built around detecting silent degradation
rather than outages.

- **MLOps Platform Architecture** — SOP + intake covering CI/CD pipeline design
  (data, training, deployment as three separable pipelines), model registry and
  version management, feature store (including the rationale for not having
  one), and experiment tracking, plus a platform-component tracker, auto-
  generating an MLOps platform architecture document.
- **Model Monitoring & Drift Detection Plan** — SOP + intake covering the
  performance dashboard and SLOs, data drift vs. concept drift detection, model
  decay alerting with threshold rationale, and hallucination/data-leakage
  protection, plus a monitored-signal tracker (signal, detection method,
  threshold and the action a breach obliges), auto-generating a monitoring plan.
- **Model Retraining Strategy** — SOP + intake covering retraining trigger
  conditions, the reproducible automated pipeline, A/B, shadow and canary
  release, and a tested rollback procedure, plus a trigger tracker tying each
  trigger to a monitored signal that actually exists, auto-generating a
  retraining strategy document.
- **Operations Runbook & On-Call Plan** — SOP + intake covering runbook scope and
  intended reader, on-call rotation and handover to the client's own team,
  escalation path and decision authority, and incident response, plus an
  incident-playbook tracker (scenario, first response, escalation), auto-
  generating an operations runbook.
- **Inference Cost Optimization Report** — SOP + intake covering cost monitoring
  and attribution, compute utilization findings, compression and distillation
  assessment, and caching strategy, plus an optimization-lever tracker ranked by
  saving against effort that also records rejected levers with the reason,
  auto-generating a cost optimization report.

All five tools follow the same established pattern (checkable SOP card, autosaved
client intake, tracker matrix, live document preview, HTML/Markdown export, agent
drafting, sample engagement, English/Danish/Swedish language selector).

## Phase 8 — Change Management & Enablement

Phase 7 keeps the system running; this phase makes the *organization* able to run
it. Most AI resistance is rational rather than ignorant — someone's judgement is
being partly automated, or their workload is about to be measured differently — so
these tools start from who loses something and work outward.

- **Change Management Plan** — SOP + intake covering change impact assessed per
  group rather than per department, the communication strategy and cadence,
  anticipated resistance and how it will be addressed, and the adoption tracking
  loop, plus a stakeholder-group tracker (group, impact, action).
- **Training Curriculum** — SOP + intake covering four tracks (AI literacy for
  non-technical staff, a technical track for engineering and data teams, tool
  training for the people who use the system daily, and a leadership track on
  decision-making with AI), plus a curriculum-module tracker.
- **AI Centre of Excellence Design** — SOP + intake covering the CoE mandate and
  organizational model (central, federated, hub-and-spoke), roles, headcount and
  funding, operating processes and decision authority, and the KPI framework, plus
  a roles-and-responsibilities tracker.
- **Knowledge Transfer Plan** — SOP + intake covering the transfer approach and its
  definition of done, the documentation set and where it lives, the best-practice
  library and standards, and the internal community that keeps knowledge alive
  after handover, plus a handover-area tracker.

## Phase 9 — Vendor Evaluation & Technology Selection

Phase 3 decided the architecture; this phase decides who and what supplies it —
deliberately, rather than by whoever gave the best demo. Vendor demos run on the
vendor's data, and for AI products that gap can stretch a long way, so every tool
here pushes the evaluation onto the client's own data.

- **RFP / RFI Builder** — SOP + intake covering the requirement and scope
  statement, the evaluation approach and scoring model, process, timeline and
  vendor communication rules, and constraints, must-haves and deal-breakers, plus
  a weighted evaluation-criteria tracker, auto-generating an RFP/RFI document.
- **Vendor Evaluation Matrix** — SOP + intake covering the shortlist and how it was
  arrived at, technical capability findings tested on the client's own data,
  implementation and ongoing support, and company stability, roadmap and lock-in
  risk, plus a per-vendor scoring matrix.
- **Build vs. Buy Analysis** — SOP + intake covering the options being compared and
  the horizon, cost comparison over that horizon, technical debt and maintenance
  burden, and strategic flexibility versus lock-in, plus a decision-factor tracker
  weighing each option.
- **Platform & Model Shortlist** — SOP + intake covering ML platform and MLOps
  tooling, model selection (LLM, embeddings) and the evaluation basis, data
  platform and vector store, and observability and evaluation tooling, plus a
  per-category selection tracker.

## Phase 10 — ROI Analysis & Cost Optimization

Phase 2 built the business case on estimates; this phase is where they meet
reality. The hard part is attribution — a model deployed alongside a new process
and a fresh analyst cohort cannot claim the whole improvement — so these tools ask
for confounders and the downside case in the same breath as the headline number.

- **ROI Analysis** — SOP + intake covering the value quantification approach, the
  ROI model, horizon and payback, the attribution method and confounders, and
  sensitivity and downside case, plus a value-driver tracker that records each
  driver's confidence rather than presenting all of them as equally solid.
- **Total Cost of Ownership** — SOP + intake covering TCO scope, horizon and
  allocation basis, run costs (platform, inference, licences), people costs to
  operate, maintain and review, and the optimization levers already applied or
  still available, plus a cost-line tracker.
- **Value Tracking & Quarterly Review** — SOP + intake covering the KPI set with
  baselines and named owners, dashboard design and where it lives, review cadence,
  attendees and decision rights (including the right to recommend stopping), and
  actions from the latest review, plus a KPI tracker showing baseline against
  current.

All eleven Phase 8–10 tools follow the same established pattern (checkable SOP
card, autosaved client intake, tracker matrix, live document preview, HTML/Markdown
export, agent drafting, sample engagement, English/Danish/Swedish language
selector). With these, all ten phases of the delivery lifecycle are built.

## Agent skills (portable, outside the browser)

`skills/` holds the one part of this toolkit that does **not** run in a browser.
Each is a `SKILL.md` — YAML frontmatter plus markdown — that an agent loads and
follows, so the same methodology works whether an architect is operating a tool
by hand or driving an agent.

| Skill | What it does | Verb | Maps to |
|---|---|---|---|
| `business-problem-sharpener` | Turns a solution-shaped request into a measurable, solution-free problem statement, then classifies it on four axes — starting with whether it is an AI problem at all. | Interrogate | Phase 1 |
| `eval-harness-designer` | Designs how you will know the system works: stratified test set, metrics by archetype, naive and human baselines, per-slice thresholds, and a regression plan for when the model changes underneath you. Bundles a stdlib-only per-slice scorer with confidence intervals. | Interrogate | Phase 4 |
| `architecture-tradeoff-analyst` | Forces criteria and weights to be agreed before options are scored, then makes the runner-up state what would have to be true for it to win. | Decide | Phase 3 |
| `architecture-red-team` | Attacks a proposed design along eight axes — load, model dependency, adversarial input, silent degradation, blast radius, privacy, cost runaway, human factors — ranked by likelihood and recoverability. | Critique | Phase 3/5 |
| `context-architecture-designer` | Designs how information reaches the model — retrieved vs prompt vs fine-tuned, chunking, reranking, permission filtering, caching — and budgets tokens and cost per request. Bundles a stdlib-only context budget script. | Design | Phase 3 |
| `roi-scenario-model` | Conservative / base / optimistic ROI with NPV, payback, sensitivity and breakeven. Bundles a stdlib-only Python engine. | Quantify | Phase 10 |
| `brand-skill-generator` | Reads a company's real brand out of its `.pptx` template, `.svg` logo, site CSS and LinkedIn, marks every value as extracted / inferred / proposed, contrast-tests the palette, and — after you approve the profile — generates a named, installable skill for that company. Bundles a stdlib-only extractor. | Distil | Any phase |

They are deliberately **self-contained** — a skill never reads another file in
this repository, so copying one out on its own breaks nothing. Frontmatter stays
at `name` and `description`, the two fields every implementation understands, and
bundled scripts need only the Python standard library.

Installing is one command, and works the same on macOS, Linux and Windows:

```bash
cd skills
python3 install.py --list                      # see what is available
python3 install.py --agent claude              # all of them, just for you
python3 install.py --agent codex  --project .  # copies + wires AGENTS.md
python3 install.py --agent cursor --project .  # copies + writes a rule file
```

Once installed on Claude Code, each skill's folder name is a slash command —
`/roi-scenario-model`, `/brand-skill-generator`, and `/columbus` for a company
skill the generator produced. You rarely need them: the descriptions are
written so the right skill loads on its own when the work matches. Codex and
Cursor have no slash commands for skills; there the wiring file does it.

`install.py` is standard-library Python, so nothing needs installing first. For
Codex and Cursor it also writes the file that points the agent at the skills,
inserting a marked block so re-running updates that block and leaves the rest of
your `AGENTS.md` alone. Manual per-OS paths and the `.skill` package format are
covered in `skills/README.md` and on the [skills page](skills/).

## Microsoft enterprise ladder (on the hub)

Most clients this toolkit is aimed at are Microsoft shops, and their AI programme
does not start at architecture — it starts with a Copilot licence somebody already
bought. The hub carries a **Microsoft Enterprise Ladder** section describing the
four rungs from that first seat to a governed agent estate. Each rung answers the
four questions a client actually asks, in the order they ask them:

- **Try this first** — the concrete first move, plus what bites if you skip ahead
- **What it gets you** — the outcome in business terms, not features
- **How to turn it on** — the numbered setup: licences, admin steps, prerequisites
- **Gate to clear** — what has to be true before the next rung is worth funding

| Rung | What it is | The first move |
| --- | --- | --- |
| 1 · Assisted | **Microsoft 365 Copilot** in Word, Excel, PowerPoint, Outlook and Teams | Two or three named weekly jobs in one or two teams, with a time baseline, after fixing SharePoint oversharing |
| 2 · Configured | **Agents in Copilot Studio**, grounded in SharePoint, Graph or Dataverse and published into Teams | One repeat-question queue turned into an agent with an owner, an escalation path and a deflection number |
| 3 · Delegated | **Copilot Cowork** — define the task, it plans and runs the steps and returns a deliverable | One whole multi-step piece of work handed over, reviewed at checkpoints, on a budget somebody owns |
| 4 · Governed estate | **Work IQ, Fabric, Dataverse/Dynamics 365, Microsoft Foundry, Agent 365 + Entra Agent ID, Purview** | Curate the knowledge agents read, register every agent that exists, then let teams build on top |

The ladder runs *alongside* the delivery phases rather than replacing them: rung 1
is a Phase 1 use case, rung 2 a Phase 4 pilot, rung 4 a Phase 6 governance
programme.

Two visuals frame the rungs. Above them, a hand-authored inline SVG shows the same
three-step flow at each rung so the only thing that changes is **where the person
stands**: doing the work, then answering what the agent cannot, then approving what
it produced, then governing the estate that produces it. That is what decides which
rung a client is really on, rather than what they have licensed. Below them, an
**enterprise footprint** matrix scores five enterprise surfaces (productivity,
business apps and process, knowledge and data, identity and governance, custom
engineering) against the four rungs, from "not in play yet" to "load-bearing" —
the footprint spreads down and to the right, which is the argument for why the last
rung is a programme and not a licence.

Like the reference-architecture layers, the rung content stays in English while
the chrome around it follows the site language selector. The section is `is-aux`,
so it stays out of the numbered path and out of the "43 tools / 10 phases" counts.

## SOP checklists & the Nordkap sample engagement

Every tool's SOP is now a **checkable checklist** — step state persists locally
with the rest of the tool's data and survives language switches. And every tool
has a **"🧪 Load sample"** button that loads its slice of one consistent
fictional engagement (*Nordkap Insurance — claims fraud detection at FNOL*,
under `sample-data/engagement-nordkap/`), so the whole toolkit — including the
hub dashboard and master report — can be demoed end-to-end in a few clicks.

## Scored rubrics, pre-seeded content & charts

- **Scored rubrics**: Infrastructure Audit, Organizational Readiness, and
  Security Architecture now score each dimension 1–5 next to its evidence
  notes, computing a live overall score and Ready / Conditional / Not-ready
  verdict that flows into the generated document and exports.
- **Pre-seeded starter content**: Compliance Gap Analysis starts with 11
  requirement rows spanning EU AI Act, NIST AI RMF, and ISO/IEC 42001
  (starting points under the existing verify-with-counsel disclaimer); QA
  starts with the 5 standard test types with suggested scopes; NFR Spec
  scaffolds one row per category; the Risk Register has an "Add common AI
  risks" button with 8 pre-scored risks and mitigations.
- **Charts** (canvas, no libraries): Use Case Prioritization draws a
  quick-win 2×2 matrix (feasibility × value, quick wins highlighted); the
  Risk Register draws a likelihood × impact heatmap colored by severity.

## Agent drafting (all 40 deliverable tools)

Every deliverable tool has an **"Agent drafting"** card: one click generates a
prompt that carries the tool's SOP methodology and your full intake (including
any matrix rows), you run it in Claude (or any capable model), and paste the
drafted Markdown back. A pasted draft **replaces** the echo template in the live
preview and in both exports — turning each tool from a form-filler into a real
drafting assistant, still with zero API calls from the page itself. Clearing
the draft returns to the template. Prompts are English (same scoping as the
DRA-5C console's agent prompts).

## Shared engagement profile, dashboard & master report

Client, assessor, and use case are entered **once** and carry across the whole
toolkit: every tool prefills those fields from a shared browser-local profile
(`localStorage` key `aoa_engagement_v1`) and writes changes back to it. The hub
shows an **engagement dashboard** — the current engagement plus a started/empty
chip for each of the 43 stateful tools. A root-level **`engagement-report.html`**
assembles every tool's saved work into one combined report (HTML/Markdown
export) and can save or restore the *entire* engagement — all tools at once —
as a single JSON file. Like everything else here, all of it is browser-local:
nothing is uploaded anywhere.

## Site-wide language selector

Every tool in the toolkit — the 40 Phase 1–10 tools above plus the 5 tools
that predate them (this hub, AI Maturity Assessment, DRA-5C console and
profiler, and the Design Layers Architecture Builder) — has an
English/Danish/Swedish language selector in the top-right of its header. The
choice is stored once (`localStorage` key `aoa_lang`) and applies across the
whole site as you move between tools.

For content-heavy reference material — the Architecture Builder's 14-layer
comparison table, the AI Maturity Assessment's 24-question bank and generated
report body, and the DRA-5C console's agent/Copilot prompt templates — only
the surrounding UI chrome is translated; the underlying content stays English,
the same scoping already used for the Design Layers markdown reference files.

All assessment tools run fully client-side — no data leaves the browser.
