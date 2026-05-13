# Course 6 — Support Vector Machines

**Duration:** 1.5 hours
**Why this matters:** SVMs are how you produce a non-linear decision boundary without ever computing the non-linear features explicitly. They also dominate when p ≫ n — which is the gene-expression and text-classification regime.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | Maximum-margin classifier and support vectors |
| 0:30 – 1:00 | The kernel trick — linear, polynomial, RBF |
| 1:00 – 1:30 | SVM in high dimensions — the Khan gene-expression lab |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; append
  `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Explain the role of C and the geometric meaning of support vectors
2. Plot decision boundaries for linear, polynomial, and RBF kernels
3. Tune (C, γ) with `GridSearchCV` and beat logistic regression on p ≫ n data

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-06-svm/
```
