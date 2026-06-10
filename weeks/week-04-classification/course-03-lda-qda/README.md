# Course 3 — LDA & QDA

**Duration:** 1.5 hours
**Why this matters:** LDA and QDA are the classical generative classifiers: they model how each class produces its data, then flip it with Bayes' theorem to classify. Understanding them builds intuition for when parametric assumptions help and when they hurt.

## Schedule

| Time        | Topic                       |
|-------------|------------------------------|
| 0:00 – 0:30 | Bayes theorem and Gaussian class models |
| 0:30 – 1:00 | LDA — shared covariance, Fisher projection |
| 1:00 – 1:30 | QDA — per-class covariance, LDA vs QDA tradeoffs |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one, followed by exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Derive and apply Bayes' theorem for classification with Gaussian class models
2. Fit LDA and QDA with sklearn and interpret the Fisher projection
3. Choose between LDA and QDA based on sample size and boundary shape

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-03-lda-qda/
```
