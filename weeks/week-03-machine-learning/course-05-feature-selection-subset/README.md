# Course 5 — Feature Selection I — Subset & Stepwise

**Duration:** 1.5 hours
**Why this matters:** When you have 19 predictors and not all of them belong in the model, subset selection is the classical answer. Understanding it builds the intuition that Ridge/Lasso then formalize.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | The combinatorial cost of best-subset selection |
| 0:30 – 1:00 | Forward and backward stepwise selection |
| 1:00 – 1:30 | AIC, BIC, Cp, adjusted R² — and which to trust |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Implement forward stepwise selection on top of `cross_val_score`
2. Compare model size selected by CV vs. BIC vs. adjusted-R²
3. Articulate why best-subset is intractable past ~30 predictors

## How to run

```bash
uv run jupyter lab weeks/week-03-machine-learning/course-05-feature-selection-subset/
```
