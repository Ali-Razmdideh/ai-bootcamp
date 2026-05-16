# Course 4 — Pandas II: Cleaning, GroupBy, Joins, Time

**Duration:** 1.5 hours
**Why this matters:** Real data is missing, messy, and split across tables.
This course covers the three reshape verbs that close most data-prep tickets:
`groupby`, `merge`, `resample`. By the end you can clean and aggregate any
flat dataset and handle a basic time series.

## Schedule

| Time        | Topic                            |
|-------------|----------------------------------|
| 0:00 – 0:30 | Missing data & column ops        |
| 0:30 – 1:00 | GroupBy, pivot, merge            |
| 1:00 – 1:30 | Time series                      |

## Files

- `slides/index.html` — Reveal.js deck. Every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter + *Run & Check* + reference solution on failure).
- `lecture.ipynb` — live-coding notebook + three exercises with solutions.

## Learning outcomes

By the end of the session a student can:

1. Diagnose missing data with `isna().sum()` and fix it with `dropna`,
   `fillna`, or `interpolate`.
2. Aggregate with `groupby` + `agg`, reshape with `pivot_table`, and join
   two tables with `pd.merge`.
3. Convert string dates to a `DatetimeIndex`, resample at a different
   frequency, and interpolate when upsampling.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-04-pandas-ii/
```
