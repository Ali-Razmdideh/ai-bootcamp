# Course 4 — Cross-Validation

**Duration:** 1.5 hours
**Why this matters:** A single train/test split is noisy: it can pick the "best" polynomial degree differently every time you change the seed. Cross-validation is how you stop fooling yourself.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | The validation-set trap |
| 0:30 – 1:00 | LOOCV and K-fold cross-validation |
| 1:00 – 1:30 | The bootstrap for SE & CI estimation |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Use `cross_val_score` and `KFold` to estimate test error reliably
2. Reproduce ISLP Figure 5.4 (CV error vs. polynomial degree)
3. Bootstrap a 95% confidence interval for a regression coefficient

## How to run

```bash
uv run jupyter lab weeks/week-03-machine-learning/course-04-cross-validation/
```
