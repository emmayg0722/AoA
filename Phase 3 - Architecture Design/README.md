# Phase 3 — Architecture Design

Phase 2 committed to building something. This phase decides what it *is* — the
layers it's composed of, the requirements it must meet, the decisions taken along
the way and why, and the security posture it carries from the start rather than
retrofits later.

The distinction that matters here: tools are replaceable, architecture decisions are
not. A stack chosen because a vendor demoed well can be swapped in a quarter; a
decision to make the agent stateless, or to skip a verification layer, propagates
through everything built afterwards. So this phase is organized around capability
layers and recorded decisions rather than around a product list.

| Asset | What it does |
|------|--------------|
| [`Design Layers/`](Design%20Layers/) | The reference material, not a tool: 18 capability stacks / decision layers for agentic AI architecture ([README](Design%20Layers/README.md), one file per layer under [`layers/`](Design%20Layers/layers/)), plus [`architecture-builder.html`](Design%20Layers/architecture-builder.html) — a 14-layer comparison table and a "lego" selector for assembling a stack layer by layer. Its saved selection feeds two of the tools below. |
| [`architecture-blueprint/`](architecture-blueprint/) | SOP + intake that **imports the Architecture Builder's selection**, covering the layer-by-layer design, data flow, deployment topology and scaling approach, auto-generating an architecture blueprint. |
| [`architecture-decision-records/`](architecture-decision-records/) | SOP + a repeatable ADR card builder (context, decision, alternatives considered, consequences, status), auto-generating a decision log. The point is the *rejected* alternatives — an ADR that lists none is a summary, not a record. |
| [`tech-stack-selection-report/`](tech-stack-selection-report/) | SOP + intake that also **imports the Architecture Builder's selection**, covering the selection criteria, per-layer choices and their rationale, auto-generating a tech stack selection report. |
| [`security-architecture/`](security-architecture/) | SOP + intake covering data protection, encryption in transit and at rest, access control and authentication, audit logging, and prompt-injection defence, auto-generating a security architecture document. |
| [`nfr-spec/`](nfr-spec/) | SOP + a repeatable requirements matrix (requirement, target, measurement method, priority), auto-generating a non-functional requirements spec. These are the numbers vendors and SLOs are later held to, so unmeasurable targets are worse than absent ones. |

The five deliverable tools follow the toolkit-wide pattern: a checkable SOP
checklist, an autosaved client intake, a live document preview, HTML/Markdown
export, a "🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting"
prompt generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work.

## Where this phase connects

- **Phase 1 `infrastructure-audit`** found what the client's platform can actually
  carry. An NFR target the audit already showed is unreachable belongs in a gap
  list, not in a spec someone will later be measured against.
- **Phase 9 `platform-shortlist` and `rfp-builder`** are the evidence behind the
  tech stack selection. Run them and let this phase's report cite them, rather than
  restating conclusions with no working shown.
- **Phase 3 `nfr-spec` → Phase 5 `quality-assurance` → Phase 7 `model-monitoring`**
  should be the same numbers all the way through. Where they diverge, one of the
  three is stale.
- **Phase 6 `security-architecture` overlap**: this phase designs the controls;
  Phase 6 governs and audits them. If the two documents disagree on who approves a
  model release, the client has a gap rather than two opinions.
