# Course 2 — Logistic Regression I — Binary

**Duration:** 1.5 hours
**Why this matters:** Logistic regression is the linear classifier — and the single most important machine-learning model in industry. Course 2 walks from the sigmoid all the way to ROC curves on a real binary problem.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | From linear regression to log-odds — the sigmoid |
| 0:30 – 1:00 | Multiple logistic regression & odds-ratio reading |
| 1:00 – 1:30 | predict_proba, threshold tuning, ROC and AUC |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Explain the log-odds link and the maximum-likelihood objective
2. Interpret a logistic-regression coefficient as an odds ratio
3. Tune the decision threshold to maximize F1 on an imbalanced problem

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-02-logistic-regression-i/
```
