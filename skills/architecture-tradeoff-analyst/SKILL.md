---
name: architecture-tradeoff-analyst
description: >-
  Work an AI architecture decision to a defensible recommendation — name the
  decision and how reversible it is, weight the criteria before looking at
  options, score the contenders against them, and state what would have to be
  true for the runner-up to win. Use whenever someone is choosing between
  technical approaches: RAG versus fine-tuning versus prompting, managed service
  versus self-hosted, agent versus fixed pipeline, one model versus another,
  vector store or framework selection, or any "which approach should we use",
  "should we build or buy", "what are the trade-offs" question. Use it before
  the comparison is written up, because criteria chosen after the options are on
  the table get reverse-engineered to justify the answer someone already wanted.
---

# Architecture Trade-off Analyst

Most architecture comparisons are decorative. The team already knows which
option they prefer, and the comparison table exists to justify it — criteria are
chosen that the favourite happens to win, and the alternatives appear as
strawmen with obvious flaws.

This is not dishonesty; it is what happens when criteria are picked after the
options are visible. The discipline that fixes it is simple and slightly
uncomfortable: **decide what matters before you look at what is available.**

## The rule that does the work

**Criteria and weights first, options second.** Write down what you are
optimising for and how much each factor matters, and get that agreed, before any
option is scored. Once the criteria are fixed, the comparison mostly does
itself — and where it produces an uncomfortable answer, that is the analysis
working rather than failing.

If the criteria are being adjusted after scores appear, stop and say so out
loud. That moment is where a comparison stops being evidence and starts being
advocacy.

## Workflow

### 1. State the decision and its reversibility

Write the decision as a single sentence, then classify how hard it is to undo.
This determines how much analysis is warranted, which is a decision in itself:

- **Two-way door** — reversible in days at low cost. Prompt structure, chunking
  strategy, which model you call. **Decide fast, run an experiment, move on.**
  Long analysis of a reversible decision is waste, and it is where architecture
  work most often stalls.
- **One-way door** — expensive or impossible to reverse. Where state lives, the
  data model, the trust boundary, whether a human is in the loop, the vendor
  holding your embeddings. **These deserve real analysis**, and they are usually
  decided too quickly while the team argues about the reversible ones.

Say which kind this is before proceeding. A surprising share of architecture
debate is spent on two-way doors dressed as one-way doors.

### 2. Name the criteria, and weight them

Five to seven criteria. Fewer misses something structural; more dilutes the two
or three that actually decide it, and a table with twelve evenly-weighted
criteria always produces a tie the author then breaks by preference.

Draw criteria from what the system must achieve, not from a generic list. The
usual sources:

- **Fit for the requirement** — accuracy, latency, freshness of information
- **Cost** — build, run, and cost at expected volume, which are three different
  numbers
- **Time to first value** — when a user sees something working
- **Operability** — what the team can actually run, given who is on it
- **Reversibility** — what it costs to change your mind later
- **Risk** — data exposure, vendor concentration, compliance obligations

Weight them explicitly — high, medium, low is enough; percentages imply a
precision that is not there. Then apply the test that makes weighting real:
**would you accept the worst option on a low-weighted criterion if it won on the
high-weighted ones?** If not, the weight is wrong, and the criterion is doing
more work than you admitted.

Get the weights agreed by whoever owns the outcome, before scoring. This is the
step that survives the meeting where the recommendation is challenged.

### 3. Assemble the options honestly

Include, always:

- **Do nothing / keep the current process.** Frequently the correct answer, and
  it is the only baseline that shows what the change is actually worth.
- **The boring option.** A SQL query, a rules engine, a template, a smaller
  model. Present it as a real contender, because it often wins on cost,
  operability and reversibility at once and it is embarrassing to discover that
  after the build.
- **The obvious favourite**, stated at its strongest.

Every option gets a fair statement. If an option can only be dismissed after
being described badly, it has not been dismissed. Read
`references/common-decisions.md` for the recurring AI architecture decisions —
RAG vs fine-tune vs prompt, managed vs self-hosted, agent vs pipeline, build vs
buy, model routing — each with the criteria that usually decide them and the
tells that point one way or the other.

### 4. Score against the criteria

Score each option per criterion, with **evidence and a confidence marker**. The
marker matters more than the score:

- **Measured** — you ran it, you have the number
- **Estimated** — derived from something comparable
- **Assumed** — someone's judgement

A comparison where the deciding criterion is scored entirely on assumptions is
not a decision; it is a hypothesis. Where that happens, the right output is
often a cheap experiment rather than a recommendation — see step 6.

Resist the composite score. Summing weighted numbers into a single figure
launders judgement into false precision, and it hides the one criterion that
actually drove the answer. Show the table, then say in prose which two or three
criteria decided it.

### 5. Argue the runner-up

For the option you did not pick, complete this sentence:

> **"We would choose X instead if ______ were true."**

This is the most useful line in the whole analysis, for three reasons. It proves
the alternative was taken seriously. It converts a preference into a testable
condition. And it gives you the trigger to revisit — when that condition changes,
the decision is due for review, and everyone can see it without re-litigating.

If you cannot complete the sentence, either the alternative was never viable and
should not be in the table, or you have not understood it well enough to reject
it.

### 6. Recommend, with conditions

A recommendation is not a preference. It states what to do, what has to hold for
it to remain right, and what would change it.

```markdown
## Decision
[One sentence. Two-way door or one-way door, and why that matters here.]

## Criteria and weights
| Criterion | Weight | Why it matters here |

## Options
[Each stated at its strongest, including do-nothing and the boring option.]

## Comparison
| Criterion | Weight | Option A | Option B | Option C |
[Score plus Measured / Estimated / Assumed per cell.]

## What decided it
[The two or three criteria that actually drove the answer. Prose, not a
composite score.]

## Recommendation
[What to do, and the conditions under which it holds.]

## We would choose the runner-up if…
[The specific condition, and how you would notice it had changed.]

## What we are assuming, and how to check it cheaply
[The assumptions the decision rests on, and the cheapest test for each.]

## Revisit trigger
[The event or date that puts this decision back on the table.]
```

### 7. When the honest answer is "run an experiment"

Sometimes the deciding criterion is scored **Assumed** on every option, and no
amount of further discussion will change that. Recommending anything at that
point is guessing with a table attached.

Say so, and specify the smallest experiment that would settle it: what to build,
what to measure, against what threshold, and by when. A two-day spike that
resolves the deciding criterion is worth more than a two-week comparison
document, and proposing it is a stronger analytical result than a confident
recommendation nobody can defend.

## Failure modes

**Criteria drift.** Weights adjusted after scores appear. Fix by getting weights
signed off in a separate step, before options are scored.

**The strawman alternative.** The rejected option described at its weakest.
Fix by having someone who prefers it write its description.

**Analysing a two-way door.** Weeks spent on something reversible in an
afternoon. Fix at step 1 — classify reversibility first and let it set the depth.

**Composite-score laundering.** A single weighted number that hides which
criterion decided it, and is trivially manipulated by adjusting a weight nobody
is looking at. Fix by naming the deciding criteria in prose.

**Ignoring the operating team.** An architecture the team cannot run is not a
good architecture, however well it scores. Operability is a criterion, and the
people who will carry the pager should score it.

**The unstated constraint.** Half of architecture debate is two people optimising
for different things without knowing it. If a disagreement will not resolve,
stop scoring and check whether you agree on the criteria — usually you do not,
and that is the actual conversation.

## Where this fits

This runs during architecture design, and again whenever a revisit trigger
fires. Its output is the reasoning behind a decision record — the record itself
captures what was decided; this captures why, what it depends on, and what would
change it, which is the part that turns out to matter a year later when the
context has moved and nobody remembers the debate.

It pairs with a design review: this decides between options, red-teaming stresses
the option you chose. Running the second without the first tends to harden a
decision nobody examined.
