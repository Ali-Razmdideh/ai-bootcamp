# Course 3 — Logistic Regression II — Multinomial & Regularized

**Duration:** 1.5 hours
**Why this matters:** Real problems have more than two classes and more predictors than observations. Course 3 generalizes binary LR to softmax and adds L1/L2 regularization — closing the loop with Week 3 Course 6.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | Multinomial logistic regression — softmax & one-vs-rest |
| 0:30 – 1:00 | L2 and L1 regularization in logistic regression |
| 1:00 – 1:30 | When LR fails — motivating non-linear classifiers |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; append
  `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Fit multinomial logistic regression and read softmax probabilities
2. Tune `C` (inverse regularization) and produce a coefficient-path plot
3. Identify problems where a linear decision boundary is fundamentally insufficient

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-03-logistic-regression-ii/
```
