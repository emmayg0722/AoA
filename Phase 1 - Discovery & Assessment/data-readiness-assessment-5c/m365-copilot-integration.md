# Integrating DRA-5C with Microsoft 365 Copilot — Feasibility & Architecture

> Status: **feasibility study (no code yet).** This document evaluates whether and how
> the Data Readiness Assessment (5C) tooling could leverage Microsoft 365 Copilot to
> make client-data gathering easier, and recommends a staged path.

## 1. The problem & the core misconception

DRA-5C's slowest part is **getting at the client's data and documentation** — data
dictionaries, lineage, schemas, sample exports. M365 Copilot is attractive because it
*already* has governed access to a client's company data, so the instinct is: "if we
connect to their Copilot, gathering this evidence gets much easier."

The important correction: **you don't "connect to" Microsoft 365 Copilot as an external
endpoint.** Copilot's data access is not a feature of Copilot you can call from outside —
it comes from **Microsoft Graph**, scoped to a single tenant, and gated by **Entra ID
(Azure AD) app registration + admin consent**. Copilot is one consumer of Graph; it
respects the same permissions, sensitivity labels, and DLP that govern everything else.

So "collaborate with Copilot" really resolves to one of two distinct things:

- **(a) Build something that runs *inside the client's* Copilot** — an agent grounded on
  their own Graph/SharePoint content. Their data stays in their tenant.
- **(b) Pull the client's data *into our* tooling via Graph** — a backend that authenticates
  into their tenant and reads metadata/files. Their data leaves their environment.

Both are real and useful. Both are a **meaningfully heavier tier** than today's DRA-5C
(static HTML, no backend, no API keys, raw data stays in the browser), because both touch
the client's tenant, security review, and per-client onboarding. That cost is appropriate
for a paid engagement and overkill for a portfolio demo — which is exactly why this is a
deliberate decision, not a default.

## 2. Three integration options

### Option A — Lightweight "Copilot prompt-pack" (no infrastructure)

Give the architect (or the client's own staff) a curated set of prompts they run **in the
client's existing M365 Copilot**, which already has the data access and admin blessing.
Copilot surfaces the relevant data dictionaries, SharePoint schemas, ownership, and policy
docs; the human pastes those answers into the DRA-5C **console** (`console.html`), exactly
like today's paste-based flow — Copilot simply becomes a data-grounded source alongside the
`dra-5c` agent.

```
Client's M365 Copilot  ──(answers, in their tenant)──►  human  ──paste──►  DRA-5C console
        ▲ grounded on their SharePoint/Graph
```

- **Infra:** none. **Tenant setup:** none on our side. **Data residency:** stays in client tenant.
- Fits the current design unchanged; works the day a client has Copilot.

### Option B — DRA-5C declarative agent inside the client tenant

Package the DRA-5C methodology as a **declarative agent** (built with **Copilot Studio**
low-code, or the **Microsoft 365 Agents Toolkit** pro-code) and deploy it **into the client's
tenant**. It runs inside their M365 Copilot, grounded on selected SharePoint sites / Graph
content, and walks the Context/Clarity/Coverage questions natively against their data.

```
Client tenant:  M365 Copilot + [DRA-5C declarative agent] ── grounded on ──► their SharePoint/Graph
                (deployed & approved by their Copilot/tenant admin)
```

- **Infra:** agent manifest + knowledge config; deployed per tenant by **their** admin.
- **Data residency:** stays in tenant. **Most "native" UX**, but it's a separate product with
  a per-client admin deployment and lifecycle, decoupled from our HTML console.

### Option C — Backend + Microsoft Graph auto-pull

A hosted service registers an Entra ID app in the client tenant, obtains **admin consent** for
read scopes (e.g. `Sites.Read.All`, `Files.Read.All`, `Sites.Selected` for least-privilege),
and **programmatically pulls** SharePoint lists/columns, file inventories, and data
dictionaries to **auto-populate Steps B/C** of the assessment.

```
Our backend ──OAuth/app perms──► Microsoft Graph (client tenant) ──metadata──► DRA-5C
   (hosts tokens; raw/derived data leaves the client environment)
```

- **Infra:** hosted backend, secret/token management, app registration, **admin consent**.
- **Data residency:** data **leaves** the client tenant → triggers the heaviest security/compliance
  review. Most automated, but highest cost and risk.

## 3. Comparison

| Dimension | A — Prompt-pack | B — Declarative agent | C — Backend + Graph |
|---|---|---|---|
| Data residency | Stays in client tenant | Stays in client tenant | **Leaves** tenant (to our backend) |
| Who sets it up | Nobody (use their Copilot) | Client's Copilot/tenant admin | Client's Entra admin + us |
| Admin consent / permissions | None (uses their existing Copilot) | Tenant admin publishes the agent | **Admin consent** on Graph scopes |
| Infra we host | None | None (lives in their tenant) | Backend + token store |
| Engineering effort | Low (write prompts) | Medium (agent build + deploy) | High (backend, auth, security) |
| Per-client repeatability | Instant | Per-tenant deploy each time | Per-tenant app reg + consent each time |
| Time-to-value | Immediate | Days–weeks per client | Weeks+ (incl. security review) |
| Ongoing cost | ~zero | Agent lifecycle per tenant | Hosting + maintenance + audits |
| Key risks | Prompt quality; manual | Tenant deployment/governance | DLP/Purview, sensitivity labels, data-residency, token security |
| Fits current design | **Yes** | Partially (separate product) | No (inverts no-backend/data-local) |

## 4. What it actually buys DRA-5C (mapping to the 5 C's)

Copilot/Graph integration helps the **document- and metadata-heavy** parts most, and barely
touches the parts that need real data computation:

| Step / C | Does Copilot help? | Why |
|---|---|---|
| **Step A/B — Context & Clarity** | **Yes, a lot** | Copilot is grounded on the client's docs/SharePoint — ideal for surfacing data dictionaries, lineage notes, ownership, policies. This is the biggest, fastest win. |
| **Step C — Coverage & Credibility** | **No — keep the local profiler** | Copilot/Graph won't compute fill-rate, duplicate-rate, or type-consistency on raw tables, and **raw rows should not be sent to an LLM**. The browser-local profiler stays the right tool; only aggregates flow onward. |
| **Step D — Capacity** | No | Infra/latency/load is a systems assessment, unrelated to Copilot. |

**Conclusion:** the integration is an *accelerator for Context/Clarity evidence gathering*,
not a replacement for the assessment. The **local profiler remains essential in every option.**

## 5. Recommendation (staged)

1. **Start with Option A.** Zero infrastructure, immediate, respects data residency, fits the
   current design. Ship a "Copilot prompt-pack" the architect runs in the client's Copilot and
   pastes into the console. This captures most of the "much easier" benefit at near-zero cost.
2. **Productize to Option B** when engagement volume justifies a per-tenant agent — when clients
   want the assessment to live natively in their own Copilot.
3. **Reserve Option C** for cases where automated metadata pull clearly beats the cost of a
   backend + a client security review. Default to `Sites.Selected` / least-privilege if pursued.

In all three, the browser-local profiler stays, and raw client data is never sent to an LLM.

## 6. What we'd need from a client to do B or C

- A named **tenant / Copilot administrator** as sponsor.
- **Entra ID app registration** (for C) and **admin consent** on the agreed read-only scopes.
- For B: the **SharePoint sites / Graph content** to ground the agent on, and a publish/approval path.
- A **security/compliance review** (DLP, Purview sensitivity labels, data-residency requirements).
- Confirmation that the client actually has **M365 Copilot licensing** for the relevant users.

---

*This is a planning artifact. No code, app registration, or tenant connection has been built.*
