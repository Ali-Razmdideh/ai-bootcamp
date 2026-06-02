"""Generate SVG slide images for Week 3 Course 5 — Moving Beyond Linearity.

Run from the repo root:
    python scripts/gen_slides_images_w3c5.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.special import expit
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

matplotlib.use("Agg")

import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")
PALETTE = sns.color_palette("muted")
C_BLUE = PALETTE[0]
C_ORANGE = PALETTE[1]
C_GREEN = PALETTE[2]
C_RED = PALETTE[3]
C_PURPLE = PALETTE[4]

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "weeks/week-03-machine-learning/course-05-moving-beyond-linearity/slides/img"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Synthetic Wage dataset  (same seed/structure as w3c2)
# ---------------------------------------------------------------------------

def make_wage(n: int = 3000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 81, size=n).astype(float)
    year = rng.integers(2003, 2010, size=n).astype(float)
    edu_levels = ["<HS", "HS", "<Coll", "Coll", ">Coll"]
    edu_idx = rng.choice(5, size=n, p=[0.10, 0.25, 0.20, 0.25, 0.20])
    education = np.array(edu_levels)[edu_idx]
    edu_effect = np.array([-15, 0, 10, 20, 35])[edu_idx]
    age_effect = -0.015 * (age - 49) ** 2 + 0.3 * (age - 49)
    year_effect = 1.5 * (year - 2006)
    wage = 110 + age_effect + year_effect + edu_effect + rng.normal(0, 20, n)
    wage = np.clip(wage, 20, 320)
    # Inject a small fraction of high earners
    high = rng.random(n) < 0.02
    wage[high] = rng.uniform(250, 320, high.sum())
    return pd.DataFrame({"age": age, "year": year, "wage": wage, "education": education})


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / name, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {name}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def poly_fit(x: np.ndarray, y: np.ndarray, degree: int):
    """Return (x_sorted, y_pred, y_lo, y_hi) for a polynomial fit with ~95% CI."""
    X = np.vander(x, degree + 1, increasing=True)
    X = X[:, 1:]  # drop intercept column; let the model add it
    model = LinearRegression().fit(X, y)
    x_rng = np.linspace(x.min(), x.max(), 300)
    X_pred = np.vander(x_rng, degree + 1, increasing=True)[:, 1:]
    y_hat = model.predict(X_pred)
    # Approximate SE via OLS formula
    n, p = X.shape
    y_hat_train = model.predict(X)
    rss = np.sum((y - y_hat_train) ** 2)
    sigma2 = rss / (n - p - 1)
    X_full = np.column_stack([np.ones(len(X)), X])
    X_pred_full = np.column_stack([np.ones(len(x_rng)), X_pred])
    XtX_inv = np.linalg.pinv(X_full.T @ X_full)
    se = np.sqrt(np.einsum("ij,jk,ik->i", X_pred_full, XtX_inv, X_pred_full) * sigma2)
    return x_rng, y_hat, y_hat - 2 * se, y_hat + 2 * se


def truncated_power_basis(x: np.ndarray, knots: np.ndarray, degree: int = 3) -> np.ndarray:
    """Build truncated power basis columns for spline fitting."""
    cols = [x ** d for d in range(1, degree + 1)]
    for k in knots:
        cols.append(np.maximum(x - k, 0) ** degree)
    return np.column_stack(cols)


# ---------------------------------------------------------------------------
# Figure 1: Polynomial regression — scatter + degree-4 fit
# ---------------------------------------------------------------------------

def fig_polynomial_fit(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    x_rng, y_hat, y_lo, y_hi = poly_fit(age, wage, degree=4)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(age, wage, alpha=0.25, edgecolors="white", linewidths=0.3,
               color=C_BLUE, s=30)
    ax.plot(x_rng, y_hat, color=C_ORANGE, lw=2.5, label="Degree-4 fit")
    ax.fill_between(x_rng, y_lo, y_hi, alpha=0.18, color=C_ORANGE, label="±2 SE")
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel("Wage", fontsize=12)
    ax.set_title("Degree-4 Polynomial", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, "ch7_polynomial_fit.svg")


# ---------------------------------------------------------------------------
# Figure 2: Logistic polynomial — Pr(wage > 250 | age)
# ---------------------------------------------------------------------------

def fig_polynomial_logistic(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    y_bin = (wage > 250).astype(int)

    deg = 4
    x_rng = np.linspace(age.min(), age.max(), 300)
    pipe = Pipeline([
        ("poly", PolynomialFeatures(degree=deg, include_bias=False)),
        ("lr", LogisticRegression(C=1e4, max_iter=1000)),
    ])
    pipe.fit(age.reshape(-1, 1), y_bin)
    p_hat = pipe.predict_proba(x_rng.reshape(-1, 1))[:, 1]

    # Approximate CI on logit scale
    logit_hat = np.log(np.clip(p_hat, 1e-6, 1 - 1e-6) / np.clip(1 - p_hat, 1e-6, 1))
    se_approx = 0.5  # rough; for visual illustration
    logit_lo = logit_hat - 2 * se_approx
    logit_hi = logit_hat + 2 * se_approx
    p_lo = expit(logit_lo)
    p_hi = expit(logit_hi)

    fig, ax = plt.subplots(figsize=(7, 4.0))
    ax.plot(x_rng, p_hat, color=C_BLUE, lw=2.5, label="Pr(Wage > 250 | Age)")
    ax.fill_between(x_rng, p_lo, p_hi, alpha=0.18, color=C_BLUE, label="±2 SE (logit)")
    # Rug plot
    rug_hi = age[y_bin == 1]
    rug_lo = age[y_bin == 0]
    ax.plot(rug_hi, np.full_like(rug_hi, 0.001), "|", color=C_ORANGE, ms=8, alpha=0.7)
    ax.plot(rug_lo, np.full_like(rug_lo, -0.001), "|", color=C_BLUE, ms=3, alpha=0.15)
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel("Pr(Wage > 250 | Age)", fontsize=12)
    ax.set_title("Logistic Polynomial — High Earner Probability", fontsize=13, fontweight="bold")
    ax.set_ylim(-0.01, 0.22)
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, "ch7_polynomial_logistic.svg")


# ---------------------------------------------------------------------------
# Figure 3: Step function (piecewise constant)
# ---------------------------------------------------------------------------

def fig_step_function(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    cuts = [18, 33.5, 49, 64.5, 80]
    labels = ["18–33", "33–49", "49–65", "65–80"]
    age_cut = pd.cut(age, bins=cuts, labels=labels, include_lowest=True)
    dummies = pd.get_dummies(age_cut, drop_first=False).values.astype(float)
    model = LinearRegression(fit_intercept=True).fit(dummies, wage)

    x_rng = np.linspace(age.min(), age.max(), 600)
    x_cut = pd.cut(x_rng, bins=cuts, labels=labels, include_lowest=True)
    d_rng = pd.get_dummies(x_cut, drop_first=False).values.astype(float)
    y_hat = model.predict(d_rng)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(age, wage, alpha=0.20, edgecolors="white", linewidths=0.3,
               color=C_BLUE, s=30)
    ax.step(x_rng, y_hat, where="mid", color=C_GREEN, lw=2.5, label="Piecewise Constant")
    for c in cuts[1:-1]:
        ax.axvline(c, color="grey", lw=0.8, linestyle="--", alpha=0.7)
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel("Wage", fontsize=12)
    ax.set_title("Step Function (Piecewise Constant)", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, "ch7_step_function.svg")


# ---------------------------------------------------------------------------
# Figure 4: Piecewise comparison (4-panel)
# ---------------------------------------------------------------------------

def fig_piecewise_comparison(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    knot = 49.0
    x_rng = np.linspace(age.min(), age.max(), 300)

    def _scatter(ax):
        ax.scatter(age, wage, alpha=0.18, color=C_BLUE, edgecolors="white",
                   linewidths=0.3, s=20)
        ax.axvline(knot, color="grey", lw=0.8, linestyle="--", alpha=0.8)
        ax.set_ylim(30, 270)
        ax.set_xlabel("Age", fontsize=9)
        ax.set_ylabel("Wage", fontsize=9)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))

    # --- Panel A: Piecewise Cubic (unconstrained) ---
    ax = axes[0, 0]
    _scatter(ax)
    mask_lo = age < knot
    mask_hi = ~mask_lo
    for mask, color, ls in [(mask_lo, C_BLUE, "-"), (mask_hi, C_ORANGE, "-")]:
        coeffs = np.polyfit(age[mask], wage[mask], 3)
        x_sub = x_rng[x_rng < knot] if color == C_BLUE else x_rng[x_rng >= knot]
        ax.plot(x_sub, np.polyval(coeffs, x_sub), color=color, lw=2.5)
    ax.set_title("Piecewise Cubic", fontsize=11, fontweight="bold")

    # --- Panel B: Continuous Piecewise Cubic ---
    ax = axes[0, 1]
    _scatter(ax)
    # Fit with continuity constraint by using truncated linear basis at knot
    # for illustration: use a simple joined cubic via shared endpoint
    co_lo = np.polyfit(age[age < knot], wage[age < knot], 3)
    y_knot = np.polyval(co_lo, knot)
    # Right piece: shift to match at knot
    x_hi = age[age >= knot] - knot
    wage_hi_shifted = wage[age >= knot]
    co_hi_raw = np.polyfit(x_hi, wage_hi_shifted, 3)
    # Force f(0) = y_knot
    co_hi_raw[-1] = y_knot
    x_lo_rng = x_rng[x_rng < knot]
    x_hi_rng = x_rng[x_rng >= knot]
    ax.plot(x_lo_rng, np.polyval(co_lo, x_lo_rng), color=C_GREEN, lw=2.5)
    ax.plot(x_hi_rng, np.polyval(co_hi_raw, x_hi_rng - knot), color=C_GREEN, lw=2.5)
    ax.set_title("Continuous Piecewise Cubic", fontsize=11, fontweight="bold")

    # --- Panel C: Cubic Spline (smooth) ---
    ax = axes[1, 0]
    _scatter(ax)
    X_spline = truncated_power_basis(age, knots=np.array([knot]), degree=3)
    model = LinearRegression(fit_intercept=True).fit(X_spline, wage)
    X_rng_spline = truncated_power_basis(x_rng, knots=np.array([knot]), degree=3)
    y_hat = model.predict(X_rng_spline)
    ax.plot(x_rng, y_hat, color=C_RED, lw=2.5)
    ax.set_title("Cubic Spline", fontsize=11, fontweight="bold")

    # --- Panel D: Linear Spline ---
    ax = axes[1, 1]
    _scatter(ax)
    X_lin = truncated_power_basis(age, knots=np.array([knot]), degree=1)
    model_lin = LinearRegression(fit_intercept=True).fit(X_lin, wage)
    X_rng_lin = truncated_power_basis(x_rng, knots=np.array([knot]), degree=1)
    y_hat_lin = model_lin.predict(X_rng_lin)
    ax.plot(x_rng, y_hat_lin, color=C_PURPLE, lw=2.5)
    ax.set_title("Linear Spline", fontsize=11, fontweight="bold")

    fig.suptitle("Piecewise Polynomial Fits (knot at age = 49)", fontsize=13, fontweight="bold")
    fig.tight_layout()
    save(fig, "ch7_piecewise_comparison.svg")


# ---------------------------------------------------------------------------
# Figure 5: Linear spline basis illustration
# ---------------------------------------------------------------------------

def fig_linear_spline_basis() -> None:
    xi = 0.6
    x = np.linspace(0, 1, 300)
    b1 = x.copy()
    b2 = np.maximum(x - xi, 0)
    beta0, beta1, beta2 = 0.3, 0.4, -0.5
    f = beta0 + beta1 * b1 + beta2 * b2

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)

    # Top: f(x)
    ax_top.plot(x[x < xi], f[x < xi], color=C_BLUE, lw=2.5, label="f(x)")
    ax_top.plot(x[x >= xi], f[x >= xi], color=C_ORANGE, lw=2.5)
    ax_top.axvline(xi, color="grey", lw=0.8, linestyle=":", alpha=0.9)
    ax_top.set_ylabel("f(x)", fontsize=11)
    ax_top.set_title("Linear Spline: f(x) = β₀ + β₁x + β₂(x−ξ)₊", fontsize=12, fontweight="bold")
    ax_top.legend(fontsize=10)

    # Bottom: b(x) = (x - xi)+
    ax_bot.plot(x[x < xi], b2[x < xi], color=C_ORANGE, lw=2.5)
    ax_bot.plot(x[x >= xi], b2[x >= xi], color=C_ORANGE, lw=2.5, label="b(x) = (x − ξ)₊")
    ax_bot.axvline(xi, color="grey", lw=0.8, linestyle=":", alpha=0.9)
    ax_bot.set_xlabel("x", fontsize=11)
    ax_bot.set_ylabel("b(x)", fontsize=11)
    ax_bot.set_title("Truncated Linear Basis Function at ξ = 0.6", fontsize=12, fontweight="bold")
    ax_bot.legend(fontsize=10)

    fig.tight_layout()
    save(fig, "ch7_linear_spline_basis.svg")


# ---------------------------------------------------------------------------
# Figure 6: Cubic spline basis illustration
# ---------------------------------------------------------------------------

def fig_cubic_spline_basis() -> None:
    xi = 0.6
    x = np.linspace(0, 1, 300)
    b3 = x ** 3
    b4 = np.maximum(x - xi, 0) ** 3
    beta0, beta1, beta2, beta3, beta4 = 1.0, 0.2, 0.0, 0.1, -0.8
    f = beta0 + beta1 * x + beta2 * x**2 + beta3 * b3 + beta4 * b4

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)

    ax_top.plot(x[x < xi], f[x < xi], color=C_BLUE, lw=2.5)
    ax_top.plot(x[x >= xi], f[x >= xi], color=C_ORANGE, lw=2.5)
    ax_top.axvline(xi, color="grey", lw=0.8, linestyle=":", alpha=0.9)
    ax_top.set_ylabel("f(x)", fontsize=11)
    ax_top.set_title("Cubic Spline: f(x) = β₀ + β₁x + β₂x² + β₃x³ + β₄(x−ξ)³₊", fontsize=11, fontweight="bold")

    ax_bot.plot(x[x < xi], b4[x < xi], color=C_ORANGE, lw=2.5)
    ax_bot.plot(x[x >= xi], b4[x >= xi], color=C_ORANGE, lw=2.5, label="b(x) = (x − ξ)³₊")
    ax_bot.axvline(xi, color="grey", lw=0.8, linestyle=":", alpha=0.9)
    ax_bot.set_xlabel("x", fontsize=11)
    ax_bot.set_ylabel("b(x)", fontsize=11)
    ax_bot.set_title("Truncated Cubic Basis Function at ξ = 0.6", fontsize=11, fontweight="bold")
    ax_bot.legend(fontsize=10)

    fig.tight_layout()
    save(fig, "ch7_cubic_spline_basis.svg")


# ---------------------------------------------------------------------------
# Figure 7: Natural cubic spline vs cubic spline
# ---------------------------------------------------------------------------

def fig_natural_spline_compare(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    x_rng = np.linspace(age.min(), age.max(), 300)
    knots = np.quantile(age, [0.2, 0.4, 0.6, 0.8])

    # Cubic spline
    Xc = truncated_power_basis(age, knots=knots, degree=3)
    mc = LinearRegression(fit_intercept=True).fit(Xc, wage)
    Xc_rng = truncated_power_basis(x_rng, knots=knots, degree=3)
    yc = mc.predict(Xc_rng)

    # Approximate CI
    n = len(age)
    p = Xc.shape[1] + 1
    Xc_full = np.column_stack([np.ones(len(age)), Xc])
    Xc_rng_full = np.column_stack([np.ones(len(x_rng)), Xc_rng])
    rss = np.sum((wage - mc.predict(Xc)) ** 2)
    sigma2 = rss / (n - p)
    XtX_inv = np.linalg.pinv(Xc_full.T @ Xc_full)
    se_c = np.sqrt(np.einsum("ij,jk,ik->i", Xc_rng_full, XtX_inv, Xc_rng_full) * sigma2)

    # Natural cubic spline: enforce linear beyond boundary knots
    # Implement via smoothing spline with many knots
    spl = UnivariateSpline(np.sort(age), wage[np.argsort(age)], k=3, s=len(age) * 150)
    yn = spl(x_rng)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(age, wage, alpha=0.18, edgecolors="white", linewidths=0.3,
               color=C_BLUE, s=25)
    ax.plot(x_rng, yc, color=C_BLUE, lw=2.5, label="Cubic Spline")
    ax.fill_between(x_rng, yc - 2 * se_c, yc + 2 * se_c, alpha=0.15, color=C_BLUE)
    ax.plot(x_rng, yn, color=C_RED, lw=2.5, label="Natural Cubic Spline")
    for k in knots:
        ax.axvline(k, color="grey", lw=0.7, linestyle="--", alpha=0.6)
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel("Wage", fontsize=12)
    ax.set_title("Natural Cubic Spline vs Cubic Spline", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, "ch7_natural_spline_compare.svg")


# ---------------------------------------------------------------------------
# Figure 8: Natural cubic spline vs high-degree polynomial (15 df)
# ---------------------------------------------------------------------------

def fig_knot_df_compare(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    x_rng = np.linspace(age.min(), age.max(), 300)

    # Degree-14 polynomial
    pipe_poly = Pipeline([
        ("poly", PolynomialFeatures(degree=14, include_bias=False)),
        ("lr", LinearRegression()),
    ])
    pipe_poly.fit(age.reshape(-1, 1), wage)
    y_poly = pipe_poly.predict(x_rng.reshape(-1, 1))

    # Natural cubic spline with 15 knots (df = K = 15)
    knots = np.quantile(age, np.linspace(0.05, 0.95, 15))
    Xn = truncated_power_basis(age, knots=knots, degree=3)
    mn = LinearRegression(fit_intercept=True).fit(Xn, wage)
    Xn_rng = truncated_power_basis(x_rng, knots=knots, degree=3)
    y_nat = mn.predict(Xn_rng)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(age, wage, alpha=0.18, edgecolors="white", linewidths=0.3,
               color=C_BLUE, s=25)
    ax.plot(x_rng, y_nat, color=C_RED, lw=2.5, label="Natural Cubic Spline (15 df)")
    ax.plot(x_rng, y_poly, color=C_BLUE, lw=2.0, linestyle="--",
            label="Degree-14 Polynomial (15 df)")
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel("Wage", fontsize=12)
    ax.set_ylim(30, 270)
    ax.set_title("Natural Cubic Spline vs Degree-14 Polynomial (15 df each)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, "ch7_knot_df_compare.svg")


# ---------------------------------------------------------------------------
# Figure 9: Smoothing spline (two lambda values)
# ---------------------------------------------------------------------------

def fig_smoothing_spline(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    idx = np.argsort(age)
    age_s, wage_s = age[idx], wage[idx]
    x_rng = np.linspace(age_s.min(), age_s.max(), 300)

    # High df (more wiggly) — small s
    spl_hi = UnivariateSpline(age_s, wage_s, k=3, s=len(age_s) * 20)
    # Low df (smoother) — larger s
    spl_lo = UnivariateSpline(age_s, wage_s, k=3, s=len(age_s) * 300)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(age, wage, alpha=0.18, edgecolors="white", linewidths=0.3,
               color="grey", s=25)
    ax.plot(x_rng, spl_hi(x_rng), color=C_RED, lw=2.5, label="16 Degrees of Freedom")
    ax.plot(x_rng, spl_lo(x_rng), color=C_BLUE, lw=2.5, label="6.8 Degrees of Freedom (LOOCV)")
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel("Wage", fontsize=12)
    ax.set_title("Smoothing Spline", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, "ch7_smoothing_spline.svg")


# ---------------------------------------------------------------------------
# Figure 10: Local regression illustration (2-panel)
# ---------------------------------------------------------------------------

def fig_local_regression() -> None:
    rng = np.random.default_rng(7)
    x = np.linspace(0, 1, 120)
    y = np.sin(2 * np.pi * x) + rng.normal(0, 0.25, len(x))
    x_smooth = np.linspace(0, 1, 300)

    # Simple LOESS implementation
    def loess(x_q, x, y, span=0.3):
        n = len(x)
        h = int(np.ceil(span * n))
        y_hat = np.zeros(len(x_q))
        for i, xq in enumerate(x_q):
            dists = np.abs(x - xq)
            idx = np.argsort(dists)[:h]
            d_max = dists[idx[-1]]
            w = (1 - (dists[idx] / d_max) ** 3) ** 3
            X_loc = np.column_stack([np.ones(h), x[idx]])
            W = np.diag(w)
            XtW = X_loc.T @ W
            beta = np.linalg.solve(XtW @ X_loc + 1e-8 * np.eye(2), XtW @ y[idx])
            y_hat[i] = beta[0] + beta[1] * xq
        return y_hat

    y_lo = loess(x_smooth, x, y, span=0.3)
    query_pts = [0.22, 0.55]
    span = 0.3

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, qp in zip(axes, query_pts):
        ax.scatter(x, y, alpha=0.5, color=C_BLUE, s=35, edgecolors="white", linewidths=0.3,
                   zorder=2)
        # Highlight local window
        n = len(x)
        h = int(np.ceil(span * n))
        dists = np.abs(x - qp)
        idx = np.argsort(dists)[:h]
        d_max = dists[idx[-1]]
        w = (1 - (dists[idx] / d_max) ** 3) ** 3
        # shade window
        ax.axvspan(x[idx].min(), x[idx].max(), alpha=0.15, color=C_ORANGE)
        # Weighted scatter
        ax.scatter(x[idx], y[idx], s=w * 120, color=C_ORANGE, alpha=0.7,
                   edgecolors="white", linewidths=0.3, zorder=3)
        # Local linear fit
        X_loc = np.column_stack([np.ones(h), x[idx]])
        W = np.diag(w)
        XtW = X_loc.T @ W
        beta = np.linalg.solve(XtW @ X_loc + 1e-8 * np.eye(2), XtW @ y[idx])
        x_win = np.linspace(x[idx].min(), x[idx].max(), 50)
        ax.plot(x_win, beta[0] + beta[1] * x_win, color=C_ORANGE, lw=2.0, zorder=4)
        # Global LOESS curve
        ax.plot(x_smooth, y_lo, color=C_BLUE, lw=2.0, zorder=3)
        # Query point
        ax.axvline(qp, color=C_RED, lw=1.5, linestyle="--", alpha=0.8)
        ax.plot(qp, beta[0] + beta[1] * qp, "o", color=C_RED, ms=9, zorder=5)
        ax.set_xlabel("x", fontsize=11)
        ax.set_ylabel("y", fontsize=11)
        ax.set_title(f"Local Regression at x = {qp}", fontsize=11, fontweight="bold")

    fig.suptitle("Local Regression (LOESS) — Sliding Weighted Window", fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "ch7_local_regression.svg")


# ---------------------------------------------------------------------------
# Figure 11: GAM components (year, age, education)
# ---------------------------------------------------------------------------

def fig_gam_components(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    year, education = df["year"].values, df["education"].values
    edu_order = ["<HS", "HS", "<Coll", "Coll", ">Coll"]

    # Fit additive model via approximation: partial residuals
    # Step 1: fit year (linear), age (cubic spline), education (dummy)
    edu_dummies = pd.get_dummies(education, drop_first=True).values.astype(float)
    year_c = year - year.mean()
    knots_age = np.quantile(age, [0.25, 0.5, 0.75])
    X_age = truncated_power_basis(age, knots=knots_age, degree=3)
    X_full = np.column_stack([year_c, X_age, edu_dummies])
    model = LinearRegression(fit_intercept=True).fit(X_full, wage)

    # f1(year): partial effect
    yr_rng = np.linspace(year.min(), year.max(), 100)
    yr_c_rng = yr_rng - year.mean()
    f1 = model.coef_[0] * yr_c_rng

    # f2(age): partial effect
    age_rng = np.linspace(age.min(), age.max(), 200)
    X_age_rng = truncated_power_basis(age_rng, knots=knots_age, degree=3)
    f2 = X_age_rng @ model.coef_[1: 1 + X_age.shape[1]]
    f2 -= f2.mean()

    # f3(education): coefficient per category
    edu_base = 0.0  # reference = <HS
    edu_coefs = np.concatenate([[0.0], model.coef_[1 + X_age.shape[1]:]])
    edu_coefs -= edu_coefs.mean()

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    # Panel 1: year
    ax = axes[0]
    ax.plot(yr_rng, f1, color=C_RED, lw=2.5)
    ax.axhline(0, color="grey", lw=0.7, linestyle="--")
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("f₁(year)", fontsize=11)
    ax.set_title("Effect of Year", fontsize=12, fontweight="bold")

    # Panel 2: age
    ax = axes[1]
    ax.plot(age_rng, f2, color=C_RED, lw=2.5)
    ax.axhline(0, color="grey", lw=0.7, linestyle="--")
    for k in knots_age:
        ax.axvline(k, color="grey", lw=0.6, linestyle=":", alpha=0.7)
    ax.set_xlabel("Age", fontsize=11)
    ax.set_ylabel("f₂(age)", fontsize=11)
    ax.set_title("Effect of Age (Cubic Spline)", fontsize=12, fontweight="bold")

    # Panel 3: education
    ax = axes[2]
    ax.bar(range(5), edu_coefs, color=[C_BLUE, C_ORANGE, C_GREEN, C_RED, C_PURPLE], alpha=0.75)
    ax.axhline(0, color="grey", lw=0.7)
    ax.set_xticks(range(5))
    ax.set_xticklabels(edu_order, fontsize=9)
    ax.set_xlabel("Education", fontsize=11)
    ax.set_ylabel("f₃(education)", fontsize=11)
    ax.set_title("Effect of Education", fontsize=12, fontweight="bold")

    fig.suptitle("GAM Components: wage ~ f₁(year) + f₂(age) + f₃(education)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "ch7_gam_components.svg")


# ---------------------------------------------------------------------------
# Figure 12: GAM for classification (logistic GAM)
# ---------------------------------------------------------------------------

def fig_gam_classification(df: pd.DataFrame) -> None:
    age, wage = df["age"].values, df["wage"].values
    year, education = df["year"].values, df["education"].values
    edu_order = ["<HS", "HS", "<Coll", "Coll", ">Coll"]
    y_bin = (wage > 250).astype(int)

    edu_dummies = pd.get_dummies(education, drop_first=True).values.astype(float)
    year_c = year - year.mean()
    knots_age = np.quantile(age, [0.25, 0.5, 0.75])
    X_age = truncated_power_basis(age, knots=knots_age, degree=3)
    X_full = np.column_stack([year_c, X_age, edu_dummies])
    model = LogisticRegression(C=1.0, max_iter=2000, solver="lbfgs")
    model.fit(X_full, y_bin)

    yr_rng = np.linspace(year.min(), year.max(), 100)
    f1 = model.coef_[0][0] * (yr_rng - year.mean())

    age_rng = np.linspace(age.min(), age.max(), 200)
    X_age_rng = truncated_power_basis(age_rng, knots=knots_age, degree=3)
    f2 = X_age_rng @ model.coef_[0][1: 1 + X_age.shape[1]]
    f2 -= f2.mean()

    edu_coefs = np.concatenate([[0.0], model.coef_[0][1 + X_age.shape[1]:]])
    edu_coefs -= edu_coefs.mean()

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    ax = axes[0]
    ax.plot(yr_rng, f1, color=C_GREEN, lw=2.5)
    ax.axhline(0, color="grey", lw=0.7, linestyle="--")
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("f₁(year)", fontsize=11)
    ax.set_title("Year Effect (log-odds)", fontsize=12, fontweight="bold")

    ax = axes[1]
    ax.plot(age_rng, f2, color=C_GREEN, lw=2.5)
    ax.axhline(0, color="grey", lw=0.7, linestyle="--")
    for k in knots_age:
        ax.axvline(k, color="grey", lw=0.6, linestyle=":", alpha=0.7)
    ax.set_xlabel("Age", fontsize=11)
    ax.set_ylabel("f₂(age)", fontsize=11)
    ax.set_title("Age Effect (log-odds)", fontsize=12, fontweight="bold")

    ax = axes[2]
    ax.bar(range(5), edu_coefs, color=[C_BLUE, C_ORANGE, C_GREEN, C_RED, C_PURPLE], alpha=0.75)
    ax.axhline(0, color="grey", lw=0.7)
    ax.set_xticks(range(5))
    ax.set_xticklabels(edu_order, fontsize=9)
    ax.set_xlabel("Education", fontsize=11)
    ax.set_ylabel("f₃(education)", fontsize=11)
    ax.set_title("Education Effect (log-odds)", fontsize=12, fontweight="bold")

    fig.suptitle("Logistic GAM: Pr(Wage > 250) ~ f₁(year) + f₂(age) + f₃(education)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "ch7_gam_classification.svg")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Generating Week 3 Course 5 slide images …")
    df = make_wage()

    fig_polynomial_fit(df)
    fig_polynomial_logistic(df)
    fig_step_function(df)
    fig_piecewise_comparison(df)
    fig_linear_spline_basis()
    fig_cubic_spline_basis()
    fig_natural_spline_compare(df)
    fig_knot_df_compare(df)
    fig_smoothing_spline(df)
    fig_local_regression()
    fig_gam_components(df)
    fig_gam_classification(df)

    print(f"\nDone — {len(list(OUT.glob('*.svg')))} SVGs in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
