# Retrieval pipeline

Read when retrieval is the route (step 3). Six stages, each with a decision that
matters and a failure it causes when skipped. Most RAG systems that answer badly
have two or three of these stages missing entirely rather than one tuned wrongly.

**Parse → chunk → embed → search → rerank → assemble**

---

## 1 · Parse

Turn source files into clean text with structure preserved.

**The decision:** how much structure survives. A PDF flattened to a wall of text
loses the headings that tell you what a section is about, and those headings are
the cheapest relevance signal you will ever get.

**What goes wrong:** tables flattened into unreadable runs of numbers; multi-
column PDFs interleaved line by line; headers and footers repeated into every
chunk, diluting embeddings; scanned documents silently producing nothing.

**Worth doing:** keep heading hierarchy as metadata; extract tables separately
rather than as prose; log documents that parse to suspiciously little text —
that check catches more real problems than any tuning.

---

## 2 · Chunk

Split into retrievable units.

**The decision:** where the boundaries fall. This is the highest-leverage choice
in the pipeline and the most painful to change later, because everything
downstream — the index, the eval set, the tuned *k* — depends on it.

**Split on structure, not character counts.** A chunk should be a semantically
complete thing: a section, a clause, a row, a Q&A pair. A chunk ending
mid-sentence has an embedding that means nothing coherent, so it retrieves for
the wrong queries and against the right ones.

**Size:** big enough to answer a question on its own, small enough not to drag
in three unrelated topics. For prose, a few hundred tokens is a common starting
point — but derive it from your content rather than a default. Ask what the
smallest self-contained answer in the corpus looks like.

**Overlap:** a modest overlap keeps a fact that spans a boundary retrievable.
Too much and near-duplicate chunks crowd each other out of the top *k*.

**Always attach context to the chunk.** Document title, section heading, date,
and source. A chunk reading *"the limit is 30 days"* is useless in a window
holding fifteen other chunks; *"Returns policy → Consumer goods → the limit is
30 days"* is answerable and citable. This single habit fixes a surprising share
of wrong-answer complaints.

---

## 3 · Embed

Turn chunks into vectors.

**The decision:** which embedding model, and what it costs to change your mind.
Switching means re-embedding the whole corpus, so treat it as a one-way door for
large collections.

**What matters more than leaderboard position:** does it handle your languages;
does it handle your domain vocabulary; what is the dimension and therefore the
index size and cost; and can you run it where the data is allowed to be.

**Embed the same text you will show.** If you enrich chunks with headings for
retrieval, embed the enriched version — otherwise you are searching one thing
and returning another.

---

## 4 · Search

Find candidates.

**The decision:** how candidates are found, and how many.

**Retrieve generously.** Vector search is a similarity filter, not a relevance
judgement. Take 20–50 candidates here so the reranker has something to work
with; the cost is small and the recall gain is large.

**Consider hybrid search.** Pure vector search is weak on exact identifiers —
part numbers, error codes, names, policy references — because those are precisely
what embeddings blur. Combining keyword and vector scoring recovers them, and
this is a common cause of "it can't find the thing I searched for by its exact
name".

**Filter here, not after.** Permission, tenant, date and document-type filters
belong in the query. Post-filtering means the model saw content it should not
have, and anything in the window can leak into the answer.

---

## 5 · Rerank

Cut candidates down to what actually goes in the window.

**The decision:** whether you do this at all. Most systems skip it, and it is
usually the single highest-yield addition to a mediocre RAG system.

A reranker scores each candidate against the query directly rather than by
vector proximity, which is why the genuinely relevant passage that sat at
position seven moves to position one. Retrieve 40, rerank, pass 5.

**Fewer chunks in the window is usually better.** Every irrelevant chunk
competes for attention with the relevant one. If quality drops when you increase
*k*, that is not a paradox — it is the expected behaviour, and it means the
reranking step is missing or too permissive.

---

## 6 · Assemble

Build the final window.

**The decision:** order, formatting, and what happens when it does not fit.

**Order deliberately.** Stable content first (instructions, schema) so prompt
caching can hit. Retrieved evidence next, most relevant nearest the question.
Question last.

**Keep sources attached** through to the prompt so the model can cite, and so a
wrong answer can be traced to a wrong source rather than blamed on the model.

**Decide the truncation rule before it happens.** Something will eventually not
fit. Dropping the last chunk silently is the default and the worst option —
prefer dropping whole chunks by rank, summarising history, and logging when it
occurs. Silent truncation is one of the hardest production failures to diagnose,
because nothing errors.

---

## What to measure

Measure **retrieval separately from generation**. One number decides which half
of the system to work on:

> **recall@k** — how often is the answer-bearing passage in the *k* chunks you
> actually pass to the model?

If recall@k is low, no prompt engineering will save you: the evidence is not in
the window. Fix parsing, chunking, hybrid search, or reranking.

If recall@k is high but answers are still wrong, the retrieval half is working —
look at ordering, chunk count, instructions, and whether the model is being asked
to reason across chunks that do not co-retrieve.

Also worth tracking: **grounding** (is the answer supported by what was
retrieved?) and **refusal on unanswerable questions**, because a system that
always produces something confident is the most common and most damaging RAG
failure, and it is invisible unless unanswerable questions are in the test set.
