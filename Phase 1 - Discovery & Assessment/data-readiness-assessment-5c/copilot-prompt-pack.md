# M365 Copilot Prompt-Pack for DRA-5C (Option A)

> The lightweight, zero-infrastructure integration. Run these prompts in the **client's
> own Microsoft 365 Copilot** (which already has governed, in-tenant access to their data),
> then paste the **findings** into the DRA-5C console's "Copilot findings" boxes on Steps A
> and B. The console can generate tailored versions of these prompts for you — this file is
> the reference and the client-facing explainer.

## How to use

1. Open the client's **M365 Copilot** (work/enterprise data mode — not the consumer web one).
2. Replace the placeholders: `[use case]`, `[entities]` (the data objects the use case needs,
   e.g. *applicant, bureau pull, transactions*), `[key fields]`, `[metric]`.
3. Run each prompt; Copilot answers from their SharePoint/Teams/OneDrive/Graph content **and
   cites its sources**.
4. Paste the **summaries + citations** into the DRA-5C console (Step A → "Copilot findings",
   Step B → "Copilot findings"). The `dra-5c` agent then folds them into the interview guide
   and document checklist.

### Privacy note (important)

Copilot already respects the client's existing permissions, sensitivity labels, and DLP — it
only returns what the running user may see. Still: **paste summaries, definitions, and source
citations into the console — never raw sensitive records.** The actual-data spot-check
(Coverage/Credibility) stays in the local **profiler**; raw rows never go to an LLM.

---

## Step A — Gather answers (Context & Clarity)

**A1 · Source-system inventory** *(Context)*
> List the systems, databases, and repositories that hold data about **[entities]** relevant
> to "**[use case]**". For each: what it contains, the team or person who owns it, and how
> often it's updated. Cite the documents or sites you used.

**A2 · Data lineage / flow** *(Context)*
> Find any data lineage, data-flow, or architecture documents describing how **[entities]**
> data moves from its source systems to reporting or analytics. Summarize the end-to-end flow
> and any transformation or enrichment steps in between, with citations.

**A3 · Ownership & stewardship** *(Context)*
> Who are the data owners and data stewards for **[entities]**? Look in org charts, RACI
> documents, data-governance pages, and SharePoint site ownership. List names/roles and the
> source for each.

**A4 · Field & data-dictionary definitions** *(Clarity)*
> Find the data dictionary or documented field definitions for **[key fields]** in
> **[entities]**. For each field, give the business definition, unit, and allowed values.
> Flag any field where the definition is missing, ambiguous, or inconsistent across documents.

**A5 · Metric-definition consistency** *(Clarity)*
> How is "**[metric]**" defined across teams and documents in our organization? Show each
> definition you find, who uses it, and highlight any conflicts or differences in how it's
> calculated. Cite sources.

---

## Step B — Locate documents (Clarity & doc/metadata review)

**B1 · Data dictionary** *(Clarity)*
> Locate the most current data dictionary covering **[entities]**. Give its title, location/
> link, owner, and last-modified date. If several exist, note which looks authoritative and
> whether any are out of date.

**B2 · Schema / ER diagrams** *(Clarity / Coverage)*
> Find ER diagrams, table schemas, or SharePoint/Dataverse list structures for **[entities]**.
> Summarize the keys, the grain (one row per what?), and the relationships, with links.

**B3 · Retention, privacy & classification policy** *(Context / Capacity)*
> Find data retention, privacy, and data-classification policies that apply to **[entities]**.
> Summarize retention periods, any sensitivity classifications, and constraints on using this
> data for "**[use case]**". Cite the policy documents.

**B4 · Pipeline / ETL documentation** *(Capacity-adjacent)*
> Find documentation for the pipelines or ETL/ELT jobs that produce or move **[entities]**
> data. Summarize what's automated vs. manual, and where the documentation looks thin. Link
> the sources.

**B5 · SLA, refresh cadence & data-quality reports** *(Coverage / Credibility context)*
> Find any SLA documents, refresh-cadence schedules, or data-quality reports for the
> **[entities]** feeds. Summarize how often the data updates and any known quality issues
> already documented. Cite sources.

---

## What this does and doesn't cover

- **Covers:** the document- and metadata-heavy evidence for **Context** and **Clarity** — the
  parts Copilot's data grounding genuinely accelerates.
- **Doesn't cover:** the actual-data **Coverage/Credibility** measurement (fill rate, duplicate
  rate, type consistency, freshness). That stays in `profiler.html` — Copilot won't compute it
  on raw tables, and raw rows shouldn't be sent to an LLM. **Capacity** is a separate infra/
  load assessment.

See `m365-copilot-integration.md` for the full feasibility comparison and the heavier options
(declarative agent in-tenant; backend + Graph auto-pull).
