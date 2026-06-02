"""Generate SVG slide images for Week 3 · Course 3 · Resampling Methods.

Outputs 8 SVG files to:
  weeks/week-03-machine-learning/course-03-resampling-methods/slides/img/

Style follows the Week-1 convention:
  sns.set_theme(style='whitegrid', palette='muted')
  alpha=0.5-0.7, tight_layout, SVG export

Usage:
    python3 scripts/gen_slides_images_w3c3.py
"""
from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold, LeaveOneOut, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

warnings.filterwarnings("ignore")

# ── style ────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 100, "font.size": 12})

COLORS   = sns.color_palette("muted")
C_BLUE   = COLORS[0]
C_ORANGE = COLORS[1]
C_GREEN  = COLORS[2]
C_RED    = COLORS[3]

# ── output directory ─────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "weeks/week-03-machine-learning/course-03-resampling-methods/slides/img"
OUT.mkdir(parents=True, exist_ok=True)


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / name, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote img/{name}")


# ── datasets ─────────────────────────────────────────────────────────────────

def make_auto() -> pd.DataFrame:
    """Simulate Auto data consistent with ISLR degree-2 fit."""
    rng = np.random.default_rng(1)
    hp  = rng.uniform(46, 230, 392)
    mpg = 56.9 - 0.4662 * hp + 0.0012 * hp**2 + rng.normal(0, 4.0, 392)
    return pd.DataFrame({"horsepower": hp, "mpg": mpg})


def make_poly_data(seed: int = 42):
    """Synthetic data: y = 2 + 3x - x² + noise (quadratic truth)."""
    rng    = np.random.default_rng(seed)
    n_tr   = 80
    n_te   = 500
    x_tr   = rng.uniform(-3, 3, n_tr)
    x_te   = rng.uniform(-3, 3, n_te)
    f      = lambda x: 2 + 3 * x - x**2          # noqa: E731
    sigma  = 2.0
    y_tr   = f(x_tr) + rng.normal(0, sigma, n_tr)
    y_te   = f(x_te) + rng.normal(0, sigma, n_te)
    return x_tr, y_tr, x_te, y_te, sigma


# ── figure functions ─────────────────────────────────────────────────────────

def fig_bias_variance_curve() -> None:
    """Training MSE (steelblue) vs test MSE (red) + irreducible floor (grey)."""
    x_tr, y_tr, x_te, y_te, sigma = make_poly_data()
    X_tr = x_tr.reshape(-1, 1)
    X_te = x_te.reshape(-1, 1)

    degrees   = [1, 2, 3, 5, 7, 9, 12]
    mse_train = []
    mse_test  = []
    for d in degrees:
        pipe = Pipeline([
            ("poly", PolynomialFeatures(d, include_bias=False)),
            ("lr",   LinearRegression()),
        ])
        pipe.fit(X_tr, y_tr)
        mse_train.append(mean_squared_error(y_tr, pipe.predict(X_tr)))
        mse_test.append(mean_squared_error(y_te,  pipe.predict(X_te)))

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(degrees, mse_train, "o-", color=C_BLUE,   lw=2, label="Training MSE")
    ax.plot(degrees, mse_test,  "o-", color=C_RED,    lw=2, label="Test MSE")
    ax.axhline(sigma**2, color="grey", linestyle="--", lw=1.5,
               label=f"Irreducible error (σ²={sigma**2:.0f})")
    ax.set_xlabel("Model complexity (polynomial degree)")
    ax.set_ylabel("MSE")
    ax.set_xticks(degrees)
    ax.legend(frameon=True, fontsize=11)
    ax.annotate("Underfitting\n(high bias)", xy=(1, mse_test[0]),
                xytext=(1.4, mse_test[0] * 1.08),
                fontsize=9, color=C_RED, ha="left")
    ax.annotate("Overfitting\n(high variance)", xy=(degrees[-1], mse_test[-1]),
                xytext=(degrees[-2] - 0.8, mse_test[-1] * 1.05),
                fontsize=9, color=C_RED, ha="right")
    fig.tight_layout()
    save(fig, "ch5_bias_variance_curve.svg")


def fig_validation_split() -> None:
    """ISLR-style horizontal bar showing a random 50/50 train/validation split."""
    n = 20   # representative indices
    rng = np.random.default_rng(7)
    indices = np.arange(1, n + 1)
    perm = rng.permutation(n)
    train_idx = np.sort(perm[:n // 2])
    val_idx   = np.sort(perm[n // 2:])

    fig, ax = plt.subplots(figsize=(9, 2.2))
    ax.axis("off")

    bar_y, bar_h = 0.35, 0.4
    cell_w = 1.0 / n

    for i, idx in enumerate(range(n)):
        color = C_BLUE if idx in train_idx else C_ORANGE
        rect  = plt.Rectangle(
            (i * cell_w, bar_y), cell_w, bar_h,
            facecolor=color, edgecolor="white", lw=1.2, alpha=0.85,
        )
        ax.add_patch(rect)
        ax.text(
            (i + 0.5) * cell_w, bar_y + bar_h / 2,
            str(idx + 1),
            ha="center", va="center", fontsize=7.5, color="white", fontweight="bold",
        )

    ax.text(0.0, bar_y - 0.08, "Observation index →", ha="left",
            va="top", fontsize=10, color="grey", transform=ax.transAxes)

    # legend patches
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=C_BLUE,   alpha=0.85, label="Training set"),
        Patch(facecolor=C_ORANGE, alpha=0.85, label="Validation set"),
    ]
    ax.legend(handles=legend_elements, loc="lower center",
              bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False, fontsize=11)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout(pad=0.5)
    save(fig, "ch5_validation_split.svg")


def fig_auto_single_split(auto: pd.DataFrame) -> None:
    """Validation MSE vs polynomial degree — single 50/50 split on Auto data."""
    X = auto["horsepower"].to_numpy().reshape(-1, 1)
    y = auto["mpg"].to_numpy()
    n = len(y)
    rng = np.random.default_rng(0)
    perm = rng.permutation(n)
    tr, va = perm[: n // 2], perm[n // 2:]

    degrees = range(1, 11)
    mse_val = []
    for d in degrees:
        pipe = Pipeline([
            ("poly", PolynomialFeatures(d, include_bias=False)),
            ("lr",   LinearRegression()),
        ])
        pipe.fit(X[tr], y[tr])
        mse_val.append(mean_squared_error(y[va], pipe.predict(X[va])))

    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.plot(degrees, mse_val, "o-", color=C_RED, lw=2)
    ax.set_xlabel("Degree of polynomial")
    ax.set_ylabel("Validation MSE")
    ax.set_title("Single validation-set split")
    ax.set_xticks(range(1, 11))
    best = int(np.argmin(mse_val)) + 1
    ax.axvline(best, color="grey", linestyle=":", lw=1.5)
    ax.annotate(f"min at d={best}", xy=(best, min(mse_val)),
                xytext=(best + 0.5, min(mse_val) + 1.2),
                fontsize=9, color="grey",
                arrowprops=dict(arrowstyle="->", color="grey"))
    fig.tight_layout()
    save(fig, "ch5_auto_single_split.svg")


def fig_auto_multi_split(auto: pd.DataFrame) -> None:
    """10 overlapping validation-MSE curves — shows high variability."""
    X = auto["horsepower"].to_numpy().reshape(-1, 1)
    y = auto["mpg"].to_numpy()
    n = len(y)
    degrees = range(1, 11)

    fig, ax = plt.subplots(figsize=(5.5, 4))
    cmap = plt.cm.tab10
    for seed in range(10):
        rng  = np.random.default_rng(seed)
        perm = rng.permutation(n)
        tr, va = perm[: n // 2], perm[n // 2:]
        mse_val = []
        for d in degrees:
            pipe = Pipeline([
                ("poly", PolynomialFeatures(d, include_bias=False)),
                ("lr",   LinearRegression()),
            ])
            pipe.fit(X[tr], y[tr])
            mse_val.append(mean_squared_error(y[va], pipe.predict(X[va])))
        ax.plot(degrees, mse_val, "-", color=cmap(seed), alpha=0.65, lw=1.5)

    ax.set_xlabel("Degree of polynomial")
    ax.set_ylabel("Validation MSE")
    ax.set_title("10 random splits — high variability")
    ax.set_xticks(range(1, 11))
    fig.tight_layout()
    save(fig, "ch5_auto_multi_split.svg")


def fig_auto_loocv_vs_10fold(auto: pd.DataFrame) -> None:
    """Two-panel: LOOCV (left) vs 10-fold CV (10 runs, right)."""
    X = auto["horsepower"].to_numpy().reshape(-1, 1)
    y = auto["mpg"].to_numpy()
    degrees = range(1, 11)

    # LOOCV
    loocv_mse = []
    for d in degrees:
        pipe = Pipeline([
            ("poly", PolynomialFeatures(d, include_bias=False)),
            ("lr",   LinearRegression()),
        ])
        sc = -cross_val_score(
            pipe, X, y, cv=LeaveOneOut(),
            scoring="neg_mean_squared_error",
        )
        loocv_mse.append(sc.mean())

    # 10-fold CV (10 random partitions)
    cv10_curves = []
    for seed in range(10):
        kf = KFold(10, shuffle=True, random_state=seed)
        row = []
        for d in degrees:
            pipe = Pipeline([
                ("poly", PolynomialFeatures(d, include_bias=False)),
                ("lr",   LinearRegression()),
            ])
            sc = -cross_val_score(pipe, X, y, cv=kf,
                                   scoring="neg_mean_squared_error")
            row.append(sc.mean())
        cv10_curves.append(row)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)

    axes[0].plot(degrees, loocv_mse, "o-", color=C_BLUE, lw=2)
    axes[0].set_xlabel("Degree of polynomial")
    axes[0].set_ylabel("Mean Squared Error")
    axes[0].set_title("LOOCV")
    axes[0].set_xticks(range(1, 11))

    cmap = plt.cm.tab10
    for i, row in enumerate(cv10_curves):
        axes[1].plot(degrees, row, "-", color=cmap(i), alpha=0.65, lw=1.5)
    axes[1].set_xlabel("Degree of polynomial")
    axes[1].set_title("10-fold CV (10 runs)")
    axes[1].set_xticks(range(1, 11))

    fig.tight_layout()
    save(fig, "ch5_auto_loocv_vs_10fold.svg")


def fig_true_vs_estimated_mse() -> None:
    """Three-panel figure: true test MSE vs 10-fold CV estimate for three scenarios."""
    rng  = np.random.default_rng(0)

    def scenario(f_true, sigma, label, ax):
        n_tr, n_te = 80, 800
        x_tr = rng.uniform(-3, 3, n_tr)
        x_te = rng.uniform(-3, 3, n_te)
        y_tr = f_true(x_tr) + rng.normal(0, sigma, n_tr)
        y_te = f_true(x_te) + rng.normal(0, sigma, n_te)

        X_tr = x_tr.reshape(-1, 1)
        X_te = x_te.reshape(-1, 1)
        degrees = range(1, 16)

        mse_train, mse_test, mse_cv = [], [], []
        for d in degrees:
            pipe = Pipeline([
                ("poly", PolynomialFeatures(d, include_bias=False)),
                ("lr",   LinearRegression()),
            ])
            pipe.fit(X_tr, y_tr)
            mse_train.append(mean_squared_error(y_tr, pipe.predict(X_tr)))
            mse_test.append(mean_squared_error(y_te,  pipe.predict(X_te)))
            cv_sc = -cross_val_score(
                pipe, X_tr, y_tr, cv=10,
                scoring="neg_mean_squared_error",
            )
            mse_cv.append(cv_sc.mean())

        ax.plot(degrees, mse_train, "-",  color="lightgrey",  lw=1.5, label="Train MSE")
        ax.plot(degrees, mse_test,  "-",  color=C_BLUE,  lw=2,   label="True test MSE")
        ax.plot(degrees, mse_cv,    "--", color=C_ORANGE, lw=2,   label="10-fold CV est.")
        ax.axhline(sigma**2, color="grey", linestyle=":", lw=1.2)

        # mark minima
        best_test = int(np.argmin(mse_test)) + 1
        best_cv   = int(np.argmin(mse_cv))   + 1
        ax.axvline(best_test, color=C_BLUE,   linestyle=":", lw=1.2, alpha=0.7)
        ax.axvline(best_cv,   color=C_ORANGE, linestyle=":", lw=1.2, alpha=0.7)

        ax.set_xlabel("Flexibility")
        ax.set_ylabel("MSE")
        ax.set_title(label)
        ax.set_xticks([1, 5, 10, 15])

    scenarios = [
        (lambda x: 2 + 0.8 * x,           1.2, "Smooth truth (linear)"),
        (lambda x: 2 + 2 * x - 0.6 * x**2, 1.8, "Moderate truth (quadratic)"),
        (lambda x: np.sin(x) * x,          2.5, "Wiggly truth (non-linear)"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for (f, sig, lbl), ax in zip(scenarios, axes):
        scenario(f, sig, lbl, ax)

    # shared legend
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center",
               bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False, fontsize=11)
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    save(fig, "ch5_true_vs_estimated_mse.svg")


def fig_bootstrap_alpha() -> None:
    """Three-panel: true α̂ distribution | bootstrap distribution | boxplot."""
    sig2_X, sig2_Y, sig_XY = 1.0, 1.25, 0.5
    alpha_true = (sig2_Y - sig_XY) / (sig2_X + sig2_Y - 2 * sig_XY)
    cov_mat    = [[sig2_X, sig_XY], [sig_XY, sig2_Y]]
    n          = 100
    rng        = np.random.default_rng(42)

    def alpha_hat(X: np.ndarray, Y: np.ndarray) -> float:
        s2x = np.var(X, ddof=1)
        s2y = np.var(Y, ddof=1)
        sxy = np.cov(X, Y, ddof=1)[0, 1]
        return (s2y - sxy) / (s2x + s2y - 2 * sxy)

    # True distribution: 1000 datasets from population
    alphas_true = np.array([
        alpha_hat(*rng.multivariate_normal([0, 0], cov_mat, size=n).T)
        for _ in range(1000)
    ])

    # Bootstrap: 1000 resamples of one dataset
    sample      = rng.multivariate_normal([0, 0], cov_mat, size=n)
    X_one, Y_one = sample[:, 0], sample[:, 1]
    alphas_boot = np.array([
        alpha_hat(X_one[idx := rng.integers(0, n, n)], Y_one[idx])
        for _ in range(1000)
    ])

    se_true = alphas_true.std(ddof=1)
    se_boot = alphas_boot.std(ddof=1)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))

    # panel 1 — true distribution
    axes[0].hist(alphas_true, bins=30, color=C_ORANGE, edgecolor="white", alpha=0.85)
    axes[0].axvline(alpha_true, color=C_RED, lw=2, label=f"True α = {alpha_true:.2f}")
    axes[0].set_title(f"True distribution\n(SE = {se_true:.3f})")
    axes[0].set_xlabel("α̂")
    axes[0].legend(fontsize=9, frameon=False)

    # panel 2 — bootstrap distribution
    axes[1].hist(alphas_boot, bins=30, color=C_BLUE, edgecolor="white", alpha=0.85)
    axes[1].axvline(alpha_true, color=C_RED, lw=2, label=f"True α = {alpha_true:.2f}")
    axes[1].set_title(f"Bootstrap distribution\n(SE = {se_boot:.3f})")
    axes[1].set_xlabel("α̂*")
    axes[1].legend(fontsize=9, frameon=False)

    # panel 3 — side-by-side boxplots
    bp = axes[2].boxplot(
        [alphas_true, alphas_boot],
        labels=["True", "Bootstrap"],
        patch_artist=True,
        widths=0.5,
        medianprops=dict(color="white", lw=2),
    )
    bp["boxes"][0].set_facecolor(C_ORANGE)
    bp["boxes"][0].set_alpha(0.85)
    bp["boxes"][1].set_facecolor(C_BLUE)
    bp["boxes"][1].set_alpha(0.85)
    axes[2].axhline(alpha_true, color=C_RED, lw=2, linestyle="--",
                    label=f"True α = {alpha_true:.2f}")
    axes[2].set_title("Comparison")
    axes[2].set_ylabel("α̂")
    axes[2].legend(fontsize=9, frameon=False)

    fig.tight_layout()
    save(fig, "ch5_bootstrap_alpha.svg")


def fig_bootstrap_overlap() -> None:
    """Fraction of observations out-of-bag vs n — shows the ~36.8% floor."""
    ns   = [10, 20, 50, 100, 200, 500, 1000, 5000, 10000]
    fracs = [(1 - 1 / n) ** n for n in ns]

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(ns, fracs, "o-", color=C_BLUE, lw=2, zorder=3)
    ax.axhline(1 / np.e, color=C_RED, linestyle="--", lw=1.8,
               label=f"Limit = 1/e ≈ {1/np.e:.3f}")
    ax.fill_between(ns, fracs, 1 / np.e, alpha=0.12, color=C_RED)

    ax.set_xscale("log")
    ax.set_xlabel("Sample size n  (log scale)")
    ax.set_ylabel("Fraction of obs. NOT in bootstrap sample")
    ax.set_title("Bootstrap overlap: ~63% of data seen in each resample")
    ax.set_ylim(0, 0.7)
    ax.legend(fontsize=11, frameon=False)

    # annotation
    ax.annotate("~36.8% always\nout-of-bag", xy=(10000, 1 / np.e),
                xytext=(500, 0.20),
                fontsize=9, color=C_RED,
                arrowprops=dict(arrowstyle="->", color=C_RED))

    fig.tight_layout()
    save(fig, "ch5_bootstrap_overlap.svg")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Generating Week-3 Course-3 slide images …")
    auto = make_auto()

    fig_bias_variance_curve()
    fig_validation_split()
    fig_auto_single_split(auto)
    fig_auto_multi_split(auto)
    fig_auto_loocv_vs_10fold(auto)
    fig_true_vs_estimated_mse()
    fig_bootstrap_alpha()
    fig_bootstrap_overlap()

    svgs = sorted(OUT.glob("*.svg"))
    print(f"\nDone — {len(svgs)} SVGs in {OUT.relative_to(ROOT)}")
    for f in svgs:
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
