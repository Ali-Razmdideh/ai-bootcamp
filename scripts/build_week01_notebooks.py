"""Generate every Jupyter notebook for Week 1.

The notebooks are emitted as plain nbformat-4 JSON. Running this script is
idempotent: it always rewrites the files from the source-of-truth content
defined below. Keeping notebook content in this file (rather than 21 hand-edited
.ipynb blobs) makes course updates a one-edit operation.

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


# Every notebook starts with this snippet so `from shared.data_utils import ...`
# works regardless of how deeply nested the notebook is. We walk up the
# directory tree until we hit the repo's pyproject.toml.
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
# COURSE 1 — NUMPY
# ============================================================================

def course1_lecture() -> list[dict]:
    return [
        md("# Course 1 — The Numerical Engine (NumPy)",
           "",
           "Live-coding notebook that mirrors the slide deck. Run each cell as you teach.",
           "",
           "**Sections**",
           "1. The ND-Array (0:00–0:30)",
           "2. Shape & Slicing (0:30–1:00)",
           "3. Vectorization & Broadcasting (1:00–1:30)"),
        code("import numpy as np",
             "rng = np.random.default_rng(0)   # seeded RNG — every run reproducible",
             "np.__version__"),
        md("## 1. The ND-Array"),
        md("### List vs. ndarray — the memory story"),
        code("py_list = [1, 2, 3, 4]",
             "arr = np.array([1, 2, 3, 4])",
             "print(py_list, type(py_list))",
             "print(arr, type(arr), arr.dtype)"),
        md("### Why it's fast — measure it"),
        code("# Sum of one million ints",
             "%timeit sum(range(1_000_000))",
             "%timeit np.arange(1_000_000).sum()"),
        md("### dtypes — one float promotes the whole array"),
        code("print(np.array([1, 2, 3]).dtype)",
             "print(np.array([1.0, 2, 3]).dtype)",
             "print(np.array([1, 2, 3], dtype=np.float32).dtype)"),
        md("### Creating arrays"),
        code("print(np.zeros((2, 3)))",
             "print(np.ones((2, 3), dtype=int))",
             "print(np.arange(0, 10, 2))",
             "print(np.linspace(0, 1, 5))",
             "print(rng.normal(size=(2, 3)))"),
        md("## 2. Shape & Slicing"),
        code("a = np.arange(12).reshape(3, 4)",
             "print(a)",
             "print('shape:', a.shape, 'ndim:', a.ndim, 'size:', a.size, 'dtype:', a.dtype)"),
        md("### reshape with -1 — let NumPy compute the missing dimension"),
        code("x = np.arange(24)",
             "print(x.reshape(2, 3, 4).shape)",
             "print(x.reshape(2, -1).shape)"),
        md("### Transpose & axis-swap (think batch-of-images conversions)"),
        code("img = rng.random((224, 224, 3))   # HWC layout (e.g. matplotlib)",
             "print('HWC:', img.shape)",
             "print('CHW:', img.transpose(2, 0, 1).shape)   # PyTorch layout"),
        md("### Slicing in N dimensions"),
        code("a = np.arange(20).reshape(4, 5)",
             "print(a)",
             "print('row 1     :', a[1])",
             "print('col 0     :', a[:, 0])",
             "print('2x2 block :\\n', a[1:3, 2:4])",
             "print('reversed  :\\n', a[::-1])"),
        md("**Gotcha:** slices are *views*, not copies."),
        code("b = a[:2, :2]",
             "b[0, 0] = -999",
             "print(a)   # the source mutated too!"),
        md("### Boolean & fancy indexing"),
        code("x = rng.normal(size=10)",
             "print('x         :', x)",
             "print('positives :', x[x > 0])",
             "x[x < 0] = 0",
             "print('clipped   :', x)",
             "",
             "ix = np.array([0, 3, 5])",
             "print('picked    :', x[ix])"),
        md("## 3. Vectorization & Broadcasting"),
        md("### The loop you should never write"),
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
        md("### Reductions — learn the `axis` argument"),
        code("a = np.arange(12).reshape(3, 4)",
             "print(a)",
             "print('sum all   :', a.sum())",
             "print('sum axis0 :', a.sum(axis=0))   # collapse rows -> per-column total",
             "print('sum axis1 :', a.sum(axis=1))   # collapse cols -> per-row total"),
        md("### Broadcasting — align shapes from the right"),
        code("row = np.array([1, 2, 3])",
             "M = np.zeros((3, 3))",
             "print(M + row)        # (3,) broadcast over (3, 3)",
             "",
             "col = np.array([[10], [20], [30]])   # (3, 1)",
             "print(col + row)      # (3, 1) + (3,) -> (3, 3)"),
        md("### Worked example — pairwise distances without a single Python loop"),
        code("pts = rng.normal(size=(100, 2))",
             "diff = pts[:, None, :] - pts[None, :, :]    # (100, 100, 2)",
             "dist = np.sqrt((diff**2).sum(axis=-1))",
             "print('dist matrix shape:', dist.shape)",
             "print('symmetric? ', np.allclose(dist, dist.T))",
             "print('zero diagonal?', np.allclose(np.diag(dist), 0))"),
        md("### Recap",
           "* ndarray is a contiguous typed buffer — that is the entire speed story.",
           "* Reshape and transpose change *strides*, not data.",
           "* Replace numeric `for` loops with broadcasting + reductions."),
    ]


def course1_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 — Array Basics",
           "",
           "Goal: get fluent with creation, dtypes, and the shape vocabulary."),
        code("import numpy as np",
             "rng = np.random.default_rng(42)"),
        md("**Task 1.** Create a `(4, 5)` array of zeros with dtype `int32`. Print its shape, dtype, and total memory in bytes."),
        code("# your code here"),
        md("**Task 2.** Build a 1-D array of 50 evenly-spaced values between -3 and 3 inclusive."),
        code("# your code here"),
        md("**Task 3.** Draw 10000 standard-normal samples. Compute the empirical mean and std and check they are close to 0 and 1."),
        code("# your code here"),
        md("**Task 4.** Make a `(3, 3)` identity matrix without using `np.eye`. (Hint: `np.arange` + boolean comparison.)"),
        code("# your code here"),
    ]


def course1_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 — Solutions"),
        code("import numpy as np",
             "rng = np.random.default_rng(42)"),
        md("**Task 1.**"),
        code("a = np.zeros((4, 5), dtype=np.int32)",
             "print(a.shape, a.dtype, a.nbytes, 'bytes')"),
        md("**Task 2.**"),
        code("xs = np.linspace(-3, 3, 50)",
             "print(xs[:5], '...', xs[-5:])",
             "print('count:', xs.size)"),
        md("**Task 3.**"),
        code("samples = rng.normal(size=10_000)",
             "print('mean:', samples.mean(), '  std:', samples.std())",
             "assert abs(samples.mean()) < 0.05",
             "assert abs(samples.std() - 1) < 0.05"),
        md("**Task 4.**"),
        code("n = 3",
             "ix = np.arange(n)",
             "I = (ix[:, None] == ix[None, :]).astype(int)",
             "print(I)",
             "assert np.array_equal(I, np.eye(n, dtype=int))"),
    ]


def course1_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 — Slicing & Reshape",
           "",
           "We will treat an image as an ndarray — exactly what every CV model sees."),
        code("import numpy as np",
             "import matplotlib.pyplot as plt",
             "rng = np.random.default_rng(0)",
             "",
             "# Synthetic 'image': a 64x64 grayscale gradient with a bright square in the center.",
             "img = np.tile(np.linspace(0, 1, 64), (64, 1))",
             "img[24:40, 24:40] = 1.0",
             "plt.imshow(img, cmap='gray'); plt.title('source'); plt.axis('off');"),
        md("**Task 1.** Crop the central 32×32 region of `img` and display it."),
        code("# your code here"),
        md("**Task 2.** Flip the image left↔right and top↔bottom (two separate outputs)."),
        code("# your code here"),
        md("**Task 3.** Convert the image to RGB by stacking it 3 times along a new last axis. Print the new shape."),
        code("# your code here"),
        md("**Task 4.** Set every pixel whose value is above 0.9 to 0 (in a copy, not the original)."),
        code("# your code here"),
    ]


def course1_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 — Solutions"),
        code("import numpy as np",
             "import matplotlib.pyplot as plt",
             "rng = np.random.default_rng(0)",
             "img = np.tile(np.linspace(0, 1, 64), (64, 1))",
             "img[24:40, 24:40] = 1.0"),
        md("**Task 1.** Center crop."),
        code("crop = img[16:48, 16:48]",
             "print(crop.shape)",
             "plt.imshow(crop, cmap='gray'); plt.axis('off');"),
        md("**Task 2.** Flips."),
        code("lr = img[:, ::-1]",
             "ud = img[::-1, :]",
             "fig, ax = plt.subplots(1, 2, figsize=(6, 3))",
             "ax[0].imshow(lr, cmap='gray'); ax[0].set_title('LR'); ax[0].axis('off')",
             "ax[1].imshow(ud, cmap='gray'); ax[1].set_title('UD'); ax[1].axis('off');"),
        md("**Task 3.** Grayscale -> RGB."),
        code("rgb = np.stack([img, img, img], axis=-1)",
             "print(rgb.shape)        # (64, 64, 3)"),
        md("**Task 4.** Threshold on a copy."),
        code("out = img.copy()",
             "out[out > 0.9] = 0",
             "print('max before:', img.max(), 'max after:', out.max())"),
    ]


def course1_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 — Vectorization & Broadcasting",
           "",
           "Replace every `for` loop with a vectorized expression."),
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "x = rng.normal(size=1_000_000)"),
        md("**Task 1.** Compute the per-element sigmoid `1 / (1 + exp(-x))` for `x` — no loops."),
        code("# your code here"),
        md("**Task 2.** Standardize a `(200, 5)` data matrix column-wise (subtract column mean, divide by column std)."),
        code("data = rng.normal(loc=5, scale=2, size=(200, 5))",
             "# your code here"),
        md("**Task 3.** Given 50 2-D points in `pts`, compute the full 50×50 pairwise Euclidean distance matrix. No loops."),
        code("pts = rng.normal(size=(50, 2))",
             "# your code here"),
        md("**Task 4 (stretch).** Time a Python-loop version of Task 3 vs your vectorized version with `%timeit`."),
        code("# your code here"),
    ]


def course1_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 — Solutions"),
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "x = rng.normal(size=1_000_000)"),
        md("**Task 1.**"),
        code("sig = 1 / (1 + np.exp(-x))",
             "print(sig[:5])"),
        md("**Task 2.** Column-wise standardize."),
        code("data = rng.normal(loc=5, scale=2, size=(200, 5))",
             "z = (data - data.mean(axis=0)) / data.std(axis=0)",
             "print('column means ~0:', z.mean(axis=0).round(4))",
             "print('column stds  ~1:', z.std(axis=0).round(4))"),
        md("**Task 3.** Pairwise distances."),
        code("pts = rng.normal(size=(50, 2))",
             "diff = pts[:, None, :] - pts[None, :, :]",
             "dist = np.sqrt((diff**2).sum(axis=-1))",
             "print(dist.shape)",
             "assert np.allclose(dist, dist.T)",
             "assert np.allclose(np.diag(dist), 0)"),
        md("**Task 4.** Timing showdown."),
        code("def naive(pts):",
             "    n = len(pts)",
             "    out = np.empty((n, n))",
             "    for i in range(n):",
             "        for j in range(n):",
             "            out[i, j] = np.sqrt(((pts[i] - pts[j])**2).sum())",
             "    return out",
             "",
             "def fast(pts):",
             "    diff = pts[:, None, :] - pts[None, :, :]",
             "    return np.sqrt((diff**2).sum(axis=-1))",
             "",
             "%timeit naive(pts)",
             "%timeit fast(pts)"),
    ]


# ============================================================================
# COURSE 2 — PANDAS
# ============================================================================

def course2_lecture() -> list[dict]:
    return [
        md("# Course 2 — Data Manipulation (Pandas)",
           "",
           "Live-coding notebook that mirrors the slide deck.",
           "",
           "**Sections**",
           "1. DataFrames & Loading (0:00–0:30)",
           "2. Selection & Filtering (0:30–1:00)",
           "3. Cleaning & Grouping (1:00–1:30)"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "import pandas as pd",
             "import numpy as np",
             "from shared.data_utils import load_dataset",
             "pd.__version__"),
        md("## 1. DataFrames & Loading"),
        code("df = load_dataset('penguins')",
             "df.head()"),
        code("df.info()",
             "df.describe(include='all')"),
        md("### Index vs columns"),
        code("print('index:', df.index)",
             "print('cols :', df.columns.tolist())",
             "# Set a more meaningful index",
             "df2 = df.reset_index().rename(columns={'index': 'penguin_id'}).set_index('penguin_id')",
             "df2.head()"),
        md("## 2. Selection & Filtering"),
        md("### `.loc` (label) vs `.iloc` (position)"),
        code("df.loc[0:3, ['species', 'island', 'bill_length_mm']]",),
        code("df.iloc[0:3, 0:3]"),
        md("### Boolean indexing — the workhorse"),
        code("adelie_long = df[(df['species'] == 'Adelie') & (df['bill_length_mm'] > 40)]",
             "adelie_long.head()"),
        code("# Cleaner syntax for complex filters",
             "df.query('species == \"Adelie\" and bill_length_mm > 40').head()"),
        md("## 3. Cleaning & Grouping"),
        md("### Missing values"),
        code("df.isna().sum()"),
        code("clean = df.dropna()",
             "print('before:', len(df), '  after dropna:', len(clean))"),
        md("Or impute instead of dropping:"),
        code("filled = df.copy()",
             "filled['bill_length_mm'] = filled['bill_length_mm'].fillna(filled['bill_length_mm'].median())",
             "filled.isna().sum()"),
        md("### groupby + agg"),
        code("clean.groupby('species')[['bill_length_mm', 'body_mass_g']].mean().round(2)"),
        code("clean.groupby(['species', 'sex']).agg(",
             "    n=('bill_length_mm', 'size'),",
             "    mass_mean=('body_mass_g', 'mean'),",
             "    mass_std=('body_mass_g', 'std'),",
             ").round(1)"),
        md("### Feature engineering — derive a new column"),
        code("clean = clean.assign(",
             "    bill_ratio=lambda d: d['bill_length_mm'] / d['bill_depth_mm'],",
             "    mass_kg=lambda d: d['body_mass_g'] / 1000,",
             ")",
             "clean[['species', 'bill_ratio', 'mass_kg']].head()"),
        md("### Recap",
           "* Treat a DataFrame like a typed, indexed table.",
           "* `.loc` for labels, `.iloc` for positions, boolean masks for filtering.",
           "* Always inspect NaNs before training anything on the data."),
    ]


def course2_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 — DataFrame I/O & Inspection"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "from shared.data_utils import load_dataset",
             "import pandas as pd"),
        md("**Task 1.** Load the `tips` dataset. Show the first 5 rows and the dtypes."),
        code("# your code here"),
        md("**Task 2.** How many rows and columns does it have? How many numeric columns?"),
        code("# your code here"),
        md("**Task 3.** Print a 5-number summary (`describe()`) for the numeric columns only."),
        code("# your code here"),
        md("**Task 4.** Set the index to a new column `bill_id` (just a 0-based range)."),
        code("# your code here"),
    ]


def course2_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 — Solutions"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "df = load_dataset('tips')"),
        md("**Task 1.**"),
        code("print(df.head())",
             "print(df.dtypes)"),
        md("**Task 2.**"),
        code("print('shape:', df.shape)",
             "print('numeric cols:', df.select_dtypes('number').columns.tolist())"),
        md("**Task 3.**"),
        code("df.describe()"),
        md("**Task 4.**"),
        code("df = df.assign(bill_id=range(len(df))).set_index('bill_id')",
             "df.head()"),
    ]


def course2_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 — Selection & Filtering"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "from shared.data_utils import load_dataset",
             "df = load_dataset('tips')"),
        md("**Task 1.** Select rows 10–19 (inclusive) and only the columns `total_bill`, `tip`, `day`. Use `.loc`."),
        code("# your code here"),
        md("**Task 2.** Find all dinners where the tip was at least 20% of the bill."),
        code("# your code here"),
        md("**Task 3.** Same as Task 2 but use `df.query(...)`."),
        code("# your code here"),
        md("**Task 4.** What is the average tip on weekends (Sat/Sun) vs weekdays?"),
        code("# your code here"),
    ]


def course2_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 — Solutions"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "from shared.data_utils import load_dataset",
             "df = load_dataset('tips')"),
        md("**Task 1.**"),
        code("df.loc[10:19, ['total_bill', 'tip', 'day']]"),
        md("**Task 2.**"),
        code("mask = (df['time'] == 'Dinner') & (df['tip'] / df['total_bill'] >= 0.20)",
             "df[mask].head()"),
        md("**Task 3.**"),
        code("df.query('time == \"Dinner\" and tip / total_bill >= 0.20').head()"),
        md("**Task 4.**"),
        code("(df.assign(weekend=df['day'].isin(['Sat', 'Sun']))",
             "   .groupby('weekend')['tip'].mean().round(2))"),
    ]


def course2_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 — Cleaning & Grouping"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "from shared.data_utils import load_dataset",
             "df = load_dataset('penguins')"),
        md("**Task 1.** Report the number of NaNs per column."),
        code("# your code here"),
        md("**Task 2.** Drop every row that has at least one NaN. How many rows did you lose?"),
        code("# your code here"),
        md("**Task 3.** On the cleaned data: per-species mean and std of `body_mass_g`. Round to 1 decimal."),
        code("# your code here"),
        md("**Task 4.** Add a column `mass_kg` (= body_mass_g / 1000) and a column `bill_ratio` (= bill_length / bill_depth). Sort by `bill_ratio` descending and show the top 5."),
        code("# your code here"),
    ]


def course2_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 — Solutions"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "from shared.data_utils import load_dataset",
             "df = load_dataset('penguins')"),
        md("**Task 1.**"),
        code("df.isna().sum()"),
        md("**Task 2.**"),
        code("clean = df.dropna()",
             "print('lost', len(df) - len(clean), 'rows')"),
        md("**Task 3.**"),
        code("clean.groupby('species')['body_mass_g'].agg(['mean', 'std']).round(1)"),
        md("**Task 4.**"),
        code("clean = clean.assign(",
             "    mass_kg=clean['body_mass_g'] / 1000,",
             "    bill_ratio=clean['bill_length_mm'] / clean['bill_depth_mm'],",
             ")",
             "clean.sort_values('bill_ratio', ascending=False).head()"),
    ]


# ============================================================================
# COURSE 3 — VIZ + SCIPY
# ============================================================================

def course3_lecture() -> list[dict]:
    return [
        md("# Course 3 — Visualization & Math Bridge",
           "",
           "Matplotlib · Seaborn · SciPy. We end by *seeing* how an optimizer minimizes a function — the demystification of how an ML model 'learns'."),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "import seaborn as sns",
             "from scipy import stats, optimize",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(0)",
             "sns.set_theme(style='whitegrid')"),
        md("## 1. Matplotlib — line, scatter, subplots"),
        code("# Fake loss curves — exactly what you'll plot for every model you train",
             "epochs = np.arange(1, 51)",
             "train = 1 / np.sqrt(epochs) + rng.normal(scale=0.02, size=50)",
             "val   = 1 / np.sqrt(epochs) + 0.05 + rng.normal(scale=0.03, size=50)",
             "",
             "fig, ax = plt.subplots(figsize=(6, 4))",
             "ax.plot(epochs, train, label='train')",
             "ax.plot(epochs, val, label='val')",
             "ax.set_xlabel('epoch'); ax.set_ylabel('loss'); ax.set_title('Loss curves')",
             "ax.legend();"),
        md("Scatter for clusters:"),
        code("X = np.vstack([rng.normal(loc=[0, 0], size=(50, 2)),",
             "               rng.normal(loc=[4, 4], size=(50, 2))])",
             "y = np.r_[np.zeros(50), np.ones(50)]",
             "plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis'); plt.title('Two clusters');"),
        md("## 2. Seaborn — heatmaps & distributions"),
        code("df = load_dataset('penguins').dropna()",
             "sns.heatmap(df.select_dtypes('number').corr(), annot=True, cmap='coolwarm');"),
        code("sns.kdeplot(data=df, x='bill_length_mm', hue='species', fill=True);"),
        md("## 3. SciPy — probability and optimization"),
        md("### `scipy.stats`"),
        code("x = np.linspace(-4, 4, 200)",
             "for mu, sigma in [(0, 1), (0, 0.5), (1, 1)]:",
             "    plt.plot(x, stats.norm.pdf(x, mu, sigma), label=f'N({mu}, {sigma})')",
             "plt.legend(); plt.title('Normal PDFs');"),
        md("### `scipy.optimize` — *this is what ML models do*"),
        code("# A bumpy 1-D loss landscape.",
             "f = lambda x: (x - 3)**2 + np.sin(5 * x)",
             "xs = np.linspace(-2, 8, 400)",
             "plt.plot(xs, f(xs)); plt.title('A loss surface'); plt.xlabel('x'); plt.ylabel('loss');"),
        code("res = optimize.minimize(f, x0=0.0)",
             "print(res)",
             "print('argmin ≈', res.x[0])"),
        md("Visualize the minimum:"),
        code("plt.plot(xs, f(xs))",
             "plt.axvline(res.x[0], color='red', ls='--', label=f'min at x={res.x[0]:.3f}')",
             "plt.legend();"),
        md("### Takeaway",
           "Every model you'll train — linear regression, neural nets — does this same trick: define a loss `f(parameters)` and call an optimizer. Today you saw the whole loop in 3 lines."),
        md("## Grand Finale — preview",
           "In the final exercise notebook you'll: load a messy stock-prices CSV, clean NaNs with pandas, compute a 7-day moving average with NumPy, and plot price + MA together with matplotlib."),
    ]


def course3_ex1_starter() -> list[dict]:
    return [
        md("# Exercise 1 — Matplotlib & Seaborn"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "import numpy as np",
             "import matplotlib.pyplot as plt",
             "import seaborn as sns",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(7)",
             "sns.set_theme(style='whitegrid')"),
        md("**Task 1.** Plot `sin(x)` and `cos(x)` on the same axes for x in [-2π, 2π]. Add legend, axis labels and a title."),
        code("# your code here"),
        md("**Task 2.** Generate 300 points from two 2-D Gaussian blobs centered at `(0,0)` and `(3,3)`. Plot a scatter colored by cluster id."),
        code("# your code here"),
        md("**Task 3.** Load the `iris` dataset and draw a Seaborn heatmap of the correlation matrix of its numeric columns."),
        code("# your code here"),
        md("**Task 4.** Same dataset — KDE of `petal_length` colored by species."),
        code("# your code here"),
    ]


def course3_ex1_solution() -> list[dict]:
    return [
        md("# Exercise 1 — Solutions"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "import numpy as np",
             "import matplotlib.pyplot as plt",
             "import seaborn as sns",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(7)",
             "sns.set_theme(style='whitegrid')"),
        md("**Task 1.**"),
        code("x = np.linspace(-2*np.pi, 2*np.pi, 400)",
             "plt.plot(x, np.sin(x), label='sin')",
             "plt.plot(x, np.cos(x), label='cos')",
             "plt.xlabel('x'); plt.ylabel('y'); plt.title('sin & cos'); plt.legend();"),
        md("**Task 2.**"),
        code("a = rng.normal(loc=[0, 0], size=(150, 2))",
             "b = rng.normal(loc=[3, 3], size=(150, 2))",
             "X = np.vstack([a, b]); y = np.r_[np.zeros(150), np.ones(150)]",
             "plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis'); plt.title('two blobs');"),
        md("**Task 3.**"),
        code("iris = load_dataset('iris')",
             "sns.heatmap(iris.select_dtypes('number').corr(), annot=True, cmap='coolwarm');"),
        md("**Task 4.**"),
        code("sns.kdeplot(data=iris, x='petal_length', hue='species', fill=True);"),
    ]


def course3_ex2_starter() -> list[dict]:
    return [
        md("# Exercise 2 — SciPy stats & optimize"),
        code("import numpy as np",
             "import matplotlib.pyplot as plt",
             "from scipy import stats, optimize",
             "rng = np.random.default_rng(1)"),
        md("**Task 1.** Sample 1000 points from a `Normal(mean=2, std=1.5)` and fit a Gaussian back to them with `stats.norm.fit`. How close do you get?"),
        code("# your code here"),
        md("**Task 2.** Plot the histogram of those samples together with the *fitted* PDF."),
        code("# your code here"),
        md("**Task 3.** Minimize `f(x) = (x - 3)**2 + sin(x)` starting from `x0 = 0`. Report the argmin and the minimum value."),
        code("# your code here"),
        md("**Task 4 (stretch).** Show that starting from `x0 = 10` finds a *different* local minimum — this is why initialization matters."),
        code("# your code here"),
    ]


def course3_ex2_solution() -> list[dict]:
    return [
        md("# Exercise 2 — Solutions"),
        code("import numpy as np",
             "import matplotlib.pyplot as plt",
             "from scipy import stats, optimize",
             "rng = np.random.default_rng(1)"),
        md("**Task 1.**"),
        code("samples = rng.normal(loc=2.0, scale=1.5, size=1000)",
             "mu_hat, sigma_hat = stats.norm.fit(samples)",
             "print(f'fitted mean = {mu_hat:.3f},  fitted std = {sigma_hat:.3f}')"),
        md("**Task 2.**"),
        code("xs = np.linspace(samples.min(), samples.max(), 200)",
             "plt.hist(samples, bins=30, density=True, alpha=0.5)",
             "plt.plot(xs, stats.norm.pdf(xs, mu_hat, sigma_hat), lw=2, label='fitted PDF')",
             "plt.legend();"),
        md("**Task 3.**"),
        code("f = lambda x: (x - 3)**2 + np.sin(x)",
             "res = optimize.minimize(f, x0=0.0)",
             "print('argmin =', res.x[0], '  min =', res.fun)"),
        md("**Task 4.**"),
        code("res2 = optimize.minimize(f, x0=10.0)",
             "print('argmin from x0=10:', res2.x[0])",
             "xs = np.linspace(-2, 12, 500)",
             "plt.plot(xs, f(xs))",
             "plt.axvline(res.x[0], color='red', ls='--', label=f'from x0=0  -> {res.x[0]:.2f}')",
             "plt.axvline(res2.x[0], color='green', ls='--', label=f'from x0=10 -> {res2.x[0]:.2f}')",
             "plt.legend();"),
    ]


def course3_ex3_starter() -> list[dict]:
    return [
        md("# Exercise 3 — Grand Finale Lab (15 min)",
           "",
           "**Mission.** Load a messy stock-prices CSV, clean it with pandas, compute a 7-day moving average with NumPy, and plot price + MA together.",
           "",
           "Constraints:",
           "- No looping over rows.",
           "- Use `shared.data_utils.load_dataset('stock-prices')` to fetch the data."),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(0)",
             "",
             "df = load_dataset('stock-prices')",
             "# Inject synthetic NaNs so there is something to clean.",
             "mask = rng.random(len(df)) < 0.05",
             "df.loc[mask, df.columns[1]] = np.nan",
             "df.head()"),
        md("**Step 1.** Inspect: how many NaNs are there in the price column? What is the dtype of the date column?"),
        code("# your code here"),
        md("**Step 2.** Parse the date column to `datetime` and sort the DataFrame chronologically."),
        code("# your code here"),
        md("**Step 3.** Fill the NaN prices using forward-fill (use the previous valid price)."),
        code("# your code here"),
        md("**Step 4.** Using NumPy only (`np.convolve` or manual stride logic), compute the 7-day moving average of the price."),
        code("# your code here"),
        md("**Step 5.** Plot price and moving average together with date on the x-axis."),
        code("# your code here"),
    ]


def course3_ex3_solution() -> list[dict]:
    return [
        md("# Exercise 3 — Grand Finale Solution"),
        code(
            "import sys, pathlib",
            "p = pathlib.Path.cwd()",
            "while not (p / 'pyproject.toml').exists() and p != p.parent:",
            "    p = p.parent",
            "if str(p) not in sys.path:",
            "    sys.path.insert(0, str(p))",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from shared.data_utils import load_dataset",
             "rng = np.random.default_rng(0)",
             "",
             "df = load_dataset('stock-prices')",
             "PRICE = df.columns[1]   # second column = closing price",
             "DATE = df.columns[0]",
             "mask = rng.random(len(df)) < 0.05",
             "df.loc[mask, PRICE] = np.nan",
             "print('shape:', df.shape, ' price col:', PRICE)"),
        md("**Step 1.** Inspect."),
        code("print('NaNs in price:', df[PRICE].isna().sum())",
             "print('date dtype  :', df[DATE].dtype)"),
        md("**Step 2.** Parse + sort."),
        code("df[DATE] = pd.to_datetime(df[DATE])",
             "df = df.sort_values(DATE).reset_index(drop=True)",
             "df.head()"),
        md("**Step 3.** Forward-fill."),
        code("df[PRICE] = df[PRICE].ffill()",
             "assert df[PRICE].isna().sum() == 0"),
        md("**Step 4.** 7-day moving average with NumPy."),
        code("window = 7",
             "kernel = np.ones(window) / window",
             "ma = np.convolve(df[PRICE].values, kernel, mode='valid')",
             "# Pad the front so lengths line up for plotting",
             "ma_full = np.concatenate([np.full(window - 1, np.nan), ma])",
             "print('ma len:', len(ma_full), '  df len:', len(df))"),
        md("**Step 5.** Plot."),
        code("fig, ax = plt.subplots(figsize=(10, 4))",
             "ax.plot(df[DATE], df[PRICE], label='price', alpha=0.5)",
             "ax.plot(df[DATE], ma_full, label='7-day MA', lw=2)",
             "ax.set_xlabel('date'); ax.set_ylabel(PRICE); ax.set_title('AAPL closing price + 7-day MA')",
             "ax.legend(); fig.autofmt_xdate();"),
    ]


# ============================================================================
# DRIVER
# ============================================================================

NOTEBOOKS = [
    # (relative path under week-01-foundations, builder)
    ("course-01-numpy/lecture.ipynb",                              course1_lecture),
    ("course-01-numpy/exercises/01_array_basics.ipynb",            course1_ex1_starter),
    ("course-01-numpy/exercises/solutions/01_array_basics.ipynb",  course1_ex1_solution),
    ("course-01-numpy/exercises/02_slicing_reshape.ipynb",         course1_ex2_starter),
    ("course-01-numpy/exercises/solutions/02_slicing_reshape.ipynb", course1_ex2_solution),
    ("course-01-numpy/exercises/03_vectorization.ipynb",           course1_ex3_starter),
    ("course-01-numpy/exercises/solutions/03_vectorization.ipynb", course1_ex3_solution),

    ("course-02-pandas/lecture.ipynb",                             course2_lecture),
    ("course-02-pandas/exercises/01_dataframe_io.ipynb",           course2_ex1_starter),
    ("course-02-pandas/exercises/solutions/01_dataframe_io.ipynb", course2_ex1_solution),
    ("course-02-pandas/exercises/02_loc_iloc_boolean.ipynb",       course2_ex2_starter),
    ("course-02-pandas/exercises/solutions/02_loc_iloc_boolean.ipynb", course2_ex2_solution),
    ("course-02-pandas/exercises/03_clean_groupby.ipynb",          course2_ex3_starter),
    ("course-02-pandas/exercises/solutions/03_clean_groupby.ipynb", course2_ex3_solution),

    ("course-03-viz-scipy/lecture.ipynb",                          course3_lecture),
    ("course-03-viz-scipy/exercises/01_matplotlib_seaborn.ipynb",  course3_ex1_starter),
    ("course-03-viz-scipy/exercises/solutions/01_matplotlib_seaborn.ipynb", course3_ex1_solution),
    ("course-03-viz-scipy/exercises/02_scipy_stats_optimize.ipynb", course3_ex2_starter),
    ("course-03-viz-scipy/exercises/solutions/02_scipy_stats_optimize.ipynb", course3_ex2_solution),
    ("course-03-viz-scipy/exercises/03_grand_finale_lab.ipynb",    course3_ex3_starter),
    ("course-03-viz-scipy/exercises/solutions/03_grand_finale_lab.ipynb", course3_ex3_solution),
]


def main() -> None:
    for rel, builder in NOTEBOOKS:
        path = WEEK1 / rel
        write_nb(path, builder())
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
