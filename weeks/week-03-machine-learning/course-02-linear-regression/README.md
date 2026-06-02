# Week 3 · Course 2 · Linear Regression

**Duration:** ~2.5 hours  
**Level:** Introductory ML  
**Prerequisites:** Course 01 (What is Statistical Learning?)

## What you will learn

| Section | Topic | Libraries |
|---|---|---|
| 1 | Simple linear regression — model, RSS, least squares | `numpy`, `sklearn` |
| 2 | Assessing coefficient accuracy — SE, CI, t-stat, p-value | `statsmodels`, `scipy.stats` |
| 3 | Model accuracy — RSE and R² | `sklearn.metrics` |
| 4 | Multiple linear regression — MLR, interpretation pitfalls | `statsmodels`, `seaborn` |
| 5 | Variable selection — forward/backward, AIC, BIC | `statsmodels` |
| 6 | Qualitative predictors — dummy variables, multi-level factors | `pandas` |
| 7 | Interactions & non-linearity — interaction terms, polynomial regression | `sklearn.pipeline` |

## Files

| File | Description |
|---|---|
| `lecture.ipynb` | Live-coding notebook with runnable examples and exercises |
| `slides/index.html` | Reveal.js slide deck (generated — do not edit directly) |

## Running the notebook

```bash
# From the project root
jupyter notebook weeks/week-03-machine-learning/course-02-linear-regression/lecture.ipynb
```

## Rebuilding the slides

```bash
python scripts/build_slides.py
```

## Key ideas

- **OLS** minimises the Residual Sum of Squares (RSS) → closed-form β̂
- **statsmodels** provides standard errors, confidence intervals, t-statistics, p-values, and the F-test in one `.summary()` call — sklearn does not
- **R²** measures fraction of variance explained; **RSE** measures average prediction error in Y's units
- Adding predictors always increases R² — use **Adjusted R²**, **AIC**, or **cross-validation** to penalise complexity
- **Dummy variables** encode qualitative predictors; always omit one level (the baseline)
- **Interaction terms** allow the effect of one predictor to depend on another; the **hierarchy principle** requires including main effects when interactions are present
- **Polynomial regression** = multiple regression with engineered features x, x², x³, …
