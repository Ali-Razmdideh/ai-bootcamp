# Week 1 — Python & Math Foundations

**Total time:** 9 hours · two days of three 1.5-hour sessions

Week 1 puts every student on the same numerical-Python footing before the
bootcamp dives into classical ML and deep learning. Every concrete example is
distilled from Aurélien Géron's tool tutorials (NumPy, Pandas, Matplotlib);
every exercise lives on the `shared.data_utils` datasets (`penguins`,
`titanic`, `tips`, `iris`, `stock-prices`) so the data-loading surface never
changes across the week.

## Day 1 — Arrays & frames

| Course | Topic | Folder |
|--------|-------|--------|
| 1 | NumPy I — The ND-Array | [course-01-numpy-i/](course-01-numpy-i/) |
| 2 | NumPy II — Vectorization & beyond | [course-02-numpy-ii/](course-02-numpy-ii/) |
| 3 | Pandas I — Series, DataFrame, indexing | [course-03-pandas-i/](course-03-pandas-i/) |

## Day 2 — Cleaning, plotting, and the math bridge

| Course | Topic | Folder |
|--------|-------|--------|
| 4 | Pandas II — Cleaning, groupby, joins, time | [course-04-pandas-ii/](course-04-pandas-ii/) |
| 5 | Matplotlib essentials | [course-05-matplotlib/](course-05-matplotlib/) |
| 6 | Viz Capstone + SciPy bridge | [course-06-viz-capstone-scipy/](course-06-viz-capstone-scipy/) |

## The arc

Day 1 shifts the student from "Python thinking" (loops) to "matrix thinking"
(vectorization), then introduces Pandas so the same arrays gain labels.
Day 2 covers the cleaning, joining, and time-series verbs Pandas adds, then
moves into plotting — first Matplotlib (the engine), then Seaborn and SciPy
(the statistical layer). Every course ships a Reveal.js slide deck and a
single `lecture.ipynb`; the notebook is a live-coding walkthrough followed
by three exercises with their solutions.

## Capstone — Grand Finale Lab

The final exercise of Course 6 — the **Grand Finale Lab** — is a synthesis:
load a messy stock-prices CSV, clean it with Pandas, compute a 7-day rolling
mean with NumPy, plot the result with Matplotlib, then refactor the whole
pipeline into a reusable function. If a student can finish it, they own the
foundations.

## Datasets

All notebooks load data via `shared.data_utils.load_dataset(name)`, which
caches CSVs to `~/.cache/ai-bootcamp/`. The Week 1 keys are:
`penguins`, `titanic`, `tips`, `iris`, `stock-prices`.

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
