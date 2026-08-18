---
name: context-architecture-designer
description: >-
  Design how information actually reaches the model — what is retrieved versus
  what sits in the prompt versus what is trained in, how documents are chunked
  and reranked, what is cached, how permissions are enforced at retrieval time,
  and what the whole thing costs per request at real volume. Use when someone is
  building or fixing a RAG or retrieval system, choosing chunk sizes or an
  embedding model, asking whether to use a long context window instead of
  retrieval, seeing wrong or stale answers from a knowledge assistant, hitting
  token limits, or watching inference cost climb faster than usage. Use it
  before the pipeline is built, since chunking and index decisions are painful
  to change once content and evaluation sets depend on them.
---

# Context Architecture Designer

Every request to a model is a context window someone assembled. Most systems
assemble it by accident: a prompt that grew by accretion, a retriever returning
whatever the default *k* was, chat history appended until something truncates.

That accident is where the failures come from. Wrong answers usually are not a
model problem — the right passage never made it into the window, or it did and
was buried under nine irrelevant ones. Cost overruns are the same story: nobody
decided what goes in each request, so everything does.

## The framing that makes this tractable

Treat the context window as a **budget you allocate**, not a container you fill.
Every token in it competes with every other token, and each has to earn its
place. Before designing anything, ask what the model needs to answer correctly:

- **Instructions** — how to behave. Usually small and stable.
- **Retrieved evidence** — the facts for *this* request. Usually the bulk.
- **History** — what happened earlier in the conversation. Usually over-weighted.
- **Examples** — how a good answer looks. Often replaceable by clearer
  instructions.

Naming the split forces the real question: *what fraction of the window is
actually carrying the answer?* In systems that answer badly, it is frequently
under a fifth.

## Workflow

### 1. Decide where knowledge lives before touching a pipeline

Three routes get information into a model, and they solve different problems.
Choosing wrong here cannot be fixed downstream by better chunking.

| Route | Fits when | Breaks when |
|---|---|---|
| **In the prompt** | Small, stable, applies to every request — policies, formats, definitions | It grows past a page, or changes per user, or you are pasting a document |
| **Retrieved** | Large corpus, changes often, needs citation, per-user permissions | Answers need holistic understanding of one whole document |
| **Trained in** | Behaviour and form, not facts; narrow and stable; hundreds of examples exist | The facts change, or you need to show a source |

**The default mistake is fine-tuning to fix a knowledge problem.** It bakes
facts in at a point in time, cannot cite a source, and goes stale silently.
Fine-tuning teaches *how* to answer; retrieval supplies *what is true*.

**The newer mistake is skipping retrieval because the window is large.** Long
context genuinely handles more, but three costs remain: you pay for every token
every request, attention degrades in the middle of very long inputs, and you
lose per-user permission filtering — a whole document in the window is a whole
document the user can extract. Long context is excellent for *one known
document*. Retrieval is for *finding which document*.

### 2. Size the window before choosing a strategy

Work out what a single request looks like: instruction tokens, retrieved tokens
(chunk size × k), history, and expected output. The script does the arithmetic
and the cost projection:

```bash
python scripts/context_budget.py --example > budget.json
python scripts/context_budget.py budget.json
python scripts/context_budget.py budget.json --format json
```

It reports tokens per request, share of the window used, cost per request, and
cost at your monthly volume — plus what caching the stable prefix would save.
See `references/budget-format.md` for the fields.

Do this early. It routinely shows that a design nobody questioned costs several
times what the business case assumed, which is much cheaper to discover now.

### 3. Design retrieval as a pipeline, not a lookup

If retrieval is the route, it has stages, and most quality problems live in a
stage teams never built. Read `references/retrieval-pipeline.md` for the detail;
the shape is:

**Parse → chunk → embed → search → rerank → assemble**

Two decisions carry most of the outcome:

**Chunking.** Chunks should be semantically complete — a chunk that ends
mid-clause retrieves badly because its embedding means nothing coherent. Prefer
splitting on document structure (headings, sections, rows) over fixed character
counts, and keep a small overlap so a fact spanning a boundary survives. Attach
the document title and section heading to each chunk; a chunk that says "the
limit is 30 days" without saying *what* limit is unusable in a window with
fifteen other chunks.

**Reranking.** Vector search optimises for similarity, not relevance — they are
not the same thing, which is why the right passage often sits at position seven.
Retrieve generously (k of 20–50), then rerank down to the 3–8 you actually pass.
This is usually the single highest-yield addition to a mediocre RAG system, and
it is cheap relative to enlarging the window.

### 4. Enforce permissions at retrieval time

Filter by the **caller's** permissions, not the service's. A retriever running
with broad access will happily summarise a document the user cannot open, and
the answer looks perfectly legitimate.

This has to be a filter on the search, not a check afterwards — post-filtering
means the model already saw the content, and anything that reaches the window
can leak into the answer. If the index spans tenants or clearance levels,
partition it or carry permission metadata on every chunk.

### 5. Decide what is cached and what is fresh

Caching is where cost architecture is won, and it follows directly from the
budget in step 2.

- **Stable prefix** — instructions and schemas are identical every request.
  Providers that cache prompt prefixes make this nearly free; put stable content
  first and variable content last, or the cache never hits.
- **Retrieved chunks** — cache the embedding, not the answer, unless the corpus
  is genuinely static.
- **Whole answers** — only where the same question recurs verbatim and staleness
  is acceptable. Say how it is invalidated, or it will serve last quarter's
  policy indefinitely.

Freshness is a design decision, not a property. State how quickly a change in a
source document must appear in an answer — minutes, or next week — because
re-indexing strategy follows from it and the two answers cost very differently.

### 6. Write it up

```markdown
## What the model needs to answer correctly
[The four budget slices, and what fraction carries the answer.]

## Where knowledge lives
[Prompt / retrieved / trained, per kind of information, with the reason.]

## Context budget
[Tokens per request, share of window, cost per request, cost at volume.]

## Retrieval pipeline
[Parse, chunk, embed, search, rerank, assemble — decisions and sizes.]

## Permissions
[How the caller's rights filter the search, and where the boundary is.]

## Caching and freshness
[What is cached, how it is invalidated, how fast a source change appears.]

## What would change this design
[The cheapest measurement that would settle the biggest assumption.]
```

## Symptoms and where they usually come from

Useful when handed a system that already answers badly. These are hypotheses to
test against the eval set, not conclusions.

| Symptom | Usually |
|---|---|
| Confident but wrong answers | The passage was never retrieved. Measure recall@k before touching the prompt. |
| Right passage retrieved, wrong answer | Too many chunks in the window, or the relevant one is buried. Rerank and cut k. |
| Answers cite the wrong document | Chunks lack source metadata, or overlap merged two documents. |
| Good on simple questions, bad on comparisons | The answer needs several chunks that similarity search will not co-retrieve. Consider query decomposition. |
| Quality dropped without a deploy | The index went stale, or an upstream format changed and chunks are now malformed. |
| Cost climbing faster than usage | History or retrieved context is growing unbounded per request. |
| Fine in testing, wrong in production | Test questions were written by people who knew the corpus. Use real logged questions. |

## The measurement that settles arguments

Most debates here — chunk size, k, embedding model, long context versus
retrieval — are unresolvable by discussion and trivial to settle with a small
evaluation set. Measure **retrieval separately from generation**: is the
answer-bearing passage in the top *k*? That single number tells you which half of
the system to work on, and teams argue for weeks without it.

If no eval set exists, that is the first deliverable, not this design.

## Where this fits

This sits inside architecture design, after the problem is sharpened and the
archetype is known, and before the build. Its output feeds the architecture
blueprint, the cost model, and the evaluation harness — the retrieval metrics it
implies are what the harness will measure.

It pairs with a design review: this decides how context is assembled,
red-teaming asks what happens when the index goes stale, a tenant boundary
leaks, or one request drags in ten times the expected tokens.
