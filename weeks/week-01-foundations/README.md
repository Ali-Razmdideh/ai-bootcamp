# Week 1 — Python & Math Foundations

**Total time:** 12 hours · four 3-hour sessions (NumPy and Pandas now merged into single courses)

Week 1 puts every student on the same numerical-Python footing before the
bootcamp dives into classical ML and deep learning. Every concrete example is
distilled from Aurélien Géron's tool tutorials (NumPy, Pandas, Matplotlib);
every exercise lives on the `shared.data_utils` datasets (`penguins`,
`titanic`, `tips`, `iris`, `stock-prices`) so the data-loading surface never
changes across the week.

## Day 1 — Arrays & frames

| Course | Topic | Folder |
|--------|-------|--------|
| 1 | NumPy — The ND-Array, vectorization & linear algebra | [course-01-numpy/](course-01-numpy/) |
| 2 | Pandas — Series, DataFrames, GroupBy, joins, time | [course-02-pandas/](course-02-pandas/) |

## Day 2 — Plotting and the math bridge

| Course | Topic | Folder |
|--------|-------|--------|
| 3 | Matplotlib essentials | [course-03-matplotlib/](course-03-matplotlib/) |
| 4 | Viz Capstone + SciPy bridge | [course-04-viz-capstone-scipy/](course-04-viz-capstone-scipy/) |

## The arc

Day 1 shifts the student from "Python thinking" (loops) to "matrix thinking"
(vectorization), then introduces Pandas so the same arrays gain labels.
Day 2 covers the cleaning, joining, and time-series verbs Pandas adds, then
moves into plotting — first Matplotlib (the engine), then Seaborn and SciPy
(the statistical layer). Every course ships a Reveal.js slide deck and a
single `lecture.ipynb`; the notebook is a live-coding walkthrough followed
by three exercises with their solutions.

## Capstone — Grand Finale Lab

The final exercise of Course 4 — the **Grand Finale Lab** — is a synthesis:
load a messy stock-prices CSV, clean it with Pandas, compute a 7-day rolling
mean with NumPy, plot the result with Matplotlib, then refactor the whole
pipeline into a reusable function. If a student can finish it, they own the
foundations.

## Datasets

All notebooks load data via `shared.data_utils.load_dataset(name)`, which
caches CSVs to `~/.cache/ai-bootcamp/`. The Week 1 keys are:
`penguins`, `titanic`, `tips`, `iris`, `stock-prices`.

## Interactive slides

Every course's `slides/index.html` is a self-contained Reveal.js deck where
each notebook code cell appears as a **runnable example** (prefilled answer
+ description + *Run* button) and each notebook exercise appears as a
**checked exercise** (starter code + *Run & Check* + reference solution on
failure). Code runs in the browser via Pyodide — no install, no kernel.

## Running everything

From the repo root:

```bash
uv sync
uv run jupyter lab weeks/week-01-foundations/
```

To regenerate every notebook from source (the notebook content lives in
`scripts/build_week01_notebooks.py`):

```bash
uv run python scripts/build_week01_notebooks.py
```
