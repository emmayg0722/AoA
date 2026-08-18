# Classification taxonomy

Read this when classifying a sharpened problem (step 5 of the workflow). Four
axes, in order. Axis A is a gate — if a problem is not AI-shaped, record why and
stop; filling in B–D for a problem that should not be built as AI produces a
document that reads like a recommendation to build it.

**Contents**
- [Axis A — problem shape (the gate)](#axis-a--problem-shape-the-gate)
- [Axis B — AI archetype](#axis-b--ai-archetype)
- [Axis C — value mechanism](#axis-c--value-mechanism)
- [Axis D — decision class](#axis-d--decision-class)
- [Worked example](#worked-example)

---

## Axis A — problem shape (the gate)

The question: **if you built a perfect model tomorrow, would the anchor metric
move?** If the honest answer is no, the problem is shaped like something else.

| Shape | The tell | What actually fixes it |
|---|---|---|
| **Process-shaped** | The work is done differently by different people, or the handoff between two teams is where time disappears. Cycle time is dominated by waiting, not doing. | Map the flow and fix the queue. A model that produces output faster just enlarges the queue in front of the real bottleneck. |
| **Data-shaped** | The information needed to make the decision does not exist, is not captured, or is captured inconsistently. Staff work around it with local spreadsheets. | Instrumentation and ownership. This is often a real, fundable project — it is simply not a modelling project, and it usually has to happen first. |
| **Integration-shaped** | The answer exists in system A and is needed in system B, and today a person is the integration. | A pipeline or an API. Using a model to read one screen and type into another is expensive plumbing that fails in novel ways. |
| **Policy-shaped** | People know the right answer and do something else, because the incentive, the target, or the approval rule pushes the other way. | Change the rule or the incentive. Models do not overrule compensation plans. |
| **UX-shaped** | The capability exists but nobody can find, trust, or be bothered to use it. Adoption of the existing tool is low. | Interface and workflow placement. If they will not use the current tool, they will not use a smarter one. |
| **Capacity-shaped** | The work is well understood and correctly done; there is simply more of it than there are people. Demand exceeds supply at acceptable quality. | Often genuinely AI-shaped — but the case is throughput, not cost savings. Note it here, then treat as AI-shaped. |
| **AI-shaped** | The task requires judgement over unstructured or high-variance input, examples of good output exist, and volume is high enough that consistency matters. | Continue to axis B. |

**Mixed problems.** Most real problems are one AI-shaped core wrapped in two or
three others. Split them and name the sequence — "the retrieval piece is
AI-shaped; it is blocked by the data-shaped ownership question, which has to
resolve first" is far more useful than one averaged verdict.

**The order trap.** When a problem is both data-shaped and AI-shaped, the
data-shaped part is almost always first and almost always underestimated. Say
which one gates the other, explicitly.

---

## Axis B — AI archetype

Only for problems that cleared axis A. The archetype determines what data you
need, how you evaluate it, and what failure looks like — which is why getting it
right early saves an architecture rewrite later.

| Archetype | The task | What you need to build it | How you evaluate it | Characteristic failure |
|---|---|---|---|---|
| **Classify / route** | Put each item into one of a known set of buckets | Labelled examples per bucket; agreement between labellers | Precision and recall per class; confusion between adjacent classes | The taxonomy is wrong or overlapping, so humans disagree too |
| **Extract / structure** | Pull named fields out of unstructured input | Documents paired with correct field values | Field-level exact and fuzzy match | Rare formats, and fields that are legitimately absent |
| **Retrieve / answer** | Find the passage that answers a question and ground the answer in it | A corpus that actually contains the answers; real questions | Answer correctness *and* citation correctness, separately | Confident answers from stale or contradictory sources |
| **Generate / draft** | Produce a first draft a human finishes | Examples of good final output; a house style | Human edit distance and acceptance rate | Fluent, plausible, subtly wrong — and expensive to check |
| **Predict / forecast** | Estimate a future value or likelihood | History with outcomes; enough events; no leakage | Calibration first, then discrimination; against a naive baseline | Beating nothing — no baseline was ever computed |
| **Rank / recommend** | Order options by expected usefulness | Interaction history; a defensible relevance definition | Top-k relevance; counterfactual or online tests | Feedback loops that entrench what was already popular |
| **Detect anomaly** | Flag the unusual | Normal-operation history; some confirmed incidents | Detection rate at a workable false-positive budget | Alert volume exceeds the team's capacity to triage |
| **Plan / optimise** | Choose actions under constraints | An explicit objective and hard constraints | Objective value vs. current practice; constraint violations | The real constraints were never written down |
| **Act (agentic)** | Take multi-step actions in real systems | Reliable tools, permissions, rollback, audit trail | End-to-end task completion; blast radius when wrong | Compounding errors and unclear accountability |

**Two practical notes.**

*Prefer the simplest archetype that solves it.* Retrieval that returns the right
paragraph often beats generation that summarises it — cheaper, more auditable,
and it fails visibly rather than silently.

*The archetype constrains the accuracy bar.* Extraction feeding an automated
posting needs a far higher bar than drafting reviewed by a human. Settle the
archetype before anyone quotes a target accuracy, or the number is meaningless.

---

## Axis C — value mechanism

How the money actually arrives. This determines who sponsors the work and what
the business case must prove.

| Mechanism | Value arrives as | Sponsor usually | What the case must prove |
|---|---|---|---|
| **Cost** | Fewer hours or lower unit cost for the same output | Operations, shared services | That the freed hours are actually removed or redeployed — not just felt |
| **Revenue** | More conversions, larger deals, less leakage | Sales, commercial | Attribution against everything else changing at the same time |
| **Risk** | Fewer incidents, penalties, or losses | Risk, compliance, legal | A defensible base rate, and that avoided losses were genuinely likely |
| **Capacity** | More throughput at unchanged headcount | The line owner | That demand exists to absorb the extra capacity |
| **Quality** | Fewer errors, rework, or escalations | Quality, service | The current error rate — which is usually unmeasured |
| **Speed** | Shorter cycle time | The process owner | That the saved time is on the critical path, not in a queue |

**The two traps.** *Cost cases that nobody harvests* — savings modelled as FTE
reduction but never realised because nobody was reassigned. *Speed cases off the
critical path* — a step made ten times faster that sits in front of a two-week
approval queue changes nothing. Test both before writing the number down.

---

## Axis D — decision class

What the output changes, and who is accountable. This sets the accuracy bar and
the governance burden more than the archetype does.

| Class | Output goes to | Accuracy bar | Governance load |
|---|---|---|---|
| **Informing** | A human who was already deciding | Moderate; being useful beats being right | Low |
| **Recommending** | A human who will usually follow it | High; needs calibration and a reason shown | Medium — automation bias becomes real |
| **Deciding with review** | Executed unless a human intervenes | High; the review must be genuine, not a rubber stamp | Medium-high — measure whether reviewers actually catch errors |
| **Deciding autonomously** | Executed directly | Very high; needs monitoring and rollback | High — accountability must be assigned before launch |

Three questions worth asking here, because they surface problems that no amount
of model quality will fix:

1. **Who is accountable when it is wrong?** If nobody can answer, the class is
   aspirational rather than real.
2. **Does the affected person get an explanation and a route to challenge it?**
   For decisions about people — credit, hiring, benefits, access — this is
   usually a legal requirement, not a nicety.
3. **What is the blast radius of a bad batch?** One wrong answer to one user is
   recoverable; ten thousand wrong postings overnight is not.

**Escalation is a design choice, not a default.** Many use cases are proposed at
"deciding autonomously" and belong at "recommending" for the first year. Moving
down a class is usually the cheapest way to make a marginal case viable.

---

## Worked example

**The ask:** *"We want an AI agent that automatically handles our supplier
invoice queries so finance stops drowning in email."*

**Trigger:** two people left the AP team last quarter and were not replaced.

**Ladder up:** queries eat AP time → invoices are approved late → suppliers
chase, and early-payment discounts are missed. Anchor: *missed early-payment
discount value*, €410k last year, in the CFO's monthly pack. Owner: AP Manager.

**Ladder down:** observable today — queries per week (~600, in the shared
mailbox), median time to first response (3.1 days), share resolved without
touching the ERP (unmeasured).

**Decision changed:** whether an invoice is released for payment today or waits
for the next run. Made by AP clerks, ~600 times a week.

**Binding constraint:** roughly 70% of queries are one of four questions whose
answers already exist in the ERP. Clerks re-look-up the same facts constantly.
The other 30% are genuine disputes needing a human. Fixing the 70% moves the
metric; fixing the 30% does not.

**Classification:**

| Axis | Call | Why |
|---|---|---|
| Problem shape | **AI-shaped**, gated by integration-shaped | The lookup is a real retrieval task, but the ERP has no query API today — that gates everything |
| AI archetype | **Retrieve / answer**, not act | The four common questions are answerable from records; nothing needs to be *changed* to resolve them |
| Value mechanism | **Speed** → discount capture | Value is in shortening time-to-release, not in AP headcount |
| Decision class | **Informing** for now | Answers go to a clerk who still releases the payment; no reason to automate release in year one |

**What would change this:** pull 100 random queries from the mailbox and check
whether the 70/30 split holds and whether the answers really are in the ERP.
Half a day of work; it decides whether this is a project or not.

**Where it goes next:** the sharpened problem is *"AP clerks spend 3.1 days on
average answering supplier queries that are answerable from existing ERP
records, delaying invoice release and costing €410k a year in missed
early-payment discounts."* Note what changed — the ask named an autonomous agent
handling all queries; the problem is a read-only assistant answering four
questions for a clerk. That is a materially smaller and more likely build, and
the integration gap is the first thing to solve.
