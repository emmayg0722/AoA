# Common AI architecture decisions

Read when assembling options (step 3). Each entry gives the criteria that
usually decide the question and the tells that point one way or the other.

These are **starting positions, not verdicts.** Use them to avoid rediscovering
well-known trade-offs from scratch; do not use them to skip the scoring. The
whole point of the workflow is that the criteria for *this* system decide it.

**Contents**
- [Prompt vs RAG vs fine-tune](#prompt-vs-rag-vs-fine-tune)
- [Managed API vs self-hosted](#managed-api-vs-self-hosted)
- [Agent vs fixed pipeline](#agent-vs-fixed-pipeline)
- [Large model vs small model vs routing](#large-model-vs-small-model-vs-routing)
- [Build vs buy](#build-vs-buy)
- [Framework vs direct integration](#framework-vs-direct-integration)

---

## Prompt vs RAG vs fine-tune

**Usually decided by:** where the missing capability actually is — knowledge,
behaviour, or format — plus how often the underlying information changes.

| | Prompt engineering | Retrieval (RAG) | Fine-tuning |
|---|---|---|---|
| Fixes | Missing instruction or format | Missing *knowledge* | Missing *behaviour or style* |
| Freshness | N/A | Immediate — update the index | Stale until retrained |
| Time to value | Hours | Days to weeks | Weeks, plus a labelled set |
| Auditability | Good | **Best — you can cite the source** | Poor; behaviour is opaque |
| Reversibility | Trivial | Easy | Costly |

**Tells that point to retrieval:** the answer exists in documents someone could
find; information changes weekly or faster; you need to show *why* an answer was
given; the corpus is large relative to what fits in context.

**Tells that point to fine-tuning:** the model knows the facts but will not
produce the required form or tone; you have hundreds of good examples; the task
is narrow and stable; per-call cost at high volume justifies a smaller
specialised model.

**Tells that point to prompting alone:** you have not actually tried a careful
prompt yet. This is more common than it sounds, and it is by far the cheapest
option to test.

**The usual mistake:** reaching for fine-tuning to fix a knowledge problem. It
bakes facts in at a point in time, cannot cite sources, and goes stale silently
— three problems retrieval does not have. Fine-tuning teaches *how* to answer,
not *what* is true.

**Not exclusive.** Retrieval plus a careful prompt is the common production
shape; fine-tuning is added later for form and cost, not instead.

---

## Managed API vs self-hosted

**Usually decided by:** whether data may leave the boundary, and whether the team
can actually operate inference infrastructure.

**Tells that point to managed:** no hard data-residency constraint; the team has
no GPU or MLOps experience; volume is low or spiky; time to value matters;
model quality is the priority.

**Tells that point to self-hosted:** a genuine regulatory or contractual bar on
sending data out; very high steady volume where per-call cost dominates; strict
latency needs; a requirement to pin a model version for years.

**The honest questions:**

- *Does the constraint really exist?* "We can't send data to the cloud" is often
  a belief rather than a policy. Check the actual policy before designing around
  it — it is the single most expensive unexamined assumption in this decision.
- *Who operates it at 3am?* Self-hosting moves cost from a bill to a rota.
  Operability is a criterion, and the people carrying the pager should score it.
- *Have you priced it properly?* Self-hosting is cheaper per call at high steady
  volume and much more expensive at low or spiky volume, because idle GPUs bill
  the same as busy ones.

**Middle options worth including:** a managed service inside your own cloud
tenancy; a provider with a zero-retention contractual term; hybrid, where only
sensitive cases go to the local model.

---

## Agent vs fixed pipeline

**Usually decided by:** whether the sequence of steps is knowable in advance.

**Tells that point to a fixed pipeline:** the steps are the same every time; you
need predictable cost and latency; failures must be debuggable; the process is
already documented as a flowchart. **If you can draw it as a flowchart, build it
as a flowchart** — you get determinism, testability and a cost you can predict.

**Tells that point to an agent:** the path genuinely varies by input; the number
of steps is not knowable up front; the task requires interleaving decisions with
tool calls in a way no fixed order captures.

**What agents cost you, and it is easily underestimated:** unpredictable cost and
latency; compounding errors, since 95% per step over ten steps is about 60%
end-to-end; harder debugging; a larger blast radius when something goes wrong.

**The middle ground that is usually right:** a fixed pipeline with one or two
model-driven decision points. You keep determinism where it matters and get
flexibility where you need it. Most systems described as agents in production
are this.

---

## Large model vs small model vs routing

**Usually decided by:** the cost-to-quality curve at your actual volume, and how
much of your traffic is genuinely hard.

**Tells that point to one large model:** low volume, where the cost difference is
noise against engineering time; wide task variety; you are still learning what
the system needs to do.

**Tells that point to a small model:** high volume on a narrow, well-defined
task; tight latency budget; a good evaluation set proving the small model clears
the bar.

**Tells that point to routing:** a clear split between an easy majority and a
hard minority, with a cheap way to tell them apart.

**Sequence this properly.** Build with the strongest model, establish quality,
*then* try to reduce cost with the evaluation harness as your safety net.
Optimising cost before quality is established means you cannot tell whether a
regression came from the cheaper model or from the change you made at the same
time. Routing without an eval set is a cost saving you cannot measure the price
of.

---

## Build vs buy

**Usually decided by:** whether this capability is a differentiator or a
commodity, and honestly how long "build" takes.

**Tells that point to buy:** it is a commodity every competitor has; you need it
this quarter; the vendor's data model fits your process without heavy
adaptation; you have no team to maintain a build.

**Tells that point to build:** the capability *is* the differentiator; your
process is genuinely unusual and configuring the product would fight it; unit
economics at your volume make licensing dominate; the vendor lock-in is on
something strategic — your data, your customers' data, your core workflow.

**Two things people get wrong in both directions:**

- **Build estimates omit the run.** The build is the smaller number. Maintenance,
  on-call, upgrades and the eval harness continue for the system's life.
- **Buy estimates omit the fit.** Configuration, integration, data migration and
  process change are frequently larger than the licence, and they are the part
  that overruns.

**Ask what happens on exit.** Where does your data live, in what format, and what
does leaving cost? For anything holding embeddings, conversation history or
labels, that answer is a one-way-door consideration.

---

## Framework vs direct integration

**Usually decided by:** how much of the framework you will actually use, and how
stable your requirements are.

**Tells that point to a framework:** you are prototyping and speed matters; you
need many integrations you would otherwise write yourself; the team is new to
the domain and the framework's structure is genuinely teaching them.

**Tells that point to direct integration:** the application is one or two calls
plus your own logic; you have hit the framework's abstractions fighting you
before; you need to debug production behaviour precisely; long-term maintenance
matters more than initial speed.

**The pattern that recurs:** frameworks are excellent for the first 80% and
expensive for the last 20%, because that is where you fight abstractions to do
something they did not anticipate. If your requirements are unusual, you will
reach that 20%.

**A reasonable middle:** use the framework's well-isolated pieces — document
loaders, splitters, connectors — without adopting its orchestration. Keep your
own control flow, since that is the part you will need to debug.
