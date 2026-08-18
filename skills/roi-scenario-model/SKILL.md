---
name: roi-scenario-model
description: >-
  Build a defensible, scenario-based ROI case for one AI solution — conservative
  / base / optimistic side by side, with NPV, payback, sensitivity showing which
  assumption the case actually rests on, and the breakeven value that assumption
  has to clear. Use whenever someone asks for the ROI, business case, cost-
  benefit, payback period, TCO, NPV, or "is this worth building" for an AI or
  automation initiative, or wants to compare best-case and worst-case outcomes
  for a single solution. Use it especially when a single-point ROI number is
  being requested or quoted, since one number invites the reader to attack the
  assumption they distrust most — scenarios and a breakeven survive that
  conversation, a point estimate does not.
---

# ROI Scenario Model

A single ROI number is a hostage to its weakest assumption. Someone in the room
distrusts one input, challenges it, and the whole case collapses — not because
the case was wrong, but because it was presented as a certainty it never had.

The fix is to stop arguing about the number and start showing the shape: what it
looks like when things go badly, what has to be true for it to work, and how
much room there is before it stops working. This skill builds that.

## Two rules that keep the case credible

**Label every figure as measured, estimated, or assumed — and keep the labels
in the final document.** A reader who cannot tell which is which will discount
all of them the moment one is questioned. Labels also make the conversation
productive: nobody argues with a measured number, and everybody knows to probe
the assumed ones.

**Model the benefit the business will actually feel, not the benefit the
arithmetic permits.** Hours saved are not money saved until someone is
redeployed or not hired. This gap is the single most common reason a delivered
AI project fails its own business case, and the model has an explicit lever for
it (`realization`).

## Workflow

### 1. Pin down what is being valued

Before any arithmetic, get four things straight. If the answer to the first is
vague, stop and sharpen the problem first — an ROI model on a fuzzy problem
produces confident nonsense.

- **The change** — what will be different in the business once this works?
  Stated as an operational change, not a technology deliverable.
- **The counterfactual** — what happens if you do nothing? If the baseline is
  already improving on its own, you can only claim the delta above that trend.
- **The horizon** — 3 years is the usual default. Beyond 5, nobody believes it.
- **Who owns the number** after the engagement ends. An ROI case nobody is
  accountable for stops being checked the month after it is presented.

### 2. Build the benefit as a driver tree, never a lump sum

Decompose each benefit into a product of quantities someone can source:

> `queries_per_year × share_answerable × hours_saved_per_query ×
> loaded_hourly_cost`

This matters for a reason beyond tidiness. A lump sum ("€400k of efficiency")
can only be accepted or rejected. A product of named quantities can be
*negotiated* — a finance reviewer can push back on one term, you adjust it, and
the case survives with its credibility intact.

Give every driver a `basis` of `measured`, `estimated`, or `assumed`, and be
honest. If most of the value sits in `assumed` drivers, that is the finding, and
the recommendation is usually to go measure before committing budget.

### 3. Count the costs the business will actually feel

Build and run, including the ones people routinely forget. Read
`references/cost-checklist.md` for the full list — inference and token cost at
production volume, human review time, data work, integration, change management
and training, model refresh, and the evaluation harness that stops you shipping
regressions. Underestimating run cost is what turns a 3-year winner into a
2-year loser.

### 4. Choose the scenarios, and make them mean something

Three is the useful number: **conservative**, **base**, **optimistic**.

The discipline that makes them worth reading: each scenario must differ by
*named assumption changes*, not by a mood. "Conservative" is not "base times
0.7" — it is base with adoption at 50% instead of 70% and realization at 60%
instead of 80%, because those are the two things most likely to disappoint.

A good conservative case is one the sponsor recognises as genuinely possible. If
it still looks comfortable, you have not been conservative; you have been
decorative. Consider whether the conservative case should include the project
landing late, since it usually does.

### 5. Run the model

The bundled script does the arithmetic — cash flows, NPV, payback, ROI,
sensitivity, and breakeven — so you do not re-derive it each time and cannot
quietly get the discounting wrong:

```bash
python scripts/roi_model.py --example > spec.json   # starter spec to edit
python scripts/roi_model.py spec.json               # markdown report
python scripts/roi_model.py spec.json --format json # machine-readable
```

Write the spec from step 2–4. The full field reference is in
`references/spec-format.md`. Validation is deliberately strict — a driver
referencing an assumption that does not exist is an error rather than a silent
zero, because a silently-zeroed benefit ships as a number someone trusts.

If Python is unavailable, the formulas in `references/spec-format.md` are simple
enough to do by hand — but prefer the script, because hand-rolled payback
interpolation and discounting are where arithmetic errors hide.

### 6. Read the sensitivity honestly

The tornado ranks assumptions by how much the NPV swings when each moves ±20%
alone. Two things to take from it:

**The top row is the number worth arguing about.** It is frequently not the one
being debated. Redirecting a meeting from a contested cost line to the adoption
rate that actually drives the case is one of the more valuable things this
analysis does.

**Identical swings mean one lever, not four.** Terms multiplied together in the
same driver always produce identical ±20% swings — they are mathematically the
same knob. Say so rather than presenting four rows as four independent risks.
When that happens, the real question is which of those terms you can actually
influence.

### 7. Lead with breakeven

`breakeven_on` solves for the value where NPV crosses zero. This reframes the
whole conversation:

> "Adoption has to reach 35% for this to wash. We have assumed 70%. The last
> two rollouts in this org hit 55% and 80%."

Now the sponsor is judging a claim against evidence they have, instead of
accepting or rejecting a number you produced. Pick the assumption that is both
uncertain and consequential — usually the tornado's top row that is also
`assumed` rather than `measured`.

### 8. Write it up

```markdown
## Recommendation
[Proceed / proceed with conditions / do not proceed, and the one reason.]

## The case in three scenarios
[Scenario table: NPV, payback, benefit, cost, ROI.]

## What we are valuing
[The operational change, the counterfactual, the horizon, the owner.]

## Value drivers
[Table with basis labels. Flag if most value sits in 'assumed' rows.]

## Costs
[Build and run, including review time and change effort.]

## What the case rests on
[Top sensitivity rows, collapsed where they are the same lever.]

## Breakeven
[The assumption, the value it must clear, and evidence for or against.]

## What would change this conclusion
[The cheapest measurement that would firm up the biggest 'assumed' driver.]

## Who owns this number
[Name, and when it gets re-checked.]
```

## Traps that invalidate a case

Check each before presenting. Every one of these has sunk a real business case
after delivery, which is a much more expensive place to discover it.

- **Savings nobody harvests.** Hours released across many people rarely become
  money. Either name the redeployment or reduce `realization` and say why.
- **Double counting across use cases.** Three projects each claiming 20% of the
  same team's time have claimed 60% of it. Track claims against a shared pool.
- **Speed off the critical path.** A step made ten times faster in front of a
  two-week approval queue changes nothing measurable.
- **Attribution.** If anything else changed in the same period — a reorg, a
  pricing change, a seasonal peak — before-and-after is not attribution, and
  claiming it is will not survive a serious finance review.
- **Optimism about ramp.** Adoption curves are slower than plans. If the ramp
  has never been validated in this organisation, the conservative case should
  assume a year one that is mostly cost.
- **Inference cost at real volume.** Pilot volumes hide it. Model production
  volume explicitly, and re-check it as a run cost, not a rounding error.
- **The counterfactual of doing it later.** Sometimes waiting six months is
  genuinely better — cheaper models, clearer requirements. Say so when true;
  the credibility carries into every case you present afterwards.

## When the answer is no

If the conservative case is negative and the breakeven requires an assumption
nobody can defend, say the case does not hold. Then offer the two constructive
paths, because a flat "no" is rarely the whole truth:

- **Shrink it.** A narrower scope with a smaller build cost frequently passes
  where the full version fails. Model the narrow version rather than only
  reporting the failure.
- **Measure first.** If the swing sits on one `assumed` driver, propose the
  cheap measurement that would resolve it. That is a real, fundable next step
  and a far better outcome than a padded case that fails eighteen months later.

## Where this fits

This is late-stage work: it needs a sharpened problem, a scoped solution, and
enough architecture to cost the build. Running it earlier produces a model whose
inputs are all `assumed`, which is worse than no model — it carries false
authority.

Its natural inputs are a sharpened problem statement and a solution scope; its
natural outputs are a go/no-go recommendation and, once delivered, the baseline
that value-tracking measures actual benefit against.
