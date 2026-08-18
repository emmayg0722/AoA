---
name: architecture-red-team
description: >-
  Stress-test a proposed AI architecture before it ships — attack it along fixed
  axes (load, model dependency, adversarial and out-of-distribution input, silent
  degradation, blast radius, rollback, cost runaway, human factors), rank the
  findings by likelihood and recoverability, and give the cheapest mitigation for
  each. Use whenever a design, blueprint, architecture diagram, ADR, RFC or
  technical proposal is put forward for review, before a go-live or production
  readiness gate, when asked "does this hold up", "what could go wrong with this
  design", "is this production-ready", or "review this architecture". Use it
  especially when a design looks clean and everyone agrees, since that is when
  nobody is looking for the failure that has not been considered.
---

# Architecture Red Team

A design review that finds nothing is not a passed review — it is a review that
did not happen. The purpose here is to find the failures the design's author
could not see, precisely because they were the one who built it.

This skill is adversarial about the *design*, never about the designer. That
distinction is what makes the output usable: a review that reads as an attack on
someone's competence gets defended against rather than acted on, and the
findings die in the meeting.

## Steelman before you attack

Start every review by restating the design as its author intended it —
including the constraints they were working under and the trade-offs they made
deliberately. Do this before raising a single finding.

Two reasons, both practical. First, half of what looks like a flaw is a
constraint you did not know about, and raising it wastes the room's credibility
on your first point. Second, a designer who sees their reasoning understood
accurately will engage with the findings; one who sees it caricatured will spend
the meeting correcting you.

If the design is not written down well enough to restate, that is finding
number one, and it usually predicts several others.

## Workflow

### 1. Establish what you are reviewing

Get these on the table. Missing answers are findings in their own right:

- **The decision the system makes**, how often, and who is accountable when it
  is wrong
- **Expected volume today** and the volume it is expected to reach
- **What it depends on** — models, data sources, services, and who owns each
- **What "working" means** — the acceptance criteria, if any exist
- **What is already decided and cannot change** — budget, platform, deadline

### 2. Attack along the axes

Work `references/attack-axes.md` in order. It carries the full prompts; the
eight axes are:

1. **Load and scale** — behaviour at 10× volume, and at a burst
2. **Model dependency** — deprecation, version drift, provider outage
3. **Input distribution** — adversarial, out-of-distribution, malformed, absent
4. **Failure visibility** — how anyone would notice it had degraded
5. **Blast radius and rollback** — damage per bad run, and the undo path
6. **Data and privacy** — leakage, retention, cross-tenant exposure
7. **Cost** — runaway loops, retry storms, unbounded context growth
8. **Human factors** — automation bias, reviewer fatigue, alert volume

Work all eight even when some seem irrelevant; the axis you skip is where the
incident comes from. Where one genuinely does not apply, record that as a
deliberate exclusion rather than silently dropping it.

**The highest-yield question in the whole review is axis 4: how would you
know?** Conventional systems fail loudly — a service is down, a queue backs up.
AI systems fail quietly: answers get subtly worse, retrieval returns
near-misses, extraction silently starts missing a field after a format change.
A design with no answer to "how would you know" has no working failure mode at
all, only an undetected one.

### 3. Make each finding concrete

A finding that cannot be pictured cannot be prioritised. "Scalability concerns"
gets nodded at and forgotten; a specific chain gets fixed.

Each finding needs:

- **The trigger** — the specific condition, with a number where one applies
- **The chain** — what happens next, step by step
- **The consequence** — what the business actually feels
- **How you would find out**, and how long that takes

> **Weak:** "The system may not handle peak load."
>
> **Usable:** "At month-end, invoice volume goes from 400/day to ~6,000/day. The
> extraction step runs 4 concurrent calls against a provider limit of 10/sec, so
> the queue grows faster than it drains. Nothing sheds load, so the backlog
> reaches the AP team as 'the system is stuck' on the busiest day of the month.
> Nobody finds out until a clerk calls, because queue depth is not monitored."

### 4. Rank by likelihood × recoverability

Rank on **likelihood × recoverability**, not severity. Severity alone pushes
every review toward dramatic, improbable scenarios while the boring
unrecoverable ones — a silent data-quality regression nobody notices for six
weeks — get filed under "medium".

| | Recoverable in minutes | Recoverable in days | Not recoverable |
|---|---|---|---|
| **Likely** | Fix before launch | Fix before launch | Stop; redesign |
| **Possible** | Monitor | Fix before launch | Fix before launch |
| **Unlikely** | Accept, note it | Monitor | Fix before launch |

Anything unrecoverable is a finding regardless of likelihood — sent emails,
posted transactions, deleted records, leaked data. You cannot apologise your way
out of an action that cannot be undone.

### 5. Give each finding its cheapest mitigation

Every finding ships with the smallest change that meaningfully reduces it. A
review that only raises problems transfers work rather than reducing it, and
gets a worse reception than it deserves.

The cheapest mitigation is often not an architectural change:

- **A limit** — max actions per run, max context length, max spend per day
- **A monitor** — the missing signal, plus who receives it and what they do
- **A narrower scope** — take the risky 10% of cases out of automation
- **A lower decision class** — recommend rather than decide, for the first year
- **A kill switch** — a flag that reverts to the previous process in one step

Name the option that is cheaper than the fix but only partially works, and say
so honestly. That is frequently the one that gets adopted.

### 6. Write it up

```markdown
## The design as I understand it
[Restated in your own words, including the constraints and deliberate
trade-offs. Confirm this before reading further.]

## Verdict
[Ship / ship with the fixes below / not ready — and the single reason.]

## Fix before launch
| # | Finding | Trigger and chain | Mitigation |

## Monitor
| # | Finding | What to watch | Threshold and owner |

## Accepted
[Findings deliberately not addressed, and who accepted them. This list
being empty usually means the review was not honest.]

## Axes not applicable
[Which of the eight, and why. Keeps the exclusion deliberate.]

## What I could not assess
[What was not available to review, and what you would need.]
```

## Calibration

A review can fail in both directions, and the second is more common than people
expect.

**Too soft** looks like: only findings the team already knew, everything ranked
medium, no unrecoverable actions identified, an empty accepted list. If a review
produces nothing the team had not thought of, either the design is genuinely
mature — say so explicitly, it is a real outcome — or the review was not
adversarial enough.

**Too harsh** looks like: findings that apply to any system ever built, risks
raised without mitigations, theoretical attacks with no plausible path, and
ignoring stated constraints. This is the more damaging failure, because it
teaches people that reviews are noise and the next real finding gets discounted
along with the rest.

The honest position sits between: a handful of specific, actionable findings,
ranked, each with a way forward — plus explicit acknowledgement of what the
design already handles well. Naming what is genuinely solid is not politeness;
it tells the reader you engaged with the whole design and makes the criticisms
land.

## Reviewing a design that does not exist yet

Often what arrives is a diagram and a conversation rather than a document. Review
it anyway — findings are cheapest at this stage — but change the emphasis.

Focus on the decisions that are hard to reverse later: where state lives, what
the trust boundary is, whether a human is in the loop, and what the system is
allowed to do without asking. Those are expensive to change once built.

Leave the details that are easy to change — model choice, chunking strategy,
prompt structure — with a note that they are deliberately deferred. Reviewing
them now spends the team's attention on the reversible decisions and leaves the
one-way doors unexamined, which is exactly backwards.

## Where this fits

This runs against a proposed architecture, blueprint or decision record, and
before any production readiness gate. Its findings feed the risk register, the
monitoring plan, and — where a finding is serious enough — back into the design
itself.

It pairs naturally with an evaluation harness: red-teaming asks what could
break, evaluation measures whether it has. Neither substitutes for the other,
and a design with both is in a materially better position than one with either.
