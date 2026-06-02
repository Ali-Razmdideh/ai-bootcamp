# Week 3 — What is Statistical Learning?

**Total time:** 1 course · lecture slides

This week introduces the conceptual foundation of statistical learning, drawing
directly from Hastie & Tibshirani's *Introduction to Statistical Learning*.
It covers the full arc from motivation (why the field matters) to the formal
framework (Y = f(X) + ε) and the core theoretical tools (bias-variance
trade-off, classification).

## Course

| # | Title | Folder |
|---|-------|--------|
| 1 | What is Statistical Learning? | [course-01-what-is-statistical-learning/](course-01-what-is-statistical-learning/) |

## What this course covers

### Part 1 — Why Statistical Learning Matters
IBM Watson, Hal Varian's "sexy job" quote, FiveThirtyEight. The eight canonical
statistical learning problems: prostate cancer, phoneme classification, heart
attack prediction, spam detection, handwritten digits, cancer gene expression,
salary & demographics, LANDSAT image classification.

### Part 2 — Eight Problems Up Close
Deep dives into each of the eight problems: what the data looks like, what the
scatter matrices reveal, and what modelling challenges arise.

### Part 3 — Types of Learning
The supervised learning problem (regression vs classification), objectives,
philosophy. Unsupervised learning (clustering, PCA). Semi-supervised learning.
Netflix Prize as a case study. Statistical learning vs machine learning.

### Part 4 — The Statistical Framework — Y = f(X) + ε
The Advertising dataset. Notation. The regression function f(x) = E[Y|X=x]
as the ideal predictor. Reducible vs irreducible error decomposition.
Nearest-neighbor estimation of f.

### Part 5 — Estimating f and Assessing Models
Curse of dimensionality. Parametric models (linear, quadratic, splines).
Overfitting. Flexibility vs interpretability trade-off. Training MSE vs test
MSE. The U-shaped test MSE curve. Bias-variance decomposition.

### Part 6 — Classification
The Bayes optimal classifier and conditional class probabilities. Bayes error
rate. KNN for classification. Decision boundaries in 2D (K=1, 10, 100).
Classification error rate.

## Source material

Slides built from:
- Hastie & Tibshirani — *Ch1_Introduction.pdf* (29 slides)
- Hastie & Tibshirani — *Ch2_Statistical_Learning.pdf* (37 slides)

Reference text: *An Introduction to Statistical Learning* (ISLR/ISLP).

## Regenerating slides

```bash
python3 scripts/build_slides.py
```

Opens in the browser:

```bash
open weeks/week-03-machine-learning/course-01-what-is-statistical-learning/slides/index.html
```
