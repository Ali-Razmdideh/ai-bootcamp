# Design: Week 04 · Course 07 — Decision Boundary Slides

**Date:** 2026-06-11  
**File:** `weeks/week-04-classification/course-07-decision-trees/slides/index.html`

---

## Goal

Add a new **Part 0 — How Splits Are Chosen** section (7 slides) inserted immediately after the Roadmap slide and before the existing Part 1. The section gives students the mathematical and visual foundation for understanding decision boundaries before they encounter the regression and classification tree applications.

---

## Placement

- Insert after the roadmap `<section>` (line ~44) and before the Part 1 `<section>` group (line ~46).
- Add one new card to the roadmap `three-col` grid (prepend, shifting all existing time labels by ~15 min).
- All existing part kicker timestamps shift by 15 min (e.g. Part 1 becomes `0:15 – 0:40`).

---

## Slide Sequence

### Slide 1 — Title slide
- Kicker: `Part 0 · 0:00 – 0:15`
- H1: "How Splits Are Chosen"
- Muted subtitle: `recursive binary splitting · threshold scan · greedy search`

### Slide 2 — The search problem
- H2: "The search problem"
- Plain-language setup: at each node we have N observations and P features; find the (feature j, threshold s) pair that produces the purest/most homogeneous children.
- Formula box defining the two child regions:
  - R_L(j, s) = { x | x_j < s }
  - R_R(j, s) = { x | x_j ≥ s }
- Callout: "We repeat this search independently at every node — recursively."

### Slide 3 — Regression: RSS criterion (expanded)
- H2: "Regression splits: minimise RSS"
- Full formula:
  - ȳ_L = mean of y_i where x_j < s
  - ȳ_R = mean of y_i where x_j ≥ s
  - Cost(j, s) = RSS_L + RSS_R = Σ_{i∈R_L}(y_i − ȳ_L)² + Σ_{i∈R_R}(y_i − ȳ_R)²
- Worked numeric mini-example in a table: 6 data points (x, y), three candidate thresholds (s=2, s=4, s=6), RSS_L, RSS_R, total for each — highlight the winning row.
- Fragment callout: "Pick the (j, s) with the smallest total RSS across all features."

### Slide 4 — Visualization: threshold scan (regression)
- H2: "Scanning thresholds — regression"
- SVG inline diagram (two panels stacked):
  - Top: 1-D number line with labelled data points (dots), a vertical dashed line labelled "threshold s".
  - Bottom: line graph of RSS_total vs. s, with a marked minimum and vertical dashed line at the argmin.
- Caption: "For each feature j, sort the values and evaluate every midpoint. The global minimum across all j wins."
- This SVG is generated inline (no external file needed for a schematic).

### Slide 5 — Classification: weighted impurity gain
- H2: "Classification splits: maximise impurity gain"
- Formula block:
  - ΔG(j, s) = G(parent) − (n_L / n)·G(R_L) − (n_R / n)·G(R_R)
  - where G is Gini index (or entropy — same formula structure)
- Worked numeric mini-example in a table: 10 binary-labelled points, two candidate thresholds:
  - s=3: n_L=4 (3 pos, 1 neg), n_R=6 (2 pos, 4 neg) → compute G_L, G_R, ΔG
  - s=7: n_L=7 (4 pos, 3 neg), n_R=3 (1 pos, 2 neg) → compute G_L, G_R, ΔG
  - Highlight winning threshold.
- Fragment callout: "We pick the (j, s) with the **largest** ΔG — the split that removes the most impurity."

### Slide 6 — Visualization: threshold scan (classification)
- H2: "Scanning thresholds — classification"
- SVG inline diagram (two panels):
  - Top: 1-D axis with coloured dots (two classes), vertical dashed threshold line.
  - Bottom: Gini gain vs. threshold curve, with marked maximum.
- Caption: "Two features shown. Feature 2 has a higher peak → it wins the split at that node."

### Slide 7 — The full search loop
- H2: "The full search loop"
- Pseudocode block (styled as `<pre>`):
  ```
  for each feature j in 1..P:
      sort observations by x_j
      for each midpoint s between adjacent values:
          compute Cost(j, s)          # RSS or weighted impurity
          if Cost(j, s) < best_cost:
              best_j, best_s = j, s
  split node on (best_j, best_s)
  recurse on left and right children
  ```
- Bullet fragments:
  - Complexity: O(n p log n) per level.
  - Greedy: no lookahead; locally optimal at each node.
- Callout: "Greedy search is fast but not globally optimal — deep trees overfit because each split ignores future consequences."

---

## SVG Diagrams

Slides 4 and 6 use inline SVG schematics (not external files). They are schematic/illustrative — exact coordinates are approximate, not data-driven. Keep them simple: axis lines, dots, a curve, a vertical marker.

---

## Roadmap Update

Add a new card to the roadmap grid as the first entry:

> **0:00 · 0:15** — How Splits Are Chosen  
> threshold scan · RSS · impurity gain

Shift all existing time labels by +15 min.

---

## What is NOT changing

- The existing Part 1–4 content and examples are untouched except for kicker timestamp strings.
- No new external SVG files needed (diagrams are inline).
- No CSS changes needed; uses existing `.callout`, `.fragment`, `<pre>`, table styles.
