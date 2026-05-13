# Course 6 — Feature Selection II — Ridge, Lasso, Elastic Net

**Duration:** 1.5 hours
**Why this matters:** Instead of picking variables in or out, shrinkage methods pull every coefficient toward zero — softly for Ridge, sharply for Lasso. They are the most common production answer to "too many features."

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | Ridge regression and the bias-variance dial |
| 0:30 – 1:00 | Lasso, sparsity, and the L1 corner |
| 1:00 – 1:30 | Elastic Net and end-to-end pipelines with CV |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; append
  `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Fit Ridge and Lasso with `GridSearchCV` over the regularization strength
2. Read a coefficient-path plot and pick a sensible λ from CV error
3. Build a Pipeline(Scaler → PolynomialFeatures → Lasso) tuned with CV

## How to run

```bash
uv run jupyter lab weeks/week-03-machine-learning/course-06-feature-selection-shrinkage/
```
