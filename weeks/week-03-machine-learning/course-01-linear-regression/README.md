# Course 1 — Linear Regression

**Duration:** 3 hours (merged simple LR + multiple LR & diagnostics)
**Why this matters:** Linear regression is the simplest learner where every concept that appears later (loss, coefficients, R², residuals, hypothesis testing) shows up in its cleanest form. Part 2 adds the multi-predictor reality: collinearity, leverage, and categorical encoding.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | Fitting a line — least squares from scratch |
| 0:30 – 1:00 | Reading the output — coef, R², RMSE, residuals |
| 1:00 – 1:30 | Inference for β — t-stat, bootstrap CI, assumptions |
| 1:30 – 2:00 | Multiple regression in matrix form & collinearity |
| 2:00 – 2:30 | Residual plots, leverage, Cook's distance |
| 2:30 – 3:00 | Qualitative predictors and interaction terms |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by six exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Derive and compute the least-squares estimate β̂ by hand and via sklearn
2. Interpret `coef_`, `intercept_`, R², and RMSE on a real dataset
3. Test whether a predictor is significant, and produce a 95% confidence interval for the slope using both formula and bootstrap
4. Fit multiple linear regression with sklearn and read the coefficient table
5. Diagnose collinearity using VIF and the four canonical residual plots
6. Encode categorical predictors with one-hot and add an interaction term

## How to run

```bash
uv run jupyter lab weeks/week-03-machine-learning/course-01-linear-regression/
```
