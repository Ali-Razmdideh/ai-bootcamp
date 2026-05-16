# Course 5 — Matplotlib Essentials

**Duration:** 1.5 hours
**Why this matters:** Numbers lie; pictures rarely do. Every model you train
in the rest of the bootcamp will be debugged by a plot — residuals, learning
curves, decision boundaries, attention maps. Matplotlib is the engine
underneath every higher-level plotting library, so a fluent grasp pays off
forever.

## Schedule

| Time        | Topic                            |
|-------------|----------------------------------|
| 0:00 – 0:30 | The Figure / Axes mental model   |
| 0:30 – 1:00 | The chart zoo                    |
| 1:00 – 1:30 | Subplots & saving                |

## Files

- `slides/index.html` — Reveal.js deck. Every notebook example becomes a runnable Pyodide block (prefilled answer + *Run*), and every exercise becomes a checked challenge (starter + *Run & Check* + reference solution on failure).
- `lecture.ipynb` — live-coding notebook + three exercises with solutions.

## Learning outcomes

By the end of the session a student can:

1. Explain the Figure / Axes / Artist hierarchy and produce any plot with
   the explicit `fig, ax = plt.subplots()` API.
2. Pick the right chart for the data: scatter for relations, hist/box for
   distributions, bar for counts.
3. Build a multi-Axes figure with shared axes, a suptitle, and
   `tight_layout`; save it to PNG.

## How to run

```bash
uv run jupyter lab weeks/week-01-foundations/course-05-matplotlib/
```
