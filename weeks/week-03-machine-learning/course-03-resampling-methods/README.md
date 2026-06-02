# Course 3 — Cross-Validation and the Bootstrap

**Duration:** 2 hours  
**Slides:** [slides/index.html](slides/index.html)  
**Notebook:** [lecture.ipynb](lecture.ipynb)

## Overview

How do we honestly estimate how well a model will perform on new data?
This course covers the two most important resampling tools in statistical
learning — cross-validation and the bootstrap — drawing directly from
Hastie & Tibshirani's *Introduction to Statistical Learning* (Chapter 5).

**Part 1 — Why Training Error Lies** establishes the gap between training
and test error, introduces the validation-set approach and its two key
drawbacks: high variance and upward-biased error estimates.

**Part 2 — Cross-Validation** covers K-fold CV from the formula up,
LOOCV and its leverage shortcut for OLS, the bias-variance tradeoff in
choosing K (K = 5 or 10 is the practical default), CV for classification,
and — critically — the right vs wrong way to apply CV when preprocessing
is involved. A hands-on leakage demo shows how skipping feature selection
inside the CV loop produces near-zero error on random labels.

**Part 3 — The Bootstrap** introduces the investment α example, shows
why we cannot draw new samples from the true population in practice,
and demonstrates resampling with replacement as the solution. Covers
bootstrap SE, the percentile confidence interval, `scipy.stats.bootstrap`,
and why bootstrap underestimates prediction error (~63% overlap).

## Libraries introduced

| Library | Key APIs |
|---|---|
| `sklearn.model_selection` | `KFold`, `LeaveOneOut`, `cross_val_score`, `GridSearchCV` |
| `sklearn.pipeline` | `Pipeline` — prevents data leakage |
| `sklearn.feature_selection` | `SelectKBest` |
| `scipy.stats` | `scipy.stats.bootstrap`, `scipy.stats.sem`, `t.interval` |
| `numpy` | `rng.integers(..., replace=True)` for manual bootstrap |

## Slides rebuilt from

- Ch5_Resampling_Methods.pdf (Hastie & Tibshirani slides)
