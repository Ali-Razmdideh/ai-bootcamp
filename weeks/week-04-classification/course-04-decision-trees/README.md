# Course 4 — Decision Trees

**Duration:** 1.5 hours
**Why this matters:** A single decision tree is the most interpretable model in the course: every prediction is a flowchart. Students who understand trees understand the building block under random forests and gradient boosting.

## Schedule

| Time        | Topic                       |
|-------------|-----------------------------|
| 0:00 – 0:30 | CART — recursive splitting on Gini or entropy |
| 0:30 – 1:00 | Regression trees and cost-complexity pruning |
| 1:00 – 1:30 | Strengths, weaknesses, and the road to ensembles |

## Files

- `slides/index.html` — Reveal.js deck. Open it in a browser; every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter code + *Run & Check* + reference solution on failure). Append `?showNotes` to see the speaker notes.
- `lecture.ipynb` — live-coding notebook that mirrors the slides one-for-one,
  followed by three exercises (each with its solution).

## Learning outcomes

By the end of the session a student can:

1. Grow, plot, and prune a decision tree with sklearn
2. Explain Gini impurity and why a tree chooses a particular split
3. Articulate why a single deep tree overfits and how pruning helps

## How to run

```bash
uv run jupyter lab weeks/week-04-classification/course-04-decision-trees/
```
