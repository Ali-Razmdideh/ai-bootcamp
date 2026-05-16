# Week 4 — Machine Learning: Classification

**Total time:** 9 hours · two days of three 1.5-hour sessions

Week 4 turns "predict a number" into "predict a label." Students learn to
read confusion matrices and ROC curves, fit logistic regression, grow
decision trees, vote with ensembles, and finally cross the chasm into
kernel methods with SVMs. Canonical examples track ISLP chapters 4, 8,
and 9; exercises stay on the seaborn datasets students already know.

## Day 1 — Classifier basics & linear classifiers

| Course | Topic | Folder |
|--------|-------|--------|
| 1 | Classification framing + KNN | [course-01-classification-knn/](course-01-classification-knn/) |
| 2 | Logistic Regression I — binary | [course-02-logistic-regression-i/](course-02-logistic-regression-i/) |
| 3 | Logistic Regression II — multinomial + regularized | [course-03-logistic-regression-ii/](course-03-logistic-regression-ii/) |

## Day 2 — Non-linear classifiers & the kernel trick

| Course | Topic | Folder |
|--------|-------|--------|
| 4 | Decision Trees (CART) | [course-04-decision-trees/](course-04-decision-trees/) |
| 5 | Ensembles — Bagging, Random Forest, Boosting | [course-05-ensembles/](course-05-ensembles/) |
| 6 | Support Vector Machines | [course-06-svm/](course-06-svm/) |

## The arc

Day 1 says "a classifier is a function from features to a label" and pours
three different shapes of that function: KNN (geometric), binary logistic
(linear in log-odds), multinomial logistic (the softmax habit you'll need
for neural nets). Day 2 walks off the linear cliff: trees split greedily,
ensembles average the noise away, and kernels make the linear decision
boundary live in a higher-dimensional space.

## Datasets

ISLP CSVs (`Default`, `Smarket`, `Carseats`, `Boston`, `Khan_*`) fetched
through `shared.data_utils.load_dataset(name)`.

## Interactive slides

Every course's `slides/index.html` is a self-contained Reveal.js deck where
each notebook code cell appears as a **runnable example** (prefilled answer
+ description + *Run* button) and each notebook exercise appears as a
**checked exercise** (starter code + *Run & Check* + reference solution on
failure). Code runs in the browser via Pyodide, which lazy-loads
scikit-learn / pandas / matplotlib on first use. ISLP datasets (Default,
Smarket, Carseats, …) that the notebooks load via `shared.data_utils` are
inlined as small seeded synthetic DataFrames in the slide examples so they
work without filesystem access.

## Running everything

```bash
uv sync
uv run jupyter lab weeks/week-04-classification/
```

To regenerate every notebook from source:

```bash
uv run python scripts/build_week04_notebooks.py
```
