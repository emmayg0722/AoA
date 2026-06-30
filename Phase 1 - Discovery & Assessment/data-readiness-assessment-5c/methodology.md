# Data Readiness Assessment — The 5C Method

> Phase 1 (Discovery & Assessment) deliverable: a **Data Readiness Scorecard** that
> judges whether a client's data is ready for a **specific** AI use case.

Data readiness is never absolute — it is always assessed **against a use case**.
The same dataset can be ready for a monthly BI dashboard and completely unready for
a real-time fraud model. Always start from the use case and its data needs.

## The five C's, and how each is actually assessed

| C | Question | How you assess it | Method type | Needs raw data? |
|---|----------|-------------------|-------------|-----------------|
| **Context** | Is the data's origin & meaning understood? | Interview data owners; review data dictionaries, lineage, source-system docs | Document review + interview | No |
| **Clarity** | Are field semantics correct & consistent? | Metadata/schema audit; reconcile field definitions/units across teams; spot-check a few fields vs. their documented meaning | Audit + light spot-check | Mostly metadata |
| **Coverage** | Is there enough data, across the right dimensions? | Quantitative completeness analysis — fill rates, time-span and segment coverage vs. what the use case needs | Statistical (aggregate) | Aggregates only |
| **Credibility** | Is the data reliable? | Sample-based QA — duplicate rate, type/format consistency, staleness, reconcile a sample against a source of truth | Sampling-based QA | Aggregates of a sample |
| **Capacity** | Can it be processed at production scale? | Infrastructure/pipeline assessment & load testing — throughput, latency, volume/velocity under production conditions | Systems/capacity testing | No (tests systems) |

Key takeaway: **only Credibility (and a slice of Coverage) is genuinely "sampling
the data."** Context and Capacity are document/interview and systems work; Clarity
is mostly metadata. So "do we just sample the client's data?" → no, sampling is one
of five techniques, and even then we work from **aggregates**, never raw rows.

## Privacy posture

Raw client data must never leave the client's environment. The actual-data spot-check
(Coverage/Credibility) is performed with the **browser-local profiler**
(`profiler.html`), which computes fill rate, duplicate rate, type consistency,
distributions, and freshness entirely in-browser. Only the **aggregate summary**
(counts and rates) is carried forward into the assessment.

## Workflow (the DRA-5C agent automates this)

1. **Step A — Context & Clarity:** tailored interview guide + questionnaire.
2. **Step B — Document & metadata review:** checklist of artifacts to request.
3. **Step C — Coverage & Credibility:** run the profiler on a sample, interpret the aggregates.
4. **Step D — Capacity & validation:** technical validation/load-test plan + the filled 5C scorecard.

## Scoring scale (per C)

| Score | Meaning |
|-------|---------|
| 1 | Not ready — fundamental gaps block the use case |
| 2 | Major gaps — significant remediation required before PoC |
| 3 | Workable — usable for a PoC with known caveats |
| 4 | Ready — minor improvements only |
| 5 | Strong — production-grade for this use case |

**Overall verdict:** Ready (all C ≥ 4) · Conditional (no C < 2, some 2–3) ·
Not ready (any C = 1 on a critical dimension).

## Reference deliverable

The output corresponds to the engagement deliverable listed in
`AI-Architect-Consulting-Work-Research.md` → Phase 1 → "数据就绪度评分卡
(Data Readiness Scorecard)".
