# Course 3 — Feature Engineering

**Duration:** 1.5 hours
**Why this matters:** Models do not learn from raw columns — they learn from the features you hand them. Scaling, polynomial expansion, one-hot encoding, and interaction terms are the four moves that turn a mediocre model into a competitive one.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | Scaling, skew, pipelines, ColumnTransformer |
| 0:30 – 1:00 | Polynomial features — underfit, fit, overfit |
| 1:00 – 1:30 | Categorical encoding & interactions |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Build an end-to-end sklearn `Pipeline` with `ColumnTransformer`
2. Visualize the underfit/overfit curve as polynomial degree changes
3. One-hot encode categoricals and add interaction features correctly

## How to run

```bash
uv run jupyter lab weeks/week-03-machine-learning/course-03-feature-engineering/
```
