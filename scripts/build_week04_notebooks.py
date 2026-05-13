"""Generate every Jupyter notebook for Week 4 (Machine Learning — classification).

Idempotent: re-running rewrites every .ipynb from the source-of-truth below.

Usage:
    python3 scripts/build_week04_notebooks.py
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEK4 = ROOT / "weeks" / "week-04-classification"


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
# COURSE 1 — CLASSIFICATION + KNN (ISLP Ch 2.2.3, Ch 4 intro)
# ============================================================================

def course1_lecture() -> list[dict]:
    return [
        md("# Course 1 — Classification + KNN",
           "",
           "What does a classifier output? How do we measure it? KNN is the",
           "simplest learner and the perfect place to meet decision boundaries,",
           "confusion matrices, and ROC curves.",
           "",
           "**Sections**",
           "1. What a classifier outputs (0:00–0:30)",
           "2. KNN — the no-training baseline (0:30–1:00)",
           "3. Class imbalance and the majority-class trap (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.neighbors import KNeighborsClassifier",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import train_test_split, cross_val_score",
             "from sklearn.metrics import (confusion_matrix, classification_report,",
             "                              roc_curve, auc, ConfusionMatrixDisplay)",
             "rng = np.random.default_rng(0)",
             "default = load_dataset('default')",
             "print(default.head())",
             "print('default rate:', (default['default'] == 'Yes').mean().round(4))"),
        md("## 1. What a classifier outputs"),
        md("### Look at the data first"),
        code("d = default.copy()",
             "d['y'] = (d['default'] == 'Yes').astype(int)",
             "fig, ax = plt.subplots(figsize=(6, 4))",
             "ax.scatter(d.loc[d.y==0, 'balance'], d.loc[d.y==0, 'income'], s=3, alpha=0.3, label='No')",
             "ax.scatter(d.loc[d.y==1, 'balance'], d.loc[d.y==1, 'income'], s=10, color='C3', label='Yes')",
             "ax.set_xlabel('balance'); ax.set_ylabel('income'); ax.legend()",
             "ax.set_title('Default — balance is the separating feature'); plt.show()"),
        md("### Confusion matrix and metrics"),
        md("The simplest possible classifier: 'predict default if balance > 1700'.",
           "Score it like any other model."),
        code("y = d['y'].to_numpy()",
             "y_hat = (d['balance'] > 1700).astype(int).to_numpy()",
             "cm = confusion_matrix(y, y_hat)",
             "print('confusion matrix [TN FP / FN TP]:'); print(cm)",
             "print()",
             "print(classification_report(y, y_hat, target_names=['No', 'Yes']))"),
        md("**Precision** = TP / (TP + FP) — of those we flagged, how many really default.",
           "**Recall** = TP / (TP + FN) — of those who really default, how many we flagged.",
           "**F1** = harmonic mean of the two. **AUC** = area under the ROC curve, the",
           "probability that a random positive scores higher than a random negative."),
        md("### ROC and AUC"),
        code("from sklearn.linear_model import LogisticRegression",
             "X = d[['balance', 'income']].to_numpy()",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "lr = LogisticRegression(max_iter=2000).fit(Xtr, ytr)",
             "scores = lr.predict_proba(Xte)[:, 1]",
             "fpr, tpr, _ = roc_curve(yte, scores)",
             "fig, ax = plt.subplots(figsize=(5, 5))",
             "ax.plot(fpr, tpr); ax.plot([0, 1], [0, 1], 'k--', alpha=0.4)",
             "ax.set_xlabel('FPR'); ax.set_ylabel('TPR')",
             "ax.set_title(f'ROC — AUC = {auc(fpr, tpr):.4f}'); plt.show()"),
        md("## 2. KNN — the no-training baseline"),
        md("### Why scale before KNN"),
        code("print('balance range:', d['balance'].min(), '...', d['balance'].max())",
             "print('income range :', d['income'].min(), '...', d['income'].max())"),
        md("Income dwarfs balance numerically — without scaling, KNN's 'nearest'",
           "is decided by income alone."),
        code("pipe = Pipeline([('s', StandardScaler()), ('knn', KNeighborsClassifier(n_neighbors=5))])",
             "pipe.fit(Xtr, ytr)",
             "print(f'KNN(k=5) test accuracy = {pipe.score(Xte, yte):.4f}')"),
        md("### How does k change the decision boundary?"),
        code("# Subsample for plotting speed",
             "rs = rng.choice(len(Xtr), 1500, replace=False)",
             "Xs, ys = Xtr[rs], ytr[rs]",
             "x_min, x_max = Xs[:, 0].min() - 100, Xs[:, 0].max() + 100",
             "y_min, y_max = Xs[:, 1].min() - 1000, Xs[:, 1].max() + 1000",
             "xx, yy = np.meshgrid(np.linspace(x_min, x_max, 120), np.linspace(y_min, y_max, 120))",
             "fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)",
             "for ax, k in zip(axes, [1, 5, 25]):",
             "    pipe = Pipeline([('s', StandardScaler()), ('knn', KNeighborsClassifier(k))])",
             "    pipe.fit(Xs, ys)",
             "    Z = pipe.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)",
             "    ax.contourf(xx, yy, Z, alpha=0.2, levels=[-0.5, 0.5, 1.5])",
             "    ax.scatter(Xs[ys==0, 0], Xs[ys==0, 1], s=3, alpha=0.3)",
             "    ax.scatter(Xs[ys==1, 0], Xs[ys==1, 1], s=12, color='C3')",
             "    ax.set_title(f'k = {k}')",
             "plt.tight_layout(); plt.show()"),
        md("k = 1 is wild (one outlier carves a region); k = 25 is smooth. Pick k",
           "with cross-validation, not by eye."),
        md("## 3. Class imbalance"),
        md("### The majority-class trap"),
        code("trivial = np.zeros_like(yte)  # 'always predict No'",
             "print(f'\"always No\" accuracy = {(trivial == yte).mean():.4f}')",
             "print('… but recall on defaulters = 0. Useless model.')"),
        md("### Fix: stratify + class_weight"),
        code("from sklearn.linear_model import LogisticRegression",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "lr = LogisticRegression(max_iter=2000, class_weight='balanced').fit(Xtr, ytr)",
             "y_pred = lr.predict(Xte)",
             "print(classification_report(yte, y_pred, target_names=['No', 'Yes']))"),
        md("Accuracy *drops* but recall on the positive class jumps — almost",
           "always the right trade-off for fraud, default, disease, etc."),
        md("### Recap",
           "- Classifier output: a label, often via a probability + threshold.",
           "- Read precision, recall, F1, AUC together. Accuracy alone lies on imbalanced data.",
           "- KNN needs scaling. k controls the bias-variance dial.",
           "- Use `stratify=y` and `class_weight='balanced'` when classes are skewed."),
    ]


def course1_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Load `penguins`, drop NaN, and fit KNN with `k=5` to",
           "predict `species` from `flipper_length_mm` and `bill_length_mm`.",
           "Use a stratified train/test split and report test accuracy."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.neighbors import KNeighborsClassifier",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import train_test_split",
             "# your code here"),
    ]


def course1_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.neighbors import KNeighborsClassifier",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import train_test_split",
             "df = load_dataset('penguins').dropna()",
             "X = df[['flipper_length_mm', 'bill_length_mm']].to_numpy()",
             "y = df['species'].to_numpy()",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "pipe = Pipeline([('s', StandardScaler()), ('knn', KNeighborsClassifier(5))]).fit(Xtr, ytr)",
             "print(f'k=5 test accuracy = {pipe.score(Xte, yte):.4f}')"),
    ]


def course1_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Plot the decision boundary for `k ∈ {1, 5, 25}` on the",
           "(flipper_length_mm, bill_length_mm) plane."),
        code("# your code here"),
    ]


def course1_ex2_solution() -> list[dict]:
    return [
        code("import numpy as np, matplotlib.pyplot as plt",
             "from sklearn.preprocessing import LabelEncoder",
             "le = LabelEncoder().fit(y)",
             "y_enc = le.transform(y)",
             "x_min, x_max = X[:,0].min()-2, X[:,0].max()+2",
             "y_min, y_max = X[:,1].min()-2, X[:,1].max()+2",
             "xx, yy = np.meshgrid(np.linspace(x_min, x_max, 120), np.linspace(y_min, y_max, 120))",
             "fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)",
             "for ax, k in zip(axes, [1, 5, 25]):",
             "    pipe = Pipeline([('s', StandardScaler()), ('knn', KNeighborsClassifier(k))]).fit(X, y_enc)",
             "    Z = pipe.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)",
             "    ax.contourf(xx, yy, Z, alpha=0.25, levels=[-0.5,0.5,1.5,2.5])",
             "    for cls in range(3):",
             "        ax.scatter(X[y_enc==cls,0], X[y_enc==cls,1], s=10, label=le.classes_[cls])",
             "    ax.set_title(f'k = {k}'); ax.legend(fontsize=7)",
             "plt.tight_layout(); plt.show()"),
    ]


def course1_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Use 5-fold CV to pick the best `k` from `[1, 3, 5, 11, 21, 51]`."),
        code("# your code here"),
    ]


def course1_ex3_solution() -> list[dict]:
    return [
        code("from sklearn.model_selection import cross_val_score",
             "ks = [1, 3, 5, 11, 21, 51]",
             "for k in ks:",
             "    pipe = Pipeline([('s', StandardScaler()), ('knn', KNeighborsClassifier(k))])",
             "    score = cross_val_score(pipe, X, y, cv=5).mean()",
             "    print(f'k={k:3d}  CV accuracy = {score:.4f}')"),
    ]


# ============================================================================
# COURSE 2 — LOGISTIC REGRESSION I (binary, ISLP Ch 4.3)
# ============================================================================

def course2_lecture() -> list[dict]:
    return [
        md("# Course 2 — Logistic Regression I",
           "",
           "From log-odds to ROC curves on the `Default` dataset, with a Smarket",
           "detour to see what 'no signal' looks like.",
           "",
           "**Sections**",
           "1. From linear regression to log-odds (0:00–0:30)",
           "2. Multiple logistic regression on Smarket (0:30–1:00)",
           "3. predict_proba, ROC, and threshold tuning (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.linear_model import LogisticRegression",
             "from sklearn.model_selection import train_test_split",
             "from sklearn.metrics import (classification_report, roc_curve, auc,",
             "                              confusion_matrix, f1_score)",
             "default = load_dataset('default')",
             "smarket = load_dataset('smarket')",
             "d = default.copy(); d['y'] = (d['default'] == 'Yes').astype(int)",
             "print('default:', d.shape, '  smarket:', smarket.shape)"),
        md("## 1. From linear regression to log-odds"),
        md("$$p(x) = \\frac{1}{1 + e^{-(\\beta_0 + \\beta_1 x)}}, \\qquad \\log\\frac{p}{1-p} = \\beta_0 + \\beta_1 x$$",
           "",
           "Linear in log-odds, S-shaped in probability. The log-likelihood",
           "$\\ell(\\beta) = \\sum_i [y_i \\log p_i + (1-y_i) \\log(1-p_i)]$ is",
           "concave — a fast maximizer always finds the unique optimum."),
        code("z = np.linspace(-6, 6, 200)",
             "fig, ax = plt.subplots(figsize=(6, 3.5))",
             "ax.plot(z, 1/(1+np.exp(-z)))",
             "ax.set_xlabel(r'$\\beta_0 + \\beta_1 x$ (log-odds)')",
             "ax.set_ylabel('p(x)'); ax.set_title('The sigmoid'); plt.show()"),
        md("### Fit on `default ~ balance`"),
        code("X = d[['balance']].to_numpy(); y = d['y'].to_numpy()",
             "m = LogisticRegression(C=1e6, max_iter=2000).fit(X, y)  # huge C -> ~unregularized",
             "print(f'intercept = {m.intercept_[0]:.4f}')",
             "print(f'slope     = {m.coef_[0][0]:.6f}')",
             "print(f'odds ratio per +1 unit of balance: {np.exp(m.coef_[0][0]):.6f}')",
             "print(f'odds ratio per +100 units:          {np.exp(100*m.coef_[0][0]):.4f}')"),
        code("xs = np.linspace(0, 2700, 200).reshape(-1, 1)",
             "ps = m.predict_proba(xs)[:, 1]",
             "fig, ax = plt.subplots(figsize=(6, 4))",
             "ax.scatter(X.ravel(), y, s=4, alpha=0.2)",
             "ax.plot(xs, ps, color='C3', linewidth=2)",
             "ax.set_xlabel('balance'); ax.set_ylabel('P(default)')",
             "ax.set_title('Logistic fit'); plt.show()"),
        md("## 2. Multiple LR on Smarket"),
        md("Predict `Direction` (Up / Down) from the lag returns *only* —",
           "`Today` is the answer, leaking it would be cheating."),
        code("Xs = smarket[['Lag1', 'Lag2', 'Lag3', 'Lag4', 'Lag5', 'Volume']]",
             "ys = (smarket['Direction'] == 'Up').astype(int)",
             "m = LogisticRegression(C=1e6, max_iter=2000).fit(Xs, ys)",
             "print(pd.Series(m.coef_[0], index=Xs.columns).round(4).to_string())",
             "print(f'training accuracy = {m.score(Xs, ys):.4f}')"),
        md("Coefficients are tiny, accuracy barely above 50%. *Markets are hard.*",
           "Use a stratified train/test split to confirm it's not just noise that"
           " happens to overfit the training set."),
        code("Xtr, Xte, ytr, yte = train_test_split(Xs, ys, test_size=0.3, random_state=0, stratify=ys)",
             "m = LogisticRegression(C=1e6, max_iter=2000).fit(Xtr, ytr)",
             "print(f'held-out accuracy = {m.score(Xte, yte):.4f}')"),
        md("## 3. predict_proba, ROC, and threshold tuning"),
        code("X = d[['balance', 'income']].to_numpy(); y = d['y'].to_numpy()",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "m = LogisticRegression(max_iter=2000).fit(Xtr, ytr)",
             "proba = m.predict_proba(Xte)[:, 1]",
             "print('first 5 probs :', proba[:5].round(3))",
             "print('first 5 preds :', (proba >= 0.5).astype(int)[:5])"),
        md("### ROC curve"),
        code("fpr, tpr, thr = roc_curve(yte, proba)",
             "fig, ax = plt.subplots(figsize=(5, 5))",
             "ax.plot(fpr, tpr); ax.plot([0,1], [0,1], 'k--', alpha=0.4)",
             "ax.set_xlabel('FPR'); ax.set_ylabel('TPR')",
             "ax.set_title(f'ROC — AUC = {auc(fpr, tpr):.4f}'); plt.show()"),
        md("### Sweep thresholds, pick the F1-max"),
        code("ts = np.linspace(0.02, 0.6, 50)",
             "f1s = [f1_score(yte, (proba >= t).astype(int)) for t in ts]",
             "fig, ax = plt.subplots(figsize=(6, 3.5))",
             "ax.plot(ts, f1s); best_t = ts[int(np.argmax(f1s))]",
             "ax.axvline(best_t, color='C3', linestyle='--', label=f'best t = {best_t:.2f}')",
             "ax.set_xlabel('threshold'); ax.set_ylabel('F1'); ax.legend()",
             "ax.set_title('Threshold tuning'); plt.show()",
             "print(f'F1 at default t=0.5: {f1_score(yte, (proba>=0.5).astype(int)):.4f}')",
             "print(f'F1 at best t = {best_t:.2f}: {max(f1s):.4f}')"),
        md("### Recap",
           "- Logistic regression = linear model in log-odds, sigmoid in probability.",
           "- e^β is the odds-ratio per unit change of the predictor.",
           "- `predict_proba` gives the score; `predict` applies a 0.5 cutoff.",
           "- Tune the cutoff with F1 (or any business cost ratio) — 0.5 is rarely",
           "  the right answer on imbalanced data."),
    ]


def course2_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Load `titanic`, drop rows missing `age`, one-hot encode",
           "`sex` and `embarked`. Fit binary logistic regression predicting",
           "`survived` from `pclass, sex, age, sibsp, parch, fare, embarked`.",
           "Report held-out accuracy and AUC."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "from sklearn.linear_model import LogisticRegression",
             "from sklearn.model_selection import train_test_split",
             "from sklearn.metrics import roc_auc_score",
             "# your code here"),
    ]


def course2_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "from sklearn.linear_model import LogisticRegression",
             "from sklearn.model_selection import train_test_split",
             "from sklearn.metrics import roc_auc_score",
             "df = load_dataset('titanic').dropna(subset=['age']).reset_index(drop=True)",
             "df = pd.get_dummies(df[['survived','pclass','sex','age','sibsp','parch','fare','embarked']].fillna(df.median(numeric_only=True)),",
             "                     columns=['sex','embarked'], drop_first=True, dtype=float)",
             "y = df['survived']; X = df.drop(columns=['survived'])",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "m = LogisticRegression(max_iter=2000).fit(Xtr, ytr)",
             "print(f'accuracy = {m.score(Xte, yte):.4f}')",
             "print(f'AUC      = {roc_auc_score(yte, m.predict_proba(Xte)[:,1]):.4f}')"),
    ]


def course2_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Tune the decision threshold for maximum F1 on the held-out set."),
        code("# your code here"),
    ]


def course2_ex2_solution() -> list[dict]:
    return [
        code("import numpy as np",
             "from sklearn.metrics import f1_score",
             "p = m.predict_proba(Xte)[:, 1]",
             "ts = np.linspace(0.1, 0.9, 81)",
             "f1s = [f1_score(yte, (p >= t).astype(int)) for t in ts]",
             "best_t = ts[int(np.argmax(f1s))]",
             "print(f'F1@0.5     = {f1_score(yte, (p>=0.5).astype(int)):.4f}')",
             "print(f'F1@{best_t:.2f}  = {max(f1s):.4f}')"),
    ]


def course2_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Add an interaction `sex_male × pclass` to the design.",
           "Does AUC improve?"),
        code("# your code here"),
    ]


def course2_ex3_solution() -> list[dict]:
    return [
        code("X2 = X.copy()",
             "X2['sex_x_pclass'] = X['sex_male'] * X['pclass']",
             "Xtr2, Xte2, ytr2, yte2 = train_test_split(X2, y, test_size=0.3, random_state=0, stratify=y)",
             "m2 = LogisticRegression(max_iter=2000).fit(Xtr2, ytr2)",
             "print(f'baseline AUC      = {roc_auc_score(yte, m.predict_proba(Xte)[:,1]):.4f}')",
             "print(f'with interaction  = {roc_auc_score(yte2, m2.predict_proba(Xte2)[:,1]):.4f}')"),
    ]


# ============================================================================
# COURSE 3 — LOGISTIC REGRESSION II (multinomial + regularized, ISLP Ch 4.3.5)
# ============================================================================

def course3_lecture() -> list[dict]:
    return [
        md("# Course 3 — Logistic Regression II",
           "",
           "Multinomial logistic regression, L1/L2 regularization, and the moment",
           "when a linear classifier runs out of road.",
           "",
           "**Sections**",
           "1. Multinomial logistic regression (0:00–0:30)",
           "2. L2 and L1 regularization (0:30–1:00)",
           "3. When linear fails — motivating non-linear classifiers (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.linear_model import LogisticRegression",
             "from sklearn.model_selection import train_test_split",
             "from sklearn.preprocessing import StandardScaler, LabelEncoder",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.datasets import make_moons",
             "iris = load_dataset('iris')",
             "print(iris['species'].value_counts())"),
        md("## 1. Multinomial logistic regression"),
        md("Softmax generalizes the sigmoid: $P(y=k|x) = \\frac{e^{\\beta_k^\\top x}}{\\sum_j e^{\\beta_j^\\top x}}$."),
        code("le = LabelEncoder().fit(iris['species'])",
             "y = le.transform(iris['species'])",
             "X = iris[['petal_length', 'petal_width']].to_numpy()",
             "m = LogisticRegression(max_iter=2000).fit(X, y)",
             "print('coef shape:', m.coef_.shape)  # (3, 2) — one row per class",
             "print(f'training accuracy = {m.score(X, y):.4f}')"),
        code("x_min, x_max = X[:,0].min()-0.5, X[:,0].max()+0.5",
             "y_min, y_max = X[:,1].min()-0.5, X[:,1].max()+0.5",
             "xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),",
             "                      np.linspace(y_min, y_max, 200))",
             "Z = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)",
             "fig, ax = plt.subplots(figsize=(6, 5))",
             "ax.contourf(xx, yy, Z, alpha=0.25, levels=[-0.5,0.5,1.5,2.5])",
             "for cls in range(3):",
             "    ax.scatter(X[y==cls,0], X[y==cls,1], label=le.classes_[cls], s=20)",
             "ax.set_xlabel('petal_length'); ax.set_ylabel('petal_width'); ax.legend()",
             "ax.set_title('Multinomial LR on iris'); plt.show()"),
        md("## 2. L2 and L1 regularization"),
        md("$C = 1/\\lambda$. Small $C$ = strong regularization (coefficients shrunk).",
           "Use `solver='liblinear'` or `'saga'` to enable L1."),
        code("# Use full 4D iris this time; standardize for regularization to be fair.",
             "X4 = iris[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']].to_numpy()",
             "Cs = np.logspace(-3, 2, 30)",
             "paths_l2 = np.empty((len(Cs), 3, 4))",
             "paths_l1 = np.empty((len(Cs), 3, 4))",
             "scaler = StandardScaler().fit(X4)",
             "Xs = scaler.transform(X4)",
             "for i, C in enumerate(Cs):",
             "    paths_l2[i] = LogisticRegression(C=C, max_iter=3000).fit(Xs, y).coef_",
             "    paths_l1[i] = LogisticRegression(C=C, penalty='l1', solver='saga', max_iter=3000).fit(Xs, y).coef_",
             "",
             "fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)",
             "feat = ['sepal_len', 'sepal_wid', 'petal_len', 'petal_wid']",
             "for ax, paths, title in zip(axes, [paths_l2, paths_l1], ['L2', 'L1']):",
             "    # show class 0 (setosa) only to keep the plot readable",
             "    for j in range(4):",
             "        ax.plot(Cs, paths[:, 0, j], label=feat[j])",
             "    ax.set_xscale('log'); ax.set_xlabel('C (= 1/λ)')",
             "    ax.set_title(f'{title} coefficient paths (class: setosa)')",
             "    ax.legend(fontsize=8)",
             "plt.tight_layout(); plt.show()"),
        md("Notice that under L1 (right) some coefficients hit zero exactly for",
           "small C — same sparsity story as Lasso in Week 3."),
        md("## 3. When linear fails"),
        code("Xm, ym = make_moons(n_samples=400, noise=0.25, random_state=0)",
             "m = LogisticRegression(max_iter=2000).fit(Xm, ym)",
             "print(f'LR on moons: accuracy = {m.score(Xm, ym):.4f}')"),
        code("xx, yy = np.meshgrid(np.linspace(Xm[:,0].min()-0.5, Xm[:,0].max()+0.5, 200),",
             "                      np.linspace(Xm[:,1].min()-0.5, Xm[:,1].max()+0.5, 200))",
             "Z = m.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)",
             "fig, ax = plt.subplots(figsize=(6, 5))",
             "ax.contourf(xx, yy, Z, alpha=0.25)",
             "ax.scatter(Xm[ym==0,0], Xm[ym==0,1], s=10)",
             "ax.scatter(Xm[ym==1,0], Xm[ym==1,1], s=10, color='C3')",
             "ax.set_title('A line cannot separate two moons'); plt.show()"),
        md("A *linear* boundary can do no better than ~85% here. We need either",
           "non-linear features (next-week: SVM with an RBF kernel) or a non-linear",
           "model (next-week: trees and ensembles)."),
        md("### Recap",
           "- Multinomial LR is the softmax classifier: one weight vector per class.",
           "- C = 1/λ controls regularization; L1 induces sparsity, L2 just shrinks.",
           "- Linear classifiers fundamentally cannot fit curved boundaries — that's",
           "  the wall that motivates Day 2."),
    ]


def course3_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Fit plain multinomial logistic regression on `penguins`",
           "to predict `species` from all four numeric measurements. Report 5-fold",
           "CV accuracy. Drop NaN first."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.linear_model import LogisticRegression",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import cross_val_score",
             "# your code here"),
    ]


def course3_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.linear_model import LogisticRegression",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import cross_val_score",
             "df = load_dataset('penguins').dropna()",
             "X = df[['bill_length_mm','bill_depth_mm','flipper_length_mm','body_mass_g']]",
             "y = df['species']",
             "pipe = Pipeline([('s', StandardScaler()),",
             "                 ('lr', LogisticRegression(max_iter=2000))])",
             "print(f'CV accuracy = {cross_val_score(pipe, X, y, cv=5).mean():.4f}')"),
    ]


def course3_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Fit L1-penalized logistic regression with `C = 0.05`.",
           "How many coefficients survive (are non-zero) for each class?"),
        code("# your code here"),
    ]


def course3_ex2_solution() -> list[dict]:
    return [
        code("import numpy as np",
             "Xs = StandardScaler().fit_transform(X)",
             "m = LogisticRegression(C=0.05, penalty='l1', solver='saga',",
             "                        max_iter=5000).fit(Xs, y)",
             "for cls, row in zip(m.classes_, m.coef_):",
             "    keep = [n for n, c in zip(X.columns, row) if c != 0]",
             "    print(f'{cls:10s}: survivors = {keep}')"),
    ]


def course3_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Compare validation accuracy for `C ∈ [0.001, 0.01, 0.1, 1, 10]`",
           "under L1. Plot accuracy vs C on a log axis."),
        code("# your code here"),
    ]


def course3_ex3_solution() -> list[dict]:
    return [
        code("import matplotlib.pyplot as plt",
             "Cs = [0.001, 0.01, 0.1, 1, 10]",
             "accs = []",
             "for C in Cs:",
             "    pipe = Pipeline([('s', StandardScaler()),",
             "                     ('lr', LogisticRegression(C=C, penalty='l1', solver='saga',",
             "                                               max_iter=5000))])",
             "    accs.append(cross_val_score(pipe, X, y, cv=5).mean())",
             "fig, ax = plt.subplots(figsize=(6, 3.5))",
             "ax.semilogx(Cs, accs, marker='o')",
             "ax.set_xlabel('C'); ax.set_ylabel('5-fold CV accuracy'); plt.show()",
             "for C, a in zip(Cs, accs): print(f'C={C:7g}  acc = {a:.4f}')"),
    ]


# ============================================================================
# COURSE 4 — DECISION TREES (ISLP Ch 8.1)
# ============================================================================

def course4_lecture() -> list[dict]:
    return [
        md("# Course 4 — Decision Trees",
           "",
           "Greedy recursive splitting on Gini or entropy. The single most",
           "interpretable model in this course — every prediction is a flowchart.",
           "",
           "**Sections**",
           "1. Classification trees on Carseats (0:00–0:30)",
           "2. Regression trees and pruning (0:30–1:00)",
           "3. Strengths, weaknesses, and the road to ensembles (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree",
             "from sklearn.model_selection import train_test_split, cross_val_score, KFold",
             "from sklearn.metrics import accuracy_score, mean_squared_error",
             "rng = np.random.default_rng(0)",
             "carseats = load_dataset('carseats')",
             "boston = load_dataset('boston')"),
        md("## 1. Classification tree on Carseats"),
        code("c = carseats.copy()",
             "c['High'] = (c['Sales'] > 8).astype(int)",
             "c = pd.get_dummies(c.drop(columns=['Sales']), columns=['ShelveLoc','Urban','US'],",
             "                    drop_first=True, dtype=float)",
             "X = c.drop(columns=['High']); y = c['High']",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "tree = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)",
             "print(f'depth-3 tree test accuracy = {tree.score(Xte, yte):.4f}')"),
        md("### Gini impurity"),
        md("At each node, the split that maximally drops $1 - \\sum_k p_k^2$ wins.",
           "For binary classification with `p = 0.5`, Gini = 0.5 (worst). For a",
           "pure node, Gini = 0."),
        code("fig, ax = plt.subplots(figsize=(11, 6))",
             "plot_tree(tree, feature_names=list(X.columns), class_names=['Low','High'],",
             "          filled=True, ax=ax, fontsize=8)",
             "plt.show()"),
        md("## 2. Regression trees and pruning"),
        code("Xb = boston.drop(columns=['medv']); yb = boston['medv']",
             "Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.3, random_state=0)",
             "tree = DecisionTreeRegressor(random_state=0).fit(Xtr, ytr)",
             "print(f'unpruned depth = {tree.get_depth()}, test MSE = {mean_squared_error(yte, tree.predict(Xte)):.2f}')"),
        md("### Cost-complexity pruning path"),
        code("path = tree.cost_complexity_pruning_path(Xtr, ytr)",
             "alphas = path.ccp_alphas[:-1]  # drop the trivial root-only tree",
             "cv_mse = []",
             "for a in alphas:",
             "    m = DecisionTreeRegressor(random_state=0, ccp_alpha=a)",
             "    cv_mse.append(-cross_val_score(m, Xtr, ytr, cv=5,",
             "                                    scoring='neg_mean_squared_error').mean())",
             "fig, ax = plt.subplots(figsize=(7, 4))",
             "ax.plot(alphas, cv_mse, marker='.')",
             "best_a = alphas[int(np.argmin(cv_mse))]",
             "ax.axvline(best_a, color='C3', linestyle='--', label=f'best α = {best_a:.3f}')",
             "ax.set_xlabel(r'$ccp\\_alpha$'); ax.set_ylabel('5-fold CV MSE'); ax.legend()",
             "ax.set_title('Cost-complexity pruning path'); plt.show()",
             "pruned = DecisionTreeRegressor(random_state=0, ccp_alpha=best_a).fit(Xtr, ytr)",
             "print(f'pruned depth={pruned.get_depth()}  test MSE = {mean_squared_error(yte, pruned.predict(Xte)):.2f}')"),
        md("## 3. Strengths, weaknesses, ensembles"),
        md("**Strengths.** Interpretable, no scaling required, mixed dtypes, captures",
           "  interactions naturally.\n",
           "**Weakness.** Very high variance. Refit on a bootstrap sample → totally",
           "  different tree."),
        code("fig, axes = plt.subplots(2, 2, figsize=(11, 8))",
             "for ax, seed in zip(axes.ravel(), [0, 1, 2, 3]):",
             "    rng = np.random.default_rng(seed)",
             "    idx = rng.choice(len(Xtr), len(Xtr), replace=True)",
             "    t = DecisionTreeClassifier(max_depth=3, random_state=seed)",
             "    # use the classification problem for clarity",
             "    Xc = c.drop(columns=['High']); yc = c['High']",
             "    Xc_tr = Xc.iloc[idx]; yc_tr = yc.iloc[idx]",
             "    t.fit(Xc_tr, yc_tr)",
             "    plot_tree(t, feature_names=list(Xc.columns), class_names=['Low','High'],",
             "              filled=True, ax=ax, fontsize=6)",
             "    ax.set_title(f'bootstrap seed = {seed}')",
             "plt.tight_layout(); plt.show()"),
        md("Same data, four different first splits, totally different trees. This",
           "variance is the problem ensembles solve in Course 5."),
        md("### Recap",
           "- A tree is a sequence of axis-aligned binary splits chosen greedily",
           "  to minimize Gini (classification) or MSE (regression).",
           "- Prune via `ccp_alpha` to fight overfitting.",
           "- Variance is the weakness — refit on a bootstrap, get a different tree.",
           "  Ensembles average that variance away."),
    ]


def course4_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Load `tips`. Create the binary target `high_tip = (tip / total_bill) > 0.18`.",
           "Fit a `DecisionTreeClassifier(max_depth=3)` to predict it from",
           "`total_bill, size`, one-hot `day, time, sex, smoker`. Report test accuracy."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "from sklearn.tree import DecisionTreeClassifier",
             "from sklearn.model_selection import train_test_split",
             "# your code here"),
    ]


def course4_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "from sklearn.tree import DecisionTreeClassifier",
             "from sklearn.model_selection import train_test_split",
             "tips = load_dataset('tips')",
             "tips['high_tip'] = ((tips['tip'] / tips['total_bill']) > 0.18).astype(int)",
             "X = pd.get_dummies(tips[['total_bill','size','day','time','sex','smoker']],",
             "                    columns=['day','time','sex','smoker'], drop_first=True, dtype=float)",
             "y = tips['high_tip']",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "tree = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xtr, ytr)",
             "print(f'depth-3 test accuracy = {tree.score(Xte, yte):.4f}')"),
    ]


def course4_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Plot the depth-3 tree. Which feature does the root split on?"),
        code("# your code here"),
    ]


def course4_ex2_solution() -> list[dict]:
    return [
        code("import matplotlib.pyplot as plt",
             "from sklearn.tree import plot_tree",
             "fig, ax = plt.subplots(figsize=(11, 6))",
             "plot_tree(tree, feature_names=list(X.columns), class_names=['Low','High'],",
             "          filled=True, ax=ax, fontsize=8)",
             "plt.show()",
             "print('root split feature:', X.columns[tree.tree_.feature[0]])"),
    ]


def course4_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Prune via `cost_complexity_pruning_path` + 5-fold CV.",
           "Compare test accuracy before and after pruning."),
        code("# your code here"),
    ]


def course4_ex3_solution() -> list[dict]:
    return [
        code("import numpy as np",
             "from sklearn.model_selection import cross_val_score",
             "full = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)",
             "path = full.cost_complexity_pruning_path(Xtr, ytr)",
             "alphas = path.ccp_alphas[:-1]",
             "scores = [cross_val_score(DecisionTreeClassifier(random_state=0, ccp_alpha=a),",
             "                           Xtr, ytr, cv=5).mean() for a in alphas]",
             "best_a = alphas[int(np.argmax(scores))]",
             "pruned = DecisionTreeClassifier(random_state=0, ccp_alpha=best_a).fit(Xtr, ytr)",
             "print(f'unpruned depth={full.get_depth()}  test acc={full.score(Xte, yte):.4f}')",
             "print(f'pruned   depth={pruned.get_depth()}  test acc={pruned.score(Xte, yte):.4f}')"),
    ]


# ============================================================================
# COURSE 5 — ENSEMBLES (ISLP Ch 8.2)
# ============================================================================

def course5_lecture() -> list[dict]:
    return [
        md("# Course 5 — Ensembles",
           "",
           "Bagging, random forests, and gradient boosting. The algorithms that",
           "win Kaggle competitions and ship in production at every data-driven",
           "company.",
           "",
           "**Sections**",
           "1. Random forests on Carseats (0:00–0:30)",
           "2. OOB error, feature importance, partial dependence (0:30–1:00)",
           "3. Gradient boosting and the learning-rate dial (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "import time",
             "from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier",
             "from sklearn.tree import DecisionTreeClassifier",
             "from sklearn.inspection import PartialDependenceDisplay",
             "from sklearn.model_selection import train_test_split, cross_val_score",
             "from sklearn.metrics import accuracy_score, mean_squared_error, roc_auc_score",
             "carseats = load_dataset('carseats')",
             "boston = load_dataset('boston')"),
        md("## 1. Random forests"),
        md("A random forest fits many trees, each on a bootstrap sample, each",
           "considering only a random subset of features at every split.",
           "`max_features='sqrt'` is the classic default for classification."),
        code("c = carseats.copy()",
             "c['High'] = (c['Sales'] > 8).astype(int)",
             "c = pd.get_dummies(c.drop(columns=['Sales']), columns=['ShelveLoc','Urban','US'],",
             "                    drop_first=True, dtype=float)",
             "X = c.drop(columns=['High']); y = c['High']",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "",
             "tree = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)",
             "rf = RandomForestClassifier(n_estimators=300, max_features='sqrt',",
             "                             oob_score=True, n_jobs=-1, random_state=0).fit(Xtr, ytr)",
             "print(f'single tree test acc = {tree.score(Xte, yte):.4f}')",
             "print(f'random forest test  = {rf.score(Xte, yte):.4f}')",
             "print(f'OOB error           = {1 - rf.oob_score_:.4f}')"),
        md("## 2. OOB, feature importance, partial dependence"),
        code("# Regression forest on Boston for the feature-importance story",
             "Xb = boston.drop(columns=['medv']); yb = boston['medv']",
             "rfr = RandomForestRegressor(n_estimators=300, n_jobs=-1, random_state=0).fit(Xb, yb)",
             "imp = pd.Series(rfr.feature_importances_, index=Xb.columns).sort_values()",
             "fig, ax = plt.subplots(figsize=(6, 4))",
             "imp.plot.barh(ax=ax); ax.set_title('RF feature importance on Boston')",
             "ax.set_xlabel('importance'); plt.show()"),
        code("top2 = imp.tail(2).index.tolist()",
             "fig, ax = plt.subplots(figsize=(10, 4))",
             "PartialDependenceDisplay.from_estimator(rfr, Xb, top2, ax=ax)",
             "plt.show()"),
        md("## 3. Gradient boosting"),
        md("Boosting fits trees *sequentially*, each one predicting the errors of",
           "the previous ensemble. The learning rate controls how much each tree",
           "contributes — small rate + many trees almost always beats big rate + few."),
        code("results = []",
             "for lr in [0.01, 0.1]:",
             "    for n in [100, 500]:",
             "        t0 = time.perf_counter()",
             "        m = GradientBoostingClassifier(learning_rate=lr, n_estimators=n,",
             "                                        max_depth=3, random_state=0).fit(Xtr, ytr)",
             "        acc = m.score(Xte, yte)",
             "        results.append((lr, n, acc, time.perf_counter() - t0))",
             "        print(f'lr={lr:.2f}  n={n:4d}  acc={acc:.4f}  t={results[-1][3]:.2f}s')"),
        md("`HistGradientBoostingClassifier` is the modern fast default — same",
           "math, histogram-based splits, often 10–100× faster on large data."),
        md("### Recap",
           "- Random forests = bagging + random feature subsets. Decorrelate the trees.",
           "- OOB error is a free CV. Feature importance and PDPs give interpretability back.",
           "- Gradient boosting fits residuals sequentially. Tune learning_rate × n_estimators.",
           "- For production tabular work today, start with GBM/XGBoost/LightGBM."),
    ]


def course5_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Reload `tips`, build `high_tip = (tip/total_bill) > 0.18`,",
           "and fit three models on the same train/test split: single decision tree,",
           "random forest (300 trees), gradient boosting (300 trees). Report",
           "test accuracy for each."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "from sklearn.tree import DecisionTreeClassifier",
             "from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier",
             "from sklearn.model_selection import train_test_split",
             "# your code here"),
    ]


def course5_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import pandas as pd",
             "from sklearn.tree import DecisionTreeClassifier",
             "from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier",
             "from sklearn.model_selection import train_test_split",
             "tips = load_dataset('tips')",
             "tips['high_tip'] = ((tips['tip']/tips['total_bill']) > 0.18).astype(int)",
             "X = pd.get_dummies(tips[['total_bill','size','day','time','sex','smoker']],",
             "                    columns=['day','time','sex','smoker'], drop_first=True, dtype=float)",
             "y = tips['high_tip']",
             "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)",
             "tree = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr)",
             "rf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=0).fit(Xtr, ytr)",
             "gbm = GradientBoostingClassifier(n_estimators=300, random_state=0).fit(Xtr, ytr)",
             "for name, m in [('tree', tree), ('rf', rf), ('gbm', gbm)]:",
             "    print(f'{name:5s}: acc = {m.score(Xte, yte):.4f}')"),
    ]


def course5_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Compare AUC of the three models."),
        code("# your code here"),
    ]


def course5_ex2_solution() -> list[dict]:
    return [
        code("from sklearn.metrics import roc_auc_score",
             "for name, m in [('tree', tree), ('rf', rf), ('gbm', gbm)]:",
             "    p = m.predict_proba(Xte)[:, 1]",
             "    print(f'{name:5s}: AUC = {roc_auc_score(yte, p):.4f}')"),
    ]


def course5_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Plot the top-5 feature importances from the random forest."),
        code("# your code here"),
    ]


def course5_ex3_solution() -> list[dict]:
    return [
        code("import matplotlib.pyplot as plt",
             "import pandas as pd",
             "imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values().tail(5)",
             "fig, ax = plt.subplots(figsize=(6, 3))",
             "imp.plot.barh(ax=ax); ax.set_xlabel('importance'); plt.show()"),
    ]


# ============================================================================
# COURSE 6 — SVM (ISLP Ch 9)
# ============================================================================

def course6_lecture() -> list[dict]:
    return [
        md("# Course 6 — Support Vector Machines",
           "",
           "Maximum-margin classifiers, the kernel trick, and SVM in the p ≫ n",
           "regime on the Khan gene-expression dataset.",
           "",
           "**Sections**",
           "1. Maximum-margin classifier and support vectors (0:00–0:30)",
           "2. Soft margin and kernels (0:30–1:00)",
           "3. SVM on Khan — p ≫ n (1:00–1:30)"),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "import numpy as np",
             "import pandas as pd",
             "import matplotlib.pyplot as plt",
             "from sklearn.svm import SVC",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import train_test_split, GridSearchCV",
             "from sklearn.datasets import make_blobs, make_moons",
             "from sklearn.metrics import accuracy_score, classification_report"),
        md("## 1. Maximum-margin classifier"),
        md("With two linearly separable classes, there are infinitely many",
           "separating hyperplanes. The maximum-margin one is the unique line that",
           "is as far as possible from the nearest point of each class. The points",
           "that touch the margin are the **support vectors**."),
        code("X, y = make_blobs(n_samples=80, centers=2, cluster_std=0.8, random_state=0)",
             "svc = SVC(kernel='linear', C=100).fit(X, y)",
             "",
             "# Plot data, boundary, margins, and support vectors",
             "xx = np.linspace(X[:,0].min()-1, X[:,0].max()+1, 200)",
             "w = svc.coef_[0]; b = svc.intercept_[0]",
             "yy = -(w[0] * xx + b) / w[1]",
             "margin = 1 / np.linalg.norm(w)",
             "yy_up = yy + margin * np.sqrt(1 + (w[0]/w[1])**2)",
             "yy_dn = yy - margin * np.sqrt(1 + (w[0]/w[1])**2)",
             "",
             "fig, ax = plt.subplots(figsize=(7, 5))",
             "ax.scatter(X[y==0,0], X[y==0,1], s=30, label='class 0')",
             "ax.scatter(X[y==1,0], X[y==1,1], s=30, color='C3', label='class 1')",
             "ax.plot(xx, yy, 'k-'); ax.plot(xx, yy_up, 'k--', alpha=0.5)",
             "ax.plot(xx, yy_dn, 'k--', alpha=0.5)",
             "ax.scatter(svc.support_vectors_[:,0], svc.support_vectors_[:,1],",
             "            s=120, facecolors='none', edgecolors='black', label='SV')",
             "ax.legend(); ax.set_title('Maximum-margin classifier'); plt.show()",
             "print(f'#support vectors: {svc.n_support_}  ->  total {len(svc.support_vectors_)}')"),
        md("## 2. Soft margin and kernels"),
        md("**Soft margin (`C`)** — small C lets points violate the margin in",
           "exchange for a wider gap. Large C is hard about the margin (few SVs,",
           "low bias, high variance)."),
        code("# Two C values on the moons dataset to show the C effect",
             "Xm, ym = make_moons(n_samples=200, noise=0.3, random_state=0)",
             "fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)",
             "for ax, kernel in zip(axes, ['linear', 'poly', 'rbf']):",
             "    svc = Pipeline([('s', StandardScaler()),",
             "                    ('svc', SVC(kernel=kernel, degree=3, C=1, gamma='scale'))]).fit(Xm, ym)",
             "    xx, yy = np.meshgrid(np.linspace(Xm[:,0].min()-0.3, Xm[:,0].max()+0.3, 200),",
             "                          np.linspace(Xm[:,1].min()-0.3, Xm[:,1].max()+0.3, 200))",
             "    Z = svc.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)",
             "    ax.contourf(xx, yy, Z, alpha=0.25)",
             "    ax.scatter(Xm[ym==0,0], Xm[ym==0,1], s=12)",
             "    ax.scatter(Xm[ym==1,0], Xm[ym==1,1], s=12, color='C3')",
             "    ax.set_title(f'{kernel} kernel — acc={svc.score(Xm, ym):.3f}')",
             "plt.tight_layout(); plt.show()"),
        md("Linear can't bend; polynomial bends but rigidly; RBF curves to fit the",
           "moons almost exactly. The kernel is the heart of SVM."),
        md("## 3. SVM on Khan — p ≫ n"),
        md("Khan's gene-expression study: 63 training cases × 2308 features, 4",
           "cancer subtypes. Classic p ≫ n: more predictors than samples. SVM",
           "thrives here; an unregularized logistic regression would diverge."),
        code("xtr = load_dataset('khan-xtrain').to_numpy()",
             "ytr = load_dataset('khan-ytrain')['x'].to_numpy()",
             "xte = load_dataset('khan-xtest').to_numpy()",
             "yte = load_dataset('khan-ytest')['x'].to_numpy()",
             "print('train:', xtr.shape, '  test:', xte.shape)",
             "print('classes:', np.bincount(ytr)[1:])  # subtypes labelled 1..4"),
        code("svc = SVC(kernel='linear', C=10).fit(xtr, ytr)",
             "print(f'train accuracy = {svc.score(xtr, ytr):.4f}')",
             "print(f'test accuracy  = {svc.score(xte, yte):.4f}')",
             "print('confusion matrix on test:')",
             "from sklearn.metrics import confusion_matrix",
             "print(confusion_matrix(yte, svc.predict(xte)))"),
        md("### Tune C with a small grid (cv=3 because n=63)"),
        code("grid = GridSearchCV(SVC(kernel='linear'), {'C': [0.1, 1, 10, 100]},",
             "                     cv=3, n_jobs=-1).fit(xtr, ytr)",
             "print(f'best C = {grid.best_params_[\"C\"]}  CV acc = {grid.best_score_:.4f}')",
             "print(f'test acc with best C = {grid.best_estimator_.score(xte, yte):.4f}')"),
        md("### Recap",
           "- The maximum-margin classifier is unique; support vectors define it.",
           "- `C` softens the margin; small C = wide margin, large C = strict.",
           "- The kernel trick lets a linear method fit non-linear boundaries.",
           "- SVMs are *the* tool when p ≫ n. Use a linear kernel and tune C."),
    ]


def course6_ex1_starter() -> list[dict]:
    return [
        md("**Task 1.** Build `Pipeline(StandardScaler → SVC(kernel='rbf'))` and",
           "fit it on `penguins` (drop NaN) to predict `species` from the four",
           "numeric measurements. Report 5-fold CV accuracy."),
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.svm import SVC",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import cross_val_score",
             "# your code here"),
    ]


def course6_ex1_solution() -> list[dict]:
    return [
        code(*REPO_ROOT_BOOTSTRAP,
             "from shared.data_utils import load_dataset",
             "from sklearn.svm import SVC",
             "from sklearn.preprocessing import StandardScaler",
             "from sklearn.pipeline import Pipeline",
             "from sklearn.model_selection import cross_val_score",
             "df = load_dataset('penguins').dropna()",
             "X = df[['bill_length_mm','bill_depth_mm','flipper_length_mm','body_mass_g']]",
             "y = df['species']",
             "pipe = Pipeline([('s', StandardScaler()), ('svc', SVC(kernel='rbf'))])",
             "print(f'CV accuracy = {cross_val_score(pipe, X, y, cv=5).mean():.4f}')"),
    ]


def course6_ex2_starter() -> list[dict]:
    return [
        md("**Task 2.** Now fit *unscaled* RBF SVM on the same data. What",
           "happens to CV accuracy?"),
        code("# your code here"),
    ]


def course6_ex2_solution() -> list[dict]:
    return [
        code("acc = cross_val_score(SVC(kernel='rbf'), X, y, cv=5).mean()",
             "print(f'unscaled CV accuracy = {acc:.4f}')",
             "print('Without scaling, body_mass_g (in grams, ~3000-6000) dominates the')",
             "print('RBF distance and the model essentially ignores the bill features.')"),
    ]


def course6_ex3_starter() -> list[dict]:
    return [
        md("**Task 3.** Tune `C ∈ [0.1, 1, 10]` and `gamma ∈ ['scale', 0.1, 1.0]`",
           "with a 5-fold `GridSearchCV` on the scaled pipeline."),
        code("# your code here"),
    ]


def course6_ex3_solution() -> list[dict]:
    return [
        code("from sklearn.model_selection import GridSearchCV",
             "grid = GridSearchCV(Pipeline([('s', StandardScaler()), ('svc', SVC(kernel='rbf'))]),",
             "                     {'svc__C': [0.1, 1, 10], 'svc__gamma': ['scale', 0.1, 1.0]},",
             "                     cv=5, n_jobs=-1).fit(X, y)",
             "print(f'best params = {grid.best_params_}')",
             "print(f'best CV acc = {grid.best_score_:.4f}')"),
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
    ("course-01-classification-knn/lecture.ipynb", lambda: combine(
        course1_lecture(),
        (course1_ex1_starter(), course1_ex1_solution()),
        (course1_ex2_starter(), course1_ex2_solution()),
        (course1_ex3_starter(), course1_ex3_solution()),
    )),
    ("course-02-logistic-regression-i/lecture.ipynb", lambda: combine(
        course2_lecture(),
        (course2_ex1_starter(), course2_ex1_solution()),
        (course2_ex2_starter(), course2_ex2_solution()),
        (course2_ex3_starter(), course2_ex3_solution()),
    )),
    ("course-03-logistic-regression-ii/lecture.ipynb", lambda: combine(
        course3_lecture(),
        (course3_ex1_starter(), course3_ex1_solution()),
        (course3_ex2_starter(), course3_ex2_solution()),
        (course3_ex3_starter(), course3_ex3_solution()),
    )),
    ("course-04-decision-trees/lecture.ipynb", lambda: combine(
        course4_lecture(),
        (course4_ex1_starter(), course4_ex1_solution()),
        (course4_ex2_starter(), course4_ex2_solution()),
        (course4_ex3_starter(), course4_ex3_solution()),
    )),
    ("course-05-ensembles/lecture.ipynb", lambda: combine(
        course5_lecture(),
        (course5_ex1_starter(), course5_ex1_solution()),
        (course5_ex2_starter(), course5_ex2_solution()),
        (course5_ex3_starter(), course5_ex3_solution()),
    )),
    ("course-06-svm/lecture.ipynb", lambda: combine(
        course6_lecture(),
        (course6_ex1_starter(), course6_ex1_solution()),
        (course6_ex2_starter(), course6_ex2_solution()),
        (course6_ex3_starter(), course6_ex3_solution()),
    )),
]


def main() -> None:
    for rel, builder in NOTEBOOKS:
        path = WEEK4 / rel
        write_nb(path, builder())
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
