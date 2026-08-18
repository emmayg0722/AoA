# Attack axes

Work all eight in order (step 2). Each carries the questions that surface
findings, the failure patterns that recur, and the mitigations that are usually
cheapest. Where an axis genuinely does not apply, record it as a deliberate
exclusion rather than dropping it silently — the axis nobody considered is where
the incident comes from.

**Contents**
1. [Load and scale](#1-load-and-scale)
2. [Model dependency](#2-model-dependency)
3. [Input distribution](#3-input-distribution)
4. [Failure visibility](#4-failure-visibility)
5. [Blast radius and rollback](#5-blast-radius-and-rollback)
6. [Data and privacy](#6-data-and-privacy)
7. [Cost](#7-cost)
8. [Human factors](#8-human-factors)

---

## 1 · Load and scale

**Ask:** What is volume today, and what is it at the busiest hour of the busiest
day? What happens at 10×? Which component hits its limit first — rate limits,
context window, database connections, the human review queue? What sheds load
when the system cannot keep up?

**Patterns that recur:**

- **Peaks are not smooth.** Month-end, campaign launches and incidents produce
  bursts many times the average. A design sized on averages fails on the day it
  matters most.
- **The human queue is a component.** If every output needs review and reviewers
  process 40/day, the system's real throughput is 40/day regardless of how fast
  inference is. This constraint is almost always missing from the diagram.
- **Retries multiply load.** A failing dependency plus automatic retry turns a
  small outage into a self-inflicted denial of service.

**Cheapest mitigations:** an explicit queue with a visible depth metric; backoff
with jitter and a retry ceiling; load shedding that degrades to the old process
rather than failing; a documented per-component ceiling.

---

## 2 · Model dependency

**Ask:** What happens when the provider deprecates this model? When they update
it silently and quality shifts? When the API is down for two hours? Is there a
second provider, and has anyone tried it? Are prompts and model versions pinned
and version-controlled?

**Patterns that recur:**

- **Silent version drift.** A provider improves a model and your carefully tuned
  prompt behaves differently. Without a regression harness this shows up as
  users complaining weeks later.
- **Deprecation timelines are shorter than project timelines.** A model chosen
  today may be retired inside the system's expected life.
- **"We'll just swap providers" is rarely true** unless someone has run the
  evaluation set against the alternative. Prompts do not transfer cleanly.

**Cheapest mitigations:** pin model versions explicitly; keep the eval set
runnable against a candidate alternative; subscribe to the provider's
deprecation notices and give that subscription an owner; cache recent responses
so a short outage degrades rather than stops.

---

## 3 · Input distribution

**Ask:** What does the system do with input it has never seen — another
language, a scanned fax, an empty file, a 400-page document, a deliberately
crafted instruction? What if a user pastes something designed to redirect it?
What if a field the design assumes is always present is missing?

**Patterns that recur:**

- **Prompt injection through content.** Any system that reads untrusted text and
  then acts is exposed. The question is not whether instructions can appear in
  the content but what the system is permitted to do when they do.
- **The confident wrong answer on out-of-distribution input.** Most systems have
  no notion of "this is not the kind of thing I handle" unless designed in.
- **Format assumptions that were true during the pilot.** Upstream systems
  change export formats without telling anyone.

**Cheapest mitigations:** validate input shape before the model sees it; keep
untrusted content separated from instructions; constrain what the system may do
to an allowlist rather than filtering what it may not; make abstention a
first-class output; alert on input that fails validation rather than dropping it.

---

## 4 · Failure visibility

**Ask:** If quality halved tomorrow, how would anyone find out, and how long
would that take? What is monitored — infrastructure only, or output quality? Who
receives the alert, and what are they meant to do? When did anyone last check
that the alert fires?

This is the highest-yield axis. Conventional systems fail loudly; AI systems
fail quietly, and the gap between degradation and detection is where the real
damage accumulates.

**Patterns that recur:**

- **Monitoring covers uptime, not correctness.** The service is up, latency is
  fine, and the answers have been wrong for a month.
- **The only detector is a customer complaint**, which means detection latency
  equals however long users tolerate it before speaking up.
- **Alerts fire into a channel nobody reads**, which is the same as no alert
  with extra steps.

**Cheapest mitigations:** run the eval set on a schedule and alert on the
delta; track a cheap proxy continuously — abstention rate, answer length,
retrieval score distribution, human override rate — since a shift in any of
these usually precedes a quality problem; name an owner per alert; test the
alert path deliberately.

---

## 5 · Blast radius and rollback

**Ask:** What does one bad output cost? What does an hour of bad outputs cost?
Can the actions be undone, and by whom? How do you stop it right now — is there
a switch, does anyone know where it is, has it been tested? What state is left
behind mid-run?

**Patterns that recur:**

- **Irreversible actions with no confirmation.** Emails sent, payments posted,
  records deleted, tickets closed. No amount of accuracy makes an unrecoverable
  action safe to take unattended in year one.
- **Rollback exists in principle.** The plan says revert; nobody has run it, and
  it takes four hours under pressure.
- **Partial completion.** An agent fails halfway and leaves records in a state
  neither system expects.

**Cheapest mitigations:** batch size limits so one bad run touches ten records
rather than ten thousand; a dry-run mode logging what would have happened; a
tested kill switch that reverts to the previous process in one step; idempotent
operations so a retry is safe; keep genuinely irreversible actions behind a
human for the first period of operation.

---

## 6 · Data and privacy

**Ask:** What data reaches the model, and where does it go? Is it retained or
used for training? Can one tenant's data surface in another's response? What is
in the logs, and who can read them? If a customer asks for erasure, what has to
happen? Has a DPIA been done where one is required?

**Patterns that recur:**

- **Logs as the leak.** Prompts and responses containing personal data land in
  logs with far wider access than the source system.
- **Retrieval crossing a boundary.** An index built across tenants or permission
  levels answers questions the asker should not be able to ask.
- **Permissions checked at the wrong layer.** The user cannot open the document,
  but retrieval can, and it summarises the contents for them.

**Cheapest mitigations:** filter retrieval by the *caller's* permissions, not the
service's; redact before logging and set a retention period; confirm the
provider's retention and training terms in writing; make erasure a designed path
rather than a discovered problem.

---

## 7 · Cost

**Ask:** What does one transaction cost, and what does the busiest day cost? What
is the worst case for a single request — the longest context, the most retries,
the deepest agent loop? What stops a runaway? Who sees the bill before it is a
surprise?

**Patterns that recur:**

- **Agent loops without a step ceiling.** A task that normally takes 4 steps
  occasionally takes 200, and nothing stops it.
- **Context growth over a session.** Cost per turn rises through a conversation
  because history accumulates unbounded.
- **Retry storms.** A degraded dependency triggers retries across every caller
  at once.

**Cheapest mitigations:** a hard step and token ceiling per run; a spend alert at
a fraction of the monthly budget, not at it; cache repeated queries; route the
easy majority to a smaller model and reserve the large one for cases that need
it.

---

## 8 · Human factors

**Ask:** Who reviews the output, how many per day, and what does the hundredth
one feel like? What happens when they disagree with the system — is there a path,
and does anyone read what they submit? How many alerts per week, and what
fraction are actionable? What does the person do the day the system is wrong and
they trusted it?

**Patterns that recur:**

- **Automation bias.** A reviewer approving a high-accuracy system's output all
  morning stops genuinely reviewing. The review step remains on the diagram and
  stops functioning, which is worse than no review because it creates false
  assurance.
- **Alert fatigue.** More than a few false alarms per week and the alert is
  ignored — including the true one.
- **No feedback channel.** Users notice failures nobody records, so the same
  error recurs indefinitely.

**Cheapest mitigations:** measure whether reviewers actually catch injected
errors, periodically and openly; surface uncertainty so attention goes where it
is needed rather than spreading evenly; cap alert volume and tune for
actionability; make disagreement one click and route it somewhere with an owner;
design for the tired reviewer on a Friday afternoon, not the attentive one during
the demo.
