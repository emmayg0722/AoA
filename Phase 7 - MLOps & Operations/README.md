# Phase 7 — MLOps & Operations

Phase 5 ships the solution; this phase keeps it working. MLOps is the connective
tissue between data science and IT operations: the pipelines that retrain and
redeploy a model, the monitoring that catches drift before users do, the runbook
the client's own on-call team will run on after the engagement ends, and the cost
controls that stop inference spend growing unnoticed.

The distinction that matters here: a model does not fail like ordinary software.
It keeps returning confident answers while quietly getting worse, so the tools in
this phase are built around detecting silent degradation rather than outages.

| Tool | What it does |
|------|--------------|
| [`mlops-platform-design/`](mlops-platform-design/) | SOP + intake covering CI/CD pipeline design (data, training, deployment), model registry and versioning, feature store, and experiment tracking, plus a platform-component tracker, auto-generating an MLOps platform architecture document. |
| [`model-monitoring/`](model-monitoring/) | SOP + intake covering the performance dashboard and SLOs, data and concept drift detection, model decay alerting, and hallucination/data-leakage checks, plus a monitored-signal tracker (signal, detection method, threshold), auto-generating a monitoring plan. |
| [`retraining-strategy/`](retraining-strategy/) | SOP + intake covering retraining triggers, the automated pipeline, A/B, shadow and canary release, and rollback, plus a trigger tracker tying each trigger to a monitored signal, auto-generating a retraining strategy document. |
| [`operations-runbook/`](operations-runbook/) | SOP + intake covering runbook scope, on-call rotation and handover, escalation path, and incident response, plus an incident-playbook tracker (scenario, first response, escalation), auto-generating an operations runbook. |
| [`cost-optimization/`](cost-optimization/) | SOP + intake covering cost attribution, compute utilization, compression and distillation, and caching, plus an optimization-lever tracker ranked by saving against effort, auto-generating a cost optimization report. |

All five tools follow the toolkit-wide pattern: a checkable SOP checklist, an
autosaved client intake, a tracker matrix, a live document preview, HTML/Markdown
export, a "🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting"
prompt generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work.

## Where this phase connects

- **Phase 4 `evaluation-godecision`** set the success criteria this phase monitors
  against. A monitoring plan whose thresholds contradict the go/no-go bar is a
  sign one of the two is stale.
- **Phase 6 `risk-management` and `responsible-ai`** name the risks and fairness
  metrics that belong in the monitored-signal list and in the retraining
  promotion gate, not just in a governance document.
- **Phase 5 `deployment-golive`** owns the first release; `retraining-strategy`
  owns every release after it, and both need to agree on rollback.
