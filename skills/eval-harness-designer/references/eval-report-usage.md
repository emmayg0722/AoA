# eval_report.py usage

The script computes per-slice metrics with confidence intervals so results are
consistent between runs and small slices announce themselves rather than being
read as fact.

```bash
python scripts/eval_report.py --example > predictions.csv   # sample input
python scripts/eval_report.py predictions.csv
python scripts/eval_report.py predictions.csv --positive fraud
python scripts/eval_report.py predictions.csv --baseline last-week.csv
python scripts/eval_report.py predictions.csv --format json
```

## Input

CSV with a header row.

| Column | Required | Meaning |
|---|---|---|
| `id` | yes | Unique per case. Duplicates are an error — they usually mean two runs got concatenated. |
| `slice` | yes | The stratum: segment, difficulty, language, input quality. Blank becomes `(unsliced)`. |
| `expected` | yes | The correct label. |
| `predicted` | yes | What the system produced. |
| `confidence` | no | Float 0–1. Present for any row, and the calibration section appears. |

One case per row. For multi-label or multi-field extraction, emit one row per
field — set `slice` to the field name and you get per-field accuracy directly.

## Flags

| Flag | Effect |
|---|---|
| `--positive LABEL` | Compute precision, recall and F1 against this label. Use for binary problems; omit for multi-class, where per-slice accuracy plus the confusion you can see in the data is more informative. |
| `--baseline FILE` | Compare against a previous run, per slice. |
| `--min-n N` | Flag slices below this size. Default 20. |
| `--format json` | Structured output for feeding a document or chart. |

## How to read it

**Confidence intervals are Wilson intervals**, not the normal approximation.
Eval slices are small and often score near 0 or 1, which is exactly where the
naive interval misbehaves — it can produce bounds below 0 or above 1 and
understates uncertainty at the extremes.

**"Within noise" is a real verdict, not a hedge.** A slice is only called
improved or regressed when the two intervals do not overlap. A ten-point move on
twelve cases will read as within noise, and that is correct: with that sample
size you cannot distinguish it from chance. The fix is more cases in that slice,
not a more optimistic reading of the ones you have.

**The thin-slice warning is the most valuable line in the output.** Most
over-claiming in evaluation comes from reading a number off a slice with a
handful of cases. If everything is flagged, the honest summary is that the test
set is not yet large enough to support conclusions per slice — say that rather
than quoting the numbers.

**Calibration buckets** compare claimed confidence against observed correctness.
A system whose 0.9 bucket is right 60% of the time has unusable confidence
values: you cannot route on them, cannot abstain on them, and should not show
them to users.

## Suggested workflow

1. Freeze a test set and keep it in version control alongside the prompt or
   model config, so a score can always be traced to what produced it.
2. Run the script and commit the output as the baseline.
3. On every prompt, model or retrieval change, re-run with `--baseline` pointing
   at the committed run.
4. Act only on slices reported as improved or regressed. Treat "within noise" as
   what it says — no evidence either way.

This is deliberately boring and repeatable. The value is in having the same
numbers computed the same way every time, which is what makes a regression
visible at all.
