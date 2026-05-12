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
  week-01-foundations/
    course-01-numpy/       # NumPy: ND-arrays, slicing, vectorization
    course-02-pandas/      # Pandas: DataFrames, selection, cleaning, groupby
    course-03-viz-scipy/   # Matplotlib/Seaborn + SciPy stats & optimize
shared/
  data_utils.py            # cached dataset fetcher used by all notebooks
  slides-template/         # Reveal.js base (theme + template)
```

Each course ships:
- `lecture.ipynb` — live-coded walkthrough mirroring the slides, with three
  exercises and their solutions appended as a final section
- `slides/index.html` — Reveal.js deck (open in a browser, no build step)

## Datasets

No datasets are committed. The notebooks call `shared.data_utils.load_dataset(name)`
which fetches CSVs from stable URLs the first time and caches them under
`~/.cache/ai-bootcamp/`.

## Viewing slides

Slides are plain HTML — just open `weeks/week-01-foundations/course-0X-*/slides/index.html`
in any browser. To present with speaker notes, append `?showNotes`.
