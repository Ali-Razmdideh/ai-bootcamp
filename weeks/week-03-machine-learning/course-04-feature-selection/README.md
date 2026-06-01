# Course 4 — Feature Selection

**Duration:** 3 hours (merged subset/stepwise + Ridge/Lasso/Elastic Net)
**Why this matters:** When you have many predictors, you need either to pick a subset (classical stepwise) or shrink coefficients toward zero (Ridge/Lasso). This session covers both families so students can choose the right tool.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | The combinatorial cost of best-subset selection |
| 0:30 – 1:00 | Forward stepwise selection |
| 1:00 – 1:30 | AIC, BIC, Cp, adjusted R² — and which to trust |
| 1:30 – 2:00 | Ridge regression and the bias-variance dial |
| 2:00 – 2:30 | Lasso, sparsity, and the L1 corner |
| 2:30 – 3:00 | Elastic Net and end-to-end pipelines with CV |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by six exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Implement forward stepwise selection on top of `cross_val_score`
2. Compare model size selected by CV vs. BIC vs. adjusted-R²
3. Articulate why best-subset is intractable past ~30 predictors
4. Fit Ridge and Lasso with `GridSearchCV` over the regularization strength
5. Read a coefficient-path plot and pick a sensible λ from CV error
6. Build a Pipeline(Scaler → PolynomialFeatures → Lasso) tuned with CV

## How to run

```bash
uv run jupyter lab weeks/week-03-machine-learning/course-04-feature-selection/
```
