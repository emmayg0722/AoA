# Cost checklist

Read when building the cost side of the model. The pattern in failed AI business
cases is almost never an overstated benefit — it is an understated run cost. The
build gets estimated carefully because someone has to quote it; the run cost
gets a round number because nobody owns it yet.

Work through both tables. Anything you deliberately exclude should be named as
excluded rather than silently dropped, so a reviewer can see the boundary of the
model.

## Build (one-off)

| Item | Commonly missed because |
|---|---|
| Discovery and solution design | Treated as pre-project, though it is real spend |
| Data work — access, cleaning, labelling | Labelling in particular is estimated from a sample and scales worse than expected |
| Integration into the systems of record | The demo runs standalone; production needs auth, error handling, and someone's change-approval process |
| Evaluation harness and test set | Without it you cannot tell whether a change made things worse, so it is not optional |
| Security review, DPIA, procurement | Calendar time as much as cost, and it gates go-live |
| Change management and training | Budgeted as a launch email; behaves like a workstream |
| UAT and pilot support | Real hours from the business, not just the delivery team |

## Run (annual)

| Item | Commonly missed because |
|---|---|
| Inference / token cost at production volume | Pilot volume hides it. Model peak and average separately, and re-check after any prompt or context change |
| Hosting, vector store, orchestration | Usually small, but grows with retained history |
| Human review time | If the design keeps a human in the loop, that time is a permanent operating cost — and it is the one that most often exceeds the licence spend |
| Monitoring and on-call | Someone has to notice when quality drifts |
| Model refresh and prompt maintenance | Upstream model changes force periodic re-validation whether or not you initiated them |
| Re-labelling and eval upkeep | Test sets go stale as the business changes |
| Support and triage of escalations | New failure modes arrive at a helpdesk that was not scoped for them |
| Licence and vendor fees | Often per-seat, so it scales with the adoption you are forecasting as a benefit |

## Two costs worth modelling explicitly

**Human review.** If the design is "recommending" or "deciding with review",
review time is not overhead — it is the largest recurring cost in many cases.
Model it as a `minus_terms` entry on the driver it belongs to, so the benefit
nets out honestly rather than being reported gross and quietly funded elsewhere.

**Inference at real volume.** Take production volume, multiply by cost per call,
and put it in `run_annual` as its own line. Then check the sensitivity output:
if inference cost is near the top of the tornado, the architecture needs a
cheaper path (smaller model, caching, retrieval instead of long context) before
the business case is worth presenting.

## Costs that are usually out of scope — say so

Naming these keeps the model honest without inflating it:

- Existing staff time for business-as-usual work the solution does not change
- Infrastructure already paid for and not incremental to this project
- Sunk discovery cost from before the decision point

## A note on comparing to "do nothing"

Doing nothing is rarely free, and a model that treats it as free understates the
case. If the current process is already growing headcount, missing SLAs, or
accruing risk, the counterfactual has a cost curve of its own. Model it when it
is material — but only with the same `basis` labels you apply everywhere else,
since an inflated do-nothing cost is the easiest way to make a weak case look
strong, and the easiest thing for a reviewer to catch.
