# Document & Metadata Review Checklist

> Step B deliverable. Artifacts to request from the client, why each matters, and
> what "good" vs. "red flag" looks like. Tailor the data-specific rows to the use case.

**Engagement:** [name]  ·  **Use case:** [one-line]

| # | Artifact to request | Informs | Why it matters | "Good" looks like | Red flag |
|---|---------------------|---------|----------------|-------------------|----------|
| 1 | Data dictionary for [datasets] | Clarity | Confirms field meaning & units | Current, owned, covers all key fields | Missing, stale, or partial |
| 2 | Data lineage / flow diagrams | Context | Shows origin & transforms | End-to-end, source→consumption | Unknown/undocumented hops |
| 3 | ER diagrams / schemas (DDL) | Clarity/Coverage | Keys, types, relationships | Versioned, matches reality | Drifts from actual data |
| 4 | Source-system inventory & owners | Context | Accountability for quality | Named owners per source | No clear ownership |
| 5 | Update cadence / SLA docs | Coverage/Credibility | Freshness vs. use-case need | Documented refresh schedule | Ad-hoc/unknown refresh |
| 6 | Data quality reports / DQ rules | Credibility | Existing quality signal | Monitored metrics, trends | None exist |
| 7 | Retention & privacy/classification policy | Context/Capacity | Legal basis & constraints | Clear classification + retention | Sensitive data, no policy |
| 8 | Pipeline / ETL documentation | Capacity | Reproducibility & scale | Versioned, tested pipelines | Manual, undocumented scripts |
| 9 | Access control / security model | Capacity | Whether AI workload can access | Role-based, documented | Unclear or blocking |
| 10 | [use-case-specific artifact] | [C] | [why] | [good] | [red flag] |

## Notes
- For each item received, record: present? · current? · who owns it? · gaps found.
- Roll the findings into the Context, Clarity, and (partially) Coverage scores in the scorecard.
