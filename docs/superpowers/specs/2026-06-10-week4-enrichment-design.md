# Week 4 Enrichment — Design Spec
Date: 2026-06-10

## Goal

Expand all 9 week-04-classification notebooks with richer inline code comments, deeper section prose, and 3 new exercises per course. Also add missing READMEs for courses 3–6.

---

## What Changes

### 1. Code Cell Enrichment (all 9 courses)

Every non-trivial code cell gets inline `#` comments explaining the *why*:
- Why we scale/normalise before a given step
- What a parameter controls (e.g. `C`, `gamma`, `max_depth`)
- What a matrix operation achieves conceptually
- Why we use `stratify=y` in `train_test_split`
- What a plot is communicating

Comments are terse (one line max). No narration of obvious steps.

### 2. Section Prose Expansion (all 9 courses)

Each `##` section markdown cell gets 1–3 added sentences of intuition:
- Math translated to plain English
- A "key insight" note
- When the method breaks down or a common pitfall

### 3. New Exercises — 3 per course (27 total)

Each exercise: blank starter cell + solution cell, matching existing format.

| Course | Exercise 4 | Exercise 5 | Exercise 6 |
|--------|-----------|-----------|-----------|
| C1 KNN | Distance metric comparison (Euclidean vs Manhattan vs Chebyshev) | Effect of k on calibration — plot predicted prob vs actual freq | Imbalanced dataset: compare SMOTE vs class_weight vs threshold tuning |
| C2 Logistic | Regularization path — plot coefficients vs log(C) for L1 | Calibration curve: reliability diagram for LR vs isotonic regression | Multi-class softmax: probability breakdown on 3-class Iris |
| C3 LDA/QDA | Visualise within-class and between-class covariance ellipses | Shrinkage LDA (ledoit-wolf) vs standard LDA on high-dim data | Multi-class threshold analysis: vary prior π_k and observe boundary shift |
| C4 Naive Bayes | Feature independence check: pairwise MI between features | Gaussian NB on text-like toy data vs MultinomialNB | Calibration: NB posterior probabilities are often overconfident — show and fix |
| C5 Poisson GLM | Negative binomial vs Poisson on overdispersed counts | Rate offset: model rate = count/exposure with np.log(exposure) as offset | Residual diagnostics: deviance residuals vs fitted values |
| C6 Comparison | Learning curves for all 5 classifiers on Default | Bias-variance decomposition: repeated train/test splits, track variance | Add a 4th dataset benchmark (Breast Cancer) to the existing comparison grid |
| C7 Trees | Feature importance bar chart + permutation importance comparison | min_samples_leaf tuning: grid search and effect on boundary smoothness | Full pruning path visualisation: all alphas and their subtree sizes |
| C8 Ensembles | OOB error vs CV error as n_estimators grows | n_estimators convergence plot: when does adding more trees stop helping? | Gradient boosting (GBM) vs Random Forest on Heart: AUC comparison |
| C9 SVM | Kernel comparison grid: linear / poly / RBF on three toy datasets | Support vector count vs C: plot n_SVs as C increases | Dual coefficients: identify which points are support vectors and visualise |

### 4. Missing READMEs (courses 3–6)

Add `README.md` to courses 3, 4, 5, 6 matching the format of course 1/2/7/8/9:
- One-line description
- Topics covered (bullet list)
- ISLR chapter reference
- Key concepts

---

## File Changes

| File | Action |
|------|--------|
| `course-01-classification-knn/lecture.ipynb` | enrich code + prose + 3 exercises |
| `course-02-logistic-regression/lecture.ipynb` | enrich code + prose + 3 exercises |
| `course-03-lda-qda/lecture.ipynb` | enrich code + prose + 3 exercises |
| `course-03-lda-qda/README.md` | create |
| `course-04-naive-bayes/lecture.ipynb` | enrich code + prose + 3 exercises |
| `course-04-naive-bayes/README.md` | create |
| `course-05-glm-poisson/lecture.ipynb` | enrich code + prose + 3 exercises |
| `course-05-glm-poisson/README.md` | create |
| `course-06-classification-comparison/lecture.ipynb` | enrich code + prose + 3 exercises |
| `course-06-classification-comparison/README.md` | create |
| `course-07-decision-trees/lecture.ipynb` | enrich code + prose + 3 exercises |
| `course-08-ensembles/lecture.ipynb` | enrich code + prose + 3 exercises |
| `course-09-svm/lecture.ipynb` | enrich code + prose + 3 exercises |

---

## Constraints

- Do not restructure existing cells or change section numbering
- New exercises append after existing ones, maintaining the same blank-starter + solution pattern
- Code style matches existing: numpy/pandas/sklearn/matplotlib, no new dependencies
- Each notebook must remain self-contained and runnable top-to-bottom
