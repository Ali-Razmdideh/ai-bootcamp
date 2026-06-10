# Course 5 — Generalized Linear Models: Poisson Regression

**Duration:** 1.5 hours
**Why this matters:** Not all outcomes are continuous and unbounded. Poisson regression extends the linear model to count data with the right variance structure. Understanding GLMs opens the door to modelling any exponential-family response — including survival, proportions, and beyond.

## Schedule

| Time        | Topic                       |
|-------------|------------------------------|
| 0:00 – 0:30 | The GLM framework — random component, systematic component, link function |
| 0:30 – 1:00 | Poisson regression — log link, rate ratios, offset terms |
| 1:00 – 1:30 | Overdispersion, diagnostics, and Negative Binomial as a fix |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one, followed by exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Explain the three components of a GLM and choose the right link function for count data
2. Fit Poisson regression with statsmodels and interpret rate-ratio coefficients
3. Diagnose overdispersion and apply a Negative Binomial fix

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-05-glm-poisson/
```
