"""Generate SVG slide images for Week 3 · Course 2 · Linear Regression.

Outputs 13 SVG files to:
  weeks/week-03-machine-learning/course-02-linear-regression/slides/img/

Style follows the Week-1 convention:
  sns.set_theme(style='whitegrid', palette='muted')
  alpha=0.5-0.7, tight_layout, SVG export

Usage:
    python3 scripts/gen_slides_images_w3c2.py
"""
from __future__ import annotations

import warnings
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

warnings.filterwarnings("ignore")

# ── style ────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 100, "font.size": 12})

COLORS = sns.color_palette("muted")
C_BLUE   = COLORS[0]
C_ORANGE = COLORS[1]
C_GREEN  = COLORS[2]
C_RED    = COLORS[3]

# ── output directory ─────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "weeks/week-03-machine-learning/course-02-linear-regression/slides/img"
OUT.mkdir(parents=True, exist_ok=True)


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / name, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote img/{name}")


# ── datasets ─────────────────────────────────────────────────────────────────

def make_advertising() -> pd.DataFrame:
    """Simulate Advertising data consistent with ISLR MLR coefficients."""
    rng = np.random.default_rng(42)
    n = 200
    TV        = rng.uniform(0.7,   296.4, n)
    radio     = rng.uniform(0.0,    49.6, n)
    newspaper = rng.uniform(0.3,   114.0, n)
    sales = (2.939
             + 0.046 * TV
             + 0.189 * radio
             - 0.001 * newspaper
             + rng.normal(0, 1.69, n))
    return pd.DataFrame({"TV": TV, "radio": radio, "newspaper": newspaper, "sales": sales})


def make_auto() -> pd.DataFrame:
    """Simulate Auto data consistent with ISLR degree-2 fit."""
    rng = np.random.default_rng(1)
    hp  = rng.uniform(46, 230, 392)
    mpg = 56.9 - 0.4662 * hp + 0.0012 * hp**2 + rng.normal(0, 4.0, 392)
    return pd.DataFrame({"horsepower": hp, "mpg": mpg})


def make_credit() -> pd.DataFrame:
    """Simulate Credit dataset for student/income interaction."""
    rng = np.random.default_rng(0)
    n = 400
    income  = rng.uniform(10, 180, n)
    student = rng.choice(["No", "Yes"], n, p=[0.7, 0.3])
    balance = (0.8 * income
               + 400 * (student == "Yes").astype(float)
               + rng.normal(0, 120, n))
    balance = np.clip(balance, 0, None)
    return pd.DataFrame({"income": income, "student": student, "balance": balance})


# ── helpers ───────────────────────────────────────────────────────────────────

def fit_slr(adv: pd.DataFrame):
    x = adv["TV"].values
    y = adv["sales"].values
    x_bar, y_bar = x.mean(), y.mean()
    b1 = np.sum((x - x_bar) * (y - y_bar)) / np.sum((x - x_bar) ** 2)
    b0 = y_bar - b1 * x_bar
    y_hat = b0 + b1 * x
    return b0, b1, x, y, y_hat


# ── figure functions ──────────────────────────────────────────────────────────

def fig_tv_sales_scatter(adv: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(adv["TV"], adv["sales"], alpha=0.55, edgecolors="white",
               linewidths=0.4, color=C_BLUE, s=50)
    ax.set_xlabel("TV budget ($thousands)", fontsize=12)
    ax.set_ylabel("Sales (thousands of units)", fontsize=12)
    ax.set_title("Advertising data — TV vs Sales", fontsize=13, fontweight="bold")
    fig.tight_layout()
    save(fig, "ch3_tv_sales_scatter.svg")


def fig_tv_sales_fitted(adv: pd.DataFrame) -> None:
    b0, b1, x, y, y_hat = fit_slr(adv)
    tv_range = np.linspace(x.min(), x.max(), 300)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    # residual segments
    for xi, yi, yhi in zip(x, y, y_hat):
        ax.plot([xi, xi], [yi, yhi], color="grey", lw=0.6, alpha=0.55)
    ax.scatter(x, y, alpha=0.55, edgecolors="white", linewidths=0.4,
               color=C_BLUE, s=45, zorder=3)
    ax.plot(tv_range, b0 + b1 * tv_range, color=C_ORANGE, lw=2.5,
            label=f"ŷ = {b0:.2f} + {b1:.4f}·TV", zorder=4)
    ax.set_xlabel("TV budget ($thousands)", fontsize=12)
    ax.set_ylabel("Sales (thousands of units)", fontsize=12)
    ax.set_title("Least-squares fit — grey lines show residuals", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, "ch3_tv_sales_fitted.svg")


def fig_residuals_vs_fitted(adv: pd.DataFrame) -> None:
    b0, b1, x, y, y_hat = fit_slr(adv)
    residuals = y - y_hat

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # left: fitted line
    tv_range = np.linspace(x.min(), x.max(), 300)
    axes[0].scatter(x, y, alpha=0.5, edgecolors="white", linewidths=0.3, color=C_BLUE, s=40)
    axes[0].plot(tv_range, b0 + b1 * tv_range, color=C_ORANGE, lw=2.5)
    axes[0].set_xlabel("TV"); axes[0].set_ylabel("Sales")
    axes[0].set_title("Fitted line")

    # right: residuals vs fitted
    axes[1].scatter(y_hat, residuals, alpha=0.5, edgecolors="white", linewidths=0.3,
                    color=C_BLUE, s=40)
    axes[1].axhline(0, color=C_RED, lw=1.5, ls="--")
    axes[1].set_xlabel("Fitted values ŷ"); axes[1].set_ylabel("Residuals e = y − ŷ")
    axes[1].set_title("Residuals vs Fitted")

    fig.tight_layout()
    save(fig, "ch3_residuals_vs_fitted.svg")


def fig_ci_beta1(adv: pd.DataFrame) -> None:
    m = smf.ols("sales ~ TV", data=adv).fit()
    b1  = m.params["TV"]
    ci  = m.conf_int().loc["TV"]
    lo, hi = ci[0], ci[1]

    fig, ax = plt.subplots(figsize=(7, 2.2))
    ax.errorbar(b1, 0, xerr=[[b1 - lo], [hi - b1]], fmt="o",
                color=C_BLUE, capsize=10, ms=9, lw=2.5,
                label=f"β̂₁ = {b1:.4f}")
    ax.axvline(0, color=C_RED, ls="--", lw=1.5, label="H₀: β₁ = 0")
    ax.set_yticks([])
    ax.set_xlabel("β̂₁  (slope for TV)", fontsize=12)
    ax.set_title(f"95 % CI for TV slope: [{lo:.4f}, {hi:.4f}]  — excludes zero",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.set_xlim(min(lo * 1.5, -0.005), max(hi * 1.5, 0.07))
    fig.tight_layout()
    save(fig, "ch3_ci_beta1.svg")


def fig_t_distribution(adv: pd.DataFrame) -> None:
    m = smf.ols("sales ~ TV", data=adv).fit()
    b1 = m.params["TV"]
    se = m.bse["TV"]
    n  = len(adv)
    dof = n - 2
    t_stat = b1 / se

    t_range = np.linspace(-22, 22, 1000)
    pdf_vals = stats.t.pdf(t_range, df=dof)

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(t_range, pdf_vals, lw=2, color=C_BLUE)
    ax.fill_between(t_range, pdf_vals,
                    where=np.abs(t_range) >= abs(t_stat),
                    alpha=0.35, color=C_RED, label=f"p-value < 0.0001")
    ax.axvline( t_stat, color=C_RED, lw=2.0, label=f"t = {t_stat:.1f}")
    ax.axvline(-t_stat, color=C_RED, lw=2.0, ls="--")
    ax.set_xlabel("t", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title(f"t-distribution (df = {dof})  — H₀: β₁ = 0", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.set_xlim(-22, 22)
    fig.tight_layout()
    save(fig, "ch3_t_distribution.svg")


def fig_correlation_heatmap(adv: pd.DataFrame) -> None:
    corr = adv.corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    sns.heatmap(corr, annot=True, fmt=".3f", cmap="coolwarm", center=0,
                vmin=-1, vmax=1, ax=ax, square=True,
                annot_kws={"size": 11}, linewidths=0.5)
    ax.set_title("Advertising — Pearson correlations", fontsize=13, fontweight="bold")
    fig.tight_layout()
    save(fig, "ch3_correlation_heatmap.svg")


def fig_mlr_coefficients(adv: pd.DataFrame) -> None:
    m = smf.ols("sales ~ TV + radio + newspaper", data=adv).fit()
    coefs = m.params.drop("Intercept")
    cis   = m.conf_int().drop("Intercept")
    errors = np.array([
        coefs.values - cis[0].values,
        cis[1].values - coefs.values,
    ])
    colors = [C_BLUE, C_ORANGE, C_GREEN]

    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    bars = ax.barh(coefs.index, coefs.values, color=colors, alpha=0.8,
                   xerr=errors, capsize=6, error_kw={"lw": 2})
    ax.axvline(0, color="black", lw=1.2)
    ax.set_xlabel("Coefficient estimate", fontsize=12)
    ax.set_title("MLR coefficients with 95 % CI\n(newspaper is not significant)",
                 fontsize=12, fontweight="bold")
    for bar, coef in zip(bars, coefs.values):
        ax.text(coef + 0.002, bar.get_y() + bar.get_height() / 2,
                f"{coef:.4f}", va="center", fontsize=10)
    fig.tight_layout()
    save(fig, "ch3_mlr_coefficients.svg")


def fig_mlr_plane(adv: pd.DataFrame) -> None:
    m = smf.ols("sales ~ TV + radio", data=adv).fit()
    b = m.params

    tv_g    = np.linspace(adv["TV"].min(),    adv["TV"].max(),    40)
    radio_g = np.linspace(adv["radio"].min(), adv["radio"].max(), 40)
    TV_g, R_g = np.meshgrid(tv_g, radio_g)
    S_g = b["Intercept"] + b["TV"] * TV_g + b["radio"] * R_g

    fig = plt.figure(figsize=(8, 5))
    ax  = fig.add_subplot(111, projection="3d")
    ax.plot_surface(TV_g, R_g, S_g, alpha=0.55, cmap="Blues", linewidth=0)
    ax.scatter(adv["TV"], adv["radio"], adv["sales"],
               c=C_RED, s=12, alpha=0.45, depthshade=True)
    ax.set_xlabel("TV", fontsize=10)
    ax.set_ylabel("Radio", fontsize=10)
    ax.set_zlabel("Sales", fontsize=10)
    ax.set_title("MLR — least-squares plane\n(TV + radio → sales)", fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "ch3_mlr_plane.svg")


def fig_forward_selection(adv: pd.DataFrame) -> None:
    features = ["TV", "radio", "newspaper"]
    rows = []
    for k in range(1, len(features) + 1):
        for combo in combinations(features, k):
            formula = f"sales ~ {' + '.join(combo)}"
            m = smf.ols(formula, data=adv).fit()
            rows.append({"k": k, "predictors": list(combo), "AIC": m.aic})
    df = pd.DataFrame(rows)
    best = df.loc[df.groupby("k")["AIC"].idxmin()].sort_values("k")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(best["k"], best["AIC"], marker="o", ms=8, lw=2,
            color=C_BLUE, markerfacecolor=C_ORANGE)
    for _, row in best.iterrows():
        ax.annotate("+".join(row["predictors"]),
                    xy=(row["k"], row["AIC"]),
                    xytext=(6, 4), textcoords="offset points",
                    fontsize=9, color="dimgrey")
    ax.set_xticks([1, 2, 3])
    ax.set_xlabel("Number of predictors (k)", fontsize=12)
    ax.set_ylabel("AIC (lower is better)", fontsize=12)
    ax.set_title("Best-subset AIC by model size\n(Advertising data)", fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "ch3_forward_selection.svg")


def fig_student_lines(credit: pd.DataFrame) -> None:
    inc_range = np.linspace(credit["income"].min(), credit["income"].max(), 200)

    m_no_int   = smf.ols("balance ~ income + C(student)", data=credit).fit()
    m_with_int = smf.ols("balance ~ income * C(student)", data=credit).fit()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    for ax, model, title, suffix in zip(
        axes,
        [m_no_int, m_with_int],
        ["No interaction (parallel lines)", "With interaction (different slopes)"],
        ["_parallel", "_interact"],
    ):
        for s_val, color, label in [("Yes", C_RED, "student"), ("No", C_BLUE, "non-student")]:
            sub = credit[credit["student"] == s_val]
            ax.scatter(sub["income"], sub["balance"], alpha=0.25, s=15,
                       color=color, edgecolors="white", linewidths=0.2)
            df_pred = pd.DataFrame({"income": inc_range, "student": s_val})
            ax.plot(inc_range, model.predict(df_pred), lw=2.5, color=color, label=label)
        ax.set_xlabel("Income ($thousands)", fontsize=11)
        ax.set_ylabel("Balance ($)", fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.legend(fontsize=10)

    fig.tight_layout()

    # save each panel separately too, for individual slide use
    for ax, suffix, title in zip(
        axes,
        ["ch3_student_parallel.svg", "ch3_student_interact.svg"],
        ["No interaction (parallel lines)", "With interaction (different slopes)"],
    ):
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        model = m_no_int if "parallel" in suffix else m_with_int
        for s_val, color, label in [("Yes", C_RED, "student"), ("No", C_BLUE, "non-student")]:
            sub = credit[credit["student"] == s_val]
            ax2.scatter(sub["income"], sub["balance"], alpha=0.25, s=15,
                        color=color, edgecolors="white", linewidths=0.2)
            df_pred = pd.DataFrame({"income": inc_range, "student": s_val})
            ax2.plot(inc_range, model.predict(df_pred), lw=2.5, color=color, label=label)
        ax2.set_xlabel("Income ($thousands)", fontsize=11)
        ax2.set_ylabel("Balance ($)", fontsize=11)
        ax2.set_title(title, fontsize=12, fontweight="bold")
        ax2.legend(fontsize=10)
        fig2.tight_layout()
        save(fig2, suffix)

    plt.close(fig)


def fig_polynomial_fits(auto: pd.DataFrame) -> None:
    hp  = auto["horsepower"].values.reshape(-1, 1)
    mpg = auto["mpg"].values
    hp_range = np.linspace(hp.min(), hp.max(), 300).reshape(-1, 1)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(hp, mpg, alpha=0.35, edgecolors="white", linewidths=0.3,
               color="steelblue", s=30, label="data")

    styles = [
        (1, "degree 1 (linear)",    C_ORANGE, "-"),
        (2, "degree 2 (quadratic)", C_BLUE,   "-"),
        (5, "degree 5",             C_GREEN,  "--"),
    ]
    for deg, label, color, ls in styles:
        pipe = Pipeline([
            ("poly", PolynomialFeatures(degree=deg, include_bias=False)),
            ("lr",   LinearRegression()),
        ])
        pipe.fit(hp, mpg)
        r2 = r2_score(mpg, pipe.predict(hp))
        ax.plot(hp_range, pipe.predict(hp_range), lw=2.5, color=color, ls=ls,
                label=f"{label}  (R²={r2:.3f})")

    ax.set_xlabel("Horsepower", fontsize=12)
    ax.set_ylabel("MPG", fontsize=12)
    ax.set_title("Polynomial regression — Auto data", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    fig.tight_layout()
    save(fig, "ch3_polynomial_fits.svg")


def fig_residuals_poly(auto: pd.DataFrame) -> None:
    hp  = auto["horsepower"].values.reshape(-1, 1)
    mpg = auto["mpg"].values

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, deg, title in zip(
        axes,
        [1, 2],
        ["Linear fit residuals\n(non-random pattern → misspecified)", "Quadratic fit residuals\n(random → good fit)"],
    ):
        pipe = Pipeline([
            ("poly", PolynomialFeatures(degree=deg, include_bias=False)),
            ("lr",   LinearRegression()),
        ])
        pipe.fit(hp, mpg)
        resid = mpg - pipe.predict(hp)
        ax.scatter(pipe.predict(hp), resid, alpha=0.4, s=18,
                   edgecolors="white", linewidths=0.3, color=C_BLUE)
        ax.axhline(0, color=C_RED, lw=1.5, ls="--")
        ax.set_xlabel("Fitted values", fontsize=11)
        ax.set_ylabel("Residuals", fontsize=11)
        ax.set_title(title, fontsize=11, fontweight="bold")

    fig.tight_layout()
    save(fig, "ch3_residuals_poly.svg")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Generating Week-3 Course-2 slide images …")
    adv    = make_advertising()
    auto   = make_auto()
    credit = make_credit()

    fig_tv_sales_scatter(adv)
    fig_tv_sales_fitted(adv)
    fig_residuals_vs_fitted(adv)
    fig_ci_beta1(adv)
    fig_t_distribution(adv)
    fig_correlation_heatmap(adv)
    fig_mlr_coefficients(adv)
    fig_mlr_plane(adv)
    fig_forward_selection(adv)
    fig_student_lines(credit)      # writes ch3_student_parallel.svg + ch3_student_interact.svg
    fig_polynomial_fits(auto)
    fig_residuals_poly(auto)

    svgs = sorted(OUT.glob("*.svg"))
    print(f"\nDone — {len(svgs)} SVGs in {OUT.relative_to(ROOT)}")
    for f in svgs:
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
