# Data Readiness Interview Guide & Questionnaire

> Step A deliverable. Tailor every question to the specific use case — replace the
> bracketed prompts. Each question is tagged with the C it informs.

**Engagement:** [client / engagement name]
**Target AI use case:** [one-line description — what it predicts/decides]
**Data the use case needs:** [entities, fields, granularity, latency, history]

## Interview targets
- [ ] Business owner of the use case
- [ ] Data owner(s) / steward(s) for the relevant domains
- [ ] Data engineering / platform lead
- [ ] [other relevant stakeholders]

## A. Source & lineage  *(Context)*
1. Which systems originate the data this use case needs? [tailor per dataset]
2. How does data flow from source to where we'd consume it? Any transforms in between?
3. Who owns each source system, and who is accountable for its data quality?
4. How often is each source updated, and is that cadence enough for the use case?

## B. Semantics & definitions  *(Clarity)*
5. For each key field [list them], what is the agreed business definition and unit?
6. Do different teams define [key metric] the same way? Where do definitions diverge?
7. Are there documented data dictionaries / schemas? How current are they?
8. What known ambiguities or "gotchas" exist in these fields?

## C. Completeness & history  *(Coverage)*
9. How far back does usable history go for [entity]? Are there gaps?
10. Which segments/populations are well-covered vs. thin? [tailor to use case]
11. Are required fields [list] populated reliably, or often blank?

## D. Quality & trust  *(Credibility)*
12. What's the known error/duplicate rate? Any reconciliation against a source of truth?
13. How stale can data be before it's a problem for this use case?
14. Have past analytics/AI efforts hit data-quality issues here? What happened?

## E. Scale & access  *(Capacity)*
15. What's the data volume and growth rate? Velocity (batch vs. streaming)?
16. Where does it live, and how would an AI workload access it (latency, throughput)?
17. Any privacy/residency/access constraints on using it for [use case]?

## Questionnaire (leave-behind, self-serve)
Provide the above as a written form the client can complete asynchronously, with
space for evidence/links to docs per answer.
