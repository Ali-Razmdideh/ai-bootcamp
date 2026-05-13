# Course 1 — Linear Regression I — Simple Linear Regression

**Duration:** 1.5 hours
**Why this matters:** Linear regression is the simplest learner where every concept that appears later (loss, coefficients, R², residuals, hypothesis testing) shows up in its cleanest form. Master it here once and the rest of the course just adds knobs.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | Fitting a line — least squares from scratch |
| 0:30 – 1:00 | Reading the output — coef, R², RMSE, residuals |
| 1:00 – 1:30 | Inference for β — t-stat, p-value, CIs, assumptions |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; append
  `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Derive and compute the least-squares estimate β̂ by hand and via sklearn
2. Interpret `coef_`, `intercept_`, R², and RMSE on a real dataset
3. Test whether a predictor is significant, and produce a 95% confidence interval for the slope using both formula and bootstrap

## How to run

```bash
uv run jupyter lab weeks/week-03-machine-learning/course-01-linear-regression-i/
```
