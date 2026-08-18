---
name: eval-harness-designer
description: >-
  Design the evaluation harness for an AI system — what to measure, the test set
  and how to stratify it, the baseline to beat, the acceptance threshold, and how
  to catch regressions when the underlying model changes. Use whenever someone
  asks how they will know an AI feature works, what accuracy target to set, how
  to build a test or golden set, how to benchmark a model or prompt, whether a
  change made things better, why quality seems to have degraded, or how to tell
  if a RAG, extraction, classification or agent system is good enough to ship.
  Use it before the build starts, not after — a system built without a baseline
  can never be shown to have improved anything, and that is the single most
  common way AI projects become unfalsifiable.
---

# Eval Harness Designer

Most AI systems ship without a way to tell whether they work. Not because
teams do not care, but because evaluation gets deferred until after the
interesting part is built — and by then there is no baseline to compare
against, no held-out data that has not leaked into prompt iteration, and no
agreement on what "good" means.

The result is a system nobody can defend and nobody can improve. Someone
changes a prompt, everyone squints at a handful of examples, and the change
ships on vibes. Later, quality drifts and no one can prove it.

## The two rules

**Establish the baseline before you build.** "85% accuracy" means nothing on
its own. Against a naive rule that gets 83%, it is a failure. Against 40%, it
is a triumph. The baseline is cheap to compute early and impossible to
reconstruct honestly later, once everyone has seen what the system produces.

**Never evaluate on data you iterated against.** Prompt engineering against your
test set is the LLM-era form of overfitting, and it is far easier to do by
accident than classical overfitting ever was — you look at failures, adjust the
prompt, and the set is contaminated. Split into *dev* (look at freely) and
*test* (touch rarely, and record when you do).

## Workflow

### 1. Anchor on the decision, not the model

Start with what the output changes: who acts on it, how often, and what happens
when it is wrong. This drives everything downstream, because the accuracy bar is
set by consequence, not by ambition.

- If a human reviews every output before it acts, moderate accuracy with good
  *calibration* — the system knowing when it is unsure — beats higher raw
  accuracy that fails silently.
- If the output executes directly, the bar is much higher, and you need
  monitoring, rollback, and a defined blast radius before launch.

Ask directly: **what error rate would make this unusable, and what error rate
would make it clearly worth having?** Two numbers, from the person accountable
for the process. If they cannot answer, that conversation is the real first
deliverable — everything else here is premature.

### 2. Identify the archetype and pick metrics from it

What you measure follows from the kind of task. Read
`references/metrics-by-archetype.md` for the full table — classification,
extraction, retrieval/RAG, generation, ranking, forecasting, and agentic tasks
each have a metric that matters and several that mislead.

Two traps worth naming here because they are near-universal:

**Accuracy on an imbalanced problem is a liar.** If 3% of invoices are
fraudulent, a model that says "never fraud" scores 97%. Use precision and recall
at a chosen operating point, and state the operating point.

**Aggregate scores hide the failures that matter.** A system at 92% overall can
be at 40% on the segment that generates the complaints. Always report per-slice,
which is what step 3 is for.

### 3. Build the test set — stratify, do not just scale

The instinct is to collect more examples. The better move is to collect the
*right* examples, deliberately grouped so you can see where the system fails.

Slice along dimensions where behaviour plausibly differs:

- **Business segment** — customer type, region, product line, language
- **Difficulty** — routine cases, edge cases, genuinely ambiguous cases
- **Known failure modes** — whatever the current human process gets wrong
- **Input quality** — clean, messy, truncated, wrong format, empty
- **Time** — include recent examples, because distributions drift

Sizing is per slice, not overall. A slice with five examples tells you nothing:
a single flip moves the score 20 points. Aim for enough per slice that a change
of the size you care about is distinguishable from noise — for most business
cases that is dozens per slice, not thousands, provided the slices are chosen
well. The script in step 6 reports confidence intervals so you can see directly
when a slice is too small to support a conclusion.

**Include cases where the right answer is "I don't know" or "refuse."** Systems
that never abstain look strong on curated sets and fail badly in production,
and this is the only way that shows up in the numbers.

### 4. Settle the labels before you trust any number

Your evaluation can never be more reliable than its labels. Before scoring
anything, have two people independently label a sample of 30–50 and measure how
often they agree.

If they agree only 70% of the time, **70% is your ceiling** — a model scoring
above it is matching one labeller's idiosyncrasies, not being correct. Low
agreement is not a labelling failure; it usually means the *task definition* is
ambiguous, and the fix is upstream: sharpen the categories, then re-label.

Record who labelled what and when. When a score moves six months from now, this
is the first thing you will need.

### 5. Compute the baseline

Before any model work, measure the simplest thing that could work:

- **Majority class** — always predict the most common answer
- **Keyword or rule** — the regex a competent analyst would write in an hour
- **Current process** — how often do the humans doing this today get it right?
- **Random or existing system**, where one is in place

The human baseline matters most for the business conversation. If people are 89%
accurate and the system reaches 91%, the case is about cost and throughput, not
quality — and that changes which benefits the business case may claim.

### 6. Run it and read per-slice

The bundled script computes per-slice metrics with confidence intervals and
compares against a baseline run, so the numbers are consistent between runs and
you are not re-deriving statistics by hand:

```bash
python scripts/eval_report.py predictions.csv --baseline baseline.csv
python scripts/eval_report.py predictions.csv --format json
python scripts/eval_report.py --example > predictions.csv   # sample input
```

Input is a CSV with `id`, `slice`, `expected`, `predicted`, and optional
`confidence`. See `references/eval-report-usage.md` for the columns, the
metrics, and how the intervals are calculated.

Read the output slice by slice. **The overall number is for the steering
committee; the per-slice table is for you.** A regression concentrated in one
slice is a specific, fixable bug; the same drop spread evenly is usually a data
or prompt-level change.

### 7. Set the threshold and the regression path

Two commitments, written down before launch:

**Acceptance threshold** — the score at which this ships, per slice where it
matters, tied to the consequence established in step 1. A single global
threshold hides the slice that will generate the complaints.

**Regression path** — AI systems degrade without anyone touching them. The
provider updates the model, an index goes stale, the input distribution shifts.
Decide now:

- Re-run the harness on a schedule, and on every prompt, model, or retrieval
  change
- Set the alert threshold *below* the acceptance threshold, so you hear about
  decay before it breaches
- Name who receives the alert and what they are expected to do

An eval that is not scheduled is an eval that ran once.

### 8. Write it up

```markdown
## What we are measuring, and why
[The decision the output drives, and the consequence of error.]

## Metrics
[Metric per archetype, the operating point, and what each does not capture.]

## Test set
[Size, slices and per-slice counts, how sourced, dev/test split.]

## Labels
[Who labelled, inter-annotator agreement, and the ceiling it implies.]

## Baseline
[The naive baseline and the human baseline, with numbers.]

## Acceptance thresholds
[Per slice where it matters. Ship / do not ship.]

## Regression plan
[Schedule, triggers, alert threshold, owner.]

## What this evaluation does not tell you
[Be explicit. Offline eval predicts; it does not measure production.]
```

## Offline, online, and the gap between them

Offline evaluation on a fixed test set is fast, repeatable, and the right tool
for iteration. It also systematically overstates production quality, because
real inputs are messier than curated ones and real users do things nobody put in
the set.

Do not treat them as substitutes. Offline eval is your regression net; online
measurement — acceptance rate, edit distance, escalation rate, task completion —
is your ground truth. Plan the online measurement before launch, because
instrumenting it afterwards means losing the first weeks of evidence, which are
the weeks people ask about.

## Using a model to grade a model

LLM-as-judge is legitimate and often the only practical option for open-ended
generation, but it is a measurement instrument and needs its own validation.

Use it when outputs are free text with no single correct answer and human
grading does not scale. Be careful when the judge shares a family with the
system under test — models favour their own style — and never use it as the sole
signal for a decision that executes without a human.

Before trusting it: have humans grade 50 examples, have the judge grade the same
50, and measure agreement. If the judge agrees with humans less often than
humans agree with each other, it is not ready. Give it a rubric with concrete
criteria rather than "rate 1–10", and hold its prompt stable — changing the
judge silently rebases every historical score you have.

## When there is no test set yet

Frequently the honest answer is that nothing exists to evaluate against. That is
a finding, not a blocker, and it has a cheap resolution:

1. Pull 50–100 real cases from whatever system holds them today.
2. Have the person who owns the process label them, thinking aloud while they do.
3. Notice where they hesitate — those are your ambiguous slices, and they are
   the most valuable part of the set.

A day of this produces a harness that outlasts several model generations. It is
also the moment most likely to reveal that the task definition itself is
unclear, which is far cheaper to discover now than after the build.

## Where this fits

This belongs before the build — during proof-of-concept scoping, alongside the
go/no-go criteria. Running it afterwards produces a harness fitted to the system
that exists rather than the problem that was posed.

Its inputs are a sharpened problem statement and the intended decision class.
Its outputs feed the go/no-go decision, the quality-assurance plan, and the
monitoring thresholds the operations team will run against in production.
