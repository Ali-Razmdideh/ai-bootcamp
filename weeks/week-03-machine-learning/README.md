# Week 3 — Machine Learning: Regression, Validation, Selection

**Total time:** 9 hours · two days of three 1.5-hour sessions

Week 3 takes students from "I can manipulate data with NumPy and Pandas" to
"I can fit, validate, and shrink a real regression model." Every canonical
example is lifted from the ISLP textbook (James, Witten, Hastie, Tibshirani,
Taylor — *An Introduction to Statistical Learning, Python edition*). The
three student exercises per course stay on the seaborn datasets from Week 1
so the data-loading surface never changes.

## Day 1 — Regression, and how to feed it

| Course | Topic | Folder |
|--------|-------|--------|
| 1 | Linear Regression I — simple LR | [course-01-linear-regression-i/](course-01-linear-regression-i/) |
| 2 | Linear Regression II — multiple LR, diagnostics | [course-02-linear-regression-ii/](course-02-linear-regression-ii/) |
| 3 | Feature Engineering | [course-03-feature-engineering/](course-03-feature-engineering/) |

## Day 2 — Validating and shrinking the model

| Course | Topic | Folder |
|--------|-------|--------|
| 4 | Cross-Validation | [course-04-cross-validation/](course-04-cross-validation/) |
| 5 | Feature Selection I — subset & stepwise | [course-05-feature-selection-subset/](course-05-feature-selection-subset/) |
| 6 | Feature Selection II — Ridge, Lasso, Elastic Net | [course-06-feature-selection-shrinkage/](course-06-feature-selection-shrinkage/) |

## The arc

Day 1 builds the regression habit: fit, read coefficients, check residuals,
add interactions, transform features. Day 2 answers the questions Day 1
raises — "how do I know my polynomial degree isn't overfitting?" (CV) and
"how do I pick predictors when I have too many?" (subset selection,
Ridge/Lasso). The narrative flows: features → fit → validate → shrink.

## Datasets

ISLP CSVs (`Auto`, `Boston`, `Hitters`) are fetched once and cached via
`shared.data_utils.load_dataset(name)` — same pattern as Week 1.

## Running everything

```bash
uv sync
uv run jupyter lab weeks/week-03-machine-learning/
```

To regenerate every notebook from source:

```bash
uv run python scripts/build_week03_notebooks.py
```
