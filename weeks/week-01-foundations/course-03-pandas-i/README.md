# Course 3 — Pandas I: Series, DataFrame, Indexing

**Duration:** 1.5 hours
**Why this matters:** NumPy gives you typed buffers. Pandas adds *labels* —
row names, column names, automatic alignment — which is what makes real data
work tolerable. This is the first course where the data you handle starts
looking like the data you will see in industry.

## Schedule

| Time        | Topic                            |
|-------------|----------------------------------|
| 0:00 – 0:30 | Series                           |
| 0:30 – 1:00 | DataFrames                       |
| 1:00 – 1:30 | Indexing & filtering             |

## Files

- `slides/index.html` — Reveal.js deck. Every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter + *Run & Check* + reference solution on failure).
- `lecture.ipynb` — live-coding notebook + three exercises with solutions.

## Learning outcomes

By the end of the session a student can:

1. Construct a `Series` and a `DataFrame` from dicts, lists, and Series with
   misaligned indices, and explain where NaNs come from on combination.
2. Inspect any new dataset in three commands: `shape`, `dtypes`, `describe()`.
3. Select rows and columns with `.loc`, `.iloc`, boolean masks, and
   `query()`; reorder with `set_index`/`sort_values`.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-03-pandas-i/
```
