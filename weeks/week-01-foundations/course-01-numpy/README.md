# Course 1 — The Numerical Engine (NumPy)

**Duration:** 1.5 hours
**Why this matters:** Every framework you will touch later — scikit-learn, PyTorch,
JAX — speaks NumPy. The single biggest leap a Python programmer makes when
becoming an ML engineer is *thinking in arrays instead of loops*. That switch
happens here.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | The ND-Array                |
| 0:30 – 1:00 | Shape & Slicing             |
| 1:00 – 1:30 | Vectorization & Broadcasting|

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; append
  `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one.
- `exercises/` — three starter notebooks; matching solutions live in
  `exercises/solutions/`.

## Learning outcomes

By the end of the session a student can:

1. Explain *why* an ndarray is faster than a Python list (contiguous memory,
   typed buffer, vectorized loops in C).
2. Reshape, transpose, slice, and fancy-index multi-dimensional arrays with
   confidence.
3. Replace a `for` loop over numeric data with a vectorized expression and
   reason about broadcasting shapes.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-01-numpy/
```
