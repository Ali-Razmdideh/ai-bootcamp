"""Generate every Reveal.js slide deck for Week 3 and Week 4.

Each deck is rendered from a Python content spec into a single index.html.
Re-running is idempotent. To edit a deck, change the spec below and re-run.

Usage:
    python3 scripts/build_slides.py
"""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reset.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/highlight/atom-one-light.css" />
  <link rel="stylesheet" href="../../../../shared/slides-template/theme.css" />
</head>
<body>
<div class="reveal"><div class="slides">
"""

TAIL = """
</div></div>

<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/notes/notes.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/highlight/highlight.js"></script>
<script>
  Reveal.initialize({
    hash: true, slideNumber: 'c/t', transition: 'slide',
    transitionSpeed: 'fast', backgroundTransition: 'fade',
    width: 1280, height: 760, margin: 0.06,
    plugins: [ RevealNotes, RevealHighlight ],
  });
</script>
</body>
</html>
"""


def title_section(kicker: str, title: str, subtitle: str) -> str:
    return f"""<section class="title-slide">
  <span class="kicker">{kicker}</span>
  <h1>{title}</h1>
  <p class="muted" style="font-size:1.1em;">{subtitle}</p>
</section>
"""


def roadmap(parts: list[tuple[str, str, str]], callout: str) -> str:
    cards = ""
    for time, name, desc in parts:
        cards += f'    <div class="card"><h4>{time}</h4><strong>{name}</strong>\n'
        cards += f'      <p class="muted" style="margin:0.3em 0 0;">{desc}</p></div>\n'
    return f"""<section>
  <span class="kicker">Roadmap</span>
  <h2>Where we are heading</h2>
  <div class="three-col">
{cards}  </div>
  <p class="callout" style="margin-top:1.2em;">{callout}</p>
</section>
"""


def part_header(kicker: str, title: str, subtitle: str) -> str:
    return f"""  <section class="title-slide">
    <span class="kicker">{kicker}</span>
    <h1>{title}</h1>
    <p class="muted">{subtitle}</p>
  </section>
"""


def slide(title: str, body_html: str, notes: str = "") -> str:
    notes_html = f'    <aside class="notes">{html.escape(notes)}</aside>\n' if notes else ""
    return f"""  <section>
    <h2>{title}</h2>
{body_html}
{notes_html}  </section>
"""


def code_block(code: str) -> str:
    return f'<pre><code class="language-python">{html.escape(code)}</code></pre>'


def bullets(items: list[str], fragments: bool = True) -> str:
    cls = ' class="fragment fade-up"' if fragments else ""
    return "<ul>\n" + "".join(f'  <li{cls}>{it}</li>\n' for it in items) + "</ul>"


def two_col(left: str, right: str) -> str:
    return f'<div class="two-col"><div>{left}</div><div>{right}</div></div>'


def recap(items: list[str], callout: str) -> str:
    lis = "".join(f'<li class="fragment fade-up">{it}</li>\n' for it in items)
    return f"""<section class="title-slide">
  <span class="kicker">Recap</span>
  <h2>Three things to leave with</h2>
  <ol>
{lis}  </ol>
  <p class="callout fragment fade-up">{callout}</p>
</section>
"""


def part(kicker, title, subtitle, slides_html: list[str]) -> str:
    return "<section>\n" + part_header(kicker, title, subtitle) + "\n".join(slides_html) + "\n</section>\n"


def build_deck(spec: dict) -> str:
    title = spec["title"]
    out = HEAD.format(title=html.escape(title))
    out += title_section(spec["kicker"], title, spec["subtitle"])
    out += roadmap(spec["parts_summary"], spec["callout"])
    for p in spec["parts"]:
        out += part(p["kicker"], p["title"], p["subtitle"], p["slides"])
    out += recap(spec["recap_items"], spec["recap_callout"])
    out += TAIL
    return out


# ============================================================================
# WEEK 3
# ============================================================================

WEEK3 = ROOT / "weeks" / "week-03-machine-learning"

W3C1 = {
    "title": "Linear Regression I — Simple LR",
    "kicker": "Week 3 · Course 1 · 1.5 hours",
    "subtitle": "Fit a line, read the output, infer for β",
    "parts_summary": [
        ("0:00 · 0:30", "Fitting a line", "Least squares, by hand and via sklearn."),
        ("0:30 · 1:00", "Reading the output", "coef, R², RMSE, residuals."),
        ("1:00 · 1:30", "Inference for β", "t-stat, bootstrap CI, assumptions."),
    ],
    "callout": "Every concept that appears later — loss, coefficients, R², residuals — shows up here in its cleanest form. Master simple LR and the rest of the course just adds knobs.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Fitting a line",
            "subtitle": "least squares, by hand",
            "slides": [
                slide("The cost we are minimizing",
                      '<p>Given <code>(x₁, y₁), …, (xₙ, yₙ)</code>, the line ŷ = β₀ + β₁ x that minimizes <strong>residual sum of squares</strong>:</p>'
                      '<p style="text-align:center;font-size:1.4em;">RSS(β) = Σᵢ (yᵢ − β₀ − β₁ xᵢ)²</p>'
                      '<p class="muted">Take the gradient, set to zero, two-line closed-form solution.</p>',
                      "Loss + closed-form solution. The point: every later model just changes the loss or the model class."),
                slide("Closed form — both coefficients",
                      '<p style="text-align:center;font-size:1.25em;">β̂₁ = Σᵢ (xᵢ − x̄)(yᵢ − ȳ) / Σᵢ (xᵢ − x̄)²</p>'
                      '<p style="text-align:center;font-size:1.25em;">β̂₀ = ȳ − β̂₁ x̄</p>'
                      '<p class="muted" style="margin-top:1em;">Two summations, no iteration. Compare with the iterative optimizers next month for neural nets.</p>'),
                slide("Sklearn in three lines",
                      code_block("from sklearn.linear_model import LinearRegression\n"
                                 "X = boston[['lstat']]\n"
                                 "y = boston['medv']\n"
                                 "model = LinearRegression().fit(X, y)\n"
                                 "print(model.intercept_, model.coef_)"),
                      "Live in notebook: derive by hand, then sklearn. Should match to 4 decimal places."),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Reading the output",
            "subtitle": "R², RMSE, residuals",
            "slides": [
                slide("Three numbers you always report",
                      bullets([
                          "<strong>R²</strong> — fraction of variance the model explains (0 = nothing, 1 = perfect).",
                          "<strong>RMSE</strong> — root mean squared error, <em>in the units of y</em>.",
                          "<strong>Residual plot</strong> — fitted vs (y − ŷ). Looks like noise? You are done. A pattern? The model is wrong somewhere.",
                      ])),
                slide("Residuals reveal everything",
                      '<p>If residuals show a curve → the relationship is not linear.</p>'
                      '<p>If residuals fan out → the variance is not constant (heteroscedasticity).</p>'
                      '<p>If residuals cluster by some category → there is a missing predictor.</p>'
                      '<p class="callout">A residual plot is the cheapest model-criticism tool you have. Run it every time.</p>'),
                slide("R² is not the whole story",
                      '<p class="muted">A model with R² = 0.95 can still be useless if:</p>'
                      + bullets([
                          "Its residuals show a clear U-shape (model misspecified).",
                          "Its predictions extrapolate badly outside the training range.",
                          "The signal is dominated by one feature with a known data leak.",
                      ])),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "Inference for β",
            "subtitle": "is the slope real?",
            "slides": [
                slide("Standard error and the t-statistic",
                      '<p style="text-align:center;font-size:1.2em;">t = β̂₁ / SE(β̂₁)</p>'
                      '<p>If |t| is big (typically > 2), the slope is significantly different from zero. Sklearn does not report this; statsmodels does — but in this course we prefer the bootstrap.</p>'),
                slide("The bootstrap — a CI for anything",
                      code_block("for k in range(2000):\n"
                                 "    idx = rng.choice(n, n, replace=True)\n"
                                 "    b1_boot[k] = slope(x[idx], y[idx])\n"
                                 "lo, hi = np.quantile(b1_boot, [0.025, 0.975])"),
                      "The bootstrap was Bradley Efron's gift to applied stats. No formulas, no distributional assumptions, just resample with replacement."),
                slide("Four assumptions of linear regression",
                      bullets([
                          "<strong>Linearity</strong> — residual plot has no curve.",
                          "<strong>Constant variance</strong> — no fan, no funnel.",
                          "<strong>Independence</strong> — observations not autocorrelated.",
                          "<strong>Normality of errors</strong> — Q-Q plot of residuals is straight.",
                      ])),
            ],
        },
    ],
    "recap_items": [
        "<strong>Least squares is two lines of arithmetic.</strong> The closed form, not gradient descent.",
        "<strong>R² and RMSE summarize fit; residuals find what they miss.</strong> Always plot residuals.",
        "<strong>A CI is what a coefficient is worth as a claim.</strong> Bootstrap one in three lines.",
    ],
    "recap_callout": "Next: multiple regression, collinearity, and the four diagnostic plots every modeler should read in five seconds.",
}


W3C2 = {
    "title": "Linear Regression II — Multiple LR & Diagnostics",
    "kicker": "Week 3 · Course 2 · 1.5 hours",
    "subtitle": "Many predictors, collinearity, residual plots, and categorical encoding",
    "parts_summary": [
        ("0:00 · 0:30", "Multiple LR", "matrix form, collinearity, VIF."),
        ("0:30 · 1:00", "Diagnostics", "residuals, leverage, Cook's distance."),
        ("1:00 · 1:30", "Categoricals & interactions", "one-hot, Price × Urban."),
    ],
    "callout": "Real datasets are multi-predictor and full of traps. The four diagnostic plots are your first reflex when a model 'looks fine'.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Multiple regression",
            "subtitle": "Y = Xβ + ε",
            "slides": [
                slide("The matrix form",
                      '<p style="text-align:center;font-size:1.3em;">Y = Xβ + ε,  β̂ = (XᵀX)⁻¹ Xᵀ Y</p>'
                      '<p class="muted">One predictor or one hundred — the formula is the same. The expensive bit is the matrix inverse, but n ≪ 10⁴ → microseconds.</p>'),
                slide("Collinearity flips signs",
                      '<p>If predictor j is well predicted by the others, its coefficient becomes unstable.</p>'
                      '<p style="text-align:center;font-size:1.2em;">VIF<sub>j</sub> = 1 / (1 − R²<sub>j</sub>)</p>'
                      '<p>VIF > 5–10 is a red flag. Drop one of the correlated pair, or use Ridge (Course 6) to stabilize.</p>',
                      "Run VIF in the notebook on Boston; tax, rad, nox are biggest offenders."),
                slide("Never read a coefficient in isolation",
                      bullets([
                          "Its sign depends on which other predictors are in the model.",
                          "Its size depends on the scale of the predictor.",
                          "Its significance depends on collinearity with the others.",
                      ])),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Diagnostic plots",
            "subtitle": "the 2×2 panel",
            "slides": [
                slide("The four plots",
                      bullets([
                          "<strong>Residuals vs fitted</strong> — look for a curve (model misspecified).",
                          "<strong>Q-Q plot</strong> — look for tails (heavy-tailed errors).",
                          "<strong>Scale-location</strong> — look for a fan (heteroscedasticity).",
                          "<strong>Residuals vs leverage</strong> — look for high-leverage outliers (Cook's distance).",
                      ])),
                slide("Leverage — the hat matrix",
                      '<p style="text-align:center;font-size:1.2em;">H = X(XᵀX)⁻¹Xᵀ,  hᵢ = Hᵢᵢ</p>'
                      '<p>A high <code>hᵢ</code> means observation i has unusual <em>predictor</em> values — it pulls the fit toward itself. Combined with a big residual = Cook\'s distance = trouble.</p>'),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "Categoricals & interactions",
            "subtitle": "one-hot and products",
            "slides": [
                slide("One-hot encoding",
                      code_block("df = pd.get_dummies(carseats,\n"
                                 "    columns=['ShelveLoc','Urban','US'],\n"
                                 "    drop_first=True, dtype=float)")
                      + '<p class="muted">drop_first=True avoids the dummy-variable trap (perfect collinearity with the intercept).</p>'),
                slide("Interactions are just products",
                      code_block("df['Price_x_Urban'] = df['Price'] * df['Urban_Yes']")
                      + '<p>The coefficient on the product term tells you how the effect of Price <em>changes</em> when Urban switches from No to Yes.</p>'),
            ],
        },
    ],
    "recap_items": [
        "<strong>β̂ = (XᵀX)⁻¹Xᵀy</strong>, but always check VIF first.",
        "<strong>The 2×2 diagnostic panel</strong> is the first reflex. Five seconds tell you a lot.",
        "<strong>Categoricals one-hot, interactions multiply.</strong> Drop one dummy to avoid collinearity.",
    ],
    "recap_callout": "Next: feature engineering — scaling, polynomial expansion, pipelines.",
}


W3C3 = {
    "title": "Feature Engineering",
    "kicker": "Week 3 · Course 3 · 1.5 hours",
    "subtitle": "Scaling, polynomial features, encodings, pipelines",
    "parts_summary": [
        ("0:00 · 0:30", "Scaling & pipelines", "StandardScaler, log1p, Pipeline."),
        ("0:30 · 1:00", "Polynomial features", "underfit, fit, overfit."),
        ("1:00 · 1:30", "Encoding & interactions", "OneHot, ColumnTransformer."),
    ],
    "callout": "Models do not learn from raw columns — they learn from the features you hand them. This is where applied ML lives.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Scaling & pipelines",
            "subtitle": "StandardScaler, log1p",
            "slides": [
                slide("Why scale at all?",
                      bullets([
                          "Plain LR doesn't care — but <em>regularized</em> LR does (Ridge/Lasso in Course 6).",
                          "Distance-based methods (KNN, SVM next week) crumble without scaling.",
                          "Neural nets converge faster on standardized inputs.",
                      ])),
                slide("Pipeline = scaler + estimator, one object",
                      code_block("from sklearn.pipeline import Pipeline\n"
                                 "from sklearn.preprocessing import StandardScaler\n"
                                 "from sklearn.linear_model import LinearRegression\n\n"
                                 "pipe = Pipeline([\n"
                                 "    ('scale', StandardScaler()),\n"
                                 "    ('lr', LinearRegression()),\n"
                                 "])\n"
                                 "pipe.fit(X_train, y_train)\n"
                                 "pipe.score(X_test, y_test)")
                      + '<p class="muted">Pipelines survive train/test splits — they fit the scaler on train only.</p>'),
                slide("Skew? log1p it.",
                      '<p>Many natural features (income, counts, prices) are right-skewed.</p>'
                      '<p style="text-align:center;font-size:1.2em;">log1p(x) = log(1 + x)</p>'
                      '<p class="muted">log1p handles zeros (unlike plain log). Always sanity-check with a histogram.</p>'),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Polynomial features",
            "subtitle": "underfit ↔ overfit",
            "slides": [
                slide("Polynomial features turn LR into a curve-fitter",
                      code_block("from sklearn.preprocessing import PolynomialFeatures\n"
                                 "PolynomialFeatures(degree=3).fit_transform(X)\n"
                                 "# [x] -> [1, x, x^2, x^3]")
                      + '<p class="muted">Linear in the parameters β, non-linear in x. Still linear regression!</p>'),
                slide("Bias / variance, visualized",
                      bullets([
                          "<strong>d = 1</strong> — too straight (underfit, high bias).",
                          "<strong>d = 2</strong> — captures the curve (just right).",
                          "<strong>d = 15</strong> — wagging tails (overfit, high variance).",
                      ])
                      + '<p class="callout">How do you pick d without eyeballing? Cross-validation, next course.</p>'),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "Encoding & interactions",
            "subtitle": "ColumnTransformer is your friend",
            "slides": [
                slide("Different transforms for different columns",
                      code_block("ColumnTransformer([\n"
                                 "    ('num', StandardScaler(), numeric_cols),\n"
                                 "    ('cat', OneHotEncoder(drop='first'), categorical_cols),\n"
                                 "])")),
                slide("Interactions in bulk",
                      code_block("PolynomialFeatures(interaction_only=True, include_bias=False)\n"
                                 "# adds every x_i * x_j pair")
                      + '<p class="muted">Combinatorial explosion ahead — combine with Lasso (Course 6) to keep only the useful interactions.</p>'),
            ],
        },
    ],
    "recap_items": [
        "<strong>Scale numeric features</strong> before regularizing or measuring distances.",
        "<strong>Polynomial features turn LR into a flexible curve fitter.</strong> Pick degree with care.",
        "<strong>Pipelines + ColumnTransformer</strong> keep preprocessing honest under train/test splits.",
    ],
    "recap_callout": "Next: how do you pick the degree without fooling yourself? Cross-validation.",
}


W3C4 = {
    "title": "Cross-Validation",
    "kicker": "Week 3 · Course 4 · 1.5 hours",
    "subtitle": "Stop fooling yourself about test error",
    "parts_summary": [
        ("0:00 · 0:30", "The trap", "one split → ten different best degrees."),
        ("0:30 · 1:00", "K-fold & LOOCV", "the right tool for tuning."),
        ("1:00 · 1:30", "The bootstrap", "CIs without distributional assumptions."),
    ],
    "callout": "A single train/test split is noisy. CV averages out the noise; the bootstrap gives a CI for anything.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "The validation-set trap",
            "subtitle": "one split lies",
            "slides": [
                slide("Why one split is not enough",
                      bullets([
                          "Pick polynomial degree by held-out MSE → answer depends on the split.",
                          "Ten random splits give ten different 'best' degrees.",
                          "That spread is <em>noise</em>, not signal.",
                      ])),
                slide("Live demo",
                      code_block("for seed in range(10):\n"
                                 "    Xtr, Xte, ytr, yte = train_test_split(\n"
                                 "        x, y, test_size=0.5, random_state=seed)\n"
                                 "    # …pick best degree from this single split…")),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "K-fold and LOOCV",
            "subtitle": "average over many splits",
            "slides": [
                slide("K-fold cross-validation",
                      '<p>Split into K folds. For k = 1…K, train on the other K−1 folds and score on fold k. Average the K scores.</p>'
                      + bullets([
                          "K = 5 or K = 10 is the standard. K = n is leave-one-out (LOOCV).",
                          "<code>cross_val_score(model, X, y, cv=KFold(10))</code> is one line.",
                      ])),
                slide("The CV curve",
                      '<p>Plot CV error vs the hyperparameter (polynomial degree, α, λ, k, …). Pick the minimum.</p>'
                      '<p class="muted">For Auto mpg, the CV curve picks a stable d ≈ 2.</p>',
                      "Reproduce ISLP Fig 5.4. Stable winner across folds = trustworthy choice."),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "The bootstrap",
            "subtitle": "resample with replacement",
            "slides": [
                slide("Bootstrap = sampling-distribution emulator",
                      code_block("for k in range(B):\n"
                                 "    idx = rng.choice(n, n, replace=True)\n"
                                 "    theta_boot[k] = compute_statistic(data[idx])\n"
                                 "se = theta_boot.std()\n"
                                 "lo, hi = np.quantile(theta_boot, [0.025, 0.975])")
                      + '<p class="muted">Works for any statistic — slope, median, ratio, correlation — without distributional assumptions.</p>'),
                slide("Preview: stratification for classification",
                      '<p>Next week <code>y</code> is a class label. <code>StratifiedKFold</code> keeps class proportions stable across folds.</p>'),
            ],
        },
    ],
    "recap_items": [
        "<strong>One split is noise.</strong> Always use K-fold for hyperparameter tuning.",
        "<strong>Plot the CV curve and pick the minimum.</strong> If it's flat, simpler wins.",
        "<strong>The bootstrap gives a CI for anything.</strong> Two lines of Python.",
    ],
    "recap_callout": "Next: with CV in hand, we can pick features and shrinkage strength honestly.",
}


W3C5 = {
    "title": "Feature Selection I — Subset & Stepwise",
    "kicker": "Week 3 · Course 5 · 1.5 hours",
    "subtitle": "Pick the predictors that matter",
    "parts_summary": [
        ("0:00 · 0:30", "Best subset", "2^p subsets — combinatorial."),
        ("0:30 · 1:00", "Forward stepwise", "greedy and cheap."),
        ("1:00 · 1:30", "AIC / BIC / Cp / adj-R²", "model-size criteria."),
    ],
    "callout": "Too many predictors hurt prediction. Subset selection is the classical answer; shrinkage (Course 6) is the modern one.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Best subset",
            "subtitle": "the combinatorial cost",
            "slides": [
                slide("Why best-subset is intractable",
                      bullets([
                          "p = 10 → 1024 subsets. p = 20 → 1 million.",
                          "Hitters has p = 19 → 524288 fits.",
                          "Wonderful for laptops but exponential — useless past ~30 predictors.",
                      ])),
                slide("RSS always drops with more predictors",
                      '<p>Adding a predictor can never <em>increase</em> training RSS. So we cannot pick model size by raw RSS.</p>'
                      '<p>We need a criterion that <em>penalizes</em> size: AIC, BIC, Cp, adjusted R², or — best — held-out CV error.</p>'),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Forward stepwise",
            "subtitle": "greedy but cheap",
            "slides": [
                slide("Forward stepwise algorithm",
                      bullets([
                          "Start with the empty model.",
                          "At each step, add the single predictor that most reduces CV error.",
                          "Stop when CV error stops improving (or fit all p, then pick the best size).",
                      ], fragments=False)),
                slide("From scratch in 12 lines",
                      code_block("while remaining:\n"
                                 "    best_col, best_mse = None, inf\n"
                                 "    for col in remaining:\n"
                                 "        mse = -cross_val_score(LinearRegression(),\n"
                                 "                  X[chosen+[col]], y,\n"
                                 "                  cv=5, scoring='neg_mean_squared_error').mean()\n"
                                 "        if mse < best_mse:\n"
                                 "            best_col, best_mse = col, mse\n"
                                 "    chosen.append(best_col); remaining.remove(best_col)")),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "Model-size criteria",
            "subtitle": "AIC, BIC, Cp, adj-R²",
            "slides": [
                slide("Four formulas, four answers",
                      '<p style="font-family:monospace;font-size:0.95em;">AIC = n log(RSS/n) + 2p</p>'
                      '<p style="font-family:monospace;font-size:0.95em;">BIC = n log(RSS/n) + p log n</p>'
                      '<p style="font-family:monospace;font-size:0.95em;">Cp  = (RSS + 2 p σ²)/n</p>'
                      '<p style="font-family:monospace;font-size:0.95em;">adj-R² = 1 − (1−R²)(n−1)/(n−p−1)</p>'),
                slide("Which to trust?",
                      bullets([
                          "<strong>BIC</strong> — most conservative; for large n it picks fewer predictors.",
                          "<strong>AIC / Cp</strong> — pick slightly larger models, focused on prediction.",
                          "<strong>adj-R²</strong> — loosest, easiest to fool with collinear predictors.",
                          "Pick a criterion <em>before</em> you look at the answers, and consider CV the gold standard.",
                      ])),
            ],
        },
    ],
    "recap_items": [
        "<strong>Best-subset is exponential</strong> — useless past ~30 predictors.",
        "<strong>Forward stepwise is greedy and almost always good enough.</strong>",
        "<strong>BIC ≤ Cp ≈ AIC ≤ adj-R²</strong> in how many predictors they keep. Pick first, then look.",
    ],
    "recap_callout": "Next: instead of picking features in or out, shrink them softly with Ridge and Lasso.",
}


W3C6 = {
    "title": "Feature Selection II — Ridge, Lasso, Elastic Net",
    "kicker": "Week 3 · Course 6 · 1.5 hours",
    "subtitle": "Shrink instead of select",
    "parts_summary": [
        ("0:00 · 0:30", "Ridge", "L2 penalty, smooth shrinkage."),
        ("0:30 · 1:00", "Lasso", "L1 penalty, exact zeros."),
        ("1:00 · 1:30", "Elastic Net & pipelines", "the modern default."),
    ],
    "callout": "Subset selection is discrete (in or out). Shrinkage is continuous (pulled toward zero). For p > 20, shrinkage almost always wins.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Ridge",
            "subtitle": "L2 penalty",
            "slides": [
                slide("Ridge objective",
                      '<p style="text-align:center;font-size:1.25em;">minimize Σᵢ (yᵢ − ŷᵢ)² + <span style="color:#c33;">α Σⱼ βⱼ²</span></p>'
                      + bullets([
                          "α → 0: same as OLS.",
                          "α → ∞: every β shrinks to 0.",
                          "Scale matters: <em>always</em> standardize before Ridge.",
                      ])),
                slide("Coefficient paths",
                      '<p>Plot every β<sub>j</sub> versus α (log axis). All paths shrink toward zero, none reach exactly zero.</p>'
                      '<p class="muted">Pick α with GridSearchCV over a log grid (e.g. np.logspace(-2, 4, 50)).</p>'),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Lasso",
            "subtitle": "L1 penalty, exact zeros",
            "slides": [
                slide("Lasso objective",
                      '<p style="text-align:center;font-size:1.25em;">minimize Σᵢ (yᵢ − ŷᵢ)² + <span style="color:#c33;">α Σⱼ |βⱼ|</span></p>'
                      + '<p>The L1 penalty creates a <em>corner</em> at zero — some coefficients land exactly there.</p>'),
                slide("Lasso is a feature selector",
                      bullets([
                          "Survivor coefficients form an interpretable subset.",
                          "Use when you suspect many irrelevant features.",
                          "Use when you want a sparse model for production speed.",
                      ])
                      + '<p class="callout">Comparison with forward stepwise: usually similar features. Lasso is faster and one-shot.</p>'),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "Elastic Net & pipelines",
            "subtitle": "the modern default",
            "slides": [
                slide("Elastic Net = α (l1_ratio · L1 + (1 − l1_ratio) · L2)",
                      bullets([
                          "Combines Lasso sparsity with Ridge stability.",
                          "Helps when features are correlated in groups.",
                          "l1_ratio = 1 → Lasso. l1_ratio = 0 → Ridge.",
                      ])),
                slide("End-to-end pipeline + CV",
                      code_block("Pipeline([\n"
                                 "    ('scale', StandardScaler()),\n"
                                 "    ('poly', PolynomialFeatures(2, interaction_only=True)),\n"
                                 "    ('lasso', Lasso(max_iter=20000)),\n"
                                 "])\n"
                                 "GridSearchCV(pipe, {'lasso__alpha': np.logspace(-1, 2, 12)},\n"
                                 "             cv=5, scoring='neg_mean_squared_error')")),
            ],
        },
    ],
    "recap_items": [
        "<strong>Ridge shrinks; Lasso shrinks and zeros.</strong> Always scale first.",
        "<strong>Tune α with GridSearchCV over a log grid.</strong> Coefficient paths are diagnostic.",
        "<strong>Pipeline + CV = honest selection.</strong> The whole loop in 5 lines of sklearn.",
    ],
    "recap_callout": "End of Week 3. Next week: from regression to classification.",
}


# ============================================================================
# WEEK 4
# ============================================================================

WEEK4 = ROOT / "weeks" / "week-04-classification"

W4C1 = {
    "title": "Classification + KNN",
    "kicker": "Week 4 · Course 1 · 1.5 hours",
    "subtitle": "Decision boundaries, confusion matrices, ROC",
    "parts_summary": [
        ("0:00 · 0:30", "What a classifier outputs", "labels, probs, metrics."),
        ("0:30 · 1:00", "KNN", "the no-training baseline."),
        ("1:00 · 1:30", "Class imbalance", "the majority-class trap."),
    ],
    "callout": "Before any specific classifier, internalize the interface: predict a label, plot a decision boundary, read a confusion matrix, pick the right metric.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "What a classifier outputs",
            "subtitle": "label, probability, boundary",
            "slides": [
                slide("From regression to classification",
                      bullets([
                          "<strong>Regression</strong>: ŷ is a number; minimize squared error.",
                          "<strong>Classification</strong>: ŷ is a label; minimize misclassification (or maximize log-likelihood).",
                          "Same X, different y. Same toolbox: pipelines, CV, regularization.",
                      ])),
                slide("Confusion matrix",
                      '<p>For binary classification:</p>'
                      '<table style="font-size:0.95em;margin:0 auto;"><tr><td></td><td><strong>pred 0</strong></td><td><strong>pred 1</strong></td></tr>'
                      '<tr><td><strong>true 0</strong></td><td>TN</td><td>FP</td></tr>'
                      '<tr><td><strong>true 1</strong></td><td>FN</td><td>TP</td></tr></table>'
                      '<p class="muted" style="margin-top:1em;">All metrics — accuracy, precision, recall, F1 — are functions of these four cells.</p>'),
                slide("Which metric for which job?",
                      bullets([
                          "<strong>Accuracy</strong> — only on balanced classes. Lies on imbalanced data.",
                          "<strong>Precision</strong> — when false positives are costly (spam filter).",
                          "<strong>Recall</strong> — when false negatives are costly (cancer screening).",
                          "<strong>F1</strong> — when both matter equally.",
                          "<strong>AUC</strong> — robust to threshold choice; ranks positives above negatives.",
                      ])),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "KNN",
            "subtitle": "the no-training baseline",
            "slides": [
                slide("KNN in one slide",
                      bullets([
                          "To predict a new point, find its k nearest training points.",
                          "Take a majority vote (classification) or average (regression).",
                          "<em>No model fit</em> — the training data <em>is</em> the model.",
                      ])),
                slide("k controls the bias-variance dial",
                      bullets([
                          "<strong>k = 1</strong> — perfectly fits training, jagged boundary, high variance.",
                          "<strong>k = 25</strong> — smooth boundary, more bias, less variance.",
                          "Pick k with cross-validation.",
                      ])),
                slide("Always scale before KNN",
                      '<p>Income (0 to 70 000) versus balance (0 to 2700) — without scaling, KNN distance is dominated by income alone. Wrap in a Pipeline:</p>'
                      + code_block("Pipeline([\n"
                                   "    ('scale', StandardScaler()),\n"
                                   "    ('knn', KNeighborsClassifier(k=5)),\n"
                                   "])")),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "Class imbalance",
            "subtitle": "the trap",
            "slides": [
                slide("'Always say No' scores 97%",
                      '<p>Default rate ≈ 3%. The constant classifier 0 has 97% accuracy and 0% recall on defaulters.</p>'
                      '<p class="callout">Accuracy is useless when classes are imbalanced. Look at recall and AUC instead.</p>'),
                slide("Two fixes that always help",
                      bullets([
                          "<code>train_test_split(stratify=y)</code> — keeps class proportions in both halves.",
                          "<code>class_weight='balanced'</code> — weights the loss inversely to class frequency.",
                      ])),
            ],
        },
    ],
    "recap_items": [
        "<strong>A classifier outputs a label (often via a probability).</strong> Read the confusion matrix every time.",
        "<strong>KNN: no training, no fancy math, but it does need scaling.</strong>",
        "<strong>Accuracy lies on imbalanced data.</strong> Reach for recall/AUC and class_weight.",
    ],
    "recap_callout": "Next: the linear classifier — logistic regression.",
}


W4C2 = {
    "title": "Logistic Regression I — Binary",
    "kicker": "Week 4 · Course 2 · 1.5 hours",
    "subtitle": "From log-odds to ROC curves",
    "parts_summary": [
        ("0:00 · 0:30", "The sigmoid & log-odds", "from LR to LR."),
        ("0:30 · 1:00", "Multiple binary LR", "Smarket — markets are hard."),
        ("1:00 · 1:30", "ROC & threshold tuning", "predict_proba in action."),
    ],
    "callout": "Logistic regression is the single most important ML model in industry. The linear classifier you'll keep using even after you know all the rest.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "From log-odds to sigmoid",
            "subtitle": "the linear classifier",
            "slides": [
                slide("The model",
                      '<p style="text-align:center;font-size:1.2em;">P(y=1|x) = σ(β₀ + β₁ x), where σ(z) = 1 / (1 + e<sup>−z</sup>)</p>'
                      '<p style="text-align:center;font-size:1.2em;">log(p / (1−p)) = β₀ + β₁ x</p>'
                      '<p class="muted">Linear in the log-odds. S-shaped in probability.</p>'),
                slide("The loss",
                      '<p style="text-align:center;font-size:1.2em;">ℓ(β) = Σᵢ [yᵢ log pᵢ + (1−yᵢ) log(1−pᵢ)]</p>'
                      '<p>Concave in β — any reasonable optimizer reaches the unique maximum.</p>'),
                slide("Interpreting coefficients",
                      '<p>e<sup>β</sup> is the <strong>odds ratio</strong> per unit change of x.</p>'
                      '<p>For Default, β<sub>balance</sub> ≈ 0.0055 → e<sup>100·β</sup> ≈ 1.74 → +$100 balance ≈ +74% odds of default.</p>'),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Multiple binary LR",
            "subtitle": "Smarket lab",
            "slides": [
                slide("Predict market direction from lag returns",
                      code_block("X = smarket[['Lag1', 'Lag2', 'Lag3', 'Lag4', 'Lag5', 'Volume']]\n"
                                 "y = (smarket['Direction'] == 'Up').astype(int)\n"
                                 "m = LogisticRegression(C=1e6).fit(X, y)")
                      + '<p class="muted">DO NOT use <code>Today</code> as a predictor — it IS the direction.</p>'),
                slide("The disappointment",
                      bullets([
                          "Coefficients are tiny.",
                          "Training accuracy barely above 50%.",
                          "Held-out accuracy: also barely above 50%.",
                          "Lesson: a clean lab dataset can still contain no signal. Markets are hard.",
                      ])),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "ROC & threshold tuning",
            "subtitle": "predict_proba",
            "slides": [
                slide("predict_proba vs predict",
                      '<p>Logistic regression naturally outputs a probability. <code>predict</code> just applies a 0.5 threshold — rarely the right answer on imbalanced data.</p>'),
                slide("ROC curve in one picture",
                      bullets([
                          "X axis: FPR. Y axis: TPR.",
                          "Sweep the threshold from 1 → 0; trace the curve.",
                          "AUC = area under this curve = P(score(pos) > score(neg)).",
                          "Diagonal line = random guessing.",
                      ])),
                slide("Threshold tuning for F1",
                      code_block("ts = np.linspace(0.05, 0.6, 50)\n"
                                 "f1s = [f1_score(y, (proba >= t)) for t in ts]\n"
                                 "best_t = ts[np.argmax(f1s)]"),
                      "For Default at default 0.5, F1 is low because few are predicted 1. Lowering threshold to ~0.15 trades precision for recall, and F1 jumps."),
            ],
        },
    ],
    "recap_items": [
        "<strong>Linear in log-odds, sigmoid in probability.</strong> The classic linear classifier.",
        "<strong>e<sup>β</sup> is the odds ratio per unit of x.</strong> The interpretation an executive will ask about.",
        "<strong>0.5 is rarely the right threshold.</strong> Tune it for F1 or any cost-sensitive metric.",
    ],
    "recap_callout": "Next: more than two classes, and the regularization knob from Week 3 returns.",
}


W4C3 = {
    "title": "Logistic Regression II — Multinomial & Regularized",
    "kicker": "Week 4 · Course 3 · 1.5 hours",
    "subtitle": "Softmax, L1/L2, and the wall that linear hits",
    "parts_summary": [
        ("0:00 · 0:30", "Multinomial LR", "softmax for K classes."),
        ("0:30 · 1:00", "L1/L2 in LR", "C = 1/λ; coefficient paths."),
        ("1:00 · 1:30", "When linear fails", "the moons dataset."),
    ],
    "callout": "Real problems have more than two classes and more predictors than observations. Multinomial LR plus regularization handles both; non-linear problems do not.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Multinomial LR",
            "subtitle": "softmax",
            "slides": [
                slide("The softmax extension",
                      '<p style="text-align:center;font-size:1.2em;">P(y = k | x) = e<sup>β<sub>k</sub><sup>T</sup>x</sup> / Σ<sub>j</sub> e<sup>β<sub>j</sub><sup>T</sup>x</sup></p>'
                      + bullets([
                          "K weight vectors β<sub>1</sub>, …, β<sub>K</sub>.",
                          "Output: a probability per class, summing to 1.",
                          "One-vs-rest is the older alternative — usually slightly worse.",
                      ])),
                slide("Sklearn in one line",
                      code_block("LogisticRegression(max_iter=2000).fit(X, y)\n"
                                 "# auto-detects multinomial when y has > 2 classes")),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "L1 and L2 in LR",
            "subtitle": "C = 1/λ",
            "slides": [
                slide("Same idea as Week 3",
                      bullets([
                          "<strong>L2</strong> (default): shrinks every β toward zero.",
                          "<strong>L1</strong> (penalty='l1', solver='saga'): zeros some β out.",
                          "<strong>C</strong> is the <em>inverse</em> regularization strength. Small C = strong regularization.",
                      ])),
                slide("Coefficient paths",
                      '<p>Vary log C, plot each β. Under L2 they shrink smoothly; under L1 they drop to zero one at a time — same Lasso geometry from last week.</p>',
                      "Connect explicitly to Week 3. Regularization is one idea, applied to many losses."),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "When linear fails",
            "subtitle": "two moons",
            "slides": [
                slide("The make_moons dataset",
                      code_block("from sklearn.datasets import make_moons\n"
                                 "X, y = make_moons(n_samples=400, noise=0.25, random_state=0)")
                      + '<p>Two interleaved half-moons. Cannot be separated by any straight line.</p>'),
                slide("LR gives up at ~85%",
                      bullets([
                          "A linear boundary <em>cannot</em> bend through the moons.",
                          "Fixes: add non-linear features (polynomial, kernel) — Course 6.",
                          "Or use a non-linear model — Courses 4 and 5.",
                      ])),
            ],
        },
    ],
    "recap_items": [
        "<strong>Softmax generalizes the sigmoid to K classes.</strong>",
        "<strong>C = 1/λ.</strong> L1 in LR is Lasso in LR. Same story, different loss.",
        "<strong>A line cannot separate two moons.</strong> Day 2 fixes that.",
    ],
    "recap_callout": "Day 2 starts now: trees, ensembles, and kernels.",
}


W4C4 = {
    "title": "Decision Trees",
    "kicker": "Week 4 · Course 4 · 1.5 hours",
    "subtitle": "The interpretable non-linear classifier",
    "parts_summary": [
        ("0:00 · 0:30", "Classification trees", "Gini, splits, plot_tree."),
        ("0:30 · 1:00", "Regression trees", "cost-complexity pruning."),
        ("1:00 · 1:30", "Strengths & weaknesses", "variance → ensembles."),
    ],
    "callout": "A single tree is the most interpretable model you'll meet. Every prediction is a flowchart. The weakness — variance — sets up next course's payoff.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Classification trees",
            "subtitle": "greedy recursive splitting",
            "slides": [
                slide("The algorithm",
                      bullets([
                          "At each node, scan every feature and every threshold.",
                          "Pick the (feature, threshold) that most reduces Gini impurity.",
                          "Recurse on the two children. Stop at depth limit or pure leaf.",
                      ], fragments=False)),
                slide("Gini impurity",
                      '<p style="text-align:center;font-size:1.2em;">Gini = 1 − Σ<sub>k</sub> p<sub>k</sub>²</p>'
                      + bullets([
                          "p=0.5 (worst): Gini = 0.5.",
                          "p=0 or 1 (pure): Gini = 0.",
                          "Entropy is an alternative; in practice they pick almost the same splits.",
                      ])),
                slide("Reading a tree",
                      '<p>Each node prints: split criterion, samples, class distribution, prediction.</p>'
                      '<p>Trace a row from root to leaf — that is the model\'s reasoning, in human language.</p>'),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Regression trees & pruning",
            "subtitle": "ccp_alpha",
            "slides": [
                slide("Same algorithm, different criterion",
                      '<p>Regression trees split to minimize MSE within each child node. Final prediction = mean of training targets in the leaf.</p>'),
                slide("Cost-complexity pruning",
                      '<p style="text-align:center;font-size:1.2em;">cost(T) = Σ<sub>leaves</sub> MSE(leaf) + α · |T|</p>'
                      + bullets([
                          "α = 0 → fully grown, overfit.",
                          "α → ∞ → root-only stump.",
                          "Pick α with 5-fold CV.",
                      ])),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "Strengths & weaknesses",
            "subtitle": "and the road to ensembles",
            "slides": [
                slide("Strengths",
                      bullets([
                          "Interpretable end-to-end.",
                          "Handles mixed dtypes without preprocessing.",
                          "No scaling required.",
                          "Captures interactions and non-linearities natively.",
                      ])),
                slide("Weakness — variance",
                      '<p>Refit the same tree on a bootstrap sample. Different root split. Different tree. <em>Massively different</em> predictions on borderline points.</p>'
                      '<p class="callout">Solution: fit many trees and vote. Next course.</p>'),
            ],
        },
    ],
    "recap_items": [
        "<strong>Greedy splits on Gini (classification) or MSE (regression).</strong>",
        "<strong>Prune with ccp_alpha to fight overfit.</strong>",
        "<strong>Single trees are interpretable but high-variance.</strong> Ensembles fix that.",
    ],
    "recap_callout": "Next: bagging, random forests, and gradient boosting.",
}


W4C5 = {
    "title": "Ensembles — Bagging, Random Forest, Boosting",
    "kicker": "Week 4 · Course 5 · 1.5 hours",
    "subtitle": "Many weak trees beat one fancy tree",
    "parts_summary": [
        ("0:00 · 0:30", "Random Forests", "bagging + feature subsets."),
        ("0:30 · 1:00", "Interpretation", "importance, partial dependence."),
        ("1:00 · 1:30", "Gradient Boosting", "the production default."),
    ],
    "callout": "Random forest and gradient boosting are the two algorithms that win Kaggle and ship in production. Master these and you have an industrial-grade tabular toolkit.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Random Forests",
            "subtitle": "bagging + feature subsets",
            "slides": [
                slide("Bagging = bootstrap aggregating",
                      bullets([
                          "Draw B bootstrap samples from the training set.",
                          "Fit a deep tree to each.",
                          "Average their predictions (regression) or vote (classification).",
                          "The average has lower variance than any single tree.",
                      ])),
                slide("Random forest adds feature subsetting",
                      '<p>At <em>every</em> split, sample √p features uniformly. Why?</p>'
                      '<p>If one strong predictor dominates, every bagged tree picks it as the root split. The trees end up correlated → averaging gains little. Subsampling decorrelates them.</p>'),
                slide("OOB error — a free CV",
                      bullets([
                          "Each bootstrap sample uses ~63% of rows.",
                          "The other 37% are out-of-bag — never seen by that tree.",
                          "Score each row on the trees that did not see it. <code>oob_score=True</code>.",
                      ])),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Interpretation",
            "subtitle": "back to explainability",
            "slides": [
                slide("Feature importance",
                      '<p>Average impurity decrease attributable to each feature across all trees and all splits. Sort, plot, ship.</p>'
                      '<p class="muted">Caveat: biased toward high-cardinality features. <code>sklearn.inspection.permutation_importance</code> is the modern alternative.</p>'),
                slide("Partial dependence",
                      '<p>For feature j: vary j across its range, hold the others fixed, plot mean prediction.</p>'
                      '<p>Tells you the <em>shape</em> of the model\'s relationship with each predictor, even though the model is a forest of 500 trees.</p>'),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "Gradient Boosting",
            "subtitle": "fit residuals sequentially",
            "slides": [
                slide("The algorithm",
                      bullets([
                          "Start with a constant prediction (mean / log-odds).",
                          "Fit a small tree to the gradient of the loss (the 'residuals').",
                          "Add learning_rate · tree to the ensemble.",
                          "Repeat n_estimators times.",
                      ], fragments=False)),
                slide("Learning rate × n_estimators",
                      bullets([
                          "Small lr + many trees → smooth, accurate, slow to train.",
                          "Large lr + few trees → fast, can overshoot the optimum.",
                          "Sweet spot: lr ≈ 0.05, n_estimators chosen by early stopping.",
                      ])),
                slide("Production-grade defaults",
                      bullets([
                          "<code>HistGradientBoostingClassifier</code> — sklearn's histogram-based GBM.",
                          "XGBoost / LightGBM / CatBoost — the third-party giants.",
                          "All four implement the same core idea with different speed/quality tweaks.",
                      ])),
            ],
        },
    ],
    "recap_items": [
        "<strong>Random forest = bagging + feature subsets.</strong> OOB error is free.",
        "<strong>Feature importance and PDPs restore interpretability.</strong>",
        "<strong>Gradient boosting fits residuals sequentially.</strong> Small lr × many trees wins.",
    ],
    "recap_callout": "Last course: SVMs — non-linear via kernels, dominant in p ≫ n.",
}


W4C6 = {
    "title": "Support Vector Machines",
    "kicker": "Week 4 · Course 6 · 1.5 hours",
    "subtitle": "Maximum margin, kernels, and p ≫ n",
    "parts_summary": [
        ("0:00 · 0:30", "Maximum margin", "support vectors and geometry."),
        ("0:30 · 1:00", "Kernels", "linear, polynomial, RBF."),
        ("1:00 · 1:30", "p ≫ n", "the Khan gene-expression lab."),
    ],
    "callout": "SVMs produce non-linear boundaries without ever computing the non-linear features. They also dominate when p ≫ n — text and genomics.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Maximum margin",
            "subtitle": "geometry and support vectors",
            "slides": [
                slide("The unique optimum",
                      '<p>Infinitely many lines separate two linearly separable clouds. The maximum-margin line is the <em>unique</em> one furthest from both classes.</p>'
                      '<p>The points exactly on the margin are the <strong>support vectors</strong>. Move any other point and the boundary does not change.</p>'),
                slide("The optimization",
                      '<p style="text-align:center;font-size:1.2em;">minimize ½‖w‖² &nbsp; s.t. y<sub>i</sub>(w·x<sub>i</sub> + b) ≥ 1</p>'
                      + '<p>Equivalent to maximizing 2 / ‖w‖, the margin width. Convex quadratic program — unique solution.</p>'),
                slide("Soft margin — the C parameter",
                      bullets([
                          "Real data overlaps. We allow some violations of the margin.",
                          "Small C → wide margin, many support vectors, more bias.",
                          "Large C → narrow margin, few support vectors, more variance.",
                          "Tune C with CV.",
                      ])),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Kernels",
            "subtitle": "non-linear, cheap",
            "slides": [
                slide("The kernel trick",
                      '<p>Map x → φ(x) into a higher-dimensional space where the classes become linearly separable. Compute only inner products φ(x<sub>i</sub>) · φ(x<sub>j</sub>) — never φ itself.</p>'
                      + '<p>A <strong>kernel</strong> K(x, x\') gives that inner product directly.</p>'),
                slide("Three kernels",
                      bullets([
                          "<strong>Linear</strong>: K(x, x') = x · x'. Same as logistic regression boundary-wise.",
                          "<strong>Polynomial</strong>: K(x, x') = (1 + x · x')<sup>d</sup>. Bends, but rigidly.",
                          "<strong>RBF</strong>: K(x, x') = exp(−γ ‖x − x'‖²). Local bumps, very flexible. The default.",
                      ])),
                slide("γ in the RBF kernel",
                      bullets([
                          "Small γ — kernel is wide. Smooth boundary, more bias.",
                          "Large γ — kernel is narrow. Boundary curls around individual points, more variance.",
                          "Grid-search (C, γ) with CV. <code>gamma='scale'</code> is the modern default starting point.",
                      ])),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:30",
            "title": "p ≫ n",
            "subtitle": "the Khan lab",
            "slides": [
                slide("Khan — 63 cases, 2308 genes",
                      bullets([
                          "Four cancer subtypes.",
                          "Unregularized logistic regression diverges.",
                          "Linear SVM thrives — the margin objective is itself a form of regularization.",
                      ])),
                slide("Use a linear kernel here",
                      code_block("svc = SVC(kernel='linear', C=10).fit(xtr, ytr)\n"
                                 "GridSearchCV(svc, {'C': [0.1, 1, 10, 100]}, cv=3)")
                      + '<p class="muted">RBF is too slow at p = 2308 and not needed — the high dimension already gives enough flexibility.</p>'),
            ],
        },
    ],
    "recap_items": [
        "<strong>SVM finds the maximum-margin boundary.</strong> Support vectors define it.",
        "<strong>The kernel trick gives non-linear boundaries cheaply.</strong> RBF is the default.",
        "<strong>SVM is the tool for p ≫ n.</strong> Use linear kernel and tune C.",
    ],
    "recap_callout": "End of Week 4. From here: deep learning and neural networks.",
}


# ============================================================================
# DRIVER
# ============================================================================

DECKS = [
    (WEEK3 / "course-01-linear-regression-i" / "slides" / "index.html", W3C1),
    (WEEK3 / "course-02-linear-regression-ii" / "slides" / "index.html", W3C2),
    (WEEK3 / "course-03-feature-engineering" / "slides" / "index.html", W3C3),
    (WEEK3 / "course-04-cross-validation" / "slides" / "index.html", W3C4),
    (WEEK3 / "course-05-feature-selection-subset" / "slides" / "index.html", W3C5),
    (WEEK3 / "course-06-feature-selection-shrinkage" / "slides" / "index.html", W3C6),
    (WEEK4 / "course-01-classification-knn" / "slides" / "index.html", W4C1),
    (WEEK4 / "course-02-logistic-regression-i" / "slides" / "index.html", W4C2),
    (WEEK4 / "course-03-logistic-regression-ii" / "slides" / "index.html", W4C3),
    (WEEK4 / "course-04-decision-trees" / "slides" / "index.html", W4C4),
    (WEEK4 / "course-05-ensembles" / "slides" / "index.html", W4C5),
    (WEEK4 / "course-06-svm" / "slides" / "index.html", W4C6),
]


def main() -> None:
    for path, spec in DECKS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_deck(spec))
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
