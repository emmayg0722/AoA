# Phase 8 — Change Management & Enablement

Phase 7 keeps the system running. This phase makes the *organization* able to run
it — because the failure mode of a technically sound AI deployment is almost never
the model. It is a client whose staff quietly route around the tool, whose one
capable ML engineer leaves, or whose executives cannot answer questions about a
system they nominally own.

The distinction that matters here: most AI resistance is rational, not ignorant.
Someone's judgement is being partly automated, or their workload is about to be
measured differently. A communications plan that treats that as a misunderstanding
to be corrected reads as spin and deepens the problem. So the tools in this phase
start from who loses something, and work outward from there.

| Tool | What it does |
|------|--------------|
| [`change-management-plan/`](change-management-plan/) | SOP + intake covering change impact per group, the communication strategy and cadence, anticipated resistance and how it will be addressed, and the adoption tracking loop, plus a stakeholder-group tracker (group, impact, action), auto-generating a change management plan. |
| [`training-curriculum/`](training-curriculum/) | SOP + intake covering four tracks — AI literacy for non-technical staff, a technical track for engineering and data teams, tool training for daily users, and a leadership track on decision-making with AI — plus a curriculum-module tracker, auto-generating a training curriculum. |
| [`ai-coe-design/`](ai-coe-design/) | SOP + intake covering the CoE mandate and organizational model (central, federated, hub-and-spoke), roles, headcount and funding, operating processes and decision authority, and the KPI framework, plus a roles-and-responsibilities tracker, auto-generating a CoE design document. |
| [`knowledge-transfer/`](knowledge-transfer/) | SOP + intake covering the transfer approach and its definition of done, the documentation set and where it lives, the best-practice library, and the internal community that keeps it alive, plus a handover-area tracker, auto-generating a knowledge transfer plan. |

All four tools follow the toolkit-wide pattern: a checkable SOP checklist, an
autosaved client intake, a tracker matrix, a live document preview, HTML/Markdown
export, a "🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting"
prompt generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work.

## Where this phase connects

- **Phase 1 `organizational-readiness`** already scored the client on skills,
  culture and sponsorship. This phase is where those scores become a plan — if the
  training curriculum does not address the gaps that assessment found, one of the
  two documents is decorative.
- **Phase 7 `operations-runbook`** names the on-call rotation the client's own team
  will staff. `knowledge-transfer` is what makes that rotation survivable, and
  `training-curriculum`'s technical track is what qualifies the people on it.
- **Phase 6 `ai-governance-framework`** assigns decision rights. The CoE design
  has to inherit them rather than invent a parallel set, or the client ends up with
  two bodies that both believe they approve model releases.
