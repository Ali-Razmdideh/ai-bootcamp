# Course 1 — NumPy: The ND-Array, Vectorization & Linear Algebra

**Duration:** 3 hours (merged Part I + Part II)
**Why this matters:** Every framework you will touch later — scikit-learn,
PyTorch, JAX — speaks NumPy. The single biggest leap a Python programmer
makes when becoming an ML engineer is *thinking in arrays instead of loops*.
That switch starts here.

## Schedule

| Time        | Topic                            |
|-------------|----------------------------------|
| 0:00 – 0:30 | The ND-Array                     |
| 0:30 – 1:00 | Shape manipulation               |
| 1:00 – 1:30 | Indexing & slicing               |
| 1:30 – 2:00 | Vectorization & ufuncs           |
| 2:00 – 2:30 | Broadcasting                     |
| 2:30 – 3:00 | Linear algebra & stacking        |

## Files

- `slides/index.html` — Reveal.js deck. Every notebook example becomes a runnable Pyodide block, and every exercise becomes a checked challenge.
- `lecture.ipynb` — live-coding notebook that mirrors the slides, followed by six exercises (each with its solution).

## Learning outcomes

1. Explain *why* an ndarray is faster than a Python list (contiguous memory, typed buffer, vectorized loops in C).
2. Reshape, transpose, and add/remove axes on multi-dimensional arrays.
3. Slice with basic, strided, fancy, and boolean indexing — and predict whether the result is a view or a copy.
4. Replace a Python numeric loop with a vectorized NumPy expression and measure the speedup with `%timeit`.
5. Predict the output shape of any broadcasting operation between two arrays.
6. Solve `Ax = b` with `np.linalg.solve`, compute matrix products with `@`, and combine arrays with `concatenate` / `stack` / `split`.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-01-numpy/
```
