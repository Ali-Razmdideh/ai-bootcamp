# Course 2 — NumPy II: Vectorization & Beyond

**Duration:** 1.5 hours
**Why this matters:** Course 1 taught you how to *describe* an ndarray. Course
2 teaches you how to *operate* on it: replace `for` loops with vectorized
expressions, reason about broadcasting shapes, and solve real linear-algebra
problems. This is the fluency every later ML library assumes you have.

## Schedule

| Time        | Topic                            |
|-------------|----------------------------------|
| 0:00 – 0:30 | Vectorization & ufuncs           |
| 0:30 – 1:00 | Broadcasting                     |
| 1:00 – 1:30 | Linear algebra & stacking        |

## Files

- `slides/index.html` — Reveal.js deck. Every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter + *Run & Check* + reference solution on failure).
- `lecture.ipynb` — live-coding notebook + three exercises with solutions.

## Learning outcomes

By the end of the session a student can:

1. Replace a Python numeric loop with a vectorized NumPy expression and
   measure the speedup with `%timeit`.
2. Predict the output shape of any broadcasting operation between two arrays.
3. Solve `Ax = b` with `np.linalg.solve`, compute matrix products with `@`,
   and combine arrays with `concatenate` / `stack` / `split`.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-02-numpy-ii/
```
