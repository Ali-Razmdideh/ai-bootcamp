# Course 5 — Ensembles — Bagging, Random Forest, Boosting

**Duration:** 1.5 hours
**Why this matters:** Combining many weak trees beats one fancy tree. Random forests and gradient boosting are the two algorithms that win Kaggle competitions and ship in production at every data-driven company.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | Bagging trees and random forests |
| 0:30 – 1:00 | OOB error, feature importance, partial dependence |
| 1:00 – 1:30 | Gradient boosting — learning rate, depth, early stopping |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Fit and tune random forests and gradient-boosted trees
2. Read OOB error and feature-importance plots
3. Pick between RF and GBM based on speed, accuracy, and interpretability

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-05-ensembles/
```
