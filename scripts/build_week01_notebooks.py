"""Generate every Jupyter notebook for Week 1 (6-course / 2-day shape).

The notebooks are emitted as plain nbformat-4 JSON. Running this script is
idempotent: it always rewrites the files from the source-of-truth content
defined below. Keeping notebook content in this file (rather than 18 hand-edited
.ipynb blobs) makes course updates a one-edit operation.

Week 1 has six 1.5-hour courses split across two teaching days:
  Day 1: NumPy I, NumPy II, Pandas I
  Day 2: Pandas II, Matplotlib, Viz Capstone + SciPy

Every concrete example is distilled from Aurelien Geron's tutorial notebooks
(tools_numpy.ipynb, tools_pandas.ipynb, tools_matplotlib.ipynb).

Usage:
    python3 scripts/build_week01_notebooks.py
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEK1 = ROOT / "weeks" / "week-01-foundations"


def md(*lines: str) -> dict:
    text = "\n".join(lines)
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(*lines: str) -> dict:
    text = textwrap.dedent("\n".join(lines)).strip("\n") + "\n"
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


# Every notebook that touches `shared.data_utils` needs sys.path bootstrapping
# so the import works no matter where the kernel is launched from.
REPO_ROOT_BOOTSTRAP = (
    "import sys, pathlib",
    "p = pathlib.Path.cwd()",
    "while not (p / 'pyproject.toml').exists() and p != p.parent:",
    "    p = p.parent",
    "if str(p) not in sys.path:",
    "    sys.path.insert(0, str(p))",
)


def write_nb(path: Path, cells: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")


# ============================================================================
# COURSE 1 - NUMPY I: THE ND-ARRAY
# ============================================================================

def course1_lecture() -> list[dict]:
    return [
        md("# Course 1 - NumPy I: The ND-Array",
           "",
           "Live-coding notebook that mirrors the slide deck.",
           "Concrete examples lifted from Aurelien Geron's NumPy tutorial.",
           "",
           "**Sections**",
           "1. The ND-Array (0:00-0:30)",
           "2. Shape manipulation (0:30-1:00)",
           "3. Indexing & slicing (1:00-1:30)"),
        code("import numpy as np",
             "np.__version__"),
        md("## 1. The ND-Array"),
        md("### List vs. ndarray - same data, different machine"),
        code("py_list = [1, 2, 3, 4]",
             "arr = np.array([1, 2, 3, 4])",
             "print(py_list, type(py_list).__name__)",
             "print(arr, type(arr).__name__, arr.dtype)"),
        md("### Measure the difference"),
        code("%timeit sum(range(1_000_000))",
             "%timeit np.arange(1_000_000).sum()"),
        md("### Creating arrays - the recipes you'll use weekly"),
        code("print(np.zeros(5))",
             "print(np.zeros((3, 4)))",
             "print(np.ones((3, 4)))",
             "print(np.full((3, 4), np.pi))"),
        code("print(np.arange(1, 5))",
             "print(np.arange(1, 5, 0.5))",
             "print(np.linspace(0, 5/3, 6))",
             "print(np.eye(3))"),
        md("### Randomness - use the modern Generator API"),
        code("rng = np.random.default_rng(seed=42)",
             "print(rng.random((3, 4)))",
             "print(rng.standard_normal((3, 4)))"),
        md("### dtypes - promotion in action"),
        code("c = np.arange(1, 5)",
             "print(c.dtype, c)        # int64",
             "",
             "k1 = np.arange(0, 5, dtype=np.uint8)",
             "k2 = k1 + np.array([5, 6, 7, 8, 9], dtype=np.int8)",
             "print(k2.dtype, k2)      # int16 - promoted",
             "",
             "k3 = k1 + 1.5",
             "print(k3.dtype, k3)      # float64"),
        md("### astype - convert dtype, get a new array"),
        code("g = np.arange(6, dtype=np.float64)",
             "print(g.dtype, g)",
             "h = g.astype(np.int32)",
             "print(h.dtype, h)"),
        md("### Inspect any array in six attributes"),
        code("a = np.zeros((3, 4))",
             "print('shape   :', a.shape)",
             "print('ndim    :', a.ndim)",
             "print('size    :', a.size)",
             "print('itemsize:', a.itemsize)",
             "print('nbytes  :', a.nbytes)",
             "print('dtype   :', a.dtype)"),
        md("## 2. Shape manipulation"),
        md("### Reshape, ravel, flatten"),
        code("g = np.arange(24)",
             "g2 = g.reshape(6, 4)        # new view, same buffer",
             "print(g2)",
             "print(g2.ravel())            # back to 1-D (view if possible)",
             "print(g2.flatten())          # always a copy"),
        md("### Transpose"),
        code("m1 = np.arange(10).reshape(2, 5)",
             "print(m1)",
             "print(m1.T)                   # shorthand for .transpose()",
             "",
             "t = np.arange(24).reshape(4, 2, 3)",
             "print(t.transpose((1, 2, 0)).shape)   # (2, 3, 4)"),
        md("### Add and remove dimensions"),
        code("v = np.array([1, 2, 3])",
             "print(v.shape)",
             "print(v[np.newaxis, :].shape)        # (1, 3) - row vector",
             "print(v[:, np.newaxis].shape)        # (3, 1) - column vector",
             "print(np.expand_dims(v, axis=0).shape)",
             "print(np.squeeze(np.array([[[1, 2, 3]]])).shape)"),
        md("### Memory contiguity - C vs F order (briefly)"),
        code("a = np.arange(12).reshape(3, 4)            # default: C-order (row-major)",
             "print('C-contig?', a.flags['C_CONTIGUOUS'])",
             "print('F-contig?', a.T.flags['F_CONTIGUOUS'])"),
        md("## 3. Indexing & slicing"),
        md("### Basic slicing - like Python, but multi-dim"),
        code("b = np.arange(48).reshape(4, 12)",
             "print(b)",
             "print('b[1, 2]   =', b[1, 2])",
             "print('b[1, :]   =', b[1, :])",
             "print('b[:, 1]   =', b[:, 1])",
             "print('b[1:3,2:5]=\\n', b[1:3, 2:5])",
             "print('b[::-1]   =\\n', b[::-1])"),
        md("### Strided slicing"),
        code("a = np.arange(20).reshape(4, 5)",
             "print(a)",
             "print(a[1:3, ::2])     # rows 1-2, every other column"),
        md("### Fancy (integer-array) indexing - pick whatever rows/cols you want"),
        code("print(b[(0, 2), 2:5])                       # rows 0 and 2, cols 2-4",
             "print(b[:, (-1, 2, -1)])                     # cols last, 2, last (repeats!)",
             "print(b[(-1, 2, -1, 2), (5, 9, 1, 9)])       # paired indices - 4 cells"),
        md("### Boolean masks"),
        code("m = np.array([20, -5, 30, 40])",
             "print(m[m < 25])             # [20 -5]",
             "",
             "rows_on = np.array([True, False, True, False])",
             "print(b[rows_on, :])         # keep rows 0 and 2",
             "",
             "print(b[b % 3 == 1])         # every elem where x % 3 == 1"),
        md("### np.where - pick from two arrays based on a mask"),
        code("x = np.arange(10)",
             "print(np.where(x % 2 == 0, x, -1))   # keep evens, replace odds with -1"),
        md("### Gotcha: slices are *views*, not copies"),
        code("a = np.arange(12).reshape(3, 4)",
             "view = a[:2, :2]",
             "view[0, 0] = -999",
             "print(a)        # the source mutated too!"),
        md("### Recap",
           "* ndarray is a contiguous typed buffer - that is the entire speed story.",
           "* Reshape and transpose change *strides*, not data.",
           "* Slice with `:`, `,` and `::`; pick anything with fancy or boolean indexing."),
    ]


def course1_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 - Multiplication Table",
           "",
           "Goal: practise array creation + broadcasting in one tiny puzzle."),
        code("import numpy as np",
             "rng = np.random.default_rng(0)"),
        md("**Task 1.** Build a `5 x 5` multiplication table where entry `(i, j)` equals `(i+1) * (j+1)`. Use `np.arange` and broadcasting - no loops."),
        code("# your code here"),
        md("**Task 2.** Print its shape, dtype, and `nbytes`."),
        code("# your code here"),
        md("**Task 3.** Extract the diagonal as a 1-D array using a single fancy-index expression."),
        code("# your code here"),
    ]


def course1_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 - Solutions"),
        code("import numpy as np"),
        md("**Task 1.**"),
        code("row = np.arange(1, 6)",
             "table = row[:, None] * row[None, :]",
             "print(table)"),
        md("**Task 2.**"),
        code("print('shape :', table.shape)",
             "print('dtype :', table.dtype)",
             "print('nbytes:', table.nbytes)"),
        md("**Task 3.**"),
        code("ix = np.arange(5)",
             "print(table[ix, ix])"),
    ]


def course1_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 - Masking divisibility"),
        code("import numpy as np"),
        md("**Task 1.** Build a 1-D array `v` of the integers 1..30 inclusive."),
        code("# your code here"),
        md("**Task 2.** Print every value in `v` that is divisible by 3 using a boolean mask."),
        code("# your code here"),
        md("**Task 3.** Replace every value divisible by 3 in `v` with `0` (use `np.where` and assign to a new array `out`)."),
        code("# your code here"),
        md("**Task 4.** How many values in `v` are divisible by both 3 *and* 5? Compute it with a vectorized expression."),
        code("# your code here"),
    ]


def course1_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 - Solutions"),
        code("import numpy as np"),
        md("**Task 1.**"),
        code("v = np.arange(1, 31)",
             "print(v)"),
        md("**Task 2.**"),
        code("print(v[v % 3 == 0])"),
        md("**Task 3.**"),
        code("out = np.where(v % 3 == 0, 0, v)",
             "print(out)"),
        md("**Task 4.**"),
        code("count = int(((v % 3 == 0) & (v % 5 == 0)).sum())",
             "print(count)"),
    ]


def course1_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 - Slicing & Reshape",
           "",
           "Treat a 2-D array as an image; every CV model sees this shape."),
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "M = rng.random((8, 4))",
             "print(M.round(2))"),
        md("**Task 1.** Extract every other row of `M` (rows 0, 2, 4, 6) using a slice."),
        code("# your code here"),
        md("**Task 2.** Reverse the column order of `M` (mirror left-right)."),
        code("# your code here"),
        md("**Task 3.** Reshape `M` into a 4x8 array (no data copy required) and print its shape."),
        code("# your code here"),
        md("**Task 4.** Convert `M` (8x4) into a 3-D `(8, 4, 1)` array using `np.newaxis`. Print the shape."),
        code("# your code here"),
    ]


def course1_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 - Solutions"),
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "M = rng.random((8, 4))"),
        md("**Task 1.**"),
        code("print(M[::2].shape)",
             "print(M[::2].round(2))"),
        md("**Task 2.**"),
        code("print(M[:, ::-1].round(2))"),
        md("**Task 3.**"),
        code("R = M.reshape(4, 8)",
             "print(R.shape)"),
        md("**Task 4.**"),
        code("E = M[:, :, np.newaxis]",
             "print(E.shape)"),
    ]


# ============================================================================
# COURSE 2 - NUMPY II: VECTORIZATION & BEYOND
# ============================================================================

def course2_lecture() -> list[dict]:
    return [
        md("# Course 2 - NumPy II: Vectorization & Beyond",
           "",
           "Live-coding notebook that mirrors the slide deck.",
           "Concrete examples lifted from Aurelien Geron's NumPy tutorial.",
           "",
           "**Sections**",
           "1. Vectorization & ufuncs (0:00-0:30)",
           "2. Broadcasting (0:30-1:00)",
           "3. Linear algebra & stacking (1:00-1:30)"),
        code("import numpy as np",
             "rng = np.random.default_rng(0)"),
        md("## 1. Vectorization & ufuncs"),
        md("### The loop you stop writing"),
        code("x = rng.normal(size=1_000_000)",
             "",
             "def slow(x):",
             "    out = np.empty_like(x)",
             "    for i in range(len(x)):",
             "        out[i] = x[i]**2 + 3*x[i]",
             "    return out",
             "",
             "def fast(x):",
             "    return x**2 + 3*x",
             "",
             "%timeit slow(x)",
             "%timeit fast(x)"),
        md("### Element-wise arithmetic on paired arrays"),
        code("a = np.array([14, 23, 32, 41])",
             "b = np.array([5,  4,  3,  2])",
             "print(a + b)",
             "print(a - b)",
             "print(a * b)",
             "print(a / b)",
             "print(np.maximum(a, b))",
             "print(np.greater(a, b))"),
        md("### Universal functions (ufuncs) - math everywhere"),
        code("print(np.sqrt(a))",
             "print(np.exp(a))",
             "print(np.sin(a))",
             "print(np.log(a))",
             "print(np.maximum(a, 0))     # ReLU in one line",
             "print(np.clip(a, 0, 30))"),
        md("### Reductions - and the axis mnemonic"),
        code("a = np.array([[-2.5, 3.1, 7], [10, 11, 12]])",
             "print('mean all :', a.mean())",
             "print('std all  :', a.std())",
             "print('min, max :', a.min(), a.max())",
             "print('argmax   :', a.argmax())"),
        code("c = np.arange(24).reshape(2, 3, 4)",
             "print('sum axis 0 :', c.sum(axis=0).shape)   # collapse axis 0 -> (3, 4)",
             "print('sum axis 1 :', c.sum(axis=1).shape)   # collapse axis 1 -> (2, 4)",
             "print('sum (0, 2) :', c.sum(axis=(0, 2)).shape)"),
        md("## 2. Broadcasting"),
        md("### Scalar broadcast"),
        code("a = np.arange(6).reshape(2, 3)",
             "print(a)",
             "print(a + 100)            # scalar broadcasts to every cell"),
        md("### Row vector across rows: (2,3) + (3,)"),
        code("print(a + np.array([100, 200, 300]))"),
        md("### Column vector across columns: (2,3) + (2,1)"),
        code("print(a + np.array([[100], [200]]))"),
        md("### Two compatible shapes: (3,1) + (1,4) -> (3,4)"),
        code("col = np.arange(3)[:, None]      # (3, 1)",
             "row = np.arange(4)[None, :]      # (1, 4)",
             "print(col + row)                 # (3, 4) outer-sum"),
        md("### Standardize a data matrix in one line (broadcast + reduction)"),
        code("X = rng.normal(loc=5, scale=2, size=(200, 5))",
             "Z = (X - X.mean(axis=0)) / X.std(axis=0)",
             "print('column means ~0:', Z.mean(axis=0).round(4))",
             "print('column stds  ~1:', Z.std(axis=0).round(4))"),
        md("## 3. Linear algebra & stacking"),
        md("### Matrix multiplication - `@` is the operator"),
        code("n1 = np.arange(10).reshape(2, 5)",
             "n2 = np.arange(15).reshape(5, 3)",
             "print(n1 @ n2)                # equivalent to n1.dot(n2)"),
        md("### Norms, inverse, determinant"),
        code("m = np.array([[1,  2,  3],",
             "              [5,  7, 11],",
             "              [21, 29, 31]], dtype=float)",
             "print('||m||_F =', np.linalg.norm(m))",
             "print('det m  =', np.linalg.det(m))",
             "print('inv m  =\\n', np.linalg.inv(m).round(3))"),
        md("### Solve a linear system - `Ax = b`"),
        code("A = np.array([[2, 6], [5, 3]], dtype=float)",
             "b = np.array([6, -9], dtype=float)",
             "x = np.linalg.solve(A, b)",
             "print('x      =', x)",
             "print('A @ x  =', A @ x, '   should equal', b)"),
        md("### Eigendecomposition - one-liner"),
        code("S = np.array([[4, 1], [1, 3]], dtype=float)",
             "w, V = np.linalg.eig(S)",
             "print('eigvals:', w)",
             "print('eigvecs:\\n', V.round(3))"),
        md("### Stack & split"),
        code("a = np.array([[1, 2], [3, 4]])",
             "b = np.array([[5, 6], [7, 8]])",
             "print(np.concatenate([a, b], axis=0))   # vstack",
             "print(np.concatenate([a, b], axis=1))   # hstack",
             "print(np.stack([a, b]).shape)           # new axis -> (2, 2, 2)"),
        code("big = np.arange(12).reshape(3, 4)",
             "left, right = np.split(big, 2, axis=1)",
             "print(left)",
             "print(right)"),
        md("### Recap",
           "* Replace numeric `for` loops with broadcasting + reductions.",
           "* `@` for matmul, `np.linalg.solve` for `Ax = b`.",
           "* Combine arrays with `concatenate` / `stack` / `split`."),
    ]


def course2_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 - Vectorize a pairwise distance loop"),
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "pts = rng.normal(size=(50, 2))"),
        md("**Task 1.** Here is a naive Python loop that computes pairwise distances. Run it once to see the result."),
        code("def naive(pts):",
             "    n = len(pts)",
             "    out = np.empty((n, n))",
             "    for i in range(n):",
             "        for j in range(n):",
             "            out[i, j] = np.sqrt(((pts[i] - pts[j])**2).sum())",
             "    return out",
             "",
             "D_naive = naive(pts)",
             "print(D_naive.shape)"),
        md("**Task 2.** Write a vectorized version `fast(pts)` that produces the same matrix using broadcasting - no Python loops."),
        code("# your code here"),
        md("**Task 3.** Verify `np.allclose(naive(pts), fast(pts))`."),
        code("# your code here"),
        md("**Task 4.** Time both versions with `%timeit`."),
        code("# your code here"),
    ]


def course2_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 - Solutions"),
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "pts = rng.normal(size=(50, 2))",
             "",
             "def naive(pts):",
             "    n = len(pts)",
             "    out = np.empty((n, n))",
             "    for i in range(n):",
             "        for j in range(n):",
             "            out[i, j] = np.sqrt(((pts[i] - pts[j])**2).sum())",
             "    return out"),
        md("**Task 2.**"),
        code("def fast(pts):",
             "    diff = pts[:, None, :] - pts[None, :, :]",
             "    return np.sqrt((diff**2).sum(axis=-1))",
             "",
             "print(fast(pts).shape)"),
        md("**Task 3.**"),
        code("assert np.allclose(naive(pts), fast(pts))",
             "print('match!')"),
        md("**Task 4.**"),
        code("%timeit naive(pts)",
             "%timeit fast(pts)"),
    ]


def course2_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 - Broadcast-normalize"),
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "X = rng.normal(loc=5, scale=2, size=(100, 3))"),
        md("**Task 1.** Compute the per-column mean and per-column std of `X` (each a length-3 array)."),
        code("# your code here"),
        md("**Task 2.** Use broadcasting to produce `Z` such that each column has mean 0 and std 1."),
        code("# your code here"),
        md("**Task 3.** Verify the column means and stds of `Z` numerically."),
        code("# your code here"),
        md("**Task 4.** Repeat normalisation but row-wise (each row has mean 0, std 1). What changes in the broadcasting?"),
        code("# your code here"),
    ]


def course2_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 - Solutions"),
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "X = rng.normal(loc=5, scale=2, size=(100, 3))"),
        md("**Task 1.**"),
        code("mu = X.mean(axis=0)",
             "sd = X.std(axis=0)",
             "print('mu:', mu)",
             "print('sd:', sd)"),
        md("**Task 2.**"),
        code("Z = (X - mu) / sd",
             "print(Z.shape)"),
        md("**Task 3.**"),
        code("print('Z col means ~ 0:', Z.mean(axis=0).round(4))",
             "print('Z col stds  ~ 1:', Z.std(axis=0).round(4))"),
        md("**Task 4.**"),
        code("mu_r = X.mean(axis=1, keepdims=True)",
             "sd_r = X.std(axis=1, keepdims=True)",
             "Zr = (X - mu_r) / sd_r",
             "print('row means ~0:', Zr.mean(axis=1)[:5].round(4))",
             "print('row stds  ~1:', Zr.std(axis=1)[:5].round(4))"),
    ]


def course2_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 - Solve a 3x3 system"),
        code("import numpy as np"),
        md("Consider the system",
           "",
           "    2x + y - z = 8",
           "   -3x - y + 2z = -11",
           "   -2x + y + 2z = -3",
           "",
           "**Task 1.** Build matrix `A` and vector `b`."),
        code("# your code here"),
        md("**Task 2.** Solve with `np.linalg.solve`."),
        code("# your code here"),
        md("**Task 3.** Verify the solution by computing `A @ x` and comparing with `b` via `np.allclose`."),
        code("# your code here"),
        md("**Task 4 (stretch).** Solve again using `np.linalg.inv(A) @ b` and compare. Which is preferred and why?"),
        code("# your code here"),
    ]


def course2_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 - Solutions"),
        code("import numpy as np"),
        md("**Task 1.**"),
        code("A = np.array([[ 2,  1, -1],",
             "              [-3, -1,  2],",
             "              [-2,  1,  2]], dtype=float)",
             "b = np.array([8, -11, -3], dtype=float)"),
        md("**Task 2.**"),
        code("x = np.linalg.solve(A, b)",
             "print('x =', x)"),
        md("**Task 3.**"),
        code("assert np.allclose(A @ x, b)",
             "print('Ax =', A @ x, '   b =', b)"),
        md("**Task 4.**"),
        code("x_inv = np.linalg.inv(A) @ b",
             "print('via inv:', x_inv)",
             "print('match  :', np.allclose(x, x_inv))",
             "# solve(A, b) is preferred: faster and more stable than forming inv(A)."),
    ]


# ============================================================================
# COURSE 3 - PANDAS I: SERIES, DATAFRAME, INDEXING
# ============================================================================

def course3_lecture() -> list[dict]:
    return [
        md("# Course 3 - Pandas I: Series, DataFrame, Indexing",
           "",
           "Live-coding notebook that mirrors the slide deck.",
           "Concrete examples lifted from Aurelien Geron's Pandas tutorial.",
           "",
           "**Sections**",
           "1. Series (0:00-0:30)",
           "2. DataFrames (0:30-1:00)",
           "3. Indexing & filtering (1:00-1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "import pandas as pd",
             "import numpy as np",
             "from shared.data_utils import load_dataset",
             "pd.__version__"),
        md("## 1. Series"),
        md("### Your first Series"),
        code("s = pd.Series([2, -1, 3, 5])",
             "s"),
        md("### NumPy plus labels"),
        code("np.exp(s)"),
        code("s + [1000, 2000, 3000, 4000]"),
        code("s + 1000      # scalar broadcasts"),
        code("s < 0         # element-wise comparison"),
        md("### Index labels - name your rows"),
        code("s2 = pd.Series([68, 83, 112, 68], index=['alice', 'bob', 'charles', 'darwin'])",
             "s2"),
        code("print(s2['bob'])",
             "print(s2.loc['bob'])",
             "print(s2.iloc[1])"),
        md("### Gotcha - default-int labels are *labels*, not positions"),
        code("surprise = pd.Series([1000, 1001, 1002, 1003])",
             "slice_ = surprise[2:]",
             "print(slice_)",
             "",
             "try:",
             "    slice_[0]",
             "except KeyError as e:",
             "    print('KeyError:', e)",
             "",
             "print('via iloc:', slice_.iloc[0])"),
        md("### Build a Series from a dict"),
        code("weights = {'alice': 68, 'bob': 83, 'colin': 86, 'darwin': 68}",
             "s3 = pd.Series(weights)",
             "s3"),
        md("### Automatic alignment when combining"),
        code("print(s2.index)",
             "print(s3.index)",
             "s2 + s3      # labels not in both -> NaN"),
        md("## 2. DataFrames"),
        md("### Build a DataFrame from a dict of Series"),
        code("people_dict = {",
             "    'weight':    pd.Series([68, 83, 112], index=['alice', 'bob', 'charles']),",
             "    'birthyear': pd.Series([1984, 1985, 1992],",
             "                           index=['bob', 'alice', 'charles'], name='year'),",
             "    'children':  pd.Series([0, 3], index=['charles', 'bob']),",
             "    'hobby':     pd.Series(['Biking', 'Dancing'], index=['alice', 'bob']),",
             "}",
             "people = pd.DataFrame(people_dict)",
             "people"),
        md("### Build a DataFrame from a list-of-lists + columns/index"),
        code("values = [[1985, np.nan, 'Biking',  68],",
             "          [1984, 3,      'Dancing', 83],",
             "          [1992, 0,       np.nan,  112]]",
             "d3 = pd.DataFrame(values,",
             "                  columns=['birthyear', 'children', 'hobby', 'weight'],",
             "                  index=['alice', 'bob', 'charles'])",
             "d3"),
        md("### From a real CSV via `shared.data_utils`"),
        code("penguins = load_dataset('penguins')",
             "penguins.head()"),
        md("### The first three things on any fresh dataset"),
        code("print(penguins.shape)",
             "print(penguins.dtypes)"),
        code("penguins.info()"),
        code("penguins.describe(include='all')"),
        md("## 3. Indexing & filtering"),
        md("### Column access"),
        code("penguins['species'].head()"),
        code("penguins[['species', 'body_mass_g']].head()"),
        md("### Row access by label vs. position"),
        code("penguins.loc[0]               # by label (here labels are 0..N)",
             "# .iloc always means positional",
             "print(penguins.iloc[2])"),
        code("penguins.iloc[1:4]            # positional slice - endpoint exclusive"),
        md("### Boolean indexing"),
        code("penguins[penguins['body_mass_g'] > 6000].head()"),
        code("mask = (penguins['species'] == 'Adelie') & (penguins['sex'] == 'Female')",
             "penguins[mask].head()"),
        md("### Compose with `&`, `|`, `~`"),
        code("penguins[~penguins['sex'].isna()].head()"),
        md("### set_index / reset_index / sort_index / sort_values"),
        code("tips = load_dataset('tips')",
             "tips_idx = tips.set_index(['day', 'time'])",
             "tips_idx.head()"),
        code("tips_idx.sort_index().head()"),
        code("tips.sort_values('tip', ascending=False).head()"),
        md("### Recap",
           "* Series = labeled NumPy array. DataFrame = dict of aligned Series.",
           "* `.loc` for labels, `.iloc` for positions, masks for filtering.",
           "* Always inspect shape / dtypes / describe on first contact."),
    ]


def course3_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 - Load + filter `tips`"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd"),
        md("**Task 1.** Load the `tips` dataset; print shape, dtypes, head."),
        code("# your code here"),
        md("**Task 2.** Select rows where `tip > 5`. How many are there?"),
        code("# your code here"),
        md("**Task 3.** Of those rows, print only the columns `total_bill`, `tip`, `day`."),
        code("# your code here"),
        md("**Task 4.** Sort the result of Task 3 by `total_bill` ascending."),
        code("# your code here"),
    ]


def course3_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 - Solutions"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "df = load_dataset('tips')"),
        md("**Task 1.**"),
        code("print(df.shape)",
             "print(df.dtypes)",
             "df.head()"),
        md("**Task 2.**"),
        code("big = df[df['tip'] > 5]",
             "print(len(big))"),
        md("**Task 3.**"),
        code("big[['total_bill', 'tip', 'day']].head()"),
        md("**Task 4.**"),
        code("big[['total_bill', 'tip', 'day']].sort_values('total_bill').head()"),
    ]


def course3_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 - Series alignment"),
        code("import pandas as pd",
             "import numpy as np"),
        md("**Task 1.** Build three Series with *misaligned* indices and combine them into a DataFrame `df`.",
           "",
           "Use:",
           "- `a = Series([1, 2, 3], index=['x', 'y', 'z'])`",
           "- `b = Series([10, 20, 30], index=['y', 'z', 'w'])`",
           "- `c = Series([100, 200], index=['x', 'w'])`"),
        code("# your code here"),
        md("**Task 2.** Print `df`. Where do the NaNs appear, and why?"),
        code("# your code here"),
        md("**Task 3.** Compute `a + b` directly (Series + Series). Inspect the index of the result."),
        code("# your code here"),
        md("**Task 4.** Drop rows that contain any NaN and report the remaining shape."),
        code("# your code here"),
    ]


def course3_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 - Solutions"),
        code("import pandas as pd",
             "import numpy as np",
             "a = pd.Series([1, 2, 3], index=['x', 'y', 'z'])",
             "b = pd.Series([10, 20, 30], index=['y', 'z', 'w'])",
             "c = pd.Series([100, 200], index=['x', 'w'])"),
        md("**Task 1.**"),
        code("df = pd.DataFrame({'a': a, 'b': b, 'c': c})",
             "df"),
        md("**Task 2.**"),
        code("# NaNs appear at any (row, column) where that label is absent from the column's Series."),
        md("**Task 3.**"),
        code("s = a + b",
             "print(s)",
             "print('index:', s.index.tolist())"),
        md("**Task 4.**"),
        code("clean = df.dropna()",
             "print(clean.shape)"),
    ]


def course3_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 - Class grades"),
        code("import pandas as pd",
             "import numpy as np"),
        md("**Task 1.** Build a 4x3 grades DataFrame: rows = students `alice, bob, charles, darwin`, columns = `math, science, history`. Use any plausible integer grades 0..20."),
        code("# your code here"),
        md("**Task 2.** Add a column `average` containing each student's row mean."),
        code("# your code here"),
        md("**Task 3.** Sort by `average` descending and print the result."),
        code("# your code here"),
        md("**Task 4.** Who has the highest grade in `science`? Use `idxmax`."),
        code("# your code here"),
    ]


def course3_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 - Solutions"),
        code("import pandas as pd",
             "import numpy as np",
             "grades = pd.DataFrame(",
             "    [[15, 17, 12], [10, 13, 16], [19, 18, 14], [12, 14, 11]],",
             "    columns=['math', 'science', 'history'],",
             "    index=['alice', 'bob', 'charles', 'darwin'])"),
        md("**Task 1.**"),
        code("grades"),
        md("**Task 2.**"),
        code("grades['average'] = grades.mean(axis=1)",
             "grades"),
        md("**Task 3.**"),
        code("grades.sort_values('average', ascending=False)"),
        md("**Task 4.**"),
        code("print('top science:', grades['science'].idxmax())"),
    ]


# ============================================================================
# COURSE 4 - PANDAS II: CLEANING, GROUPBY, JOINS, TIME
# ============================================================================

def course4_lecture() -> list[dict]:
    return [
        md("# Course 4 - Pandas II: Cleaning, GroupBy, Joins, Time",
           "",
           "Live-coding notebook that mirrors the slide deck.",
           "Concrete examples lifted from Aurelien Geron's Pandas tutorial.",
           "",
           "**Sections**",
           "1. Missing data & column ops (0:00-0:30)",
           "2. GroupBy, pivot, merge (0:30-1:00)",
           "3. Time series (1:00-1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "import pandas as pd",
             "import numpy as np",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(0)"),
        md("## 1. Missing data & column ops"),
        md("### Load `titanic` - the canonical messy dataset"),
        code("titanic = load_dataset('titanic')",
             "titanic.head()"),
        md("### Find the NaNs"),
        code("titanic.isna().sum()"),
        md("### Drop, fill, interpolate"),
        code("clean = titanic.dropna(subset=['embarked'])",
             "print('rows lost:', len(titanic) - len(clean))"),
        code("filled = titanic.assign(age=titanic['age'].fillna(titanic['age'].median()))",
             "print('age NaNs after fillna:', filled['age'].isna().sum())"),
        md("### Interpolate across columns - Geron-style"),
        code("bonus = pd.DataFrame(",
             "    [[0, np.nan, 2], [np.nan, 1, 0], [0, 1, 0], [3, 3, 0]],",
             "    columns=['oct', 'nov', 'dec'],",
             "    index=['bob', 'colin', 'darwin', 'charles'])",
             "bonus.interpolate(axis=1)"),
        md("### Column ops - `assign` and `query`"),
        code("tips = load_dataset('tips')",
             "(tips",
             "   .assign(tip_pct=lambda df: df['tip'] / df['total_bill'])",
             "   .query('tip_pct > 0.2 and time == \"Dinner\"')",
             "   .head())"),
        md("## 2. GroupBy, pivot, merge"),
        md("### `groupby` + aggregation - the workhorse"),
        code("tips.groupby('day', observed=False)['tip'].mean()"),
        code("tips.groupby(['day', 'sex'], observed=False)['tip'].agg(['mean', 'count'])"),
        md("### Pivot table - Geron's `more_grades` shape"),
        code("more = pd.DataFrame({",
             "    'name':   ['alice', 'alice', 'bob', 'bob', 'charles', 'charles'],",
             "    'month':  ['sep',   'oct',   'sep', 'oct', 'sep',     'oct'],",
             "    'grade':  [ 8,       8,       10,    9,    4,         8],",
             "})",
             "more"),
        code("pd.pivot_table(more, index='name', values='grade',",
             "               columns='month', margins=True)"),
        md("### SQL-style joins with `pd.merge`"),
        code("city_loc = pd.DataFrame(",
             "    [['CA', 'San Francisco', 37.78, -122.42],",
             "     ['NY', 'New York',      40.71,  -74.01],",
             "     ['FL', 'Miami',         25.79,  -80.32]],",
             "    columns=['state', 'city', 'lat', 'lng'])",
             "",
             "city_pop = pd.DataFrame(",
             "    [[ 808976, 'San Francisco', 'California'],",
             "     [8363710, 'New York',      'New-York'],",
             "     [2242193, 'Houston',       'Texas']],",
             "    columns=['population', 'city', 'state'])",
             "",
             "pd.merge(city_loc, city_pop, on='city')               # INNER"),
        code("pd.merge(city_loc, city_pop, on='city', how='outer')  # OUTER"),
        code("pd.merge(city_loc, city_pop, on='city', how='left')   # LEFT"),
        md("### Concatenation - vertical and horizontal"),
        code("pd.concat([city_loc, city_pop], ignore_index=True)   # vertical"),
        code("pd.concat([city_loc.set_index('city'), city_pop.set_index('city')], axis=1)   # horizontal"),
        md("## 3. Time series"),
        md("### `pd.date_range` and a DatetimeIndex"),
        code("temps = [4.4, 5.1, 6.1, 6.2, 6.1, 6.1, 5.7, 5.2, 4.7, 4.1, 3.9, 3.5]",
             "dates = pd.date_range('2016-10-29 17:30', periods=12, freq='h')",
             "ts = pd.Series(temps, index=dates, name='Temperature')",
             "ts.head()"),
        md("### Resample - down and up"),
        code("ts.resample('2h').mean()       # downsample: aggregate"),
        code("ts.resample('15min').interpolate(method='cubic').head()   # upsample: interpolate"),
        md("### Real CSV - `stock-prices` (Plotly's 2014 AAPL closing prices)"),
        code("sp = load_dataset('stock-prices')",
             "print(sp.columns.tolist())",
             "sp.head()"),
        code("# The Plotly file labels its columns AAPL_x (date) and AAPL_y (price).",
             "DATE  = sp.columns[0]",
             "PRICE = sp.columns[1]",
             "sp[DATE] = pd.to_datetime(sp[DATE])",
             "sp = sp.sort_values(DATE).set_index(DATE)",
             "sp.head()"),
        md("### Daily -> weekly mean - and a quick `.plot()`"),
        code("weekly = sp[PRICE].resample('W').mean()",
             "ax = weekly.plot(title='AAPL - weekly mean closing price')",
             "ax.set_ylabel('USD');"),
        md("### Recap",
           "* `isna`/`dropna`/`fillna`/`interpolate` cover 90% of cleaning.",
           "* `groupby`/`pivot_table`/`merge` cover 90% of reshaping.",
           "* `resample` makes time-series cleaning a one-liner."),
    ]


def course4_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 - Clean `titanic`"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "import numpy as np",
             "titanic = load_dataset('titanic')"),
        md("**Task 1.** How many NaNs are in each column? Print the counts."),
        code("# your code here"),
        md("**Task 2.** Impute `age` with the median age. Confirm `age` has 0 NaNs after."),
        code("# your code here"),
        md("**Task 3.** Drop rows where `embarked` is NaN. Report rows lost."),
        code("# your code here"),
        md("**Task 4.** On the cleaned frame, compute the survival rate by `pclass`."),
        code("# your code here"),
    ]


def course4_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 - Solutions"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "import numpy as np",
             "titanic = load_dataset('titanic')"),
        md("**Task 1.**"),
        code("titanic.isna().sum()"),
        md("**Task 2.**"),
        code("titanic = titanic.assign(age=titanic['age'].fillna(titanic['age'].median()))",
             "print('age NaNs:', titanic['age'].isna().sum())"),
        md("**Task 3.**"),
        code("before = len(titanic)",
             "titanic = titanic.dropna(subset=['embarked'])",
             "print('rows lost:', before - len(titanic))"),
        md("**Task 4.**"),
        code("titanic.groupby('pclass')['survived'].mean().round(3)"),
    ]


def course4_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 - GroupBy `tips`"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "df = load_dataset('tips')"),
        md("**Task 1.** Add a column `tip_pct = tip / total_bill`."),
        code("# your code here"),
        md("**Task 2.** Group by `day` and `sex` (use `observed=False`) and compute the mean `tip_pct`."),
        code("# your code here"),
        md("**Task 3.** Pivot the result of Task 2 so that `day` is the index and `sex` is the columns."),
        code("# your code here"),
        md("**Task 4.** On which (day, sex) cell is `tip_pct` highest?"),
        code("# your code here"),
    ]


def course4_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 - Solutions"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "df = load_dataset('tips')"),
        md("**Task 1.**"),
        code("df = df.assign(tip_pct=df['tip'] / df['total_bill'])",
             "df.head()"),
        md("**Task 2.**"),
        code("g = df.groupby(['day', 'sex'], observed=False)['tip_pct'].mean()",
             "g"),
        md("**Task 3.**"),
        code("pv = g.unstack('sex')",
             "pv"),
        md("**Task 4.**"),
        code("flat = g.reset_index()",
             "top = flat.loc[flat['tip_pct'].idxmax()]",
             "print(top)"),
    ]


def course4_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 - Resample `stock-prices`"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "sp = load_dataset('stock-prices')",
             "print(sp.columns.tolist())",
             "sp.head()"),
        md("**Task 1.** Parse the date column to datetime and set it as the index. Sort by date."),
        code("# your code here"),
        md("**Task 2.** Resample the price column from daily to weekly mean."),
        code("# your code here"),
        md("**Task 3.** Plot the result. (Just `.plot()` - Course 5 covers Matplotlib in depth.)"),
        code("# your code here"),
        md("**Task 4 (stretch).** Resample to monthly mean and plot daily + weekly + monthly on the same axes."),
        code("# your code here"),
    ]


def course4_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 - Solutions"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "sp = load_dataset('stock-prices')",
             "DATE  = sp.columns[0]",
             "PRICE = sp.columns[1]"),
        md("**Task 1.**"),
        code("sp[DATE] = pd.to_datetime(sp[DATE])",
             "sp = sp.sort_values(DATE).set_index(DATE)",
             "sp.head()"),
        md("**Task 2.**"),
        code("weekly = sp[PRICE].resample('W').mean()",
             "weekly.head()"),
        md("**Task 3.**"),
        code("ax = weekly.plot(title='AAPL weekly mean')",
             "ax.set_ylabel('USD');"),
        md("**Task 4.**"),
        code("monthly = sp[PRICE].resample('ME').mean()",
             "ax = sp[PRICE].plot(alpha=0.4, label='daily')",
             "weekly.plot(ax=ax, label='weekly')",
             "monthly.plot(ax=ax, label='monthly', lw=2)",
             "ax.legend();"),
    ]


# ============================================================================
# COURSE 5 - MATPLOTLIB ESSENTIALS
# ============================================================================

def course5_lecture() -> list[dict]:
    return [
        md("# Course 5 - Matplotlib Essentials",
           "",
           "Live-coding notebook that mirrors the slide deck.",
           "Concrete examples distilled from Aurelien Geron's Matplotlib tutorial.",
           "",
           "**Sections**",
           "1. The Figure / Axes mental model (0:00-0:30)",
           "2. The chart zoo (0:30-1:00)",
           "3. Subplots & saving (1:00-1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(0)"),
        md("## 1. Figure -> Axes -> Artists"),
        md("A **Figure** is the page. An **Axes** is one rectangular plot area on the page. Everything you draw - lines, markers, text - is an *Artist* on an Axes. `plt.subplots()` returns both, and that is the modern, explicit API."),
        code("fig, ax = plt.subplots()",
             "ax.plot([-3, -2, 5, 0], [1, 6, 4, 3]);"),
        md("### Plot a function - labels, title, grid, legend"),
        code("x = np.linspace(-2, 2, 500)",
             "fig, ax = plt.subplots()",
             "ax.plot(x, x**2, label='y = x^2')",
             "ax.set_xlabel('x')",
             "ax.set_ylabel('y')",
             "ax.set_title('Square function')",
             "ax.grid(True)",
             "ax.legend();"),
        md("### Line styles, colors, markers"),
        code("fig, ax = plt.subplots()",
             "ax.plot(x, x,        label='x',     linestyle='-')",
             "ax.plot(x, x**2,     label='x^2',   linestyle='--')",
             "ax.plot(x, x**3,     label='x^3',   linestyle=':', marker='.', markevery=20)",
             "ax.set_title('Powers of x')",
             "ax.legend();"),
        md("### Axis limits"),
        code("fig, ax = plt.subplots()",
             "ax.plot(x, x**2)",
             "ax.set_xlim(-2.5, 2.5)",
             "ax.set_ylim(0, 5)",
             "ax.set_title('Zoomed');"),
        md("## 2. The chart zoo"),
        md("### Scatter - colored by a third variable"),
        code("penguins = load_dataset('penguins').dropna()",
             "fig, ax = plt.subplots()",
             "colors = penguins['species'].astype('category').cat.codes",
             "ax.scatter(penguins['bill_length_mm'],",
             "           penguins['bill_depth_mm'],",
             "           c=colors, cmap='viridis', s=30, alpha=0.7)",
             "ax.set_xlabel('bill length (mm)')",
             "ax.set_ylabel('bill depth (mm)')",
             "ax.set_title('Penguins - bill length vs depth');"),
        md("### Bar"),
        code("counts = penguins['species'].value_counts()",
             "fig, ax = plt.subplots()",
             "ax.bar(counts.index, counts.values)",
             "ax.set_ylabel('count')",
             "ax.set_title('Penguins per species');"),
        md("### Histogram"),
        code("fig, ax = plt.subplots()",
             "ax.hist(penguins['body_mass_g'], bins=30, rwidth=0.9)",
             "ax.set_xlabel('body mass (g)')",
             "ax.set_ylabel('count');"),
        md("### Boxplot"),
        code("groups = [penguins.loc[penguins['species'] == s, 'body_mass_g']",
             "          for s in penguins['species'].unique()]",
             "fig, ax = plt.subplots()",
             "ax.boxplot(groups, tick_labels=list(penguins['species'].unique()))",
             "ax.set_ylabel('body mass (g)');"),
        md("## 3. Subplots & saving"),
        md("### A 2x2 grid"),
        code("fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharex=True)",
             "x = np.linspace(-1.4, 1.4, 30)",
             "axes[0, 0].plot(x, x);     axes[0, 0].set_title('x')",
             "axes[0, 1].plot(x, x**2);  axes[0, 1].set_title('x^2')",
             "axes[1, 0].plot(x, x**3);  axes[1, 0].set_title('x^3')",
             "axes[1, 1].plot(x, x**4);  axes[1, 1].set_title('x^4')",
             "fig.suptitle('Powers of x - sharex=True')",
             "fig.tight_layout();"),
        md("### Saving to PNG"),
        code("fig, ax = plt.subplots()",
             "ax.plot(x, x**2)",
             "ax.set_title('Saved')",
             "fig.savefig('/tmp/square.png', dpi=120, bbox_inches='tight')",
             "print('wrote /tmp/square.png');"),
        md("### Style sheets - change the whole vibe in one line"),
        code("with plt.style.context('seaborn-v0_8-whitegrid'):",
             "    fig, ax = plt.subplots()",
             "    ax.plot(x, np.sin(2 * np.pi * x))",
             "    ax.set_title('with seaborn-v0_8-whitegrid');"),
        md("### Recap",
           "* Always start with `fig, ax = plt.subplots()` - explicit beats implicit.",
           "* Pick the right chart for the data: distribution -> hist/box, relation -> scatter, count -> bar.",
           "* Subplots share with `sharex=`/`sharey=`; finish with `fig.tight_layout()`."),
    ]


def course5_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 - Sine + cosine"),
        code("%matplotlib inline",
             "import numpy as np",
             "import matplotlib.pyplot as plt"),
        md("**Task 1.** Plot `sin(x)` and `cos(x)` on the same axes for `x` in `[-2 pi, 2 pi]`."),
        code("# your code here"),
        md("**Task 2.** Add a title, axis labels, a legend, and a grid."),
        code("# your code here"),
        md("**Task 3.** Use different linestyles for sin (`-`) and cos (`--`)."),
        code("# your code here"),
    ]


def course5_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 - Solutions"),
        code("%matplotlib inline",
             "import numpy as np",
             "import matplotlib.pyplot as plt",
             "x = np.linspace(-2*np.pi, 2*np.pi, 400)",
             "fig, ax = plt.subplots()",
             "ax.plot(x, np.sin(x), '-',  label='sin')",
             "ax.plot(x, np.cos(x), '--', label='cos')",
             "ax.set_xlabel('x')",
             "ax.set_ylabel('y')",
             "ax.set_title('sin and cos')",
             "ax.grid(True)",
             "ax.legend();"),
    ]


def course5_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 - Penguin scatter grid"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "penguins = load_dataset('penguins').dropna()"),
        md("**Task 1.** There are 3 species (`Adelie`, `Chinstrap`, `Gentoo`). Use `plt.subplots(2, 2)` to make a 2x2 grid."),
        code("# your code here"),
        md("**Task 2.** In each of the first three Axes, draw a scatter of `bill_length_mm` vs `bill_depth_mm` for one species, colored by `sex`."),
        code("# your code here"),
        md("**Task 3.** Set per-Axes titles to the species name, add `fig.suptitle('Penguins - bill morphology')`, and call `fig.tight_layout()`."),
        code("# your code here"),
    ]


def course5_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 - Solutions"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "penguins = load_dataset('penguins').dropna()",
             "",
             "fig, axes = plt.subplots(2, 2, figsize=(9, 7))",
             "species = ['Adelie', 'Chinstrap', 'Gentoo']",
             "for ax, sp in zip(axes.flat, species):",
             "    sub = penguins[penguins['species'] == sp]",
             "    c = (sub['sex'] == 'Female').astype(int)",
             "    ax.scatter(sub['bill_length_mm'], sub['bill_depth_mm'],",
             "               c=c, cmap='coolwarm', alpha=0.7)",
             "    ax.set_title(sp)",
             "    ax.set_xlabel('bill length (mm)')",
             "    ax.set_ylabel('bill depth (mm)')",
             "axes[1, 1].axis('off')",
             "fig.suptitle('Penguins - bill morphology')",
             "fig.tight_layout();"),
    ]


def course5_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 - Histogram with reference line"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "tips = load_dataset('tips')"),
        md("**Task 1.** Plot a histogram of `tips['total_bill']` with 30 bins."),
        code("# your code here"),
        md("**Task 2.** Overlay a vertical line at the mean using `ax.axvline`; label it in a legend."),
        code("# your code here"),
        md("**Task 3.** Add axis labels and a title; save the figure to `/tmp/tips_hist.png`."),
        code("# your code here"),
    ]


def course5_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 - Solutions"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "tips = load_dataset('tips')",
             "",
             "fig, ax = plt.subplots()",
             "ax.hist(tips['total_bill'], bins=30, rwidth=0.9)",
             "mu = tips['total_bill'].mean()",
             "ax.axvline(mu, color='red', linestyle='--', label=f'mean = {mu:.2f}')",
             "ax.set_xlabel('total_bill ($)')",
             "ax.set_ylabel('count')",
             "ax.set_title('Distribution of total_bill in tips')",
             "ax.legend()",
             "fig.savefig('/tmp/tips_hist.png', dpi=120, bbox_inches='tight')",
             "print('saved /tmp/tips_hist.png');"),
    ]


# ============================================================================
# COURSE 6 - VIZ CAPSTONE + SCIPY BRIDGE
# ============================================================================

def course6_lecture() -> list[dict]:
    return [
        md("# Course 6 - Viz Capstone + SciPy Bridge",
           "",
           "Seaborn for statistical plots, SciPy for distributions and optimization,",
           "then the **Grand Finale Lab** - your end-to-end Week 1 capstone.",
           "",
           "**Sections**",
           "1. Seaborn for statistical plotting (0:00-0:30)",
           "2. SciPy stats (0:30-1:00)",
           "3. SciPy optimize + Grand Finale (1:00-1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "import seaborn as sns",
             "from scipy import stats, optimize",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(0)",
             "sns.set_theme(style='whitegrid')"),
        md("## 1. Seaborn - statistical plots in one line"),
        code("penguins = load_dataset('penguins').dropna()",
             "penguins.head()"),
        md("### Scatter coloured by category"),
        code("sns.scatterplot(data=penguins, x='bill_length_mm', y='bill_depth_mm',",
             "                hue='species', style='sex');"),
        md("### Boxplot - distribution per group"),
        code("sns.boxplot(data=penguins, x='species', y='body_mass_g', hue='sex');"),
        md("### Violinplot - boxplot + KDE in one"),
        code("sns.violinplot(data=penguins, x='species', y='flipper_length_mm');"),
        md("### Pairplot - every numeric column against every other"),
        code("sns.pairplot(penguins, hue='species', height=1.8);"),
        md("### Heatmap - correlation matrix"),
        code("corr = penguins.select_dtypes('number').corr()",
             "sns.heatmap(corr, annot=True, cmap='coolwarm', center=0);"),
        md("## 2. SciPy stats - distributions and tests"),
        md("### PDFs and CDFs"),
        code("x = np.linspace(-4, 4, 200)",
             "fig, ax = plt.subplots()",
             "for mu, sigma in [(0, 1), (0, 0.5), (1, 1)]:",
             "    ax.plot(x, stats.norm.pdf(x, mu, sigma), label=f'N({mu}, {sigma})')",
             "ax.set_title('Normal PDFs')",
             "ax.legend();"),
        code("fig, ax = plt.subplots()",
             "ax.plot(x, stats.norm.cdf(x), label='Normal CDF')",
             "ax.plot(x, stats.t.cdf(x, df=3), label='t(df=3) CDF')",
             "ax.plot(x, stats.chi2.cdf(np.clip(x, 0, None), df=3), label='chi2(df=3) CDF')",
             "ax.legend();"),
        md("### Fit a Normal to a sample"),
        code("samples = rng.normal(loc=2.0, scale=1.5, size=1000)",
             "mu_hat, sigma_hat = stats.norm.fit(samples)",
             "print(f'mu_hat = {mu_hat:.3f}, sigma_hat = {sigma_hat:.3f}')",
             "",
             "xs = np.linspace(samples.min(), samples.max(), 200)",
             "fig, ax = plt.subplots()",
             "ax.hist(samples, bins=30, density=True, alpha=0.5)",
             "ax.plot(xs, stats.norm.pdf(xs, mu_hat, sigma_hat), lw=2, label='fitted')",
             "ax.legend();"),
        md("### One-sample t-test"),
        code("res = stats.ttest_1samp(samples, popmean=0)",
             "print('t =', res.statistic, '  p =', res.pvalue)"),
        md("## 3. SciPy optimize - minimize a function"),
        md("### Rosenbrock - the classical test bed"),
        code("def rosen(x):",
             "    return (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2",
             "",
             "res = optimize.minimize(rosen, x0=[0.0, 0.0])",
             "print('x* =', res.x.round(4))",
             "print('f* =', res.fun)",
             "print('iters:', res.nit)"),
        md("### A 1-D loss surface - what every model trainer sees"),
        code("f = lambda x: (x - 3)**2 + np.sin(5 * x)",
             "xs = np.linspace(-2, 8, 400)",
             "fig, ax = plt.subplots()",
             "ax.plot(xs, f(xs))",
             "res = optimize.minimize(f, x0=0.0)",
             "ax.axvline(res.x[0], color='red', ls='--', label=f'min at x={res.x[0]:.3f}')",
             "ax.legend(); ax.set_title('A loss surface');"),
        md("## Grand Finale Lab - end-to-end pipeline"),
        md("**Mission.** Load `stock-prices`, inject synthetic NaNs, clean with Pandas, "
           "compute a 7-day rolling mean with NumPy, plot raw + smoothed with Matplotlib. "
           "This is the Week 1 capstone - every skill from the 6 courses fires in 6 cells."),
        code("# Step 1 - load and inject NaNs",
             "df = load_dataset('stock-prices').copy()",
             "DATE  = df.columns[0]",
             "PRICE = df.columns[1]",
             "mask = rng.random(len(df)) < 0.05",
             "df.loc[mask, PRICE] = np.nan",
             "print('shape:', df.shape, '  NaNs injected:', int(mask.sum()))"),
        code("# Step 2 - parse dates and sort",
             "df[DATE] = pd.to_datetime(df[DATE])",
             "df = df.sort_values(DATE).reset_index(drop=True)"),
        code("# Step 3 - clean: forward-fill the price",
             "df[PRICE] = df[PRICE].ffill()",
             "assert df[PRICE].isna().sum() == 0"),
        code("# Step 4 - NumPy 7-day moving average via convolution",
             "window = 7",
             "kernel = np.ones(window) / window",
             "ma = np.convolve(df[PRICE].values, kernel, mode='valid')",
             "ma_full = np.concatenate([np.full(window - 1, np.nan), ma])",
             "print('ma length matches df:', len(ma_full) == len(df))"),
        code("# Step 5 - plot",
             "fig, ax = plt.subplots(figsize=(10, 4))",
             "ax.plot(df[DATE], df[PRICE], label='price', alpha=0.5)",
             "ax.plot(df[DATE], ma_full, label='7-day MA', lw=2)",
             "ax.set_xlabel('date'); ax.set_ylabel(PRICE)",
             "ax.set_title('AAPL - closing price + 7-day moving average')",
             "ax.legend(); fig.autofmt_xdate();"),
        md("### Recap - Week 1 in one breath",
           "* Seaborn for fast statistical plots; SciPy stats for distributions; SciPy optimize for the loss landscape every model walks.",
           "* The Grand Finale = load -> clean -> smooth -> plot. That is the shape of every analysis you will write."),
    ]


def course6_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 - Fit a Normal to `tips`"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import numpy as np",
             "import matplotlib.pyplot as plt",
             "from scipy import stats",
             "from shared.data_utils import load_dataset",
             "tips = load_dataset('tips')"),
        md("**Task 1.** Use `stats.norm.fit` to estimate `(mu, sigma)` from `tips['total_bill']`."),
        code("# your code here"),
        md("**Task 2.** Plot a density histogram of `total_bill` and overlay the fitted PDF."),
        code("# your code here"),
        md("**Task 3.** Report whether the fit looks good. (Eyeball - Course 4 of Week 4 covers formal tests.)"),
        code("# your code here"),
    ]


def course6_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 - Solutions"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import numpy as np",
             "import matplotlib.pyplot as plt",
             "from scipy import stats",
             "from shared.data_utils import load_dataset",
             "tips = load_dataset('tips')",
             "vals = tips['total_bill'].values"),
        md("**Task 1.**"),
        code("mu, sigma = stats.norm.fit(vals)",
             "print(f'mu = {mu:.3f}, sigma = {sigma:.3f}')"),
        md("**Task 2.**"),
        code("xs = np.linspace(vals.min(), vals.max(), 200)",
             "fig, ax = plt.subplots()",
             "ax.hist(vals, bins=30, density=True, alpha=0.5)",
             "ax.plot(xs, stats.norm.pdf(xs, mu, sigma), lw=2, label='fitted Normal')",
             "ax.set_xlabel('total_bill'); ax.legend();"),
        md("**Task 3.**"),
        code("# The distribution is right-skewed; a Normal underfits the right tail.",
             "# A log-Normal or Gamma would likely do better."),
    ]


def course6_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 - Minimize a 1-D function"),
        code("import numpy as np",
             "import matplotlib.pyplot as plt",
             "from scipy import optimize"),
        md("**Task 1.** Define `f(x) = (x - 3)**2 + 5`."),
        code("# your code here"),
        md("**Task 2.** Use `optimize.minimize` starting from `x0 = 0.0`. Report `res.x` and `res.fun`."),
        code("# your code here"),
        md("**Task 3.** Verify by computing `f(res.x)` and checking it equals `res.fun` up to floating-point tolerance."),
        code("# your code here"),
        md("**Task 4 (stretch).** Plot `f` over `x in [-2, 8]` and mark the minimum with a vertical line."),
        code("# your code here"),
    ]


def course6_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 - Solutions"),
        code("import numpy as np",
             "import matplotlib.pyplot as plt",
             "from scipy import optimize"),
        md("**Task 1.**"),
        code("def f(x):",
             "    return (x - 3)**2 + 5"),
        md("**Task 2.**"),
        code("res = optimize.minimize(f, x0=0.0)",
             "print('x* =', res.x[0])",
             "print('f* =', res.fun)"),
        md("**Task 3.**"),
        code("assert np.isclose(float(f(res.x[0])), res.fun)",
             "print('verified - minimum at (3, 5)')"),
        md("**Task 4.**"),
        code("xs = np.linspace(-2, 8, 200)",
             "fig, ax = plt.subplots()",
             "ax.plot(xs, f(xs))",
             "ax.axvline(res.x[0], color='red', ls='--', label=f'min at x={res.x[0]:.3f}')",
             "ax.legend();"),
    ]


def course6_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 - Grand Finale, reusable",
           "",
           "**Mission.** Wrap the Grand Finale pipeline in a one-screen function and call it.",
           "",
           "Constraints:",
           "- The function should accept a DataFrame, a date-column name, a price-column name, and a window size.",
           "- It returns the figure so callers can save or display it.",
           "- It performs: parse date -> sort -> forward-fill -> moving average -> plot."),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(0)",
             "",
             "df = load_dataset('stock-prices').copy()",
             "# inject 5% NaNs in the price column",
             "PRICE = df.columns[1]",
             "mask = rng.random(len(df)) < 0.05",
             "df.loc[mask, PRICE] = np.nan"),
        md("**Step 1.** Write `def grand_finale(df, date_col, price_col, window=7) -> plt.Figure`."),
        code("# your code here"),
        md("**Step 2.** Call it on the data and display the figure."),
        code("# your code here"),
        md("**Step 3 (stretch).** Add a `title` parameter; default it to `f'{price_col} + {window}-day MA'`."),
        code("# your code here"),
    ]


def course6_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 - Solutions"),
        code(*REPO_ROOT_BOOTSTRAP,
             "%matplotlib inline",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(0)",
             "",
             "df = load_dataset('stock-prices').copy()",
             "DATE  = df.columns[0]",
             "PRICE = df.columns[1]",
             "mask = rng.random(len(df)) < 0.05",
             "df.loc[mask, PRICE] = np.nan"),
        md("**Step 1.**"),
        code("def grand_finale(df, date_col, price_col, window=7, title=None):",
             "    df = df.copy()",
             "    df[date_col] = pd.to_datetime(df[date_col])",
             "    df = df.sort_values(date_col).reset_index(drop=True)",
             "    df[price_col] = df[price_col].ffill()",
             "    kernel = np.ones(window) / window",
             "    ma = np.convolve(df[price_col].values, kernel, mode='valid')",
             "    ma_full = np.concatenate([np.full(window - 1, np.nan), ma])",
             "    fig, ax = plt.subplots(figsize=(10, 4))",
             "    ax.plot(df[date_col], df[price_col], label='price', alpha=0.5)",
             "    ax.plot(df[date_col], ma_full, label=f'{window}-day MA', lw=2)",
             "    ax.set_xlabel('date'); ax.set_ylabel(price_col)",
             "    ax.set_title(title or f'{price_col} + {window}-day MA')",
             "    ax.legend(); fig.autofmt_xdate()",
             "    return fig"),
        md("**Step 2.**"),
        code("fig = grand_finale(df, DATE, PRICE)",
             "fig;"),
        md("**Step 3.**"),
        code("fig = grand_finale(df, DATE, PRICE, window=14, title='AAPL - 14-day smoothing')",
             "fig;"),
    ]


# ============================================================================
# DRIVER
# ============================================================================

def combine(lecture, *exercise_pairs):
    """Concatenate lecture + (exercise, solution) pairs into one notebook.

    Each exercise/solution gets its own divider so the instructor can fold
    sections in JupyterLab. The bootstrap/import cell duplicated in every
    builder is harmless on re-run (sys.path insert is idempotent).
    """
    cells = list(lecture)
    cells.append(md("---", "", "# Exercises",
                    "",
                    "Each exercise below is followed by its solution.",
                    "Try to solve the tasks yourself before revealing the next cell."))
    for i, (starter, solution) in enumerate(exercise_pairs, 1):
        cells.append(md(f"---\n\n## Exercise {i}"))
        cells.extend(starter)
        cells.append(md(f"### Exercise {i} - Solution"))
        cells.extend(solution)
    return cells


NOTEBOOKS = [
    ("course-01-numpy/lecture.ipynb", lambda: combine(
        course1_lecture() + course2_lecture(),
        (course1_ex1_starter(), course1_ex1_solution()),
        (course1_ex2_starter(), course1_ex2_solution()),
        (course1_ex3_starter(), course1_ex3_solution()),
        (course2_ex1_starter(), course2_ex1_solution()),
        (course2_ex2_starter(), course2_ex2_solution()),
        (course2_ex3_starter(), course2_ex3_solution()),
    )),
    ("course-02-pandas/lecture.ipynb", lambda: combine(
        course3_lecture() + course4_lecture(),
        (course3_ex1_starter(), course3_ex1_solution()),
        (course3_ex2_starter(), course3_ex2_solution()),
        (course3_ex3_starter(), course3_ex3_solution()),
        (course4_ex1_starter(), course4_ex1_solution()),
        (course4_ex2_starter(), course4_ex2_solution()),
        (course4_ex3_starter(), course4_ex3_solution()),
    )),
    ("course-03-matplotlib/lecture.ipynb", lambda: combine(
        course5_lecture(),
        (course5_ex1_starter(), course5_ex1_solution()),
        (course5_ex2_starter(), course5_ex2_solution()),
        (course5_ex3_starter(), course5_ex3_solution()),
    )),
    ("course-04-viz-capstone-scipy/lecture.ipynb", lambda: combine(
        course6_lecture(),
        (course6_ex1_starter(), course6_ex1_solution()),
        (course6_ex2_starter(), course6_ex2_solution()),
        (course6_ex3_starter(), course6_ex3_solution()),
    )),
]


def main() -> None:
    for rel, builder in NOTEBOOKS:
        path = WEEK1 / rel
        write_nb(path, builder())
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
