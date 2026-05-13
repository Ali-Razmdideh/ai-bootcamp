# Course 1 — Classification + KNN

**Duration:** 1.5 hours
**Why this matters:** Before any specific classifier, students need to internalize the classification interface: predict a label, plot a decision boundary, read a confusion matrix, choose the right metric. KNN is the simplest classifier and makes a perfect first encounter with all of these.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | What a classifier outputs — boundary, confusion matrix, ROC |
| 0:30 – 1:00 | K-Nearest Neighbors — the no-training baseline |
| 1:00 – 1:30 | Class imbalance, stratification, the majority-class trap |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; append
  `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Read a confusion matrix and pick the right metric for the problem
2. Fit KNN and explain how k controls the bias-variance trade-off
3. Handle imbalanced classes with `class_weight` and stratified splits

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-01-classification-knn/
```
