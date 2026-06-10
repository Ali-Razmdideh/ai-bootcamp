# Course 6 — Comparing Classifiers: When to Use What

**Duration:** 1.5 hours
**Why this matters:** Having five classifiers is only useful if you know when to use each one. This course synthesises everything from courses 1–5 into a practical decision framework backed by empirical benchmarks.

## Schedule

| Time        | Topic                       |
|-------------|------------------------------|
| 0:00 – 0:30 | Methods at a glance — assumptions, complexity, interpretability |
| 0:30 – 1:00 | Four canonical scenarios from ISLR §4.5 |
| 1:00 – 1:30 | Benchmark on real datasets + decision guide |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one, followed by exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. State the key assumptions and failure modes of each Week 4 classifier
2. Choose a classifier given data size, feature type, and boundary shape
3. Run a fair multi-classifier benchmark using cross-validation

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-06-classification-comparison/
```
