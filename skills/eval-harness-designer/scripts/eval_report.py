#!/usr/bin/env python3
"""Per-slice evaluation report with confidence intervals.

Reads predictions as CSV and reports accuracy, precision and recall per slice
with Wilson confidence intervals, so you can see at a glance which slices are
too small to support a conclusion — the commonest way eval results get
over-read. Optionally compares against a baseline run and flags the slices
that moved beyond their intervals.

Standard library only, so it runs anywhere the agent can run Python.

    python eval_report.py predictions.csv
    python eval_report.py predictions.csv --baseline baseline.csv
    python eval_report.py predictions.csv --format json
    python eval_report.py --example > predictions.csv

Input columns (header required):

    id         unique identifier for the case
    slice      the stratum this case belongs to (segment, difficulty, ...)
    expected   the correct label
    predicted  what the system produced
    confidence optional float 0-1, enables the calibration section

For binary problems, set --positive to the label that counts as positive so
precision and recall are computed against it. Without it, only accuracy is
reported per slice, which is the right default for multi-class work.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict

REQUIRED = ("id", "slice", "expected", "predicted")


# ── input ────────────────────────────────────────────────────────────────

def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit("%s has a header but no rows" % path)
    missing = [c for c in REQUIRED if c not in rows[0]]
    if missing:
        raise SystemExit("%s is missing column(s): %s" % (path, ", ".join(missing)))
    seen, dupes = set(), []
    for r in rows:
        if r["id"] in seen:
            dupes.append(r["id"])
        seen.add(r["id"])
    if dupes:
        raise SystemExit("duplicate id(s) in %s: %s%s" % (
            path, ", ".join(dupes[:5]), " ..." if len(dupes) > 5 else ""))
    return rows


# ── statistics ───────────────────────────────────────────────────────────

def wilson(successes, n, z=1.96):
    """Wilson score interval. Chosen over the normal approximation because
    slices are small and the naive interval misbehaves near 0 and 1 —
    exactly where eval slices tend to sit."""
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (p, max(0.0, centre - margin), min(1.0, centre + margin))


def prf(rows, positive):
    """Precision, recall and F1 against a nominated positive label."""
    tp = sum(1 for r in rows if r["predicted"] == positive and r["expected"] == positive)
    fp = sum(1 for r in rows if r["predicted"] == positive and r["expected"] != positive)
    fn = sum(1 for r in rows if r["predicted"] != positive and r["expected"] == positive)
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision and recall else None)
    return {"tp": tp, "fp": fp, "fn": fn,
            "precision": precision, "recall": recall, "f1": f1}


def score(rows, positive=None):
    n = len(rows)
    correct = sum(1 for r in rows if r["expected"] == r["predicted"])
    acc, lo, hi = wilson(correct, n)
    out = {"n": n, "correct": correct, "accuracy": acc, "ci_low": lo, "ci_high": hi}
    if positive:
        out.update(prf(rows, positive))
    return out


def by_slice(rows, positive=None):
    groups = defaultdict(list)
    for r in rows:
        groups[r["slice"] or "(unsliced)"].append(r)
    return {k: score(v, positive) for k, v in sorted(groups.items())}


def calibration(rows, bins=5):
    """Are stated confidences honest? Buckets by confidence and compares the
    claimed rate with the observed one. A system whose 0.9 bucket is right
    60% of the time cannot be used in a business rule that trusts it."""
    usable = []
    for r in rows:
        try:
            usable.append((float(r["confidence"]), r["expected"] == r["predicted"]))
        except (KeyError, TypeError, ValueError):
            continue
    if not usable:
        return None
    out = []
    for i in range(bins):
        lo, hi = i / bins, (i + 1) / bins
        sel = [ok for c, ok in usable if (lo <= c < hi or (i == bins - 1 and c == 1.0))]
        if not sel:
            continue
        out.append({"bucket": "%.1f-%.1f" % (lo, hi), "n": len(sel),
                    "claimed": (lo + hi) / 2,
                    "observed": sum(1 for s in sel if s) / len(sel)})
    return out


def compare(current, baseline):
    """Flag slices whose change clears both intervals — a move that survives
    the noise, rather than one the sample size cannot support."""
    rows = []
    for name, cur in current.items():
        base = baseline.get(name)
        if not base:
            rows.append({"slice": name, "status": "new", "delta": None})
            continue
        delta = cur["accuracy"] - base["accuracy"]
        separated = cur["ci_low"] > base["ci_high"] or cur["ci_high"] < base["ci_low"]
        rows.append({
            "slice": name,
            "baseline": base["accuracy"],
            "current": cur["accuracy"],
            "delta": delta,
            "status": ("improved" if separated and delta > 0 else
                       "regressed" if separated and delta < 0 else "within noise"),
        })
    for name in baseline:
        if name not in current:
            rows.append({"slice": name, "status": "missing", "delta": None})
    return rows


# ── output ───────────────────────────────────────────────────────────────

def pct(x):
    return "—" if x is None else "%.1f%%" % (x * 100)


def render(overall, slices, cal, cmp_rows, positive, min_n):
    out = ["# Evaluation report", ""]
    out.append("Overall accuracy **%s** (95%% CI %s–%s) over %d cases."
               % (pct(overall["accuracy"]), pct(overall["ci_low"]),
                  pct(overall["ci_high"]), overall["n"]))
    if positive:
        out.append("")
        out.append("Against positive label `%s`: precision %s, recall %s, F1 %s."
                   % (positive, pct(overall.get("precision")),
                      pct(overall.get("recall")), pct(overall.get("f1"))))
    out.append("")
    out.append("The overall number is for the steering committee. The per-slice "
               "table below is the one that tells you what to fix.")
    out.append("")

    out.append("## By slice")
    out.append("")
    header = "| Slice | n | Accuracy | 95% CI |"
    sep = "|---|---:|---:|---:|"
    if positive:
        header += " Precision | Recall |"
        sep += "---:|---:|"
    out.append(header)
    out.append(sep)
    for name, s in slices.items():
        row = "| %s | %d | %s | %s–%s |" % (
            name, s["n"], pct(s["accuracy"]), pct(s["ci_low"]), pct(s["ci_high"]))
        if positive:
            row += " %s | %s |" % (pct(s.get("precision")), pct(s.get("recall")))
        out.append(row)
    out.append("")

    thin = [n for n, s in slices.items() if s["n"] < min_n]
    if thin:
        out.append("> **Too thin to conclude from:** %s. Fewer than %d cases, so "
                   "a single flip moves the score materially. Widen these before "
                   "reading anything into their numbers."
                   % (", ".join("`%s`" % t for t in thin), min_n))
        out.append("")

    if cal:
        out.append("## Calibration")
        out.append("")
        out.append("Does stated confidence match observed correctness? A gap here "
                   "means the confidence value cannot be used to route or abstain.")
        out.append("")
        out.append("| Confidence | n | Claimed | Observed |")
        out.append("|---|---:|---:|---:|")
        for b in cal:
            out.append("| %s | %d | %s | %s |"
                       % (b["bucket"], b["n"], pct(b["claimed"]), pct(b["observed"])))
        out.append("")

    if cmp_rows:
        out.append("## Against baseline")
        out.append("")
        out.append("A slice is only called improved or regressed when the two "
                   "confidence intervals do not overlap — otherwise the move is "
                   "inside the noise the sample size permits.")
        out.append("")
        out.append("| Slice | Baseline | Current | Delta | Verdict |")
        out.append("|---|---:|---:|---:|---|")
        for r in sorted(cmp_rows, key=lambda r: (r["delta"] is None, r["delta"] or 0)):
            out.append("| %s | %s | %s | %s | %s |" % (
                r["slice"], pct(r.get("baseline")), pct(r.get("current")),
                ("%+.1f pp" % (r["delta"] * 100)) if r["delta"] is not None else "—",
                r["status"]))
        out.append("")
    return "\n".join(out)


EXAMPLE = """id,slice,expected,predicted,confidence
1,routine,approve,approve,0.95
2,routine,approve,approve,0.91
3,routine,decline,decline,0.88
4,routine,approve,approve,0.97
5,routine,approve,approve,0.93
6,edge-case,decline,approve,0.62
7,edge-case,decline,decline,0.71
8,edge-case,approve,decline,0.55
9,edge-case,decline,decline,0.68
10,edge-case,approve,approve,0.74
11,ambiguous,refer,approve,0.51
12,ambiguous,refer,refer,0.58
13,ambiguous,approve,refer,0.49
14,messy-input,approve,approve,0.81
15,messy-input,decline,approve,0.64
16,messy-input,approve,approve,0.86
17,messy-input,decline,decline,0.79
18,messy-input,approve,approve,0.83
19,routine,decline,decline,0.9
20,routine,approve,approve,0.94
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("predictions", nargs="?", help="CSV of predictions")
    ap.add_argument("--baseline", help="CSV from a previous run to compare against")
    ap.add_argument("--positive", help="label to treat as positive for precision/recall")
    ap.add_argument("--min-n", type=int, default=20,
                    help="flag slices smaller than this, default 20")
    ap.add_argument("--format", choices=("markdown", "json"), default="markdown")
    ap.add_argument("--example", action="store_true",
                    help="print a sample predictions CSV and exit")
    args = ap.parse_args()

    if args.example:
        sys.stdout.write(EXAMPLE)
        return
    if not args.predictions:
        ap.error("give a predictions CSV, or --example to print a sample")

    rows = load(args.predictions)
    labels = Counter(r["expected"] for r in rows)
    positive = args.positive
    if positive and positive not in labels:
        raise SystemExit("--positive %r never appears in 'expected'; found: %s"
                         % (positive, ", ".join(sorted(labels))))

    overall = score(rows, positive)
    slices = by_slice(rows, positive)
    cal = calibration(rows)
    cmp_rows = None
    if args.baseline:
        cmp_rows = compare(slices, by_slice(load(args.baseline), positive))

    if args.format == "json":
        print(json.dumps({"overall": overall, "slices": slices,
                          "calibration": cal, "comparison": cmp_rows}, indent=2))
    else:
        print(render(overall, slices, cal, cmp_rows, positive, args.min_n))


if __name__ == "__main__":
    sys.exit(main())
