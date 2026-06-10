# Course 4 — Naive Bayes

**Duration:** 1.5 hours
**Why this matters:** Naive Bayes is the fastest generative classifier and often surprisingly competitive. Understanding the conditional independence assumption and its consequences builds intuition for when simplifying assumptions help — and when they hurt.

## Schedule

| Time        | Topic                       |
|-------------|------------------------------|
| 0:00 – 0:30 | The naive independence assumption and Bayes classifier |
| 0:30 – 1:00 | Gaussian, Multinomial, and Bernoulli NB variants |
| 1:00 – 1:30 | Connections to LDA, calibration, and when NB wins |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one, followed by exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Explain the naive independence assumption and why it often works anyway
2. Choose the right NB variant (Gaussian / Multinomial / Bernoulli) for a given feature type
3. Diagnose and fix overconfident NB posteriors with calibration

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-04-naive-bayes/
```
