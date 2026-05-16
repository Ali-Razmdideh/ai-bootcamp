# Course 6 — Viz Capstone + SciPy Bridge

**Duration:** 1.5 hours
**Why this matters:** This is where the foundations meet. Seaborn gives you
statistical plots in one line; SciPy gives you distributions and the
optimizer that lives under every supervised model. The hour ends with the
**Grand Finale Lab** — a live, end-to-end pipeline that uses every skill from
the previous five courses.

## Schedule

| Time        | Topic                                |
|-------------|--------------------------------------|
| 0:00 – 0:30 | Seaborn for statistical plotting     |
| 0:30 – 1:00 | SciPy stats                          |
| 1:00 – 1:30 | SciPy optimize + Grand Finale Lab    |

## Files

- `slides/index.html` — Reveal.js deck. Every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter + *Run & Check* + reference solution on failure).
- `lecture.ipynb` — live-coding notebook + three exercises with solutions.

## Learning outcomes

By the end of the session a student can:

1. Produce a `scatterplot`, `boxplot`, `pairplot`, and correlation `heatmap`
   with Seaborn on a real dataset.
2. Fit a Normal distribution with `stats.norm.fit`, overlay the fitted PDF
   on a histogram, and run a one-sample t-test.
3. Use `optimize.minimize` to find the argmin of a real function and
   complete a load → clean → smooth → plot pipeline on `stock-prices`.

## Capstone — Grand Finale Lab

The last exercise wraps the entire week into one reusable function: load the
`stock-prices` CSV, inject synthetic NaNs, clean with Pandas, compute a
7-day rolling mean with NumPy, and plot raw + smoothed with Matplotlib. If a
student can write it, they own the Week 1 foundations.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-06-viz-capstone-scipy/
```
