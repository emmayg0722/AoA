# Metrics by archetype

Read when choosing what to measure (step 2). Pick the archetype that matches the
task, use the metric that matters, and state explicitly what it does not capture
— every metric is blind to something, and naming the blind spot is what stops it
being discovered by a customer.

**Contents**
- [Classify / route](#classify--route)
- [Extract / structure](#extract--structure)
- [Retrieve / answer (RAG)](#retrieve--answer-rag)
- [Generate / draft](#generate--draft)
- [Rank / recommend](#rank--recommend)
- [Predict / forecast](#predict--forecast)
- [Act (agentic)](#act-agentic)
- [Cross-cutting](#cross-cutting-measures)

---

## Classify / route

**Measure:** precision and recall per class at a stated operating point, plus the
confusion matrix.

**Not accuracy alone.** On imbalanced problems accuracy is dominated by the
majority class — 97% on a 3% fraud rate is achieved by always saying "no".

Which of precision or recall matters follows from the cost of each error. Missing
a fraud case costs more than reviewing a clean one, so recall leads; flooding a
small team with false alerts destroys trust in the system, so precision
constrains it. State both, with the threshold that produced them.

**Read the confusion matrix, not just the totals.** Confusion concentrated
between two adjacent classes usually means the taxonomy is wrong rather than the
model — humans will be disagreeing on the same boundary. Fix the categories.

**Blind spot:** says nothing about the cases the system should have refused.

---

## Extract / structure

**Measure:** field-level exact match and a normalised fuzzy match, reported per
field.

Document-level "all fields correct" is a useful headline but useless for
debugging: one bad field sinks the document and hides which one. Report per
field, always.

Handle three cases separately, because collapsing them hides real failures:
correctly extracted, wrongly extracted, and **correctly identified as absent**. A
system that invents a value for a field that is not present is far more dangerous
than one that leaves it blank, and only the three-way split shows that.

**Blind spot:** exact match punishes harmless formatting differences. Normalise
dates, currency and whitespace before scoring, and say that you did.

---

## Retrieve / answer (RAG)

**Measure retrieval and generation separately.** This is the single most useful
thing to do with a RAG system, because the two failure modes need completely
different fixes and the end-to-end number cannot tell them apart.

- **Retrieval:** is the passage containing the answer in the top *k*? Report
  recall@k for the k you actually pass to the model.
- **Grounding:** is the answer supported by the retrieved passages? An answer
  that is correct but unsupported got lucky, and it will not stay lucky.
- **Answer correctness:** is it right?

The combination matters: correct-and-grounded is success; correct-but-ungrounded
is a warning; incorrect-but-grounded means the source is wrong or stale, which is
a content problem, not a model problem.

Also measure the **refusal case** — questions the corpus genuinely cannot answer.
A system that always produces something confident is the most common and most
damaging RAG failure, and it is invisible unless unanswerable questions are in
the set.

**Blind spot:** end-to-end scores hide which half is broken, which is exactly why
they are split here.

---

## Generate / draft

**Measure:** human acceptance rate and edit distance — what fraction ships
unedited, and how much work the rest needs. These correspond to the value being
claimed, which reference-overlap scores do not.

Avoid BLEU and ROUGE for business drafting. They reward surface overlap with one
reference wording, and there are usually many good answers.

For open-ended output where human grading does not scale, an LLM judge with a
concrete rubric is reasonable — validate it against human grades first, as the
skill body describes.

**Blind spot:** acceptance rate rises as reviewers get tired or trusting. Track
it over time and treat a steadily climbing rate with suspicion rather than
satisfaction.

---

## Rank / recommend

**Measure:** precision@k and NDCG at the k users actually see, with position bias
accounted for.

Offline ranking metrics are weakly predictive of online behaviour, more so than
in other archetypes, because logged interactions reflect what the *old* system
showed. Treat offline numbers as a regression net and plan an online test.

**Blind spot:** feedback loops. A system trained on its own recommendations
entrenches what was already popular, and every offline metric will look fine
while diversity collapses.

---

## Predict / forecast

**Measure calibration first, then discrimination.** A model claiming 70%
confidence should be right about 70% of the time; check with a reliability plot
or Brier score. Calibration is what makes a probability usable in a business
rule, and it is routinely skipped.

Then discrimination — AUC, or precision/recall at the operating threshold.

**Always against a naive baseline.** For time series that is "same as last
period" or a seasonal average. A model that cannot beat last week's value is
common and needs to be caught early.

**Blind spot:** leakage. If any feature encodes information unavailable at
prediction time, scores look excellent and collapse in production. Check the
temporal availability of every feature before believing a strong result.

---

## Act (agentic)

**Measure:** end-to-end task completion on realistic tasks, plus what happens
when it fails.

Step-level accuracy is misleading because errors compound — 95% per step over ten
steps is 60% overall. Score the whole task.

Then measure the things unique to acting in real systems:

- **Recoverability** — when a step fails, does the system stop, retry sensibly,
  or make it worse?
- **Blast radius** — how much damage does one bad run do?
- **Cost and step variance** — runaway loops appear as tail latency and tail cost
  long before they appear as wrong answers.

**Blind spot:** a curated task set will not contain the situation that causes the
expensive incident. Pair evaluation with a hard limit on actions per run and a
rollback path.

---

## Cross-cutting measures

Worth reporting for any archetype, because they surface problems the primary
metric cannot see:

**Calibration / abstention.** Does the system know when it is unsure, and does it
say so? A calibrated system that abstains on 10% of cases is usually worth more
operationally than a confident one with the same raw accuracy.

**Latency and cost at the percentiles that hurt.** Report p95 and p99, not the
mean. The mean hides the tail that generates complaints and the retry storms that
generate bills.

**Stability.** Run the same input several times. Non-determinism that swings the
answer is a finding in itself, especially for anything feeding an automated
decision.

**Fairness across slices.** Where outputs affect people, per-slice performance
gaps are a governance issue, not just a quality one — and they only ever show up
in a stratified test set.
