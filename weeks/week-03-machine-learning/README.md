# Week 3 — Machine Learning: Regression, Validation, Selection

**Total time:** 9 hours · four sessions (two 3-hour + two 1.5-hour)

Week 3 takes students from "I can manipulate data with NumPy and Pandas" to
"I can fit, validate, and shrink a real regression model." Every canonical
example is lifted from the ISLP textbook (James, Witten, Hastie, Tibshirani,
Taylor — *An Introduction to Statistical Learning, Python edition*). The
three student exercises per short course (six per merged course) stay on the
seaborn datasets from Week 1 so the data-loading surface never changes.

## Day 1 — Regression, and how to feed it

| Course | Topic | Folder |
|--------|-------|--------|
| 1 | Linear Regression — simple & multiple LR, diagnostics | [course-01-linear-regression/](course-01-linear-regression/) |
| 2 | Feature Engineering | [course-02-feature-engineering/](course-02-feature-engineering/) |

## Day 2 — Validating and shrinking the model

| Course | Topic | Folder |
|--------|-------|--------|
| 3 | Cross-Validation | [course-03-cross-validation/](course-03-cross-validation/) |
| 4 | Feature Selection — subset/stepwise & Ridge/Lasso/Elastic Net | [course-04-feature-selection/](course-04-feature-selection/) |

## The arc

Day 1 builds the regression habit: fit, read coefficients, check residuals,
add interactions, transform features. Day 2 answers the questions Day 1
raises — "how do I know my polynomial degree isn't overfitting?" (CV) and
"how do I pick predictors when I have too many?" (subset selection,
Ridge/Lasso). The narrative flows: features → fit → validate → shrink.

## Datasets

ISLP CSVs (`Auto`, `Boston`, `Hitters`) are fetched once and cached via
`shared.data_utils.load_dataset(name)` — same pattern as Week 1.

## Interactive slides

Every course's `slides/index.html` is a self-contained Reveal.js deck where
each notebook code cell appears as a **runnable example** (prefilled answer
+ description + *Run* button) and each notebook exercise appears as a
**checked exercise** (starter code + *Run & Check* + reference solution on
failure). Code runs in the browser via Pyodide, which lazy-loads
scikit-learn / pandas / matplotlib on first use. ISLP datasets (Boston,
Hitters, Auto, …) that the notebooks load via `shared.data_utils` are
inlined as small seeded synthetic DataFrames in the slide examples so they
work without filesystem access.

## Running everything

```bash
uv sync
uv run jupyter lab weeks/week-03-machine-learning/
```

To regenerate every notebook and slide deck from source:

```bash
uv run python scripts/build_week03_notebooks.py
uv run python scripts/merge_week03_slides.py
```

(`build_slides.py` only covers Week 4+; Week 3 slide decks are merged/restored
from the full interactive HTML via `merge_week03_slides.py`.)
