#!/usr/bin/env python3
"""Scenario ROI model for a single AI solution case.

Reads a JSON spec describing value drivers, costs and named scenarios, and
emits the cash-flow table, NPV / payback / ROI for each scenario, a one-at-a-
time sensitivity (tornado) ranking, and the breakeven value of whichever
assumption the case hinges on.

Standard library only, so it runs anywhere the agent can run Python.

    python roi_model.py spec.json                 # markdown report
    python roi_model.py spec.json --format json   # machine-readable
    python roi_model.py --example                 # print a starter spec

Spec shape (see references/spec-format.md for the annotated version):

    {
      "case": "Supplier query assistant",
      "currency": "EUR",
      "horizon_years": 3,
      "discount_rate": 0.10,
      "assumptions": {"queries_per_year": 31200, "share_answerable": 0.7, ...},
      "drivers": [
        {"name": "Clerk time released", "basis": "measured",
         "terms": ["queries_per_year", "share_answerable", "hours_saved",
                   "loaded_hourly_cost"]}
      ],
      "costs": {"build_once": 180000, "run_annual": 90000},
      "ramp": [0.4, 1.0, 1.0],
      "realization": 0.8,
      "scenarios": {
        "conservative": {"assumptions": {"share_answerable": 0.5},
                         "realization": 0.6},
        "base": {},
        "optimistic": {"assumptions": {"share_answerable": 0.8}}
      },
      "breakeven_on": "share_answerable"
    }

Every driver's annual value is the product of its `terms`, each looked up in
`assumptions`. Products of named quantities keep the arithmetic auditable —
a reader can see exactly which numbers produced the benefit, which is the
whole point of a business case that has to survive a finance review.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys

CONFIDENCE = ("measured", "estimated", "assumed")


# ── spec handling ────────────────────────────────────────────────────────

def load_spec(path):
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    validate(spec)
    return spec


def validate(spec):
    """Fail loudly and specifically. A silent default in a business case is
    worse than a crash, because it ships as a number someone trusts."""
    errors = []
    if not spec.get("drivers"):
        errors.append("spec needs at least one entry in 'drivers'")
    assumptions = spec.get("assumptions", {})
    for d in spec.get("drivers", []):
        if not d.get("name"):
            errors.append("every driver needs a 'name'")
        if not d.get("terms"):
            errors.append("driver %r needs 'terms'" % d.get("name", "?"))
        for term in d.get("terms", []):
            if term not in assumptions:
                errors.append(
                    "driver %r uses term %r, which is not in 'assumptions'"
                    % (d.get("name", "?"), term))
        conf = d.get("basis", "assumed")
        if conf not in CONFIDENCE:
            errors.append("driver %r has basis %r; expected one of %s"
                          % (d.get("name", "?"), conf, ", ".join(CONFIDENCE)))
    horizon = spec.get("horizon_years", 3)
    ramp = spec.get("ramp")
    if ramp and len(ramp) != horizon:
        errors.append("'ramp' has %d entries but horizon_years is %d"
                      % (len(ramp), horizon))
    be = spec.get("breakeven_on")
    if be and be not in assumptions:
        errors.append("'breakeven_on' names %r, which is not an assumption" % be)
    if errors:
        raise SystemExit("Spec problems:\n  - " + "\n  - ".join(errors))


def resolve(spec, scenario_name):
    """Merge a scenario's overrides onto the base spec."""
    merged = copy.deepcopy(spec)
    scen = spec.get("scenarios", {}).get(scenario_name, {}) or {}
    merged["assumptions"].update(scen.get("assumptions", {}))
    merged.setdefault("costs", {}).update(scen.get("costs", {}))
    for key in ("realization", "ramp", "discount_rate", "horizon_years"):
        if key in scen:
            merged[key] = scen[key]
    return merged


# ── the model ────────────────────────────────────────────────────────────

def driver_values(resolved):
    a = resolved["assumptions"]
    out = []
    for d in resolved["drivers"]:
        value = 1.0
        for term in d["terms"]:
            value *= a[term]
        for term in d.get("minus_terms", []):
            value -= a[term]
        out.append({
            "name": d["name"],
            "basis": d.get("basis", "assumed"),
            "note": d.get("note", ""),
            "annual_value": value,
        })
    return out


def run(resolved):
    horizon = int(resolved.get("horizon_years", 3))
    rate = float(resolved.get("discount_rate", 0.10))
    realization = float(resolved.get("realization", 1.0))
    ramp = resolved.get("ramp") or [1.0] * horizon
    costs = resolved.get("costs", {})
    build = float(costs.get("build_once", 0.0))
    run_annual = float(costs.get("run_annual", 0.0))

    drivers = driver_values(resolved)
    gross_annual = sum(d["annual_value"] for d in drivers)

    years, cumulative, npv = [], 0.0, -build
    for y in range(1, horizon + 1):
        benefit = gross_annual * ramp[y - 1] * realization
        cost = run_annual + (build if y == 1 else 0.0)
        net = benefit - cost
        cumulative += net
        npv += net / ((1 + rate) ** y) if y else net
        years.append({
            "year": y,
            "benefit": benefit,
            "cost": cost,
            "net": net,
            "cumulative": cumulative,
        })

    # NPV convention: year-1 flows already carry the build cost, so discount
    # every year uniformly rather than treating build as a t=0 outflow twice.
    npv = sum(y["net"] / ((1 + rate) ** y["year"]) for y in years)

    total_benefit = sum(y["benefit"] for y in years)
    total_cost = sum(y["cost"] for y in years)

    return {
        "drivers": drivers,
        "gross_annual_benefit": gross_annual,
        "years": years,
        "npv": npv,
        "total_benefit": total_benefit,
        "total_cost": total_cost,
        "net_benefit": total_benefit - total_cost,
        "roi_pct": ((total_benefit - total_cost) / total_cost * 100.0
                    if total_cost else float("inf")),
        "payback_months": payback_months(years),
    }


def payback_months(years):
    """Months until cumulative net turns positive, interpolating inside the
    year it happens. None means it never pays back inside the horizon."""
    prior = 0.0
    for y in years:
        if y["cumulative"] >= 0:
            if y["net"] <= 0:
                return (y["year"] - 1) * 12
            frac = (-prior) / y["net"] if prior < 0 else 0.0
            return round((y["year"] - 1) * 12 + frac * 12, 1)
        prior = y["cumulative"]
    return None


# ── sensitivity and breakeven ────────────────────────────────────────────

def tornado(spec, scenario_name, swing=0.2):
    """Vary each assumption one at a time and rank by NPV swing. Shows which
    number the case actually rests on — usually not the one under debate."""
    base_resolved = resolve(spec, scenario_name)
    base_npv = run(base_resolved)["npv"]
    rows = []
    for key, value in sorted(base_resolved["assumptions"].items()):
        if not isinstance(value, (int, float)) or value == 0:
            continue
        low = copy.deepcopy(base_resolved)
        low["assumptions"][key] = value * (1 - swing)
        high = copy.deepcopy(base_resolved)
        high["assumptions"][key] = value * (1 + swing)
        lo_npv, hi_npv = run(low)["npv"], run(high)["npv"]
        rows.append({
            "assumption": key,
            "base_value": value,
            "low_npv": lo_npv,
            "high_npv": hi_npv,
            "swing": abs(hi_npv - lo_npv),
        })
    rows.sort(key=lambda r: r["swing"], reverse=True)
    return {"base_npv": base_npv, "swing_pct": swing * 100, "rows": rows}


def breakeven(spec, scenario_name, key):
    """Solve for the value of `key` where NPV crosses zero, by bisection.

    This reframes the debate usefully: instead of arguing whether adoption
    will be 60% or 75%, everyone can look at the number it has to clear."""
    resolved = resolve(spec, scenario_name)
    base = resolved["assumptions"][key]
    if not isinstance(base, (int, float)) or base == 0:
        return None

    def npv_at(x):
        trial = copy.deepcopy(resolved)
        trial["assumptions"][key] = x
        return run(trial)["npv"]

    lo, hi = 0.0, base * 4 or 1.0
    npv_lo, npv_hi = npv_at(lo), npv_at(hi)
    if npv_lo > 0:
        return {"assumption": key, "base_value": base, "breakeven_value": 0.0,
                "outcome": "positive_at_zero", "search_ceiling": hi}
    if npv_hi < 0:
        return {"assumption": key, "base_value": base, "breakeven_value": None,
                "outcome": "never", "search_ceiling": hi}
    for _ in range(80):
        mid = (lo + hi) / 2
        if npv_at(mid) < 0:
            lo = mid
        else:
            hi = mid
    be = (lo + hi) / 2
    return {
        "assumption": key,
        "base_value": base,
        "breakeven_value": be,
        "outcome": "found",
        "headroom_pct": (base - be) / base * 100.0 if base else None,
    }


# ── rendering ────────────────────────────────────────────────────────────

def money(x, currency):
    if x is None:
        return "—"
    sign = "-" if x < 0 else ""
    # "EUR 1,200" reads; "EUR1,200" does not. Symbols like € stay tight.
    gap = " " if currency and currency.isalpha() else ""
    return "%s%s%s%s" % (sign, currency, gap, format(abs(round(x)), ",d"))


def render_markdown(spec, results, sens, be, ref):
    cur = spec.get("currency", "")
    horizon = int(spec.get("horizon_years", 3))
    rate = float(spec.get("discount_rate", 0.10))
    out = []
    out.append("# ROI scenarios — %s" % spec.get("case", "unnamed case"))
    out.append("")
    out.append("%d-year horizon, %.0f%% discount rate. Every figure below is "
               "modelled, not measured; the basis column says how much weight "
               "each driver can carry." % (horizon, rate * 100))
    out.append("")

    out.append("## Scenario summary")
    out.append("")
    out.append("| Scenario | NPV | Payback | %d-yr benefit | %d-yr cost | ROI |"
               % (horizon, horizon))
    out.append("|---|---:|---:|---:|---:|---:|")
    for name, r in results.items():
        pb = ("%.0f mo" % r["payback_months"]
              if r["payback_months"] is not None else "never")
        out.append("| %s | %s | %s | %s | %s | %.0f%% |" % (
            name, money(r["npv"], cur), pb, money(r["total_benefit"], cur),
            money(r["total_cost"], cur), r["roi_pct"]))
    out.append("")

    for name, r in results.items():
        out.append("### %s — cash flow" % name)
        out.append("")
        out.append("| Year | Benefit | Cost | Net | Cumulative |")
        out.append("|---|---:|---:|---:|---:|")
        for y in r["years"]:
            out.append("| %d | %s | %s | %s | %s |" % (
                y["year"], money(y["benefit"], cur), money(y["cost"], cur),
                money(y["net"], cur), money(y["cumulative"], cur)))
        out.append("")

    out.append("## Value drivers")
    out.append("")
    out.append("| Driver | Basis | Annual value (%s) |" % ref)
    out.append("|---|---|---:|")
    for d in results[ref]["drivers"]:
        out.append("| %s | %s | %s |" % (
            d["name"], d["basis"].title(), money(d["annual_value"], cur)))
    out.append("")

    out.append("## What the case rests on")
    out.append("")
    out.append("Each assumption moved +/-%.0f%% on its own, ranked by how much "
               "the NPV moves. The top row is the number worth arguing about."
               % sens["swing_pct"])
    out.append("")
    out.append("| Assumption | Base | NPV low | NPV high | Swing |")
    out.append("|---|---:|---:|---:|---:|")
    for row in sens["rows"][:10]:
        out.append("| %s | %s | %s | %s | %s |" % (
            row["assumption"], format_number(row["base_value"]),
            money(row["low_npv"], cur), money(row["high_npv"], cur),
            money(row["swing"], cur)))
    out.append("")

    if be:
        out.append("## Breakeven")
        out.append("")
        outcome = be.get("outcome")
        if outcome == "never":
            out.append("`%s` never reaches breakeven, even at %s — %.0fx the base "
                       "assumption of %s. No setting of this assumption rescues the "
                       "case at this cost, so the question is not what to assume but "
                       "whether to shrink the scope or drop it."
                       % (be["assumption"], format_number(be["search_ceiling"]),
                          be["search_ceiling"] / be["base_value"] if be["base_value"] else 0,
                          format_number(be["base_value"])))
        elif outcome == "positive_at_zero":
            out.append("The case is positive even with `%s` at zero, so it is not "
                       "load-bearing. Pick a different assumption to test."
                       % be["assumption"])
        else:
            gap = be.get("headroom_pct")
            if gap is None:
                tail = ""
            elif gap >= 0:
                # Breakeven sits below the assumption: room to be wrong.
                tail = (", leaving %.0f%% headroom — the assumption can be this "
                        "much too optimistic and the case still holds" % gap)
            else:
                # Breakeven sits above it: the case does not work as assumed.
                tail = (", which is %.0f%% **above** the base assumption — on these "
                        "numbers the case does not clear, and this is the gap to "
                        "close or concede" % abs(gap))
            out.append("`%s` has to reach **%s** for the case to wash "
                       "(base assumption: %s%s)." % (
                           be["assumption"],
                           format_number(be["breakeven_value"]),
                           format_number(be["base_value"]), tail))
        out.append("")
    return "\n".join(out)


def format_number(x):
    if x is None:
        return "—"
    if isinstance(x, float) and 0 < abs(x) < 10:
        return "%.3g" % x
    return format(round(x, 2), ",")


EXAMPLE = {
    "case": "Supplier query assistant",
    "currency": "EUR",
    "horizon_years": 3,
    "discount_rate": 0.10,
    "assumptions": {
        "queries_per_year": 31200,
        "share_answerable": 0.70,
        "hours_saved_per_query": 0.25,
        "loaded_hourly_cost": 48.0,
        "discount_capture_uplift": 120000.0,
    },
    "drivers": [
        {"name": "Clerk time released", "basis": "estimated",
         "terms": ["queries_per_year", "share_answerable",
                   "hours_saved_per_query", "loaded_hourly_cost"],
         "note": "Time released, not headcount removed — see harvest test."},
        {"name": "Early-payment discounts captured", "basis": "assumed",
         "terms": ["discount_capture_uplift"],
         "note": "Assumes faster release actually reaches the payment run."},
    ],
    "costs": {"build_once": 180000, "run_annual": 90000},
    "ramp": [0.4, 1.0, 1.0],
    "realization": 0.8,
    "scenarios": {
        "conservative": {"assumptions": {"share_answerable": 0.5,
                                         "discount_capture_uplift": 40000.0},
                         "realization": 0.6},
        "base": {},
        "optimistic": {"assumptions": {"share_answerable": 0.8,
                                       "discount_capture_uplift": 180000.0},
                       "realization": 0.9},
    },
    "breakeven_on": "share_answerable",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("spec", nargs="?", help="path to the JSON spec")
    ap.add_argument("--format", choices=("markdown", "json"), default="markdown")
    ap.add_argument("--swing", type=float, default=0.2,
                    help="sensitivity swing, default 0.2 for +/-20%%")
    ap.add_argument("--example", action="store_true",
                    help="print a starter spec and exit")
    args = ap.parse_args()

    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    if not args.spec:
        ap.error("give a spec path, or --example to print a starter spec")

    spec = load_spec(args.spec)
    names = list(spec.get("scenarios") or {"base": {}})
    results = {n: run(resolve(spec, n)) for n in names}
    ref = "base" if "base" in names else names[0]
    sens = tornado(spec, ref, args.swing)
    be = breakeven(spec, ref, spec["breakeven_on"]) if spec.get("breakeven_on") else None

    if args.format == "json":
        print(json.dumps({"case": spec.get("case"), "scenarios": results,
                          "sensitivity": sens, "breakeven": be}, indent=2))
    else:
        print(render_markdown(spec, results, sens, be, ref))


if __name__ == "__main__":
    sys.exit(main())
