---
name: business-problem-sharpener
description: >-
  Turn a vague, solution-shaped business request into a sharp, measurable,
  solution-free problem statement, then classify it — whether it is actually an
  AI problem at all, which AI archetype fits, what value mechanism it runs on,
  and which decision it changes. Use this whenever someone brings a business
  problem, an AI use-case idea, a "we want a chatbot / copilot / agent / model
  for X" request, a project brief, an intake form, a stakeholder complaint, or
  an RFP paragraph and wants to know what the real issue is, whether it is worth
  pursuing, or how to categorise it. Use it early in discovery, before scoping,
  estimating, or designing anything — and especially when the ask already names
  a technology, since that is the strongest sign the real problem has not been
  stated yet.
---

# Business Problem Sharpener

Most business problems arrive pre-solved. Someone says "we need an AI chatbot
for customer service," and buried inside that sentence is an unexamined chain:
a symptom someone noticed, a cause they guessed at, and a solution they picked.
Your job is to pull that chain apart, find out which link is actually load-
bearing, and hand back a problem statement sharp enough to design against.

This matters because the cost of a wrong problem statement compounds. A muddy
problem produces a muddy architecture, and nobody discovers the mismatch until
the pilot fails to move a number anyone cares about.

## The one rule that makes this work

**Be willing to conclude it isn't an AI problem.** A large share of requests
that arrive dressed as AI use cases are process, data, integration, or incentive
problems wearing a costume. Saying so is the single most valuable thing this
skill does — it is what separates an architect from an order-taker.

If the honest answer is "your handoffs are broken and a model will just generate
polite responses faster," say that plainly, then say what would fix it. Do not
soften it into a recommendation to build the thing anyway.

## Workflow

Work through these in order. Steps 1–3 are interrogation, 4 is judgement, 5–6
are the deliverable.

### 1. Record the ask verbatim

Capture the request exactly as it was said, including the technology name and
any emotive language. Do not tidy it. The original wording is evidence — the
words people reach for reveal what they think is broken, and you will want to
show the before-and-after at the end.

Then separate four things that are usually tangled in one sentence:

- **Trigger** — what happened recently that made this come up now? Problems
  rarely get raised on their merits; something forced it (a bad quarter, a
  competitor launch, a complaint from a board member, a departing employee).
- **Stated solution** — the technology or approach they already named.
- **Claimed outcome** — the benefit they expect.
- **Requester** — who is asking, and is it their number that moves?

If the trigger is a person rather than a metric ("the CEO saw a demo"), note it.
That is not disqualifying, but it changes how you validate everything after.

### 2. Ladder up to a number the business already tracks

Ask "why does that matter?" repeatedly until you reach a metric that appears in
a report someone already receives. Stop there — going further gets you to
"shareholder value," which is true and useless.

The test for a good stopping point: **could you look up its current value this
week?** If yes, you have found the anchor. If the ladder dead-ends in something
nobody measures, that is itself a finding — the problem may be real but
currently invisible, and instrumenting it is the first project, not the model.

Watch for the ladder splitting. "Handling time is too high" may serve both cost
reduction and customer satisfaction, and those pull toward different designs.
When it splits, make the requester choose which one is primary; a use case
optimising two masters usually satisfies neither.

### 3. Ladder down to something observable today

Now the opposite direction: "how would we know this problem is solved?" Push
until you reach something you could observe or count in the current system,
without building anything new.

This is where most problem statements quietly fail. If nobody can describe a
measurement that exists today, you cannot prove improvement later — and an AI
project with no baseline is unfalsifiable, which means it can never be declared
successful either.

Then ask the question that decides whether any of this is worth doing:

> **What decision changes because of this?** Who makes it, how often, and what
> do they do differently?

If no human and no system behaves differently as a result of the output, there
is no value to capture regardless of how good the model is. That is a reporting
or curiosity project. Name it as such.

### 4. Find the binding constraint

You now have a set of candidate causes. Only some of them are load-bearing.
For each one, ask: **if this were fixed tomorrow and nothing else changed, would
the anchor metric move?**

Usually one or two survive. The rest are real irritations that are not the
reason the number is what it is. Removing a non-binding constraint feels
productive and changes nothing — which is exactly how AI pilots end up
technically successful and commercially pointless.

Where the requester disagrees with your read, do not overrule them from the
armchair. Name the disagreement, and specify the cheapest evidence that would
settle it. That evidence request is often the most useful line in the document.

### 5. Classify

Four axes, in this order. The first is a gate — if it fails, the rest are
academic and you should say so rather than filling them in for completeness.

Read `references/taxonomy.md` for the full category definitions, the tells that
distinguish them, and the data and evaluation implications of each AI archetype.
The short version:

- **A · Problem shape** — is this AI-shaped, or is it process-, data-,
  integration-, policy-, UX-, or capacity-shaped? This is the gate.
- **B · AI archetype** (only if A says AI-shaped) — classify / extract /
  retrieve / generate / predict / rank / detect / plan / act. This determines
  what data you need and how you will evaluate it.
- **C · Value mechanism** — cost, revenue, risk, capacity, quality, or speed.
  Determines who sponsors it and what the business case has to prove.
- **D · Decision class** — what decision the output changes, and whether a human
  stays in the loop. Determines the accuracy bar and the governance burden.

A problem can be genuinely mixed. When it is, split it into named sub-problems
and classify each, rather than averaging them into a blur. Two clean problems
beat one muddy one, and they can be sequenced.

### 6. Write it up

Use this structure. Keep the sharpened statement to one or two sentences — if it
needs a paragraph, it is still more than one problem.

```markdown
## Sharpened problem
[One or two sentences. Solution-free, measurable, bounded, owned.]

## What was asked for, and what the problem turned out to be
| | |
|---|---|
| **Asked for** | [verbatim] |
| **Trigger** | [what made this surface now] |
| **Real problem** | [the binding constraint] |
| **Anchor metric** | [metric, current value, source, owner] |

## Classification
| Axis | Call | Why |
|---|---|---|
| Problem shape | | |
| AI archetype | | |
| Value mechanism | | |
| Decision class | | |

## What would change the diagnosis
[The cheapest evidence that would prove this reading wrong. Be specific:
which report, which sample, which conversation, and roughly how long it takes.]

## Where this goes next
[Either: the next piece of work, and what it should answer.
Or: this is not an AI problem — here is what would actually fix it.]
```

### Quality bar

Before handing over, check the sharpened statement against all five. A statement
that fails any of these is not finished:

1. **Solution-free** — names no technology, vendor, or architecture. If you
   cannot state the problem without naming the fix, you have not found it yet.
2. **Measurable** — names a metric that exists today, with its current value.
3. **Bounded** — says where, for whom, and how often. "Customer service is slow"
   is not bounded; "tier-1 billing enquiries in the Nordics take 4.2 days to
   first resolution" is.
4. **Owned** — names the person whose number it is. Not a department.
5. **Falsifiable** — you could discover you were wrong. If no evidence could
   overturn it, it is a belief, not a diagnosis.

## Common disguises

These recur often enough to be worth pattern-matching. They are starting
hypotheses to test, never conclusions to assert — the point is to know which
question to ask next, not to skip the interrogation.

| What they say | What it often turns out to be | The question that separates them |
|---|---|---|
| "We need a chatbot for support" | A knowledge problem: answers exist but staff cannot find them | Do your best agents answer this correctly today? If yes, it is retrieval, not generation. |
| "We need AI to summarise our documents" | Nobody has decided what the summary is *for* | Who reads the summary, and what do they do next? |
| "We want a copilot for our sales team" | Uneven process adherence between top and bottom performers | Do your top performers do something different, or just more of it? |
| "We need to predict churn" | They can already predict it; nobody acts on the prediction | If you had a perfect list today, what would you do with it, and who is funded to do that? |
| "Our data isn't AI-ready" | Ownership dispute, not a technical gap | Who would have to agree for this data to be usable, and have they been asked? |
| "We need an agent to automate this workflow" | The workflow is undocumented and varies by person | Can two people describe the same steps the same way? |
| "Our competitors are doing AI" | A positioning need, not an operational one | What would you stop doing if this worked? |
| "We need to reduce headcount with AI" | Capacity is the binding constraint, not cost | If the work doubled, would you hire? If yes, this is capacity — the case is throughput, not savings. |

## Working with the requester

You are interrogating the problem, not the person. The distinction shows up in
how you phrase things: "what happens today when someone gets that wrong?" opens
a conversation; "that assumption seems weak" closes it.

Two habits that keep this productive:

- **Ask for one example, in detail, rather than a general description.** People
  describe processes as they are supposed to work and remember incidents as they
  actually happened. One walked-through case surfaces more than ten minutes of
  process description.
- **When they push back on a reframe, take it seriously.** They know their
  business. Often the pushback contains the constraint you missed — an
  obligation, a prior failure, a political reality. Fold it in rather than
  arguing; the reframe gets better and they stay engaged.

If the requester is not the metric owner, the sharpened statement is provisional
until the owner has seen it. Say so explicitly rather than letting it harden.

## Where this fits

This is discovery work: it comes before use-case prioritisation, data-readiness
assessment, and any architecture decision. Its output is the input to those.

Two natural handoffs:

- **A sharpened, AI-shaped problem** → score it for value and feasibility, and
  check whether the data can actually support it, before designing anything.
- **A problem that is not AI-shaped** → hand back a plain recommendation, and
  resist the pull to design an AI solution anyway. The credibility you keep by
  saying so is worth more than the engagement you lose.
