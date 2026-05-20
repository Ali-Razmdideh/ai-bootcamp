# Course 2 — Pandas: Series, DataFrame, GroupBy, Joins, Time

**Duration:** 3 hours (merged Part I + Part II)
**Why this matters:** NumPy gives you typed buffers. Pandas adds *labels* —
row names, column names, automatic alignment — which is what makes real data
work tolerable. This course is the first place the data you handle starts
looking like the data you will see in industry.

## Schedule

| Time        | Topic                            |
|-------------|----------------------------------|
| 0:00 – 0:30 | Series                           |
| 0:30 – 1:00 | DataFrames                       |
| 1:00 – 1:30 | Indexing & filtering             |
| 1:30 – 2:00 | Missing data & column ops        |
| 2:00 – 2:30 | GroupBy, pivot, merge            |
| 2:30 – 3:00 | Time series                      |

## Files

- `slides/index.html` — Reveal.js deck.
- `lecture.ipynb` — live-coding notebook + six exercises with solutions.

## Learning outcomes

1. Construct a `Series` / `DataFrame` from dicts, lists, and Series with misaligned indices.
2. Inspect any new dataset in three commands: `shape`, `dtypes`, `describe()`.
3. Select rows/columns with `.loc`, `.iloc`, boolean masks, and `query()`.
4. Diagnose missing data with `isna().sum()` and fix it with `dropna` / `fillna` / `interpolate`.
5. Aggregate with `groupby` + `agg`, reshape with `pivot_table`, join with `pd.merge`.
6. Convert string dates to a `DatetimeIndex`, resample at a different frequency, and interpolate when upsampling.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-02-pandas/
```
