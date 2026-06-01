"""Generate every Jupyter notebook for Week 3 (Machine Learning — regression).

Idempotent: re-running rewrites every .ipynb from the source-of-truth below.

Usage:
    python3 scripts/build_week03_notebooks.py
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEK3 = ROOT / "weeks" / "week-03-machine-learning"


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
# COURSE 1 — LINEAR REGRESSION I (simple LR, Boston, ISLP Ch 3.1)
# ============================================================================

def course1_lecture() -> list[dict]:
    return [
        md("# Course 1 — Linear Regression",
           "",
           "Live-coding notebook mirroring the slides.",
           "Part 1: simple LR on the ISLP `Boston` dataset (`medv` ~ `lstat`).",
           "Part 2: multiple LR, diagnostics, and categorical predictors.",
           "",
           "**Part 1 sections**",
           "1. Fitting a line (0:00–0:30)",
           "2. Reading the output (0:30–1:00)",
           "3. Inference for β (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.metrics import r2_score, mean_squared_error",
             "rng = np.random.default_rng(0)",
             "boston = load_dataset('boston')",
             "boston.head()"),
        md("## 1. Fitting a line"),
        md("### The dataset"),
        code("print(boston.shape)",
             "print(boston.columns.tolist())",
             "print(boston[['lstat', 'medv']].describe().round(2))"),
        md("### Whiteboard formula — least squares"),
        md("$$\\hat\\beta_1 = \\frac{\\sum_i (x_i - \\bar x)(y_i - \\bar y)}{\\sum_i (x_i - \\bar x)^2}, \\qquad \\hat\\beta_0 = \\bar y - \\hat\\beta_1 \\bar x$$"),
        code("x = boston['lstat'].to_numpy()",
             "y = boston['medv'].to_numpy()",
             "x_bar, y_bar = x.mean(), y.mean()",
             "b1 = ((x - x_bar) * (y - y_bar)).sum() / ((x - x_bar)**2).sum()",
             "b0 = y_bar - b1 * x_bar",
             "print(f'by hand: intercept={b0:.4f}, slope={b1:.4f}')"),
        md("### Same fit, three lines of sklearn"),
        code("X = boston[['lstat']]",
             "model = LinearRegression().fit(X, y)",
             "print(f'sklearn: intercept={model.intercept_:.4f}, slope={model.coef_[0]:.4f}')"),
        md("### Plot the data and the fit"),
        code("fig, ax = plt.subplots(figsize=(6, 4))",
             "ax.scatter(x, y, s=10, alpha=0.6)",
             "x_line = np.linspace(x.min(), x.max(), 100)",
             "ax.plot(x_line, b0 + b1 * x_line, color='C3', linewidth=2)",
             "ax.set_xlabel('lstat (% lower status)'); ax.set_ylabel('medv ($1000s)')",
             "ax.set_title('Boston: medv ~ lstat'); plt.show()"),
        md("## 2. Reading the output"),
        md("### Predictions and residuals"),
        code("y_hat = model.predict(X)",
             "resid = y - y_hat",
             "print('first 5 predictions:', y_hat[:5].round(2))",
             "print('first 5 residuals: ', resid[:5].round(2))"),
        md("### R² and RMSE"),
        code("r2 = r2_score(y, y_hat)",
             "rmse = np.sqrt(mean_squared_error(y, y_hat))",
             "print(f'R^2  = {r2:.4f}   (fraction of variance explained)')",
             "print(f'RMSE = {rmse:.4f} (in same units as medv: $1000s)')"),
        md("### Residual plot — your first diagnostic"),
        code("fig, ax = plt.subplots(figsize=(6, 3.5))",
             "ax.scatter(y_hat, resid, s=10, alpha=0.6)",
             "ax.axhline(0, color='C3', linewidth=1)",
             "ax.set_xlabel('fitted'); ax.set_ylabel('residual')",
             "ax.set_title('Residuals vs fitted — curvature is a red flag'); plt.show()"),
        md("The clear U-shape says: a *line* is the wrong shape for medv ~ lstat.",
           "We will fix this next week with polynomial features."),
        md("## 3. Inference for β"),
        md("### Standard error and t-statistic"),
        code("n, p = len(y), 1",
             "rss = (resid**2).sum()",
             "sigma2 = rss / (n - p - 1)",
             "se_b1 = np.sqrt(sigma2 / ((x - x_bar)**2).sum())",
             "t = b1 / se_b1",
             "print(f'SE(beta1) = {se_b1:.4f}')",
             "print(f't-stat    = {t:.2f}   (huge -> reject beta1 = 0)')"),
        md("### Bootstrap CI for the slope"),
        code("n_boot = 2000",
             "b1_boot = np.empty(n_boot)",
             "idx = np.arange(n)",
             "for k in range(n_boot):",
             "    sample = rng.choice(idx, n, replace=True)",
             "    xb, yb = x[sample], y[sample]",
             "    b1_boot[k] = ((xb - xb.mean()) * (yb - yb.mean())).sum() / ((xb - xb.mean())**2).sum()",
             "lo, hi = np.quantile(b1_boot, [0.025, 0.975])",
             "print(f'95% bootstrap CI for slope: [{lo:.4f}, {hi:.4f}]')"),
        code("fig, ax = plt.subplots(figsize=(6, 3))",
             "ax.hist(b1_boot, bins=40, color='C0', alpha=0.7)",
             "ax.axvline(b1, color='C3', label='point estimate')",
             "ax.set_xlabel('bootstrapped slope'); ax.legend(); plt.show()"),
        md("### Four assumptions, four diagnostics"),
        md("1. **Linearity** — residuals vs fitted should look like noise.",
           "2. **Constant variance** — same plot, no funnel.",
           "3. **Independence** — no serial correlation (matters for time-series data).",
           "4. **Normality** — Q-Q plot of residuals."),
        code("from scipy import stats",
             "fig, ax = plt.subplots(figsize=(5, 4))",
             "stats.probplot(resid, plot=ax)",
             "ax.set_title('Q-Q plot of residuals'); plt.show()"),
        md("### Recap",
           "- Least squares = minimize Σ residuals². The closed form is two lines of arithmetic.",
           "- R² and RMSE summarize fit. Residual plots find what they miss.",
           "- A confidence interval is what a single coefficient is worth as a *claim*.",
           "- The bootstrap gives a CI for *anything* without distributional assumptions."),
    ]


def course1_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Load the `penguins` dataset, drop NaN, and fit a simple",
           "linear regression of `body_mass_g` on `flipper_length_mm`. Report the",
           "slope, intercept, and R²."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd, numpy as np",
             "from sklearn.linear_model import LinearRegression",
             "# your code here"),
    ]


def course1_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd, numpy as np",
             "from sklearn.linear_model import LinearRegression",
             "df = load_dataset('penguins').dropna()",
             "X = df[['flipper_length_mm']]",
             "y = df['body_mass_g']",
             "m = LinearRegression().fit(X, y)",
             "print(f'intercept = {m.intercept_:.1f}')",
             "print(f'slope     = {m.coef_[0]:.2f} g per mm')",
             "print(f'R^2       = {m.score(X, y):.4f}')"),
    ]


def course1_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Plot residuals vs fitted for that model. Do the residuals",
           "look like a band of noise around zero, or is there a pattern?"),
        code("# your code here"),
    ]


def course1_ex2_solution() -> list[dict]:
    return [
        code("import matplotlib.pyplot as plt",
             "y_hat = m.predict(X)",
             "resid = y - y_hat",
             "fig, ax = plt.subplots(figsize=(5, 3))",
             "ax.scatter(y_hat, resid, s=10, alpha=0.6)",
             "ax.axhline(0, color='C3')",
             "ax.set_xlabel('fitted'); ax.set_ylabel('residual')",
             "plt.show()",
             "# residuals look reasonable — mostly a band, mild fanning out for large fits"),
    ]


def course1_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Bootstrap a 95% confidence interval for the slope. Use",
           "2000 resamples."),
        code("# your code here"),
    ]


def course1_ex3_solution() -> list[dict]:
    return [
        code("rng = np.random.default_rng(0)",
             "x = df['flipper_length_mm'].to_numpy()",
             "y = df['body_mass_g'].to_numpy()",
             "n = len(x)",
             "slopes = np.empty(2000)",
             "for k in range(2000):",
             "    idx = rng.choice(n, n, replace=True)",
             "    xb, yb = x[idx], y[idx]",
             "    slopes[k] = ((xb - xb.mean()) * (yb - yb.mean())).sum() / ((xb - xb.mean())**2).sum()",
             "lo, hi = np.quantile(slopes, [0.025, 0.975])",
             "print(f'95% CI for slope: [{lo:.2f}, {hi:.2f}] g/mm')"),
    ]


# ============================================================================
# COURSE 2 — LINEAR REGRESSION II (multiple LR + diagnostics, ISLP Ch 3.2-3.3)
# ============================================================================

def course2_lecture() -> list[dict]:
    return [
        md("---",
           "",
           "# Part 2 — Multiple LR & diagnostics",
           "",
           "Multiple regression, diagnostics, qualitative predictors and",
           "interactions. We continue with `Boston` and bring in `Carseats`.",
           "",
           "**Part 2 sections**",
           "4. Multiple LR and collinearity (1:30–2:00)",
           "5. Diagnostic plots and leverage (2:00–2:30)",
           "6. Qualitative predictors and interactions (2:30–3:00)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.metrics import r2_score",
             "boston = load_dataset('boston')",
             "carseats = load_dataset('carseats')",
             "print('boston   :', boston.shape)",
             "print('carseats :', carseats.shape)"),
        md("## 1. Multiple LR and collinearity"),
        md("### Fit `medv` on all 12 predictors"),
        code("X = boston.drop(columns=['medv'])",
             "y = boston['medv']",
             "m = LinearRegression().fit(X, y)",
             "coefs = pd.Series(m.coef_, index=X.columns).round(4)",
             "print(coefs.to_string())",
             "print(f'R^2 = {m.score(X, y):.4f}')"),
        md("### Variance Inflation Factor — VIF"),
        md("For predictor j, fit `x_j ~ rest`, get R²_j, then VIF_j = 1/(1 - R²_j).",
           "Anything above 5–10 is collinear with the rest of the design."),
        code("def vif(X: pd.DataFrame) -> pd.Series:",
             "    out = {}",
             "    for col in X.columns:",
             "        others = X.drop(columns=[col])",
             "        r2 = LinearRegression().fit(others, X[col]).score(others, X[col])",
             "        out[col] = 1.0 / (1.0 - r2)",
             "    return pd.Series(out).sort_values(ascending=False)",
             "",
             "print(vif(X).round(2).to_string())"),
        md("`tax`, `rad`, `nox` are the biggest offenders. Coefficient *signs* on a",
           "regression with collinear predictors can flip when you add or drop a",
           "feature — never read coefficients in isolation."),
        md("## 2. Diagnostic plots and leverage"),
        code("y_hat = m.predict(X)",
             "resid = y - y_hat",
             "std_resid = resid / resid.std()",
             "",
             "fig, axes = plt.subplots(2, 2, figsize=(10, 7))",
             "axes[0, 0].scatter(y_hat, resid, s=8, alpha=0.6)",
             "axes[0, 0].axhline(0, color='C3'); axes[0, 0].set_title('Residuals vs Fitted')",
             "axes[0, 0].set_xlabel('fitted'); axes[0, 0].set_ylabel('residual')",
             "",
             "from scipy import stats",
             "stats.probplot(resid, plot=axes[0, 1])",
             "axes[0, 1].set_title('Q-Q')",
             "",
             "axes[1, 0].scatter(y_hat, np.sqrt(np.abs(std_resid)), s=8, alpha=0.6)",
             "axes[1, 0].set_title('Scale-Location'); axes[1, 0].set_xlabel('fitted')",
             "axes[1, 0].set_ylabel(r'$\\sqrt{|standardized\\ resid|}$')",
             "",
             "# Leverage: diag of the hat matrix H = X(X'X)^{-1} X'",
             "X_aug = np.column_stack([np.ones(len(X)), X.to_numpy()])",
             "H_diag = np.einsum('ij,ji->i', X_aug @ np.linalg.inv(X_aug.T @ X_aug), X_aug.T)",
             "axes[1, 1].scatter(H_diag, std_resid, s=8, alpha=0.6)",
             "axes[1, 1].axhline(0, color='C3')",
             "axes[1, 1].set_title('Residuals vs Leverage')",
             "axes[1, 1].set_xlabel('leverage'); axes[1, 1].set_ylabel('std residual')",
             "plt.tight_layout(); plt.show()"),
        md("**Cook's distance** roughly combines leverage and residual size. Any",
           "point in the upper-right of the leverage plot deserves a look."),
        md("## 3. Qualitative predictors and interactions"),
        md("### Carseats: one-hot the categorical predictors"),
        code("print(carseats.dtypes)",
             "print(carseats[['ShelveLoc', 'Urban', 'US']].head())"),
        code("df = pd.get_dummies(carseats, columns=['ShelveLoc', 'Urban', 'US'],",
             "                    drop_first=True, dtype=float)",
             "X = df.drop(columns=['Sales'])",
             "y = df['Sales']",
             "m = LinearRegression().fit(X, y)",
             "print(pd.Series(m.coef_, index=X.columns).round(3).to_string())",
             "print(f'R^2 = {m.score(X, y):.4f}')"),
        md("### Add an interaction: Price × Urban"),
        code("df['Price_x_Urban'] = df['Price'] * df['Urban_Yes']",
             "X2 = df.drop(columns=['Sales'])",
             "m2 = LinearRegression().fit(X2, y)",
             "print('coef on Price:           ', m2.coef_[X2.columns.get_loc('Price')].round(4))",
             "print('coef on Price_x_Urban:   ', m2.coef_[X2.columns.get_loc('Price_x_Urban')].round(4))",
             "print(f'R^2 with interaction:    {m2.score(X2, y):.4f}')"),
        md("### Recap",
           "- Multiple regression in matrix form: $\\hat\\beta = (X^\\top X)^{-1} X^\\top y$.",
           "- Always check VIF — collinearity inflates standard errors and flips signs.",
           "- The 2×2 diagnostic panel is your first reflex when a model 'looks fine'.",
           "- One-hot encoding turns categoricals into numeric. Interactions are just",
           "  products of two predictors."),
    ]


def course2_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Load `penguins`, drop NaN, one-hot `species` and `sex`,",
           "and fit `body_mass_g ~ all other numeric + dummies`. Print R²."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "from sklearn.linear_model import LinearRegression",
             "# your code here"),
    ]


def course2_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "from sklearn.linear_model import LinearRegression",
             "df = load_dataset('penguins').dropna()",
             "df = pd.get_dummies(df, columns=['species', 'sex', 'island'], drop_first=True, dtype=float)",
             "X = df.drop(columns=['body_mass_g'])",
             "y = df['body_mass_g']",
             "m = LinearRegression().fit(X, y)",
             "print(f'R^2 = {m.score(X, y):.4f}')"),
    ]


def course2_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Compute VIF for the numeric predictors (`bill_length_mm`,",
             "`bill_depth_mm`, `flipper_length_mm`). Any of them above 5?"),
        code("# your code here"),
    ]


def course2_ex2_solution() -> list[dict]:
    return [
        code("numeric = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm']",
             "Xn = df[numeric]",
             "for col in numeric:",
             "    others = Xn.drop(columns=[col])",
             "    r2 = LinearRegression().fit(others, Xn[col]).score(others, Xn[col])",
             "    print(f'{col:22s}  VIF = {1/(1-r2):.2f}')"),
    ]


def course2_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Add an interaction `flipper_length_mm × species_Chinstrap`",
           "to the model. Does R² improve?"),
        code("# your code here"),
    ]


def course2_ex3_solution() -> list[dict]:
    return [
        code("df['flipper_x_chinstrap'] = df['flipper_length_mm'] * df['species_Chinstrap']",
             "X2 = df.drop(columns=['body_mass_g'])",
             "m2 = LinearRegression().fit(X2, df['body_mass_g'])",
             "print(f'R^2 with interaction = {m2.score(X2, df[\"body_mass_g\"]):.4f}')"),
    ]


# ============================================================================
# COURSE 3 — FEATURE ENGINEERING (ISLP Ch 3.3 + Ch 7)
# ============================================================================

def course3_lecture() -> list[dict]:
    return [
        md("# Course 2 — Feature Engineering",
           "",
           "Scaling, polynomial expansions, encoding, interactions, and the",
           "`Pipeline` pattern that holds it all together.",
           "",
           "**Sections**",
           "1. Scaling, skew, pipelines (0:00–0:30)",
           "2. Polynomial features and the bias-variance picture (0:30–1:00)",
           "3. Categorical encoding and interactions (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.preprocessing import StandardScaler, PolynomialFeatures, OneHotEncoder, OrdinalEncoder",
             "from sklearn.compose import ColumnTransformer",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.metrics import r2_score, mean_squared_error",
             "rng = np.random.default_rng(0)",
             "auto = load_dataset('auto')",
             "tips = load_dataset('tips')",
             "print(auto.shape, tips.shape)"),
        md("## 1. Scaling, skew, pipelines"),
        md("### Why scale at all?"),
        code("print('weight: min={:.0f}  max={:.0f}'.format(auto['weight'].min(), auto['weight'].max()))",
             "print('accel : min={:.0f}  max={:.0f}'.format(auto['acceleration'].min(), auto['acceleration'].max()))"),
        md("Linear regression doesn't care, but the moment you add regularization",
           "(Ridge, Lasso in Course 4) or anything distance-based (KNN, SVM next",
           "week), the column with the bigger numbers eats the model. Standardize."),
        code("scaler = StandardScaler()",
             "Z = scaler.fit_transform(auto[['weight', 'acceleration']])",
             "print('after scaling mean/std:', Z.mean(axis=0).round(2), Z.std(axis=0).round(2))"),
        md("### Skew and `log1p`"),
        code("fig, axes = plt.subplots(1, 2, figsize=(9, 3))",
             "axes[0].hist(auto['horsepower'], bins=30); axes[0].set_title('horsepower (raw)')",
             "axes[1].hist(np.log1p(auto['horsepower']), bins=30); axes[1].set_title('log1p(horsepower)')",
             "plt.show()"),
        md("### Pipeline: scaler + linear model in one object"),
        code("pipe = Pipeline([('scale', StandardScaler()), ('lr', LinearRegression())])",
             "X = auto[['weight', 'acceleration']]",
             "y = auto['mpg']",
             "pipe.fit(X, y)",
             "print(f'R^2 = {pipe.score(X, y):.4f}')"),
        md("## 2. Polynomial features"),
        md("### Underfit, fit, overfit — the same data, four degrees"),
        code("x = auto[['horsepower']].to_numpy()",
             "y = auto['mpg'].to_numpy()",
             "order = np.argsort(x.ravel())",
             "xs = x.ravel()[order]; ys = y[order]",
             "",
             "fig, ax = plt.subplots(figsize=(7, 4.5))",
             "ax.scatter(xs, ys, s=10, alpha=0.4, color='gray')",
             "x_grid = np.linspace(xs.min(), xs.max(), 200).reshape(-1, 1)",
             "for d, color in zip([1, 2, 5, 15], ['C0', 'C1', 'C2', 'C3']):",
             "    poly = PolynomialFeatures(degree=d, include_bias=False)",
             "    pipe = Pipeline([('p', poly), ('lr', LinearRegression())])",
             "    pipe.fit(x, y)",
             "    ax.plot(x_grid, pipe.predict(x_grid), label=f'd = {d}', color=color)",
             "ax.set_xlabel('horsepower'); ax.set_ylabel('mpg'); ax.legend()",
             "ax.set_title('Polynomial fits: d=1 underfit, d=15 overfit'); plt.show()"),
        md("d = 1 is too straight, d = 15 starts wagging at the edges. Course 3",
           "will give us a principled way to pick d via cross-validation."),
        md("## 3. Categorical encoding and interactions"),
        md("### One-hot vs ordinal"),
        code("oh = OneHotEncoder(sparse_output=False, drop='first')",
             "encoded = oh.fit_transform(tips[['day', 'time']])",
             "print('OneHot columns:', oh.get_feature_names_out().tolist())",
             "print(encoded[:3])"),
        code("# Ordinal encoding is appropriate only if categories have an order.",
             "# 'size' (party size) is a count, but pretend day-of-week is ordered.",
             "ord_enc = OrdinalEncoder(categories=[['Thur', 'Fri', 'Sat', 'Sun']])",
             "print(ord_enc.fit_transform(tips[['day']])[:5].ravel())"),
        md("### Interaction features"),
        code("X = pd.get_dummies(tips[['day', 'time', 'sex']], drop_first=True, dtype=float)",
             "X['total_bill'] = tips['total_bill']",
             "X['size'] = tips['size']",
             "poly = PolynomialFeatures(interaction_only=True, include_bias=False)",
             "X_int = poly.fit_transform(X)",
             "print(f'before: {X.shape[1]} cols, after pairwise interactions: {X_int.shape[1]}')"),
        md("### ColumnTransformer — different recipes for different columns"),
        code("num = ['total_bill', 'size']",
             "cat = ['day', 'time', 'sex', 'smoker']",
             "preproc = ColumnTransformer([",
             "    ('num', StandardScaler(), num),",
             "    ('cat', OneHotEncoder(drop='first'), cat),",
             "])",
             "pipe = Pipeline([('prep', preproc), ('lr', LinearRegression())])",
             "pipe.fit(tips[num + cat], tips['tip'])",
             "print(f'R^2 (tip ~ everything) = {pipe.score(tips[num + cat], tips[\"tip\"]):.4f}')"),
        md("### Recap",
           "- Scale before regularizing or computing distances.",
           "- Polynomial features let a linear model fit curves — but degree must be",
           "  chosen with care.",
           "- Pipelines keep preprocessing + model in lockstep and survive train/test splits.",
           "- ColumnTransformer routes numeric and categorical columns through",
           "  different transforms in one expression."),
    ]


def course3_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Build a `Pipeline` for `tips`: scale numeric columns",
           "(`total_bill`, `size`), one-hot encode `day` and `time`, fit",
           "`LinearRegression` to predict `tip`. Report R²."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.compose import ColumnTransformer",
             "from sklearn.preprocessing import StandardScaler, OneHotEncoder",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.linear_model import LinearRegression",
             "import pandas as pd",
             "# your code here"),
    ]


def course3_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.compose import ColumnTransformer",
             "from sklearn.preprocessing import StandardScaler, OneHotEncoder",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.linear_model import LinearRegression",
             "import pandas as pd",
             "tips = load_dataset('tips')",
             "pre = ColumnTransformer([",
             "    ('num', StandardScaler(), ['total_bill', 'size']),",
             "    ('cat', OneHotEncoder(drop='first'), ['day', 'time']),",
             "])",
             "pipe = Pipeline([('pre', pre), ('lr', LinearRegression())])",
             "pipe.fit(tips[['total_bill', 'size', 'day', 'time']], tips['tip'])",
             "print(f'R^2 = {pipe.score(tips[[\"total_bill\",\"size\",\"day\",\"time\"]], tips[\"tip\"]):.4f}')"),
    ]


def course3_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Add an interaction `day × time` to the design. Does R²",
           "go up? (Hint: build the dummies first, then multiply.)"),
        code("# your code here"),
    ]


def course3_ex2_solution() -> list[dict]:
    return [
        code("import pandas as pd",
             "X = pd.get_dummies(tips[['day', 'time']], drop_first=True, dtype=float)",
             "for c1 in [c for c in X.columns if c.startswith('day')]:",
             "    for c2 in [c for c in X.columns if c.startswith('time')]:",
             "        X[f'{c1}_x_{c2}'] = X[c1] * X[c2]",
             "X['total_bill'] = tips['total_bill']; X['size'] = tips['size']",
             "m = LinearRegression().fit(X, tips['tip'])",
             "print(f'R^2 with interactions = {m.score(X, tips[\"tip\"]):.4f}')"),
    ]


def course3_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Compare held-out R² before and after the interaction.",
           "Use a fixed `train_test_split(random_state=0, test_size=0.3)`."),
        code("# your code here"),
    ]


def course3_ex3_solution() -> list[dict]:
    return [
        code("from sklearn.model_selection import train_test_split",
             "# baseline: no interactions",
             "X0 = pd.get_dummies(tips[['day', 'time']], drop_first=True, dtype=float)",
             "X0['total_bill'] = tips['total_bill']; X0['size'] = tips['size']",
             "# with interactions",
             "X1 = X0.copy()",
             "for c1 in [c for c in X0.columns if c.startswith('day')]:",
             "    for c2 in [c for c in X0.columns if c.startswith('time')]:",
             "        X1[f'{c1}_x_{c2}'] = X0[c1] * X0[c2]",
             "y = tips['tip']",
             "X0tr, X0te, ytr, yte = train_test_split(X0, y, test_size=0.3, random_state=0)",
             "X1tr, X1te, _, _ = train_test_split(X1, y, test_size=0.3, random_state=0)",
             "m0 = LinearRegression().fit(X0tr, ytr); m1 = LinearRegression().fit(X1tr, ytr)",
             "print(f'baseline      held-out R^2 = {m0.score(X0te, yte):.4f}')",
             "print(f'+interactions held-out R^2 = {m1.score(X1te, yte):.4f}')"),
    ]


# ============================================================================
# COURSE 4 — CROSS-VALIDATION (ISLP Ch 5)
# ============================================================================

def course4_lecture() -> list[dict]:
    return [
        md("# Course 3 — Cross-Validation",
           "",
           "One train/test split is noisy. K-fold cross-validation is how you",
           "stop fooling yourself when tuning a hyperparameter.",
           "",
           "**Sections**",
           "1. The validation-set trap (0:00–0:30)",
           "2. LOOCV and K-fold (0:30–1:00)",
           "3. The bootstrap (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.preprocessing import PolynomialFeatures",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import train_test_split, cross_val_score, KFold, LeaveOneOut",
             "from sklearn.metrics import mean_squared_error",
             "rng = np.random.default_rng(0)",
             "auto = load_dataset('auto')",
             "x = auto[['horsepower']].to_numpy()",
             "y = auto['mpg'].to_numpy()"),
        md("## 1. The validation-set trap"),
        md("### Pick the polynomial degree with one split — repeat ten times"),
        code("degrees = range(1, 11)",
             "test_mse_runs = np.empty((10, len(degrees)))",
             "for r, seed in enumerate(range(10)):",
             "    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.5, random_state=seed)",
             "    for j, d in enumerate(degrees):",
             "        pipe = Pipeline([('p', PolynomialFeatures(d, include_bias=False)),",
             "                         ('lr', LinearRegression())])",
             "        pipe.fit(xtr, ytr)",
             "        test_mse_runs[r, j] = mean_squared_error(yte, pipe.predict(xte))",
             "",
             "fig, ax = plt.subplots(figsize=(7, 4))",
             "for r in range(10):",
             "    ax.plot(degrees, test_mse_runs[r], color='gray', linewidth=1, alpha=0.7)",
             "ax.set_xlabel('polynomial degree'); ax.set_ylabel('held-out MSE')",
             "ax.set_title('10 different validation splits → 10 different \"best\" degrees')",
             "plt.show()"),
        md("Each gray line is one random split. The minimum jumps around — that is",
           "noise, not signal. We need to average over splits."),
        md("## 2. LOOCV and K-fold"),
        md("### K-fold via `cross_val_score`"),
        code("cv_mse = []",
             "for d in degrees:",
             "    pipe = Pipeline([('p', PolynomialFeatures(d, include_bias=False)),",
             "                     ('lr', LinearRegression())])",
             "    scores = cross_val_score(pipe, x, y, cv=KFold(n_splits=10, shuffle=True, random_state=0),",
             "                              scoring='neg_mean_squared_error')",
             "    cv_mse.append(-scores.mean())",
             "",
             "fig, ax = plt.subplots(figsize=(7, 4))",
             "ax.plot(list(degrees), cv_mse, marker='o')",
             "best = int(np.argmin(cv_mse)) + 1",
             "ax.axvline(best, color='C3', linestyle='--', label=f'best d = {best}')",
             "ax.set_xlabel('degree'); ax.set_ylabel('10-fold CV MSE'); ax.legend()",
             "ax.set_title('ISLP Fig 5.4 style: CV picks a stable winner'); plt.show()"),
        md("### LOOCV — k equals n"),
        code("# Use degree 2 to make it cheap (n = 392 fits).",
             "pipe = Pipeline([('p', PolynomialFeatures(2, include_bias=False)),",
             "                 ('lr', LinearRegression())])",
             "loo_scores = cross_val_score(pipe, x, y, cv=LeaveOneOut(),",
             "                              scoring='neg_mean_squared_error')",
             "print(f'LOOCV MSE (d=2) = {-loo_scores.mean():.4f}')"),
        md("## 3. The bootstrap"),
        md("### Estimate SE of a regression coefficient by resampling"),
        code("n = len(x)",
             "B = 1000",
             "slopes = np.empty(B)",
             "for k in range(B):",
             "    idx = rng.choice(n, n, replace=True)",
             "    m = LinearRegression().fit(x[idx], y[idx])",
             "    slopes[k] = m.coef_[0]",
             "print(f'bootstrap mean slope = {slopes.mean():.4f}')",
             "print(f'bootstrap SE        = {slopes.std(ddof=1):.4f}')",
             "lo, hi = np.quantile(slopes, [0.025, 0.975])",
             "print(f'95% CI              = [{lo:.4f}, {hi:.4f}]')"),
        code("fig, ax = plt.subplots(figsize=(6, 3))",
             "ax.hist(slopes, bins=40, alpha=0.7); ax.set_xlabel('bootstrapped slope')",
             "ax.set_title('1000 resamples — sampling distribution of the slope'); plt.show()"),
        md("### Preview: stratified folds for classification"),
        md("Next week, when `y` is a class label, K-fold can accidentally put all",
           "of one class in one fold. `StratifiedKFold` preserves the class",
           "proportions in every fold. Same `cross_val_score` API."),
        md("### Recap",
           "- One split is noise; K-fold averages out the noise.",
           "- LOOCV is just K-fold with K = n. Expensive, low bias, high variance.",
           "- The bootstrap gives a CI for any statistic without distributional",
           "  assumptions — just resample the data with replacement."),
    ]


def course4_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** On `iris` *as regression* (predict `petal_length` from",
           "`sepal_length`, `sepal_width`, `petal_width`), compute the 5-fold CV",
           "MSE for plain linear regression."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.model_selection import cross_val_score, KFold",
             "# your code here"),
    ]


def course4_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.model_selection import cross_val_score, KFold",
             "iris = load_dataset('iris')",
             "X = iris[['sepal_length', 'sepal_width', 'petal_width']]",
             "y = iris['petal_length']",
             "scores = cross_val_score(LinearRegression(), X, y,",
             "                          cv=KFold(5, shuffle=True, random_state=0),",
             "                          scoring='neg_mean_squared_error')",
             "print(f'5-fold CV MSE = {-scores.mean():.4f} ± {scores.std():.4f}')"),
    ]


def course4_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Bootstrap a 95% CI for the coefficient on `petal_width` in",
           "that model. Use 1000 resamples."),
        code("# your code here"),
    ]


def course4_ex2_solution() -> list[dict]:
    return [
        code("import numpy as np",
             "rng = np.random.default_rng(0)",
             "x = X.to_numpy(); yy = y.to_numpy(); n = len(x)",
             "j = list(X.columns).index('petal_width')",
             "coefs = np.empty(1000)",
             "for k in range(1000):",
             "    idx = rng.choice(n, n, replace=True)",
             "    coefs[k] = LinearRegression().fit(x[idx], yy[idx]).coef_[j]",
             "lo, hi = np.quantile(coefs, [0.025, 0.975])",
             "print(f'95% CI on petal_width coef: [{lo:.3f}, {hi:.3f}]')"),
    ]


def course4_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** *Gotcha.* Tune polynomial degree with CV on the *whole*",
           "dataset, then report training-set R² for the chosen model. Why is that",
           "training-set number misleading? (Hint: degree was chosen using these",
           "rows.)"),
        code("# your code here"),
    ]


def course4_ex3_solution() -> list[dict]:
    return [
        code("from sklearn.preprocessing import PolynomialFeatures",
             "from sklearn.pipeline import Pipeline",
             "best_d, best_mse = None, float('inf')",
             "for d in range(1, 6):",
             "    pipe = Pipeline([('p', PolynomialFeatures(d, include_bias=False)),",
             "                     ('lr', LinearRegression())])",
             "    s = -cross_val_score(pipe, X, y, cv=5, scoring='neg_mean_squared_error').mean()",
             "    if s < best_mse:",
             "        best_d, best_mse = d, s",
             "final = Pipeline([('p', PolynomialFeatures(best_d, include_bias=False)),",
             "                  ('lr', LinearRegression())]).fit(X, y)",
             "print(f'CV picked d = {best_d}; training R^2 = {final.score(X, y):.4f}')",
             "print('This R^2 is on data the model already saw — inflated. For an honest')",
             "print('estimate, use NESTED CV: outer fold for evaluation, inner fold for tuning.')"),
    ]


# ============================================================================
# COURSE 5 — FEATURE SELECTION I (subset & stepwise, ISLP Ch 6.1)
# ============================================================================

def course5_lecture() -> list[dict]:
    return [
        md("# Course 4 — Feature Selection",
           "",
           "Part 1: best-subset selection, forward stepwise, and model-size criteria.",
           "Part 2: Ridge, Lasso, and Elastic Net shrinkage.",
           "",
           "**Part 1 sections**",
           "1. The combinatorial cost of best-subset (0:00–0:30)",
           "2. Forward stepwise from scratch (0:30–1:00)",
           "3. AIC, BIC, Cp, adjusted R² (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from itertools import combinations",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.model_selection import cross_val_score, KFold",
             "from sklearn.metrics import mean_squared_error",
             "",
             "hitters = load_dataset('hitters').dropna(subset=['Salary']).reset_index(drop=True)",
             "hitters = pd.get_dummies(hitters, columns=['League', 'Division', 'NewLeague'],",
             "                          drop_first=True, dtype=float)",
             "y = hitters['Salary'].to_numpy()",
             "X = hitters.drop(columns=['Salary'])",
             "print(X.shape, X.columns.tolist()[:6], '...')"),
        md("## 1. Best-subset is exponential"),
        md("With p = 19 predictors, $2^{19} = 524{,}288$ subsets. We will not enumerate",
           "all of them; we will enumerate a few to see the shape of the problem."),
        code("# Best-subset on the first 5 predictors only -> 2^5 - 1 = 31 subsets",
             "small = X.columns[:5].tolist()",
             "best_by_size = {}",
             "for k in range(1, len(small) + 1):",
             "    best_rss = float('inf'); best_combo = None",
             "    for combo in combinations(small, k):",
             "        Xs = X[list(combo)].to_numpy()",
             "        m = LinearRegression().fit(Xs, y)",
             "        rss = ((y - m.predict(Xs)) ** 2).sum()",
             "        if rss < best_rss:",
             "            best_rss, best_combo = rss, combo",
             "    best_by_size[k] = (best_combo, best_rss)",
             "    print(f'k={k}: RSS={best_rss:.0f}  cols={best_combo}')"),
        md("RSS always drops as we add predictors — that's why we *can't* pick a",
           "model size by raw RSS. We need a criterion that penalizes size."),
        md("## 2. Forward stepwise from scratch"),
        code("def forward_stepwise(X: pd.DataFrame, y: np.ndarray, n_folds: int = 5) -> list[tuple[str, float]]:",
             "    remaining = list(X.columns); chosen: list[str] = []; trace = []",
             "    cv = KFold(n_folds, shuffle=True, random_state=0)",
             "    while remaining:",
             "        best_col, best_mse = None, float('inf')",
             "        for col in remaining:",
             "            cols = chosen + [col]",
             "            scores = cross_val_score(LinearRegression(), X[cols].to_numpy(), y,",
             "                                     cv=cv, scoring='neg_mean_squared_error')",
             "            mse = -scores.mean()",
             "            if mse < best_mse:",
             "                best_mse, best_col = mse, col",
             "        chosen.append(best_col); remaining.remove(best_col)",
             "        trace.append((best_col, best_mse))",
             "    return trace",
             "",
             "trace = forward_stepwise(X, y)",
             "for i, (col, mse) in enumerate(trace, 1):",
             "    print(f'{i:2d}. add {col:15s}  CV-MSE = {mse:.0f}')"),
        code("sizes = list(range(1, len(trace) + 1))",
             "mses = [m for _, m in trace]",
             "fig, ax = plt.subplots(figsize=(7, 4))",
             "ax.plot(sizes, mses, marker='o')",
             "best = int(np.argmin(mses)) + 1",
             "ax.axvline(best, color='C3', linestyle='--', label=f'best = {best}')",
             "ax.set_xlabel('model size'); ax.set_ylabel('5-fold CV MSE')",
             "ax.set_title('Forward stepwise on Hitters'); ax.legend(); plt.show()"),
        md("## 3. AIC, BIC, Cp, adjusted R²"),
        code("def info_criteria(X: np.ndarray, y: np.ndarray) -> dict:",
             "    n, p = X.shape",
             "    m = LinearRegression().fit(X, y)",
             "    rss = ((y - m.predict(X)) ** 2).sum()",
             "    r2 = m.score(X, y)",
             "    sigma2 = rss / (n - p - 1)",
             "    return dict(",
             "        aic = n * np.log(rss / n) + 2 * p,",
             "        bic = n * np.log(rss / n) + p * np.log(n),",
             "        cp  = (rss + 2 * p * sigma2) / n,",
             "        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1),",
             "    )",
             "",
             "rows = []",
             "chosen = []",
             "for col, _ in trace:",
             "    chosen.append(col)",
             "    ic = info_criteria(X[chosen].to_numpy(), y)",
             "    ic['size'] = len(chosen)",
             "    rows.append(ic)",
             "ic_df = pd.DataFrame(rows).set_index('size')",
             "print(ic_df.round(2).to_string())"),
        code("fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))",
             "for ax, col in zip(axes, ['aic', 'bic', 'cp', 'adj_r2']):",
             "    ax.plot(ic_df.index, ic_df[col], marker='o')",
             "    pick = ic_df[col].idxmin() if col != 'adj_r2' else ic_df[col].idxmax()",
             "    ax.axvline(pick, color='C3', linestyle='--')",
             "    ax.set_title(f'{col} (picks size {pick})')",
             "    ax.set_xlabel('model size')",
             "plt.tight_layout(); plt.show()"),
        md("### Recap",
           "- Best-subset is exponential; stepwise is greedy but cheap and usually fine.",
           "- AIC / BIC / Cp / adj-R² each penalize size differently. BIC is the most",
           "  conservative; adjusted R² is the loosest.",
           "- Pick a single criterion *before* you look at the answers."),
    ]


def course5_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Load `titanic`, drop rows with missing `fare`, one-hot",
           "`sex`, `embarked`, `class`. Implement forward stepwise to predict",
           "`fare` and plot the CV-MSE curve."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd, numpy as np",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.model_selection import cross_val_score, KFold",
             "# your code here"),
    ]


def course5_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd, numpy as np, matplotlib.pyplot as plt",
             "from sklearn.linear_model import LinearRegression",
             "from sklearn.model_selection import cross_val_score, KFold",
             "df = load_dataset('titanic').dropna(subset=['fare']).reset_index(drop=True)",
             "df = pd.get_dummies(df[['fare','pclass','sex','age','sibsp','parch','embarked','class']].fillna(df.median(numeric_only=True)),",
             "                     columns=['sex','embarked','class'], drop_first=True, dtype=float)",
             "y = df['fare'].to_numpy(); X = df.drop(columns=['fare'])",
             "cv = KFold(5, shuffle=True, random_state=0)",
             "remaining = list(X.columns); chosen = []; mses = []",
             "while remaining:",
             "    best_col, best_mse = None, float('inf')",
             "    for col in remaining:",
             "        s = -cross_val_score(LinearRegression(), X[chosen+[col]].to_numpy(), y, cv=cv,",
             "                              scoring='neg_mean_squared_error').mean()",
             "        if s < best_mse: best_mse, best_col = s, col",
             "    chosen.append(best_col); remaining.remove(best_col); mses.append(best_mse)",
             "fig, ax = plt.subplots(figsize=(6,3.5))",
             "ax.plot(range(1, len(mses)+1), mses, marker='o')",
             "ax.set_xlabel('size'); ax.set_ylabel('CV-MSE'); plt.show()",
             "print('order added:', chosen)"),
    ]


def course5_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Which model size does *BIC* pick on the titanic-fare problem?"),
        code("# your code here"),
    ]


def course5_ex2_solution() -> list[dict]:
    return [
        code("n = len(y)",
             "rows = []",
             "for k in range(1, len(chosen)+1):",
             "    Xk = X[chosen[:k]].to_numpy()",
             "    m = LinearRegression().fit(Xk, y)",
             "    rss = ((y - m.predict(Xk))**2).sum()",
             "    rows.append((k, n*np.log(rss/n) + k*np.log(n)))",
             "import pandas as pd",
             "bic_df = pd.DataFrame(rows, columns=['size', 'bic']).set_index('size')",
             "print('BIC picks size =', bic_df['bic'].idxmin())"),
    ]


def course5_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Does CV pick the same size as BIC? Print both. Which one",
           "do you trust more, and why?"),
        code("# your code here"),
    ]


def course5_ex3_solution() -> list[dict]:
    return [
        code("cv_best = mses.index(min(mses)) + 1",
             "bic_best = bic_df['bic'].idxmin()",
             "print(f'CV picks size = {cv_best}, BIC picks size = {bic_best}')",
             "print('CV is the more honest test-error estimate;')",
             "print('BIC is faster but assumes the linear model is correctly specified.')"),
    ]


# ============================================================================
# COURSE 6 — FEATURE SELECTION II (shrinkage, ISLP Ch 6.2)
# ============================================================================

def course6_lecture() -> list[dict]:
    return [
        md("---",
           "",
           "# Part 2 — Ridge, Lasso, Elastic Net",
           "",
           "Shrinkage methods: Ridge, Lasso, Elastic Net. Instead of picking",
           "predictors in or out, every coefficient is pulled toward zero — softly",
           "for Ridge, sharply for Lasso.",
           "",
           "**Part 2 sections**",
           "4. Ridge regression (1:30–2:00)",
           "5. Lasso and sparsity (2:00–2:30)",
           "6. Elastic Net and the end-to-end pipeline (2:30–3:00)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.linear_model import Ridge, Lasso, ElasticNet, LinearRegression",
             "from sklearn.preprocessing import StandardScaler, PolynomialFeatures",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import GridSearchCV, KFold",
             "",
             "hitters = load_dataset('hitters').dropna(subset=['Salary']).reset_index(drop=True)",
             "hitters = pd.get_dummies(hitters, columns=['League', 'Division', 'NewLeague'],",
             "                          drop_first=True, dtype=float)",
             "y = hitters['Salary'].to_numpy()",
             "X = hitters.drop(columns=['Salary']).to_numpy()",
             "feat_names = hitters.drop(columns=['Salary']).columns.tolist()",
             "print(X.shape)"),
        md("## 1. Ridge regression"),
        md("Ridge minimizes $\\sum (y_i - \\hat y_i)^2 + \\alpha \\sum \\beta_j^2$.",
           "The `α` knob trades training fit (α → 0) for shrinkage (α → ∞)."),
        code("alphas = np.logspace(-2, 4, 80)",
             "coef_paths = np.empty((len(alphas), len(feat_names)))",
             "scaler = StandardScaler().fit(X)",
             "Xs = scaler.transform(X)",
             "for i, a in enumerate(alphas):",
             "    coef_paths[i] = Ridge(alpha=a).fit(Xs, y).coef_",
             "",
             "fig, ax = plt.subplots(figsize=(7, 4.5))",
             "for j, name in enumerate(feat_names):",
             "    ax.plot(alphas, coef_paths[:, j], label=name)",
             "ax.set_xscale('log'); ax.set_xlabel(r'$\\alpha$'); ax.set_ylabel('coefficient')",
             "ax.set_title('Ridge coefficient paths on Hitters'); plt.show()"),
        md("### Pick α with CV"),
        code("pipe = Pipeline([('s', StandardScaler()), ('r', Ridge())])",
             "grid = GridSearchCV(pipe, {'r__alpha': np.logspace(-2, 4, 25)},",
             "                    cv=KFold(5, shuffle=True, random_state=0),",
             "                    scoring='neg_mean_squared_error', n_jobs=-1)",
             "grid.fit(X, y)",
             "print(f'best alpha = {grid.best_params_[\"r__alpha\"]:.3f}')",
             "print(f'CV MSE     = {-grid.best_score_:.0f}')"),
        md("## 2. Lasso and sparsity"),
        md("Lasso minimizes $\\sum (y_i - \\hat y_i)^2 + \\alpha \\sum |\\beta_j|$.",
           "The L1 penalty creates a *corner* at zero, so some coefficients get",
           "set exactly to zero."),
        code("alphas = np.logspace(-1, 3, 60)",
             "nz_count = []; coef_paths_l = np.empty((len(alphas), len(feat_names)))",
             "for i, a in enumerate(alphas):",
             "    m = Lasso(alpha=a, max_iter=20000).fit(Xs, y)",
             "    coef_paths_l[i] = m.coef_",
             "    nz_count.append(int((m.coef_ != 0).sum()))",
             "",
             "fig, axes = plt.subplots(1, 2, figsize=(11, 4))",
             "for j in range(len(feat_names)):",
             "    axes[0].plot(alphas, coef_paths_l[:, j])",
             "axes[0].set_xscale('log'); axes[0].set_xlabel(r'$\\alpha$')",
             "axes[0].set_ylabel('coefficient'); axes[0].set_title('Lasso paths')",
             "axes[1].plot(alphas, nz_count, marker='o')",
             "axes[1].set_xscale('log'); axes[1].set_xlabel(r'$\\alpha$')",
             "axes[1].set_ylabel('# non-zero coefficients'); axes[1].set_title('Sparsity')",
             "plt.tight_layout(); plt.show()"),
        code("pipe = Pipeline([('s', StandardScaler()), ('l', Lasso(max_iter=20000))])",
             "grid = GridSearchCV(pipe, {'l__alpha': np.logspace(-1, 3, 30)},",
             "                    cv=KFold(5, shuffle=True, random_state=0),",
             "                    scoring='neg_mean_squared_error', n_jobs=-1)",
             "grid.fit(X, y)",
             "best = grid.best_estimator_.named_steps['l']",
             "active = [n for n, c in zip(feat_names, best.coef_) if c != 0]",
             "print(f'best alpha = {grid.best_params_[\"l__alpha\"]:.3f}')",
             "print(f'survivors  = {active}')"),
        md("## 3. Elastic Net and the end-to-end pipeline"),
        md("Elastic Net mixes the L1 and L2 penalties. `l1_ratio = 1` is Lasso,",
           "`l1_ratio = 0` is Ridge. Anywhere in between gives Lasso-style sparsity",
           "with Ridge-style stability when groups of features are correlated."),
        code("pipe = Pipeline([",
             "    ('scale', StandardScaler()),",
             "    ('poly', PolynomialFeatures(2, interaction_only=True, include_bias=False)),",
             "    ('lasso', Lasso(max_iter=20000)),",
             "])",
             "grid = GridSearchCV(pipe, {'lasso__alpha': np.logspace(-1, 2, 12)},",
             "                    cv=KFold(5, shuffle=True, random_state=0),",
             "                    scoring='neg_mean_squared_error', n_jobs=-1)",
             "grid.fit(X, y)",
             "best = grid.best_estimator_.named_steps['lasso']",
             "n_active = int((best.coef_ != 0).sum())",
             "print(f'best alpha = {grid.best_params_[\"lasso__alpha\"]:.3f}')",
             "print(f'CV MSE     = {-grid.best_score_:.0f}')",
             "print(f'{n_active} non-zero coefs out of {best.coef_.size} (poly features)')"),
        md("### Recap",
           "- Ridge shrinks every coefficient toward zero — none ever reaches zero.",
           "- Lasso shrinks *and* zeros some coefficients out — it's a feature",
           "  selector and a regularizer in one.",
           "- Elastic Net is the compromise for correlated-feature situations.",
           "- Wrap preprocessing + estimator in a `Pipeline` and grid-search the",
           "  regularization strength via CV."),
    ]


def course6_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Fit a Lasso to predict `fare` on `titanic`. Standardize",
           "first. Tune `alpha` with 5-fold CV. Print the survivors and the chosen α."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd, numpy as np",
             "from sklearn.linear_model import Lasso",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import GridSearchCV, KFold",
             "# your code here"),
    ]


def course6_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd, numpy as np",
             "from sklearn.linear_model import Lasso",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import GridSearchCV, KFold",
             "df = load_dataset('titanic').dropna(subset=['fare']).reset_index(drop=True)",
             "df = pd.get_dummies(df[['fare','pclass','sex','age','sibsp','parch','embarked','class']].fillna(df.median(numeric_only=True)),",
             "                     columns=['sex','embarked','class'], drop_first=True, dtype=float)",
             "y = df['fare'].to_numpy(); X = df.drop(columns=['fare'])",
             "pipe = Pipeline([('s', StandardScaler()), ('l', Lasso(max_iter=20000))])",
             "grid = GridSearchCV(pipe, {'l__alpha': np.logspace(-2, 2, 25)},",
             "                    cv=KFold(5, shuffle=True, random_state=0),",
             "                    scoring='neg_mean_squared_error', n_jobs=-1).fit(X, y)",
             "best = grid.best_estimator_.named_steps['l']",
             "print(f'alpha = {grid.best_params_[\"l__alpha\"]:.3f}')",
             "for name, c in zip(X.columns, best.coef_):",
             "    if c != 0: print(f'  keep {name:18s} coef = {c:+.3f}')"),
    ]


def course6_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Re-run with Ridge instead. Are any coefficients exactly",
           "zero? Compare CV MSE between Ridge and Lasso."),
        code("# your code here"),
    ]


def course6_ex2_solution() -> list[dict]:
    return [
        code("from sklearn.linear_model import Ridge",
             "pipe_r = Pipeline([('s', StandardScaler()), ('r', Ridge())])",
             "grid_r = GridSearchCV(pipe_r, {'r__alpha': np.logspace(-2, 4, 25)},",
             "                       cv=KFold(5, shuffle=True, random_state=0),",
             "                       scoring='neg_mean_squared_error', n_jobs=-1).fit(X, y)",
             "ridge = grid_r.best_estimator_.named_steps['r']",
             "n_zero = int((ridge.coef_ == 0).sum())",
             "print(f'Ridge: alpha={grid_r.best_params_[\"r__alpha\"]:.2f}  CV-MSE={-grid_r.best_score_:.0f}  exact-zero coefs={n_zero}')",
             "print(f'Lasso: alpha={grid.best_params_[\"l__alpha\"]:.2f}  CV-MSE={-grid.best_score_:.0f}  exact-zero coefs={int((best.coef_==0).sum())}')"),
    ]


def course6_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Does Lasso pick the same features as forward stepwise from",
           "Part 1? List both and report the overlap size."),
        code("# your code here"),
    ]


def course6_ex3_solution() -> list[dict]:
    return [
        code("from sklearn.linear_model import LinearRegression",
             "from sklearn.model_selection import cross_val_score",
             "# forward stepwise to convergence",
             "remaining = list(X.columns); chosen = []; mses = []",
             "while remaining:",
             "    best_col, best_mse = None, float('inf')",
             "    for col in remaining:",
             "        s = -cross_val_score(LinearRegression(), X[chosen+[col]].to_numpy(), y,",
             "                              cv=5, scoring='neg_mean_squared_error').mean()",
             "        if s < best_mse: best_mse, best_col = s, col",
             "    chosen.append(best_col); remaining.remove(best_col); mses.append(best_mse)",
             "fwd = set(chosen[: mses.index(min(mses)) + 1])",
             "lasso = set(n for n, c in zip(X.columns, best.coef_) if c != 0)",
             "print(f'forward stepwise picked {len(fwd)} features: {sorted(fwd)}')",
             "print(f'lasso picked            {len(lasso)} features: {sorted(lasso)}')",
             "print(f'overlap                  {len(fwd & lasso)} features: {sorted(fwd & lasso)}')"),
    ]


# ============================================================================
# DRIVER
# ============================================================================

def combine(lecture, *exercise_pairs):
    cells = list(lecture)
    cells.append(md("---", "", "# Exercises",
                    "",
                    "Each exercise below is followed by its solution.",
                    "Try to solve the tasks yourself before revealing the next cell."))
    for i, (starter, solution) in enumerate(exercise_pairs, 1):
        cells.append(md(f"---\n\n## Exercise {i}"))
        cells.extend(starter)
        cells.append(md(f"### Exercise {i} — Solution"))
        cells.extend(solution)
    return cells


NOTEBOOKS = [
    ("course-01-linear-regression/lecture.ipynb", lambda: combine(
        course1_lecture() + course2_lecture(),
        (course1_ex1_starter(), course1_ex1_solution()),
        (course1_ex2_starter(), course1_ex2_solution()),
        (course1_ex3_starter(), course1_ex3_solution()),
        (course2_ex1_starter(), course2_ex1_solution()),
        (course2_ex2_starter(), course2_ex2_solution()),
        (course2_ex3_starter(), course2_ex3_solution()),
    )),
    ("course-02-feature-engineering/lecture.ipynb", lambda: combine(
        course3_lecture(),
        (course3_ex1_starter(), course3_ex1_solution()),
        (course3_ex2_starter(), course3_ex2_solution()),
        (course3_ex3_starter(), course3_ex3_solution()),
    )),
    ("course-03-cross-validation/lecture.ipynb", lambda: combine(
        course4_lecture(),
        (course4_ex1_starter(), course4_ex1_solution()),
        (course4_ex2_starter(), course4_ex2_solution()),
        (course4_ex3_starter(), course4_ex3_solution()),
    )),
    ("course-04-feature-selection/lecture.ipynb", lambda: combine(
        course5_lecture() + course6_lecture(),
        (course5_ex1_starter(), course5_ex1_solution()),
        (course5_ex2_starter(), course5_ex2_solution()),
        (course5_ex3_starter(), course5_ex3_solution()),
        (course6_ex1_starter(), course6_ex1_solution()),
        (course6_ex2_starter(), course6_ex2_solution()),
        (course6_ex3_starter(), course6_ex3_solution()),
    )),
]


def main() -> None:
    for rel, builder in NOTEBOOKS:
        path = WEEK3 / rel
        write_nb(path, builder())
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
