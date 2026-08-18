# Budget spec format

The JSON file `scripts/context_budget.py` reads. Run
`python scripts/context_budget.py --example` to print a working spec you can
edit rather than writing one from scratch.

## Fields

| Field | Type | Meaning |
|---|---|---|
| `case` | string | Name of the request shape being sized. |
| `currency` | string | `"USD"`, `"EUR"`, `"€"` — alphabetic codes get a space, symbols do not. |
| `context_window` | int | The model's window in tokens. |
| `chars_per_token` | float | Estimation ratio, default 4.0. Lower it for code or non-Latin scripts. |
| `output_tokens` | number | Expected response length. |
| `requests_per_month` | number | Volume for the cost projection. |
| `pricing` | object | `input_per_1k`, `output_per_1k`, and optionally `cached_input_per_1k` (defaults to a tenth of input). |
| `parts` | object | One entry per component of the request. |

## Parts

```json
"retrieved chunks": {
  "tokens": 600,
  "repeat": 8,
  "carries_answer": true,
  "note": "k=8 after reranking from k=40."
}
```

| Key | Meaning |
|---|---|
| `tokens` or `chars` | Size of one instance. `chars` is divided by `chars_per_token`. |
| `repeat` | How many instances per request. Use for chunks and history turns. |
| `cacheable` | Identical on every request, so a prompt cache can serve it. |
| `carries_answer` | This part contains the information the answer depends on. |
| `note` | Shown nowhere in the report; kept in the spec as the reason for the number. |

**`carries_answer` is the interesting flag.** The report shows what share of
your input actually carries the answer. When that share is low, the window is
mostly overhead competing for attention with the evidence — and enlarging *k*
will make it worse, not better.

**`cacheable` drives the caching comparison.** Mark only genuinely invariant
content. Anything that changes per user or per request is not cacheable, even if
it feels stable.

## What the report tells you

**Window used.** Above 70% you get a warning, because a long retrieved passage
or a long answer will start truncating — silently, before it does so visibly.

**Answer-bearing share.** The diagnostic. In a system answering badly this is
frequently under 20%.

**Cost with and without prefix caching.** The saving is real only if stable
content sits at the *front* of the prompt. Put a per-user greeting before the
system instructions and the cache never hits, however cacheable the instructions
are in principle.

## Accuracy

Token counts are estimates from a characters-per-token ratio. Real tokenisation
depends on the model and the language — code, JSON and non-Latin scripts are
denser than English prose.

This is for **sizing a design**, not for billing. When a figure decides
something that matters — a go/no-go, a contract, an architecture choice — measure
it with the provider's own tokeniser on real inputs. The estimate is here to
catch the order-of-magnitude problem early, which is the one that actually
changes decisions.
