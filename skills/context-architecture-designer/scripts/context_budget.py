#!/usr/bin/env python3
"""Context window budget and cost projection for one AI request shape.

Adds up what a single request actually sends, what share of the window that
uses, and what it costs at real volume — plus what caching the stable prefix
would save. The point is to make the arithmetic visible before the pipeline is
built, because a design nobody questioned routinely costs several times what
the business case assumed.

Standard library only, so it runs anywhere the agent can run Python.

    python context_budget.py --example > budget.json
    python context_budget.py budget.json
    python context_budget.py budget.json --format json

Token counts here are estimates. Real tokenisation depends on the model and the
language; the figures are for sizing a design, not for billing. Where a number
decides something important, measure it with the provider's own tokeniser.
"""

from __future__ import annotations

import argparse
import json
import sys

# Rough characters-per-token, English prose. Code and non-Latin scripts are
# denser; the spec can override this per case.
CHARS_PER_TOKEN = 4.0


def validate(spec):
    errors = []
    win = spec.get("context_window")
    if not win or win <= 0:
        errors.append("'context_window' must be a positive token count")
    parts = spec.get("parts")
    if not parts:
        errors.append("spec needs a 'parts' object describing the request")
    for name, part in (parts or {}).items():
        if "tokens" not in part and "chars" not in part:
            errors.append("part %r needs 'tokens' or 'chars'" % name)
        if part.get("repeat", 1) <= 0:
            errors.append("part %r has repeat <= 0" % name)
    pricing = spec.get("pricing", {})
    for key in ("input_per_1k", "output_per_1k"):
        if key in pricing and pricing[key] < 0:
            errors.append("'pricing.%s' cannot be negative" % key)
    if errors:
        raise SystemExit("Spec problems:\n  - " + "\n  - ".join(errors))


def tokens_of(part, cpt):
    if "tokens" in part:
        base = float(part["tokens"])
    else:
        base = float(part["chars"]) / cpt
    return base * float(part.get("repeat", 1))


def analyse(spec):
    cpt = float(spec.get("chars_per_token", CHARS_PER_TOKEN))
    window = int(spec["context_window"])
    parts = []
    for name, part in spec["parts"].items():
        tk = tokens_of(part, cpt)
        parts.append({
            "name": name,
            "tokens": tk,
            "cacheable": bool(part.get("cacheable", False)),
            "carries_answer": bool(part.get("carries_answer", False)),
            "note": part.get("note", ""),
        })
    parts.sort(key=lambda p: p["tokens"], reverse=True)

    input_tokens = sum(p["tokens"] for p in parts)
    output_tokens = float(spec.get("output_tokens", 0))
    cacheable = sum(p["tokens"] for p in parts if p["cacheable"])
    answer_bearing = sum(p["tokens"] for p in parts if p["carries_answer"])

    pricing = spec.get("pricing", {})
    in_rate = float(pricing.get("input_per_1k", 0.0))
    out_rate = float(pricing.get("output_per_1k", 0.0))
    cache_rate = float(pricing.get("cached_input_per_1k", in_rate * 0.1))

    cost = input_tokens / 1000 * in_rate + output_tokens / 1000 * out_rate
    cost_cached = ((input_tokens - cacheable) / 1000 * in_rate
                   + cacheable / 1000 * cache_rate
                   + output_tokens / 1000 * out_rate)

    volume = float(spec.get("requests_per_month", 0))
    return {
        "parts": parts,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "window": window,
        "window_used_pct": (input_tokens + output_tokens) / window * 100 if window else 0,
        "answer_bearing_pct": answer_bearing / input_tokens * 100 if input_tokens else 0,
        "cacheable_tokens": cacheable,
        "cost_per_request": cost,
        "cost_per_request_cached": cost_cached,
        "requests_per_month": volume,
        "cost_per_month": cost * volume,
        "cost_per_month_cached": cost_cached * volume,
        "currency": spec.get("currency", "USD"),
    }


def money(x, cur):
    gap = " " if cur and cur.isalpha() else ""
    if abs(x) < 1:
        return "%s%s%.4f" % (cur, gap, x)
    return "%s%s%s" % (cur, gap, format(x, ",.2f"))


def render(spec, r):
    cur = r["currency"]
    out = ["# Context budget — %s" % spec.get("case", "unnamed request shape"), ""]
    out.append("One request sends **%s input tokens** and expects %s out, using "
               "**%.1f%%** of a %s-token window."
               % (format(round(r["input_tokens"]), ","),
                  format(round(r["output_tokens"]), ","),
                  r["window_used_pct"], format(r["window"], ",")))
    out.append("")
    out.append("**%.0f%% of the input is answer-bearing.** Everything else is "
               "instructions, history and overhead — it competes for attention "
               "with the part that carries the answer."
               % r["answer_bearing_pct"])
    out.append("")

    out.append("## Where the tokens go")
    out.append("")
    out.append("| Part | Tokens | Share | Answer-bearing | Cacheable |")
    out.append("|---|---:|---:|---|---|")
    for p in r["parts"]:
        out.append("| %s | %s | %.0f%% | %s | %s |" % (
            p["name"], format(round(p["tokens"]), ","),
            p["tokens"] / r["input_tokens"] * 100 if r["input_tokens"] else 0,
            "yes" if p["carries_answer"] else "—",
            "yes" if p["cacheable"] else "—"))
    out.append("")

    if r["window_used_pct"] > 70:
        out.append("> **Tight.** Over 70% of the window is in use, which leaves "
                   "little room for a long retrieved passage or a long answer. "
                   "Truncation will start silently before it starts visibly.")
        out.append("")

    out.append("## Cost")
    out.append("")
    out.append("| | Per request | Per month (%s requests) |"
               % format(round(r["requests_per_month"]), ","))
    out.append("|---|---:|---:|")
    out.append("| As designed | %s | %s |" % (
        money(r["cost_per_request"], cur), money(r["cost_per_month"], cur)))
    out.append("| With prefix caching | %s | %s |" % (
        money(r["cost_per_request_cached"], cur), money(r["cost_per_month_cached"], cur)))
    saving = r["cost_per_month"] - r["cost_per_month_cached"]
    if saving > 0:
        out.append("")
        out.append("Caching the %s stable tokens saves **%s a month** — but only "
                   "if the stable content sits at the *front* of the prompt. "
                   "Variable content before it means the cache never hits."
                   % (format(round(r["cacheable_tokens"]), ","), money(saving, cur)))
    out.append("")
    out.append("Token counts are estimates at %.1f characters per token. Where a "
               "figure decides something important, measure it with the "
               "provider's own tokeniser."
               % float(spec.get("chars_per_token", CHARS_PER_TOKEN)))
    return "\n".join(out)


EXAMPLE = {
    "case": "Policy assistant (RAG)",
    "currency": "USD",
    "context_window": 128000,
    "chars_per_token": 4.0,
    "output_tokens": 400,
    "requests_per_month": 40000,
    "pricing": {"input_per_1k": 0.003, "output_per_1k": 0.015,
                "cached_input_per_1k": 0.0003},
    "parts": {
        "system instructions": {"tokens": 900, "cacheable": True,
                                "note": "Stable across every request."},
        "output schema": {"tokens": 350, "cacheable": True},
        "few-shot examples": {"tokens": 1200, "cacheable": True,
                              "note": "Check whether clearer instructions replace these."},
        "retrieved chunks": {"tokens": 600, "repeat": 8, "carries_answer": True,
                             "note": "k=8 after reranking from k=40."},
        "conversation history": {"tokens": 250, "repeat": 6,
                                 "note": "Grows unbounded unless summarised."},
        "user question": {"tokens": 60, "carries_answer": True},
    },
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec", nargs="?", help="path to the JSON budget spec")
    ap.add_argument("--format", choices=("markdown", "json"), default="markdown")
    ap.add_argument("--example", action="store_true",
                    help="print a starter spec and exit")
    args = ap.parse_args()

    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    if not args.spec:
        ap.error("give a spec path, or --example to print a starter spec")

    with open(args.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    validate(spec)
    r = analyse(spec)

    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        print(render(spec, r))


if __name__ == "__main__":
    sys.exit(main())
