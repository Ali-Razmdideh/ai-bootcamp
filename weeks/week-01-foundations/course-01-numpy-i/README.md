# Course 1 — NumPy I: The ND-Array

**Duration:** 1.5 hours
**Why this matters:** Every framework you will touch later — scikit-learn,
PyTorch, JAX — speaks NumPy. The single biggest leap a Python programmer makes
when becoming an ML engineer is *thinking in arrays instead of loops*. That
switch starts here, with the ndarray itself: how to create one, inspect its
shape, and pick any subset of it.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | The ND-Array                |
| 0:30 – 1:00 | Shape manipulation          |
| 1:00 – 1:30 | Indexing & slicing          |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; append
  `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides, followed by
  three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Explain *why* an ndarray is faster than a Python list (contiguous memory,
   typed buffer, vectorized loops in C).
2. Reshape, transpose, and add/remove axes on multi-dimensional arrays.
3. Slice with basic, strided, fancy (integer-array), and boolean indexing —
   and predict whether the result is a view or a copy.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-01-numpy-i/
```
