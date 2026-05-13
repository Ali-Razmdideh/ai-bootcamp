# Course 2 — Linear Regression II — Multiple LR & Diagnostics

**Duration:** 1.5 hours
**Why this matters:** Real datasets are multi-predictor and full of traps: collinearity, leverage, non-linearity, heteroscedasticity. Course 2 teaches the four diagnostic plots every working modeler should be able to read in five seconds.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | Multiple regression in matrix form & collinearity |
| 0:30 – 1:00 | Residual plots, leverage, Cook's distance |
| 1:00 – 1:30 | Qualitative predictors and interaction terms |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; append
  `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Fit multiple linear regression with sklearn and read the coefficient table
2. Diagnose collinearity using VIF and the four canonical residual plots
3. Encode categorical predictors with one-hot and add an interaction term

## How to run

```bash
uv run jupyter lab weeks/week-03-machine-learning/course-02-linear-regression-ii/
```
