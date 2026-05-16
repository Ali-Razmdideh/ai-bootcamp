# Quera AI Bootcamp

Course materials for the [Quera AI Bootcamp](https://quera.org/bootcamp/ai).

## Quickstart

```bash
# 1. Install uv (https://docs.astral.sh/uv/) if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Sync the environment
uv sync

# 3. Launch JupyterLab
uv run jupyter lab
```

Open any course folder and start with `lecture.ipynb`.

## Layout

```
weeks/
  week-01-foundations/         # NumPy, Pandas, Matplotlib/SciPy
    course-01-numpy/
    course-02-pandas/
    course-03-viz-scipy/
  week-03-machine-learning/    # Regression, CV, feature selection (ISLP Ch 3, 5, 6)
    course-01-linear-regression-i/
    course-02-linear-regression-ii/
    course-03-feature-engineering/
    course-04-cross-validation/
    course-05-feature-selection-subset/
    course-06-feature-selection-shrinkage/
  week-04-classification/      # KNN, logistic, trees, ensembles, SVM (ISLP Ch 4, 8, 9)
    course-01-classification-knn/
    course-02-logistic-regression-i/
    course-03-logistic-regression-ii/
    course-04-decision-trees/
    course-05-ensembles/
    course-06-svm/
shared/
  data_utils.py            # cached dataset fetcher used by all notebooks
  slides-template/         # Reveal.js base (theme) + Pyodide-powered
                           # interactive runtime (interactive.js / .css)
```

Each course ships:
- `lecture.ipynb` — live-coded walkthrough mirroring the slides, with three
  exercises and their solutions appended as a final section
- `slides/index.html` — Reveal.js deck (open in a browser, no build step).
  Every code example and every exercise from the notebook is **runnable in
  the browser** via Pyodide — click *Run* to execute, exercises check the
  learner's answer and reveal the reference solution on failure.

## Datasets

No datasets are committed. The notebooks call `shared.data_utils.load_dataset(name)`
which fetches CSVs from stable URLs the first time and caches them under
`~/.cache/ai-bootcamp/`.

## Viewing slides

Slides are plain HTML — just open `weeks/week-01-foundations/course-0X-*/slides/index.html`
in any browser. To present with speaker notes, append `?showNotes`.

### Interactive code in the browser

Each deck is wired to [Pyodide](https://pyodide.org/) so students can run code
without leaving the slides. Two block types live inline next to the related
concept:

- **Examples** — prefilled with the full answer, click *Run* to execute and
  see the printed output. A short description explains what the example
  demonstrates.
- **Exercises** — a description + a starter textarea; *Run & Check* runs the
  learner's code and validates it. A wrong answer reveals the failure reason,
  a short *why* explanation, and the reference solution. *Show solution*
  reveals the answer on demand.

Pyodide loads the first time you click *Run*; subsequent runs are instant.
Datasets used by the notebooks (`shared.data_utils`) are inlined as small
seeded synthetic DataFrames in the slide examples so they work without
filesystem access.
