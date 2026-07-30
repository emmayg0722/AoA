# Phase 10 — ROI Analysis & Cost Optimization

Phase 2 built the business case on estimates. This phase is where the estimates
meet reality: what the system was actually worth, what it costs to keep, and the
review cadence that keeps both numbers honest long after the engagement ends.

The distinction that matters here: attribution. A fraud-detection model deployed in
the same quarter as a new claims process and a fresh analyst cohort cannot claim the
whole improvement, and an ROI figure that ignores this is the one a CFO will
dismantle in the first review. So these tools ask for the confounders and the
downside case in the same breath as the headline number, and treat an unverifiable
benefit as excluded rather than assumed.

| Tool | What it does |
|------|--------------|
| [`roi-analysis/`](roi-analysis/) | SOP + intake covering the value quantification approach, the ROI model, horizon and payback, the attribution method and confounders, and sensitivity and downside case, plus a value-driver tracker recording each driver's confidence, auto-generating an ROI analysis. |
| [`tco-analysis/`](tco-analysis/) | SOP + intake covering TCO scope, horizon and allocation basis, run costs (platform, inference, licences), people costs to operate, maintain and review, and the optimization levers already applied or still available, plus a cost-line tracker, auto-generating a total cost of ownership analysis. |
| [`value-tracking/`](value-tracking/) | SOP + intake covering the KPI set with baselines and named owners, dashboard design and where it lives, review cadence, attendees and decision rights, and actions from the latest review, plus a KPI tracker showing baseline against current, auto-generating a value tracking report. |

All three tools follow the toolkit-wide pattern: a checkable SOP checklist, an
autosaved client intake, a tracker matrix, a live document preview, HTML/Markdown
export, a "🧪 Load sample" button (Nordkap sample engagement), an "Agent drafting"
prompt generator, and an English/Danish/Swedish language selector. See the
[root README](../README.md) for how those shared mechanics work.

## Where this phase connects

- **Phase 2 `business-case-development`** made the original projection. This phase
  should be read against it explicitly, including where the projection was wrong —
  a Phase 10 report that happens to confirm every Phase 2 estimate is not a
  measurement, it is a restatement.
- **Phase 7 `cost-optimization`** covers inference spend specifically;
  `tco-analysis` is the wider picture (people, licences, platform, review time)
  and should pull the Phase 7 figures in rather than re-deriving them.
- **Phase 4 `evaluation-godecision`** set the success criteria. `value-tracking`'s
  KPI set should be recognisably the same measures, or the client is being graded
  on a curve that moved after go-live.
- **Phase 8 `change-management-plan`** carries the training and change effort that
  belongs on the cost side of the ROI model — leaving it out is the most common way
  an AI business case flatters itself.
