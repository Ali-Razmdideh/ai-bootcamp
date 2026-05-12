# Week 1 — Python & Math Foundations

**Total time:** 4.5 hours · three 1.5-hour sessions

The goal of week 1 is to put every student on the same numerical-Python footing
before the bootcamp dives into classical ML and deep learning.

| Course | Topic | Folder |
|--------|-------|--------|
| 1 | The Numerical Engine (NumPy) | [course-01-numpy/](course-01-numpy/) |
| 2 | Data Manipulation (Pandas) | [course-02-pandas/](course-02-pandas/) |
| 3 | Visualization & Math Bridge (Matplotlib/Seaborn & SciPy) | [course-03-viz-scipy/](course-03-viz-scipy/) |

## The arc

1. **NumPy** — shift from "Python thinking" (loops) to "matrix thinking"
   (vectorization). Everything downstream assumes this fluency.
2. **Pandas** — treat data like a database; load, filter, clean, group.
3. **Viz + SciPy** — make the math visible and watch an optimizer minimize a
   function. This demystifies what "training a model" really means.

Each course ships a Reveal.js slide deck and a single `lecture.ipynb`. The
lecture is a live-coding walkthrough; three exercises with their solutions are
appended as the final section of the same notebook.

## Capstone

The final exercise in Course 3 — the **Grand Finale Lab** — is a 15-minute
synthesis: load a messy stock-prices CSV, clean it with Pandas, compute a 7-day
moving average with NumPy, and plot the result with Matplotlib. If a student
can finish it, they own the foundations.

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
