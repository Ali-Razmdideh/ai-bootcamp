# Course 2 — Data Manipulation (Pandas)

**Duration:** 1.5 hours
**Why this matters:** Real datasets are dirty. Before any model can learn,
someone has to load, filter, fill, and reshape the data. Pandas is the de-facto
language for that work in Python.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | DataFrames & Loading        |
| 0:30 – 1:00 | Selection & Filtering       |
| 1:00 – 1:30 | Cleaning & Grouping         |

## Files

- `slides/index.html` — Reveal.js deck.
- `lecture.ipynb` — live walkthrough on the Palmer Penguins dataset, followed
  by three exercises (each with its solution).

## Learning outcomes

1. Load CSV data into a DataFrame; reason about index vs. columns.
2. Select rows/columns using `.loc`, `.iloc`, and boolean masks fluently.
3. Detect and handle missing values; compute per-group statistics with
   `groupby` + `agg`.
