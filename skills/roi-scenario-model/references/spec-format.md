# Spec format

The JSON file `scripts/roi_model.py` reads. Run `python scripts/roi_model.py
--example` to print a working starter spec you can edit rather than writing one
from scratch.

## Fields

| Field | Type | Meaning |
|---|---|---|
| `case` | string | Name of the solution being valued. Appears in the report title. |
| `currency` | string | `"EUR"`, `"USD"`, `"€"` — alphabetic codes get a space after them, symbols do not. |
| `horizon_years` | int | Years modelled. 3 is the usual default; past 5 nobody believes it. |
| `discount_rate` | float | Annual discount rate as a decimal. `0.10` = 10%. Use the client's own hurdle rate when they have one. |
| `assumptions` | object | Every named quantity the drivers multiply together. The single source of truth for numbers. |
| `drivers` | array | The benefit tree. One entry per distinct value driver. |
| `costs` | object | `build_once` and `run_annual`. |
| `ramp` | array of float | Share of full benefit realised in each year. Length must equal `horizon_years`. |
| `realization` | float | Share of modelled benefit the business actually banks. `0.8` means 20% leaks away. |
| `scenarios` | object | Named scenarios, each overriding assumptions/costs/realization/ramp. |
| `breakeven_on` | string | Which assumption to solve for the zero-NPV value of. |

## Drivers

```json
{
  "name": "Clerk time released",
  "basis": "estimated",
  "terms": ["queries_per_year", "share_answerable",
            "hours_saved_per_query", "loaded_hourly_cost"],
  "minus_terms": ["review_time_cost"],
  "note": "Time released, not headcount removed."
}
```

- `terms` — assumption keys multiplied together to give the annual value. Every
  key must exist in `assumptions`; a missing one is a hard error rather than a
  silent zero, because a silently-zeroed benefit ships as a number someone
  trusts.
- `minus_terms` — optional, subtracted after the product. Use for costs that
  belong to this specific driver (the human review time a benefit creates)
  rather than to the project as a whole.
- `basis` — `measured`, `estimated`, or `assumed`. Carried through to the report
  so the reader can weight each row. Be honest here; it is what makes the
  document credible rather than promotional.
- `note` — a short caveat shown alongside the driver.

**Keep terms in consistent units.** The commonest error is mixing a monthly
volume with an annual cost. Name assumptions with their period in the key
(`queries_per_year`, not `queries`) and the mistake becomes visible.

## Scenarios

Each scenario overrides only what differs from the base spec:

```json
"scenarios": {
  "conservative": {
    "assumptions": {"share_answerable": 0.5},
    "realization": 0.6,
    "ramp": [0.2, 0.7, 1.0]
  },
  "base": {},
  "optimistic": {"assumptions": {"share_answerable": 0.8}}
}
```

An empty `base` inherits everything. Sensitivity and breakeven are computed
against `base` when it exists, otherwise the first scenario listed.

Scenarios should differ by *named assumptions you can defend*, not by a blanket
multiplier. If you cannot say which assumption makes the conservative case
conservative, it is not a scenario — it is a haircut.

## The arithmetic

For each year *y* in 1..horizon:

```
gross_annual   = Σ over drivers of (Π terms − Σ minus_terms)
benefit(y)     = gross_annual × ramp[y] × realization
cost(y)        = run_annual + (build_once if y == 1 else 0)
net(y)         = benefit(y) − cost(y)
NPV            = Σ net(y) / (1 + discount_rate)^y
ROI%           = (Σ benefit − Σ cost) / Σ cost × 100
payback        = first month where cumulative net ≥ 0, interpolated within
                 the crossing year
```

`build_once` sits in year 1 rather than at t=0, which matches how these projects
are actually funded and avoids double-counting it as a separate outflow.

**Sensitivity** moves each assumption ±20% (configurable with `--swing`) on its
own and ranks by the resulting NPV swing. Terms multiplied inside the same
driver produce identical swings — they are one lever, and the report should say
so rather than presenting them as independent risks.

**Breakeven** bisects for the value of `breakeven_on` where NPV = 0, searching
between zero and 4× the base value. If the case is positive even at zero, that
assumption is not load-bearing and a different one should be chosen.

## Output

`--format markdown` (default) prints a report with the scenario summary, per-
scenario cash flows, the driver table with basis labels, the sensitivity
ranking, and breakeven. `--format json` prints the same data structured, for
feeding into a document generator or a chart.
