"""Generate every Reveal.js slide deck for Week 3 and Week 4.

Each deck is rendered from a Python content spec into a single index.html.
Re-running is idempotent. To edit a deck, change the spec below and re-run.

Usage:
    python3 scripts/build_slides.py
"""
from __future__ import annotations

import html
import re
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


def svg_diagram(svg_content: str, extra_style: str = "") -> str:
    """Wrap an inline SVG for use inside a slide body (Week-1 style)."""
    style = f' style="{extra_style}"' if extra_style else ""
    return f'<div class="diagram-wrap"{style}>{svg_content}</div>'


def example_slide(title: str, prompt: str, code: str,
                  packages: str = "numpy,matplotlib") -> str:
    """Produce a Week-1-style runnable code block as a full slide section."""
    escaped = html.escape(code)
    return f"""  <section class="example" data-packages="{packages}">
    <h2>{title}</h2>
    <div class="ex-prompt">{prompt}</div>
<textarea class="ex-code">{escaped}</textarea>
    <div class="ex-controls">
      <button class="ex-run">Run</button>
      <button class="ex-reset">Reset</button>
      <span class="ex-status"></span>
    </div>
    <pre class="ex-output"></pre>
  </section>
"""


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


def _add_minutes(time_str: str, offset_h: float) -> str:
    h, m = (int(x) for x in time_str.split(":"))
    total = h * 60 + m + int(offset_h * 60)
    return f"{total // 60}:{total % 60:02d}"


def _retime_summary_slot(slot: str, offset_h: float) -> str:
    if " · " not in slot:
        return slot
    start, end = slot.split(" · ", 1)
    return f"{_add_minutes(start.strip(), offset_h)} · {_add_minutes(end.strip(), offset_h)}"


def _retime_part_kicker(kicker: str, part_num: int, offset_h: float) -> str:
    m = re.search(r"(\d+:\d+)\s*[–-]\s*(\d+:\d+)", kicker)
    if not m:
        return kicker
    start, end = m.group(1), m.group(2)
    return f"Part {part_num} · {_add_minutes(start, offset_h)} – {_add_minutes(end, offset_h)}"


def merge_deck_specs(
    a: dict,
    b: dict,
    *,
    title: str,
    kicker: str,
    subtitle: str,
    callout: str,
    recap_items: list[str],
    recap_callout: str,
    offset_h: float = 1.5,
) -> dict:
    n_parts_a = len(a["parts"])
    parts_b = []
    for i, p in enumerate(b["parts"], start=1):
        p2 = dict(p)
        p2["kicker"] = _retime_part_kicker(p["kicker"], n_parts_a + i, offset_h)
        parts_b.append(p2)
    summary_b = [
        (_retime_summary_slot(s[0], offset_h), s[1], s[2]) for s in b["parts_summary"]
    ]
    return {
        "title": title,
        "kicker": kicker,
        "subtitle": subtitle,
        "parts_summary": a["parts_summary"] + summary_b,
        "callout": callout,
        "parts": a["parts"] + parts_b,
        "recap_items": recap_items,
        "recap_callout": recap_callout,
    }


# ============================================================================
# WEEK 3
# ============================================================================

WEEK3 = ROOT / "weeks" / "week-03-machine-learning"

W3_SL = {
    "title": "What is Statistical Learning?",
    "kicker": "Week 3 · Course 1",
    "subtitle": "From real-world motivation to f(X)+ε, bias-variance trade-off, and classification",
    "parts_summary": [
        ("Part 1", "Why it matters", "Watson, Varian, and 8 real problems."),
        ("Part 2", "Types of learning", "Supervised, unsupervised, semi-supervised."),
        ("Part 3", "Y = f(X) + ε", "Notation, regression function, estimation."),
        ("Part 4", "Estimating f", "KNN, curse of dimensionality, parametric models."),
        ("Part 5", "Model accuracy", "Train/test MSE and bias-variance trade-off."),
        ("Part 6", "Classification", "Bayes classifier and KNN boundaries."),
    ],
    "callout": "Statistical learning is the set of tools for estimating f — the function that maps inputs X to output Y. This course builds the full mental model: from Watson to the bias-variance decomposition.",
    "parts": [
        # ── Part 1 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 1",
            "title": "Why Statistical Learning Matters",
            "subtitle": "from Watson to eight real problems",
            "slides": [
                slide("Statistics in the news — IBM Watson",
                      '<blockquote style="font-style:italic;border-left:4px solid #c00;padding-left:1em;">'
                      '"It\'s machine learning allows the computer to become smarter as it tries to answer questions — '
                      'and to learn as it gets them right or wrong."'
                      '</blockquote>'
                      '<p class="muted" style="margin-top:0.8em;">— David Ferrucci (PI of IBM Watson DeepQA), on why Watson beat Ken Jennings at <em>Jeopardy!</em> — <em>DailyFinance</em>, February 8, 2011.</p>',
                      "Watson's Jeopardy win was a landmark. It was not rule-based programming — it was machine learning: iterating on labelled question-answer pairs to build a system that improves with experience. The distinction matters: you couldn't write down rules for every possible Jeopardy clue."),
                slide("Statistics in the news — Hal Varian",
                      '<blockquote style="font-style:italic;border-left:4px solid #c00;padding-left:1em;">'
                      '"I keep saying that the sexy job in the next 10 years will be statisticians. And I\'m not kidding."'
                      '</blockquote>'
                      '<p class="muted" style="margin-top:0.6em;">— Hal Varian, Chief Economist at Google — <em>New York Times</em>, August 5, 2009.</p>'
                      '<p style="margin-top:0.8em;">Carrie Grimes (Harvard anthropology → Google): '
                      '"People think of field archaeology as Indiana Jones, but much of what you really do is data analysis."</p>',
                      "Varian's quote was prescient — by 2015 'data scientist' was everywhere. The underlying skill is the same: extract signal from noisy data. The NYT article is from 2009, before deep learning, before TensorFlow. The insight was that demand for quantitative reasoning skills would far outpace supply."),
                slide("Statistics in the news — FiveThirtyEight",
                      '<p>Nate Silver\'s <strong>FiveThirtyEight</strong> aggregated polls with a statistical model to predict state-level election results with remarkable accuracy.</p>'
                      + two_col(
                          '<p style="font-size:1.8em;margin:0;"><strong>90.9%</strong></p>'
                          '<p class="muted" style="margin:0;">Chance of winning (+13.5 since Oct. 30)</p>'
                          '<p style="margin-top:0.6em;">vs.</p>'
                          '<p style="font-size:1.8em;margin:0;"><strong>9.1%</strong></p>'
                          '<p class="muted" style="margin:0;">(−13.5 since Oct. 30)</p>',
                          '<p>Silver\'s book <em>The Signal and the Noise</em> (2012) explains why most predictions fail: mistaking noise for signal.</p>'
                          '<p>Key idea: combine many noisy polls via a statistical model to produce a more stable probability estimate.</p>'
                      ),
                      "FiveThirtyEight used weighted poll averages with adjustments for house effects, likely-voter screens, and economic fundamentals. Classic statistical learning applied to publicly available data — no proprietary information required."),
                slide("Eight statistical learning problems",
                      bullets([
                          "Identify the <strong>risk factors for prostate cancer</strong>.",
                          "Classify a recorded phoneme based on a <strong>log-periodogram</strong>.",
                          "Predict whether someone will have a <strong>heart attack</strong> from demographic, diet and clinical measurements.",
                          "Customize an <strong>email spam detection</strong> system.",
                          "Identify the numbers in a <strong>handwritten zip code</strong>.",
                          "Classify a tissue sample into one of several <strong>cancer classes</strong>, based on a gene expression profile.",
                          "Establish the relationship between <strong>salary and demographic variables</strong> in population survey data.",
                          "Classify the pixels in a <strong>LANDSAT image</strong>, by usage.",
                      ], fragments=False),
                      "All eight are real published datasets used in ISLR. Point out the variety: some have quantitative Y (salary, lpsa), some have categorical Y (cancer subtype, spam/ham). Some we want to understand (what drives PSA?), some we want to predict (is this email spam?). The same statistical machinery handles all of them."),
            ],
        },
        # ── Part 2 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 2",
            "title": "Eight Problems Up Close",
            "subtitle": "what the data looks like",
            "slides": [
                slide("Prostate cancer — predict lpsa",
                      '<img src="img/ch1_prostate_scatter.svg" style="width:55%;float:right;margin-left:1em;">'
                      '<p><strong>Data:</strong> 97 men; 8 clinical predictors; outcome = <code>lpsa</code> (log PSA).</p>'
                      + bullets([
                          "<code>lcavol</code> (log cancer volume) has the strongest relationship with <code>lpsa</code>.",
                          "<code>lcp</code> and <code>lcavol</code> are correlated — multicollinearity matters.",
                          "<code>svi</code> (seminal vesicle invasion) is binary — visible as two-column strips.",
                          "<code>gleason</code> is an ordered integer — only a few distinct values.",
                      ], fragments=False),
                      "Walk through the scatter matrix. The top row (lpsa vs everything) is what matters for prediction. Collinearity between predictors is why we need multiple regression, not separate simple regressions."),
                slide("Phoneme classification — aa vs ao",
                      '<img src="img/ch1_phoneme.svg" style="width:100%;max-height:52vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.3em;"><strong>Top:</strong> log-periodograms for "aa" (green) and "ao" (orange) overlap at high frequencies. <strong>Bottom:</strong> raw LR coefficients (grey bars, noisy) vs. smooth restricted fit (red curve) — regularisation is needed.</p>',
                      "The bottom panel shows raw LR coefficients (grey bars — very noisy) vs. a restricted smooth fit (red curve). The smooth version is correct — it imposes that nearby frequencies should have similar coefficients. This motivates regularisation."),
                slide("Heart attack prediction — South African data",
                      '<img src="img/ch1_heartattack_scatter.svg" style="width:52%;float:right;margin-left:1em;">'
                      '<p><strong>Data:</strong> 462 males; outcome: <strong>chd</strong> (coronary heart disease, binary). Predictors: sbp, tobacco, ldl, famhist, obesity, alcohol, age.</p>'
                      '<p><span style="color:#c00;">■</span> chd=1 &nbsp; <span style="color:#0cc;">■</span> chd=0</p>'
                      + bullets([
                          "<strong>Age</strong> and <strong>ldl</strong>: clearest separation.",
                          "<strong>Tobacco</strong>: heavily right-skewed.",
                          "<strong>famhist</strong>: binary — two-column strips.",
                          "No single predictor separates perfectly.",
                      ], fragments=False),
                      "Classification problem, binary outcome. No single predictor is sufficient — but together they carry substantial signal. South African Heart Disease dataset (Rousseauw et al., 1983)."),
                slide("Spam detection — customised filters",
                      '<img src="img/ch1_spam_table.svg" style="width:100%;max-height:60vh;object-fit:contain;">',
                      "The word 'george' appears frequently in legitimate email (it's the recipient) but never in spam — a personalised signal. 'free', '!', and 'remove' are classic spam signals. The key word 'customised' in the problem statement: a generic spam filter trained on someone else's email would miss the 'hp' and 'george' signals."),
                slide("Handwritten zip codes — digit recognition",
                      '<img src="img/ch1_digits.svg" style="width:100%;max-height:55vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.3em;">p = 256 features (16×16 pixels) · K = 10 classes · N ≈ 9000 training images. The same digit looks dramatically different across writers.</p>',
                      "Key teaching point: 256 inputs, 10 output classes, no natural ordering of classes. A 9 can look like a 4; an 8 can look like a 3. This dataset was a key early benchmark for neural networks (LeCun et al., 1989)."),
                slide("Cancer gene expression — breast cancer subtypes",
                      '<img src="img/ch1_cancer_heatmap.svg" style="width:60%;float:right;margin-left:1em;">'
                      '<p><strong>Data:</strong> Gene expression from breast tumour biopsies. Thousands of genes; ~200 patient samples.</p>'
                      '<p>Hierarchical clustering heatmap (green = below average, red = above average) reveals four subtypes — <em>without any pathologist labels</em>:</p>'
                      + bullets([
                          '<strong>Luminal A</strong> — most common, best prognosis.',
                          '<strong>Luminal B</strong> — more aggressive.',
                          '<strong>ERBB2+</strong> — HER2-positive.',
                          '<strong>Basal</strong> — triple-negative, worst prognosis.',
                      ], fragments=False),
                      "Perou et al. (2000) transformed breast oncology with this analysis. The subtypes have different clinical outcomes and respond differently to treatment — validating the data-driven grouping."),
                slide("Salary and demographics",
                      '<img src="img/ch1_salary.svg" style="width:100%;max-height:57vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.2em;">Central Atlantic USA males, 2009 CPS. <strong>Age:</strong> non-linear (peaks ~40). <strong>Year:</strong> slight upward trend. <strong>Education:</strong> ordered categorical, clear step-up effect.</p>',
                      "The three panels show three different types of predictor-response relationships: non-linear continuous (Age), linear continuous (Year), and ordered categorical (Education). A good model of Wage needs to handle all three."),
                slide("LANDSAT image classification",
                      '<img src="img/ch1_landsat.svg" style="width:100%;max-height:58vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.2em;">4 spectral bands per pixel → classify into: red soil, cotton crop, vegetation stubble, mixture, grey soil, damp grey soil. Predicted map (right) nearly matches the true map (middle).</p>',
                      "Multi-class pixel-level classification. Only 4 features per pixel, but the classes are well-separated in spectral space — KNN and LDA work well here."),
            ],
        },
        # ── Part 3 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 3",
            "title": "Types of Learning",
            "subtitle": "supervised, unsupervised, and semi-supervised",
            "slides": [
                slide("The supervised learning problem",
                      two_col(
                          '<h3>The components</h3>'
                          + bullets([
                              "<strong>Y</strong> — outcome (response, target, dependent variable).",
                              "<strong>X = (X₁, …, Xₚ)</strong> — p predictors (features, inputs, covariates).",
                              "<strong>Training data</strong> (x₁,y₁), …, (xN,yN) — N labelled observations.",
                          ], fragments=False),
                          '<h3>Two sub-types</h3>'
                          + bullets([
                              "<strong>Regression</strong>: Y is quantitative (wage, lpsa, sales).",
                              "<strong>Classification</strong>: Y is categorical (spam/ham, digit 0–9, cancer subtype).",
                          ], fragments=False)
                          + '<p class="muted" style="margin-top:0.8em;">Both regression and classification use the same framework; only the type of Y and the loss function change.</p>'
                      ),
                      "The word 'supervised' comes from having labelled examples — a supervisor told us the correct answer for each training case. The goal is to generalise: given a new X not in training, predict Y correctly."),
                slide("Objectives of supervised learning",
                      bullets([
                          "<strong>Accurately predict</strong> unseen test cases.",
                          "<strong>Understand</strong> which inputs affect the outcome and how.",
                          "<strong>Assess</strong> the quality of our predictions and inferences.",
                      ]),
                      "These three objectives often conflict. Maximising prediction accuracy can require a black-box model (random forest, neural net) that sacrifices interpretability. Maximising interpretability (simple linear model) may sacrifice accuracy. The right balance depends on the application."),
                slide("Unsupervised learning",
                      two_col(
                          '<h3>No outcome variable</h3>'
                          '<p>Just predictors X measured on a set of samples. No Y to predict.</p>'
                          '<h3>Objectives (fuzzier)</h3>'
                          + bullets([
                              "Find <strong>groups</strong> of similar samples (clustering).",
                              "Find <strong>features</strong> that vary together.",
                              "Find <strong>low-dimensional structure</strong> in high-d data (PCA).",
                          ], fragments=False),
                          '<h3>The challenge</h3>'
                          '<p>No ground truth to evaluate against. Hard to know how well you are doing.</p>'
                          '<h3>Still very useful</h3>'
                          '<p>Often a pre-processing step for supervised learning — or the only option when labels are unavailable.</p>'
                          '<p class="muted">Example: the cancer subtypes from Part 2 emerged from unsupervised clustering with no pathologist labels.</p>'
                      ),
                      "Unsupervised learning is harder because there is no right answer. K-means, hierarchical clustering, and PCA are the main tools. It is sometimes called 'learning without a teacher'."),
                slide("Semi-supervised learning",
                      two_col(
                          '<h3>The setting</h3>'
                          '<p>A small set of <strong>labelled</strong> examples and a much larger set of <strong>unlabelled</strong> examples.</p>'
                          '<h3>Why it arises</h3>'
                          + bullets([
                              "Labels are expensive: pathologist time, human annotation, clinical trials.",
                              "Raw data is cheap: images, text, genomic sequences.",
                          ], fragments=False),
                          '<h3>The idea</h3>'
                          '<p>Use the unlabelled data to learn the <em>structure</em> of X (clusters, manifolds), then use the few labelled examples to attach Y to that structure.</p>'
                          '<h3>Modern examples</h3>'
                          + bullets([
                              "Foundation models (GPT, BERT): pre-trained on vast unlabelled text, fine-tuned with small labelled sets.",
                              "Medical imaging: one annotated scan per patient, thousands without labels.",
                          ], fragments=False)
                      ),
                      "Semi-supervised learning sits between supervised and unsupervised. It is the dominant paradigm in modern deep learning: pre-training on unlabelled data (self-supervised learning) followed by supervised fine-tuning on a small labelled dataset."),
                slide("The Netflix Prize — supervised or unsupervised?",
                      '<p>October 2006: Netflix releases a matrix of ratings: <strong>18,000 movies</strong> × <strong>400,000 customers</strong>, each rating 1–5 stars. The matrix is <strong>98% missing</strong>.</p>'
                      '<p>Goal: predict the rating for 1 million missing (customer, movie) pairs. Netflix\'s own algorithm achieved RMSE = 0.953. The prize: <strong>$1,000,000</strong> for the first team achieving 10% improvement.</p>'
                      '<p class="callout">Looks unsupervised (no explicit Y column), but each known rating is a labelled observation. This is a supervised regression problem with a massive missing-data challenge.</p>',
                      "The Netflix Prize was enormously influential. It introduced matrix factorisation to a wide audience, showed that ensemble methods (blending 100+ models) reliably beat any single model, and raised important questions about privacy (the de-anonymisation paper by Narayanan and Shmatikoff appeared shortly after)."),
                slide("BellKor's Pragmatic Chaos wins",
                      '<p>After nearly 3 years, two teams simultaneously achieved the 10% threshold. <strong>BellKor\'s Pragmatic Chaos</strong> won by 20 minutes — their submission was received first.</p>'
                      '<table style="font-size:0.88em;margin:0.8em auto;border-collapse:collapse;">'
                      '<tr style="border-bottom:2px solid #ccc;"><th>Rank</th><th>Team</th><th>RMSE</th><th>% Improvement</th></tr>'
                      '<tr><td>1</td><td>BellKor\'s Pragmatic Chaos</td><td>0.8567</td><td>10.06</td></tr>'
                      '<tr><td>2</td><td>The Ensemble</td><td>0.8567</td><td>10.06</td></tr>'
                      '<tr><td>3</td><td>Grand Prize Team</td><td>0.8582</td><td>9.90</td></tr>'
                      '<tr><td>4</td><td>Opera Solutions and Vandelay United</td><td>0.8588</td><td>9.84</td></tr>'
                      '</table>'
                      '<p class="muted" style="font-size:0.85em;">The winning solution blended over 100 different models. The best single method was matrix factorisation.</p>',
                      "No single algorithm won the prize. Blending uncorrelated models always beats any individual model — this is the fundamental insight behind ensemble methods (which we cover in Week 4)."),
                slide("Statistical Learning vs Machine Learning",
                      two_col(
                          '<h3>Different roots</h3>'
                          + bullets([
                              "<strong>Machine learning</strong> arose as a subfield of Artificial Intelligence.",
                              "<strong>Statistical learning</strong> arose as a subfield of Statistics.",
                              "<em>Both</em> focus on supervised and unsupervised problems using the same algorithms.",
                          ], fragments=False),
                          '<h3>Different emphases</h3>'
                          + bullets([
                              "<strong>ML</strong>: large-scale applications, prediction accuracy, computational efficiency.",
                              "<strong>SL</strong>: models, interpretability, precision and uncertainty of estimates.",
                              "The distinction has blurred enormously — there is massive cross-fertilisation.",
                          ], fragments=False)
                          + '<p class="callout" style="margin-top:0.6em;">"Machine learning has the upper hand in marketing." — Hastie &amp; Tibshirani</p>'
                      ),
                      "Practical takeaway: 'ML' and 'statistical learning' are solving the same problems. If you come from CS you say ML; if you come from statistics you say SL. This course uses the ISLR framework (statistical flavour) but all the code is scikit-learn (ML flavour)."),
            ],
        },
        # ── Part 4 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 4",
            "title": "The Statistical Framework — Y = f(X) + ε",
            "subtitle": "notation, the regression function, and how to estimate f",
            "slides": [
                slide("Running example: the Advertising data",
                      '<img src="img/ch2_advertising.svg" style="width:100%;max-height:55vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.2em;">200 markets. <strong>TV</strong>: strong (but non-linear). <strong>Radio</strong>: moderate. <strong>Newspaper</strong>: weak. Goal: Sales ≈ f(TV, Radio, Newspaper).</p>',
                      "The Advertising dataset is the canonical ISLR example. Three predictors, one outcome, 200 rows. The simplicity lets us focus on the methodology without fighting the data."),
                slide("Notation: Y = f(X) + ε",
                      '<p>We observe a response <strong>Y</strong> and p predictors <strong>X = (X₁, X₂, …, Xₚ)</strong>.</p>'
                      '<p style="text-align:center;font-size:1.6em;margin:0.8em 0;">Y = f(X) + ε</p>'
                      + bullets([
                          "<strong>f</strong> — the systematic information X contains about Y. Fixed but unknown.",
                          "<strong>ε</strong> — error term: measurement noise, unmeasured causes, randomness. Independent of X, mean zero.",
                          "Statistical learning is the set of approaches for <strong>estimating f</strong>.",
                      ], fragments=False),
                      "Write this on the board. This single equation is the foundation of everything in the course. Every model we see — linear regression, decision trees, neural networks — is a different way of estimating f."),
                slide("What is f(X) good for?",
                      two_col(
                          '<h3>Prediction</h3>'
                          '<p>With a good f̂, predict Y at new X = x. The internal form of f̂ does not matter — a black box is fine if it predicts well.</p>'
                          '<p><em>Example:</em> Credit card default. Predict P(default | X) to decide whether to approve a loan. The model can be complex — we only care about the final probability.</p>',
                          '<h3>Inference</h3>'
                          '<p>Understand which Xⱼ matter and how they affect Y.</p>'
                          '<p><em>Example:</em> Income survey. Seniority and years of education have big impacts on Income; marital status typically does not. We need a simple, interpretable model to make such statements.</p>'
                      ),
                      "Prediction and inference pull in opposite directions. Prediction wants the most accurate f̂. Inference wants f̂ to be simple enough to explain. Depending on the complexity of f, we may be able to understand how each component Xⱼ affects Y."),
                slide("Is there an ideal f(X)?",
                      '<img src="img/ch2_regression_function.svg" style="width:55%;float:right;margin-left:1em;">'
                      '<p>At X = x there are many possible Y values (due to ε). The best single prediction is:</p>'
                      '<p style="text-align:center;font-size:1.4em;margin:0.8em 0;"><strong>f(x) = E[Y | X = x]</strong></p>'
                      '<p>The <strong>regression function</strong> — the average Y at a given x. The red curve threads through the cloud; each grey point deviates by ε.</p>',
                      "Draw on the board: a scatter plot of (x, y) pairs. The conditional mean curve threads through the middle. Each point deviates from the curve by ε. The curve is the signal; the deviations are the noise."),
                slide("Reducible vs irreducible error",
                      '<p>For any estimate f̂(x) of f(x):</p>'
                      '<p style="text-align:center;font-size:1.1em;margin:0.8em 0;">'
                      'E[(Y − f̂(X))²|X=x] = '
                      '<span style="color:#c00;">[f(x) − f̂(x)]²</span>'
                      ' + '
                      '<span style="color:#0066cc;">Var(ε)</span>'
                      '</p>'
                      + two_col(
                          '<p><span style="color:#c00;"><strong>Reducible error</strong></span></p>'
                          '<p>The gap between our f̂ and the true f. Can be closed with more data, better features, or smarter models.</p>',
                          '<p><span style="color:#0066cc;"><strong>Irreducible error</strong></span></p>'
                          '<p>Var(ε). Even knowing f exactly, we still err on individual Y values because of noise.</p>'
                      )
                      + '<p class="callout" style="margin-top:0.8em;">The irreducible error sets a hard floor on test error. No model — however complex — can beat Var(ε).</p>',
                      "This is one of the most important ideas in the course. When students ask 'why isn't the test error zero?', the answer is: irreducible error. The goal is to push test error as close to Var(ε) as possible by minimising [f − f̂]²."),
            ],
        },
        # ── Part 5 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 5",
            "title": "Estimating f and Assessing Models",
            "subtitle": "from nearest-neighbor to the bias-variance trade-off",
            "slides": [
                slide("How to estimate f — nearest-neighbor averaging",
                      '<p>We want f̂(x) ≈ E[Y | X = x]. Problem: typically no training points have <em>exactly</em> X = x.</p>'
                      '<p>Solution — relax to a <strong>neighbourhood</strong>:</p>'
                      '<p style="text-align:center;font-size:1.3em;margin:0.8em 0;">f̂(x) = Ave(Y | X ∈ 𝒩(x))</p>'
                      '<p>Average Y over the k nearest neighbours of x in the training data.</p>'
                      + bullets([
                          "Works well for small p (p ≤ 4) and large N.",
                          "A sliding window on a 1D scatter traces out f(x) by averaging nearby Y values.",
                      ], fragments=False),
                      "Draw the sliding window. As the window moves right, the local average traces the conditional mean. The window width controls bias vs variance: wide window = more data averaged = lower variance but higher bias."),
                slide("Curse of dimensionality",
                      '<img src="img/ch2_curse_dim.svg" style="width:100%;max-height:52vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.2em;"><strong>Left:</strong> 10% neighbourhood in 2D stays local. <strong>Right:</strong> radius needed to capture 10% of volume grows rapidly — at p=10 it spans almost the entire space.</p>',
                      "At p=10, capturing 10% of the data requires going out to radius 0.80 in a unit hypercube. The 'neighbourhood' is no longer local — you are averaging points that are nothing like x. This is why parametric models (that impose structure on f) become necessary as p grows."),
                slide("Parametric models — the linear model",
                      '<p>Instead of estimating f freely at every x, assume f has a specific form with few parameters:</p>'
                      '<p style="text-align:center;font-size:1.3em;margin:0.8em 0;">f<sub>L</sub>(X) = β₀ + β₁X₁ + β₂X₂ + … + βₚXₚ</p>'
                      + bullets([
                          "A linear model is specified by <strong>p + 1 parameters</strong>: β₀, β₁, …, βₚ.",
                          "Estimate the parameters by <strong>fitting to training data</strong> (e.g. least squares).",
                          "Almost never exactly correct, but often a good <strong>interpretable approximation</strong> to the unknown true f.",
                      ], fragments=False),
                      "The key advantage over nearest-neighbor: the linear model makes a strong assumption about f's shape, which drastically reduces the amount of data needed to estimate it well. The price is bias if the true f is non-linear."),
                slide("Linear vs quadratic fit",
                      '<img src="img/ch2_linear_quad.svg" style="width:100%;max-height:57vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.2em;"><strong>Top:</strong> linear f̂<sub>L</sub>(x) = β̂₀ + β̂₁x — misses the curvature (high bias). <strong>Bottom:</strong> quadratic f̂<sub>Q</sub>(x) = β̂₀ + β̂₁x + β̂₂x² — fits much better.</p>',
                      "The quadratic model is still parametric but more flexible than linear. Adding basis terms keeps increasing flexibility. The question is always: how flexible should f̂ be? Too rigid → underfit. Too flexible → overfit."),
                slide("The income surface — three fits",
                      two_col(
                          '<img src="img/ch2_income_true.svg" style="width:100%;height:26vh;object-fit:contain;">'
                          '<p class="muted" style="font-size:0.75em;text-align:center;margin:0;">True f — smooth curved surface</p>',
                          '<img src="img/ch2_income_linear.svg" style="width:100%;height:26vh;object-fit:contain;">'
                          '<p class="muted" style="font-size:0.75em;text-align:center;margin:0;">Linear f̂ — flat plane (underfit)</p>'
                      )
                      + '<img src="img/ch2_income_overfit.svg" style="width:50%;display:block;margin:0.4em auto 0;">'
                      + '<p class="muted" style="font-size:0.75em;text-align:center;margin:0;"><strong>Overfit spline</strong> — zero training error, generalises poorly</p>'
                      + '<p class="callout" style="margin-top:0.4em;"><strong>Overfitting</strong>: the model memorised training noise. Training error ≈ 0, test error is large.</p>',
                      "The three surface plots from ISLR Figs 3.2–3.4. True f is non-linear; linear model misses curvature but is still useful; overfit spline has zero training error but learns the noise."),
                slide("Trade-offs in choosing a model",
                      bullets([
                          "<strong>Prediction accuracy vs interpretability</strong> — linear models are easy to explain; splines and neural nets are not.",
                          "<strong>Good fit vs over-fit vs under-fit</strong> — how do we know when the fit is just right?",
                          "<strong>Parsimony vs black-box</strong> — we often prefer fewer variables and a simpler story, even at a small cost in accuracy.",
                      ])
                      + '<table style="font-size:0.85em;margin:0.8em auto;border-collapse:collapse;width:85%;">'
                      + '<tr style="border-bottom:2px solid #ccc;"><th>← More interpretable</th><th>More flexible →</th></tr>'
                      + '<tr><td>Subset selection, Lasso</td><td>Bagging, Boosting</td></tr>'
                      + '<tr><td>Least squares linear regression</td><td>Support Vector Machines</td></tr>'
                      + '<tr><td>Generalised Additive Models, Trees</td><td>Deep neural networks</td></tr>'
                      + '</table>',
                      "The flexibility/interpretability trade-off chart from ISLR Fig 2.7. Always ask: 'Do I need to explain this model?' If yes, stay left on the spectrum. If pure prediction performance is all that matters, flexible models are often better."),
                slide("Assessing model accuracy — train vs test MSE",
                      '<p>Given training data Tr = {xᵢ, yᵢ}₁ᴺ and a fitted model f̂:</p>'
                      + two_col(
                          '<p><strong>Training MSE:</strong></p>'
                          '<p style="font-size:1.15em;">MSE<sub>Tr</sub> = Ave<sub>i∈Tr</sub>[yᵢ − f̂(xᵢ)]²</p>'
                          '<p class="muted">Always decreases as complexity increases. Biased toward overfit models. Not a reliable guide.</p>',
                          '<p><strong>Test MSE (what actually matters):</strong></p>'
                          '<p style="font-size:1.15em;">MSE<sub>Te</sub> = Ave<sub>i∈Te</sub>[yᵢ − f̂(xᵢ)]²</p>'
                          '<p class="muted">Evaluated on fresh data not seen during fitting. The true measure of how well the model generalises.</p>'
                      )
                      + '<p class="callout" style="margin-top:0.8em;">Training MSE is not a reliable guide to test MSE. Always evaluate on held-out data.</p>',
                      "This is the core evaluation principle. A model that memorises training data (k=1 KNN, a very deep tree, a degree-20 polynomial) will have near-zero training MSE but terrible test MSE. In practice we use cross-validation to estimate test MSE when we don't have a separate test set."),
                slide("The U-shaped test MSE curve — three scenarios",
                      '<div style="display:flex;gap:0.5em;justify-content:center;">'
                      '<div style="flex:1;text-align:center;">'
                      '<img src="img/ch2_mse_scenario1.svg" style="width:100%;height:28vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.72em;margin:0;">Curved truth: moderate flexibility optimal</p>'
                      '</div>'
                      '<div style="flex:1;text-align:center;">'
                      '<img src="img/ch2_mse_scenario2.svg" style="width:100%;height:28vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.72em;margin:0;">Linear truth: linear model wins</p>'
                      '</div>'
                      '<div style="flex:1;text-align:center;">'
                      '<img src="img/ch2_mse_scenario3.svg" style="width:100%;height:28vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.72em;margin:0;">Wiggly truth: high flexibility needed</p>'
                      '</div>'
                      '</div>'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.4em;">Each panel: grey = train MSE (decreases monotonically), red = test MSE (U-shape), dashed = irreducible Var(ε).</p>',
                      "The U-shaped test MSE curve is one of the central images of the course. Students should be able to sketch it from memory: training MSE monotonically decreasing, test MSE U-shaped, minimum of the U is what we want."),
                slide("Bias-Variance Trade-off",
                      '<p style="text-align:center;font-size:1.05em;margin:0.4em 0;">'
                      'E[(y₀ − f̂(x₀))²] = '
                      '<span style="color:#e07000;">Var(f̂(x₀))</span>'
                      ' + '
                      '<span style="color:#0066cc;">[Bias(f̂(x₀))]²</span>'
                      ' + '
                      '<span style="color:#888;">Var(ε)</span>'
                      '</p>'
                      '<img src="img/ch2_bias_variance.svg" style="width:100%;max-height:50vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.78em;margin-top:0.2em;">Three scenarios: MSE (dark red), Bias² (cyan), Variance (orange), Var(ε) (dashed). As flexibility ↑: Bias² ↓, Variance ↑. The U-shape is their sum.</p>',
                      "The bias-variance decomposition is the theoretical foundation for the U-shaped test MSE curve. The minimum of the U is where bias and variance balance. This formula explains why it exists."),
            ],
        },
        # ── Part 6 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 6",
            "title": "Classification",
            "subtitle": "qualitative Y, the Bayes classifier, and KNN boundaries",
            "slides": [
                slide("Classification problems",
                      '<p>When the response Y is <strong>qualitative</strong> (categorical), the problem is called classification.</p>'
                      + bullets([
                          "Email is <strong>spam</strong> or <strong>ham</strong> — binary classification (K = 2).",
                          "Digit is one of <strong>0, 1, …, 9</strong> — 10-class classification.",
                          "Breast tumour subtype — 4-class classification.",
                      ], fragments=False)
                      + '<p style="margin-top:0.8em;">Goals: <strong>(1)</strong> build a classifier C(X) that assigns a class label to new X; <strong>(2)</strong> assess the uncertainty in each classification; <strong>(3)</strong> understand which predictors drive the classification.</p>',
                      "Classification is one of the two main problem types (regression is the other). In both cases we have Y and X — only the type of Y changes. The same cross-validation, bias-variance, and model selection ideas apply to both."),
                slide("The Bayes optimal classifier",
                      '<p>Define the <strong>conditional class probabilities</strong>:</p>'
                      '<p style="text-align:center;font-size:1.2em;margin:0.6em 0;">pₖ(x) = Pr(Y = k | X = x),  k = 1, 2, …, K</p>'
                      '<p>The <strong>Bayes classifier</strong> assigns x to the class with the highest conditional probability:</p>'
                      '<p style="text-align:center;font-size:1.2em;margin:0.6em 0;">C(x) = j &nbsp; if &nbsp; p<sub>j</sub>(x) = max{p₁(x), p₂(x), …, p<sub>K</sub>(x)}</p>'
                      + two_col(
                          '<p>In a 1D binary example: the black curve shows p₁(x) = Pr(Y=1|X=x). The <strong>Bayes boundary</strong> is where p₁(x) = 0.5.</p>',
                          '<p class="callout">The Bayes classifier has the <em>smallest possible</em> error rate of any classifier in the population. It is the gold standard — but it requires knowing the true pₖ(x), which we never do in practice.</p>'
                      ),
                      "In the 1D example from ISLR Fig 2.13: the bar plot at x=5 shows the conditional class probabilities at that point — about 75% class 1, 25% class 0. The Bayes classifier would say 'class 1' at x=5."),
                slide("Nearest-neighbor for classification",
                      '<p>Estimate pₖ(x) by local averaging — just as in regression:</p>'
                      '<p style="text-align:center;font-size:1.2em;margin:0.8em 0;">p̂ₖ(x) = fraction of the k nearest neighbors with class k</p>'
                      '<p>Assign x to the most common class among its k nearest neighbours.</p>'
                      + bullets([
                          "The 1D classifier plot shows the estimated p̂₁(x) curve (green) tracking the true p₁(x) (black) reasonably well.",
                          "Still breaks down as p grows — same curse of dimensionality.",
                          "But the impact on the classifier Ĉ(x) is <em>less severe</em> than on the probabilities p̂ₖ(x) themselves.",
                      ], fragments=False),
                      "The 1D example from ISLR Fig 2.14: the green curve is the KNN estimate of p₁(x) with k=15. It tracks the true black curve well in regions with data, but the bar chart at x=5 shows the local estimate is slightly off (65% vs true 75%). The classifier (majority vote) is usually still correct even when the probability estimate is off."),
                slide("KNN in two dimensions — the decision boundary",
                      two_col(
                          '<img src="img/ch2_knn_raw.svg" style="width:100%;height:38vh;object-fit:contain;">'
                          '<p class="muted" style="font-size:0.75em;text-align:center;margin:0;">Raw data + Bayes boundary (dashed purple)</p>',
                          '<img src="img/ch2_knn_k10.svg" style="width:100%;height:38vh;object-fit:contain;">'
                          '<p class="muted" style="font-size:0.75em;text-align:center;margin:0;">KNN K=10 boundary (black) vs Bayes (dashed)</p>'
                      )
                      + '<p class="muted" style="font-size:0.8em;margin-top:0.4em;">KNN K=10 closely tracks the Bayes boundary without any parametric assumptions.</p>',
                      "KNN with K=10 produces a non-linear decision boundary that closely approximates the Bayes boundary. The dashed purple curve is the Bayes (optimal) boundary."),
                slide("K controls the bias-variance dial",
                      '<img src="img/ch2_knn_k1_k100.svg" style="width:100%;max-height:48vh;object-fit:contain;">'
                      + two_col(
                          '<p><strong>K = 1</strong>: zero training error, extremely wiggly boundary — overfit.</p>'
                          '<p><strong>K = 100</strong>: too smooth, misses non-linearities — underfit.</p>',
                          '<p class="callout">K = 1 → max flexibility. K = N → predict majority class. Pick K by cross-validation.</p>'
                      ),
                      "The two-panel figure from ISLR Fig 2.16. K=1 is very jagged (overfits); K=100 is too smooth (underfits). The sweet spot was K=10 shown in the previous slide."),
                slide("Classification error rate and the KNN U-shape",
                      '<img src="img/ch2_knn_error.svg" style="width:100%;max-height:50vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;margin-top:0.3em;"><strong>Blue (training):</strong> 0 at K=1, rises as K grows. <strong>Orange (test):</strong> U-shape, minimum at K≈10. <strong>Dashed:</strong> Bayes error — irreducible floor.</p>'
                      '<p class="callout" style="margin-top:0.4em;">Same story as regression: training error decreases with flexibility, test error has a U-shape.</p>',
                      "This plot from ISLR Fig 2.17 closes the circle. KNN already demonstrates all the core ideas: training vs test error, overfitting, underfitting, the U-shape, and the Bayes floor. Every more sophisticated model is a more elaborate version of the same story."),
            ],
        },
    ],
    "recap_items": [
        "<strong>Y = f(X) + ε.</strong> Statistical learning estimates f. The reducible error [f − f̂]² can be minimised; the irreducible Var(ε) cannot.",
        "<strong>Bias-variance trade-off:</strong> Test MSE = Bias² + Variance + Var(ε). As flexibility increases, bias falls and variance rises. The U-shaped test MSE curve is the result.",
        "<strong>Supervised, unsupervised, and semi-supervised</strong> learning differ in whether labelled Y values are available. The same bias-variance logic applies to all three.",
    ],
    "recap_callout": "Next: Linear Regression — the simplest f̂, and the workhorse that every later model generalises.",
}



W3_LR = {
    "title": "Linear Regression",
    "kicker": "Week 3 · Course 2",
    "subtitle": "From simple least squares to interactions, qualitative predictors and polynomial fits",
    "parts_summary": [
        ("Part 1", "Simple linear regression", "Model, RSS, least-squares formulas."),
        ("Part 2", "Assessing coefficients", "SE, confidence intervals, t-stat, p-value."),
        ("Part 3", "Model accuracy", "RSE, R², correlation."),
        ("Part 4", "Multiple linear regression", "MLR, interpretation pitfalls, F-statistic."),
        ("Part 5", "Variable selection", "Forward/backward selection, AIC, BIC, CV."),
        ("Part 6", "Qualitative predictors", "Dummy variables, baseline, multi-level factors."),
        ("Part 7", "Interactions & non-linearity", "Interaction terms, hierarchy principle, polynomial regression."),
    ],
    "callout": "Linear regression is the foundation: every concept — coefficients, residuals, R², p-values — reappears in every model you'll ever build. Understand it deeply and the rest of the course is revision.",
    "parts": [
        # ── Part 1 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 1",
            "title": "Simple Linear Regression",
            "subtitle": "one predictor, one line, one loss",
            "slides": [
                slide("The linear regression model",
                      bullets([
                          "We assume <strong>Y = β₀ + β₁X + ε</strong>",
                          "β₀ (intercept) and β₁ (slope) are unknown constants — the <em>coefficients</em>.",
                          "ε is the error term: everything the model doesn't explain.",
                          "True regression functions are <em>never</em> linear — but linear is often a useful approximation.",
                      ]),
                      notes="Slide 1 of ISLR Ch3. Stress that the model is an approximation. George Box: 'All models are wrong, but some are useful.'"),
                slide("Advertising data — the running example",
                      '<img src="img/ch3_tv_sales_scatter.svg" style="width:100%;max-height:52vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.85em;margin-top:0.4em;">'
                      '200 markets · TV, radio, newspaper budgets ($thousands) · sales (thousands of units). '
                      'Positive trend — a straight line looks reasonable.</p>',
                      notes="The Advertising dataset is the workhorse for ISLR Ch3. Make sure students understand what a row represents."),
                slide("Least-squares estimation",
                      bullets([
                          "Prediction for the i-th point: ŷᵢ = β̂₀ + β̂₁xᵢ",
                          "Residual: eᵢ = yᵢ − ŷᵢ  (actual minus predicted)",
                          "<strong>RSS</strong> = e₁² + e₂² + … + eₙ² = Σ(yᵢ − β̂₀ − β̂₁xᵢ)²",
                          "Least-squares minimises RSS. The closed-form solution: β̂₁ = Σ(xᵢ−x̄)(yᵢ−ȳ) / Σ(xᵢ−x̄)², β̂₀ = ȳ − β̂₁x̄",
                      ]),
                      notes="This is the core algebra. Stress that RSS is the training loss; minimising it gives us the OLS estimates."),
                slide("Advertising example: fitted line",
                      two_col(
                          bullets([
                              "β̂₀ = 7.03 → expected sales when TV = 0",
                              "β̂₁ = 0.0475 → each extra $1 000 on TV is associated with ~47 additional units sold",
                              "The fit captures the trend but under-predicts at low TV spend.",
                          ], fragments=False),
                          '<img src="img/ch3_tv_sales_fitted.svg" style="width:100%;max-height:46vh;object-fit:contain;">'
                      ),
                      notes="β̂₁ = 0.0475 means a $1 000 increase in TV spend → about 47.5 extra units. Not causation — this is observational data."),
                slide("Predictions & residual diagnostics",
                      '<img src="img/ch3_residuals_vs_fitted.svg" style="width:100%;max-height:50vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.85em;margin-top:0.3em;">'
                      'Left: fitted line. Right: residuals vs fitted — any pattern here signals a mis-specified model. '
                      'Predict: ŷ = β̂₀ + β̂₁x. Extrapolation beyond the training range is risky.</p>'),
            ],
        },
        # ── Part 2 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 2",
            "title": "Assessing Coefficient Accuracy",
            "subtitle": "standard errors, confidence intervals, hypothesis tests",
            "slides": [
                slide("Standard errors of the estimates",
                      bullets([
                          "β̂₁ varies across repeated samples — its spread is SE(β̂₁).",
                          "SE(β̂₁)² = σ² / Σ(xᵢ − x̄)²",
                          "SE(β̂₀)² = σ²[1/n + x̄² / Σ(xᵢ − x̄)²]",
                          "σ² = Var(ε) is estimated from the residuals (RSE²).",
                          "<em>Wider spread in X → smaller SE(β̂₁)</em> — more information about the slope.",
                      ]),
                      notes="Intuition: if X barely varies, we can't pin down the slope precisely. More X-spread = better leverage on β₁."),
                slide("95 % confidence intervals",
                      '<img src="img/ch3_ci_beta1.svg" style="width:100%;max-height:30vh;object-fit:contain;">'
                      + bullets([
                          "A 95 % CI contains the true β with 95 % probability over repeated samples.",
                          "Approximate formula: β̂₁ ± 2 · SE(β̂₁)",
                          "Advertising TV: CI = [0.042, 0.053] — <em>excludes zero</em> → TV spend is reliably associated with sales.",
                      ]),
                      notes="Stress the frequentist interpretation: if we repeated the study 100 times, about 95 of the CIs would contain the true β₁."),
                slide("Hypothesis test: is β₁ = 0?",
                      '<img src="img/ch3_t_distribution.svg" style="width:100%;max-height:36vh;object-fit:contain;">'
                      + bullets([
                          "H₀: β₁ = 0 (no relationship). Hₐ: β₁ ≠ 0.",
                          "t-statistic: t = β̂₁ / SE(β̂₁) = 17.67 for TV — far into the tail.",
                          "p-value = P(|T| ≥ |t| | H₀) — shaded area above. Here p ≪ 0.001.",
                      ]),
                      notes="t ≈ N(0,1) for large n. For Advertising TV: t = 0.0475/0.0027 = 17.67, p < 0.0001 — overwhelming evidence."),
                slide("Results table: TV → Sales",
                      '<table style="font-size:0.95em;margin:0.5em auto;">'
                      '<tr><th></th><th>Coefficient</th><th>Std. Error</th><th>t-statistic</th><th>p-value</th></tr>'
                      '<tr><td>Intercept</td><td>7.03</td><td>0.4578</td><td>15.36</td><td>&lt; 0.0001</td></tr>'
                      '<tr><td>TV</td><td>0.0475</td><td>0.0027</td><td>17.67</td><td>&lt; 0.0001</td></tr>'
                      '</table>'
                      '<p class="muted" style="margin-top:1em;">Both coefficients are highly significant. The t-statistics are far from zero.</p>',
                      notes="Walk through every column. The p-value for the intercept tests whether mean sales = 0 when TV = 0, which is also significant but less interesting."),
            ],
        },
        # ── Part 3 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 3",
            "title": "Assessing Model Accuracy",
            "subtitle": "RSE and R²",
            "slides": [
                slide("Residual Standard Error (RSE)",
                      bullets([
                          "RSE = √(RSS / (n − 2)) — the average size of a residual.",
                          "It estimates σ, the standard deviation of ε.",
                          "RSE is in the same units as Y (thousands of units of sales).",
                          "Advertising TV: RSE = 3.26 → typical prediction error ≈ 3 260 units.",
                          "Whether 3.26 is 'large' depends on the mean of Y (avg sales ≈ 14.0 → ~23 % error).",
                      ]),
                      notes="RSE is an absolute measure of fit; R² is relative. Always report both."),
                slide("R-squared (fraction of variance explained)",
                      bullets([
                          "TSS = Σ(yᵢ − ȳ)² — total variance in Y before the model.",
                          "RSS = Σ(yᵢ − ŷᵢ)² — residual variance after the model.",
                          "<strong>R² = (TSS − RSS) / TSS = 1 − RSS/TSS</strong>",
                          "R² ∈ [0, 1]: 0 means the model explains nothing; 1 means a perfect fit.",
                          "Advertising TV: R² = 0.612 → TV alone explains 61 % of the variance in sales.",
                      ]),
                      notes="In SLR, R² = r² where r is the Pearson correlation coefficient between X and Y."),
                slide("Summary for TV → Sales SLR",
                      '<table style="font-size:0.95em;margin:0.5em auto;">'
                      '<tr><th>Quantity</th><th>Value</th></tr>'
                      '<tr><td>RSE</td><td>3.26</td></tr>'
                      '<tr><td>R²</td><td>0.612</td></tr>'
                      '<tr><td>F-statistic</td><td>312.1</td></tr>'
                      '</table>'
                      '<p class="muted" style="margin-top:1em;">61 % of variance in sales is explained by TV spend. Decent, but there is clearly more going on.</p>',
                      notes="The F-statistic tests whether at least one predictor is useful. In SLR it equals t². 312 = 17.67² — consistent."),
            ],
        },
        # ── Part 4 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 4",
            "title": "Multiple Linear Regression",
            "subtitle": "more predictors, one model",
            "slides": [
                slide("The MLR model",
                      bullets([
                          "<strong>Y = β₀ + β₁X₁ + β₂X₂ + … + βₚXₚ + ε</strong>",
                          "Each βⱼ is the expected change in Y per unit increase in Xⱼ, <em>holding all other predictors fixed</em>.",
                          "Advertising: sales = β₀ + β₁·TV + β₂·radio + β₃·newspaper + ε",
                          "Least squares extends naturally — minimise RSS over all coefficients simultaneously.",
                          "The fit is now a <em>hyperplane</em> in p+1 dimensions.",
                      ]),
                      notes="The interpretation 'holding others fixed' is ideal; in practice predictors are correlated and change together."),
                slide("Woes of interpreting regression coefficients",
                      two_col(
                          bullets([
                              "Mosteller & Tukey (1977): predictors usually change <em>together</em> — ceteris-paribus is theoretical.",
                              "<strong>Example:</strong> newspaper appears significant alone, but insignificant in MLR — its signal was radio's.",
                              "<em>Correlations among predictors inflate variance and shift coefficients.</em>",
                          ], fragments=False),
                          '<img src="img/ch3_correlation_heatmap.svg" style="width:100%;max-height:46vh;object-fit:contain;">'
                      ),
                      notes="These examples from ISLR Ch3 are classic suppressors. The key lesson: MLR coefficients are partial effects, not marginal effects."),
                slide("MLR results: Advertising data",
                      '<table style="font-size:0.88em;margin:0.3em auto;">'
                      '<tr><th></th><th>Coef.</th><th>SE</th><th>t</th><th>p-value</th></tr>'
                      '<tr><td>Intercept</td><td>2.939</td><td>0.312</td><td>9.42</td><td>&lt;0.0001</td></tr>'
                      '<tr><td>TV</td><td>0.046</td><td>0.001</td><td>32.81</td><td>&lt;0.0001</td></tr>'
                      '<tr><td>radio</td><td>0.189</td><td>0.009</td><td>21.89</td><td>&lt;0.0001</td></tr>'
                      '<tr><td>newspaper</td><td>−0.001</td><td>0.006</td><td>−0.18</td><td>0.8599</td></tr>'
                      '</table>'
                      '<p class="muted" style="font-size:0.85em;margin-top:0.5em;">'
                      'Newspaper is <em>insignificant</em> once radio is in the model (corr(radio, newspaper) = 0.35).</p>',
                      notes="Key insight: newspaper was significant in isolation because of its correlation with radio. MLR removes that spurious signal."),
                slide("MLR coefficients and model fit",
                      two_col(
                          '<img src="img/ch3_mlr_coefficients.svg" style="width:100%;max-height:46vh;object-fit:contain;">',
                          '<table style="font-size:0.88em;margin:0.5em auto;">'
                          '<tr><th>Quantity</th><th>SLR (TV)</th><th>MLR (all)</th></tr>'
                          '<tr><td>RSE</td><td>3.26</td><td>1.69</td></tr>'
                          '<tr><td>R²</td><td>0.612</td><td>0.897</td></tr>'
                          '<tr><td>F-stat</td><td>312</td><td>570</td></tr>'
                          '</table>'
                          '<p class="muted" style="font-size:0.85em;margin-top:0.5em;">'
                          'Newspaper CI crosses zero — not significant. MLR R² = 89.7 %.</p>'
                      ),
                      notes="R² always increases when you add predictors (even noise). Adjusted R² and test-set MSE penalise model complexity."),
                slide("MLR — least-squares plane",
                      '<img src="img/ch3_mlr_plane.svg" style="width:100%;max-height:54vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.85em;margin-top:0.3em;">'
                      'The least-squares plane through TV × radio space. Red dots: observations. '
                      'Residuals are vertical distances from the plane to each point.</p>',
                      notes="Geometric intuition for MLR: one hyperplane per predictor dimension. Residuals are still vertical distances from the plane to the data points."),
            ],
        },
        # ── Part 5 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 5",
            "title": "Variable Selection",
            "subtitle": "F-statistic, forward/backward selection, information criteria",
            "slides": [
                slide("Is at least one predictor useful? — the F-test",
                      bullets([
                          "H₀: β₁ = β₂ = … = βₚ = 0 (none of the predictors help)",
                          "F = [(TSS − RSS) / p] / [RSS / (n − p − 1)]",
                          "Under H₀, F ~ Fₚ,ₙ₋ₚ₋₁. A large F rejects H₀.",
                          "Advertising MLR: F = 570, p ≈ 0 → at least one of TV/radio/newspaper predicts sales.",
                          "<em>Do not rely on individual t-tests alone when p is large</em> — you'll get false positives by chance.",
                      ]),
                      notes="With p = 100 predictors and α = 0.05, expect ~5 false positives by chance. The F-test controls for this."),
                slide("Deciding which variables matter",
                      two_col(
                          bullets([
                              "<strong>All-subsets:</strong> 2ᵖ models — infeasible for p ≥ 40.",
                              "<strong>Forward selection:</strong> greedily add the predictor that most reduces AIC.",
                              "<strong>Backward selection:</strong> drop the predictor with the largest p-value.",
                              "Both are heuristics — no global optimality guarantee.",
                          ], fragments=False),
                          '<img src="img/ch3_forward_selection.svg" style="width:100%;max-height:46vh;object-fit:contain;">'
                      ),
                      notes="Forward selection cannot remove a variable once added; backward cannot add one once removed. Stepwise selection allows both directions."),
                slide("Choosing the optimal model size",
                      bullets([
                          "<strong>Adjusted R²</strong> = 1 − [RSS/(n−p−1)] / [TSS/(n−1)] — penalises for adding uninformative predictors.",
                          "<strong>AIC</strong> = n·log(RSS/n) + 2p — prefer smaller AIC.",
                          "<strong>BIC</strong> = n·log(RSS/n) + p·log(n) — stronger penalty than AIC; prefers sparser models.",
                          "<strong>Cross-validation (CV)</strong> — the gold standard; directly estimates test MSE.",
                          "All four criteria trade training fit against model complexity.",
                      ]),
                      notes="CV is most reliable but computationally expensive. AIC/BIC are fast analytical approximations. We'll study CV in depth in a later course."),
            ],
        },
        # ── Part 6 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 6",
            "title": "Qualitative Predictors",
            "subtitle": "dummy variables, baselines, multi-level factors",
            "slides": [
                slide("Encoding binary qualitative predictors",
                      bullets([
                          "Qualitative (categorical) variables can't enter the model as raw values.",
                          "Create a <strong>dummy variable</strong>: xᵢ = 1 if female, 0 if male.",
                          "Model: yᵢ = β₀ + β₁xᵢ + εᵢ = β₀ + β₁ (female) or β₀ (male).",
                          "β₁ = expected difference in balance between females and males.",
                          "pandas: <code>pd.get_dummies(df, drop_first=True)</code>",
                      ]),
                      notes="The baseline (reference) category is the one without a dummy variable — here, male. β₀ is the intercept for the baseline."),
                slide("Credit card data: gender model",
                      '<table style="font-size:0.95em;margin:0.5em auto;">'
                      '<tr><th></th><th>Coefficient</th><th>SE</th><th>t</th><th>p-value</th></tr>'
                      '<tr><td>Intercept</td><td>509.80</td><td>33.13</td><td>15.39</td><td>&lt;0.0001</td></tr>'
                      '<tr><td>gender[Female]</td><td>19.73</td><td>46.05</td><td>0.43</td><td>0.669</td></tr>'
                      '</table>'
                      '<p class="muted" style="margin-top:0.8em;">Female cardholders carry $19.73 more balance on average — but p = 0.67, not significant.</p>',
                      notes="The baseline (Male) has expected balance = $509.80. Females: 509.80 + 19.73 = $529.53. The difference is not statistically meaningful."),
                slide("Multi-level factors: ethnicity example",
                      bullets([
                          "For k levels, create <strong>k − 1 dummy variables</strong>. The omitted level is the <em>baseline</em>.",
                          "Ethnicity (3 levels): create Asian and Caucasian dummies; African American is baseline.",
                          "yᵢ = β₀ + β₁·Asian + β₂·Caucasian + εᵢ",
                          "β₀ = expected balance for AA; β₁ = AA–Asian difference; β₂ = AA–Caucasian difference.",
                      ]),
                      notes="Changing the baseline level doesn't change predictions or model fit — only the interpretation of coefficients changes."),
                slide("Credit card data: ethnicity model",
                      '<table style="font-size:0.95em;margin:0.5em auto;">'
                      '<tr><th></th><th>Coefficient</th><th>SE</th><th>t</th><th>p-value</th></tr>'
                      '<tr><td>Intercept (AA)</td><td>531.00</td><td>46.32</td><td>11.46</td><td>&lt;0.0001</td></tr>'
                      '<tr><td>ethnicity[Asian]</td><td>−18.69</td><td>65.02</td><td>−0.29</td><td>0.774</td></tr>'
                      '<tr><td>ethnicity[Caucasian]</td><td>−12.50</td><td>56.68</td><td>−0.22</td><td>0.826</td></tr>'
                      '</table>'
                      '<p class="muted" style="margin-top:0.8em;">Neither Asian nor Caucasian is significantly different from African American in balance.</p>'),
            ],
        },
        # ── Part 7 ─────────────────────────────────────────────────────────────
        {
            "kicker": "Part 7",
            "title": "Interactions & Non-linearity",
            "subtitle": "synergy effects, hierarchy principle, polynomial regression",
            "slides": [
                slide("The additive assumption and its limits",
                      bullets([
                          "The standard MLR model assumes each predictor's effect on Y is <em>additive</em> and <em>independent</em>.",
                          "Advertising: the effect of TV on sales is the same regardless of radio spend.",
                          "But: if radio boosts the effectiveness of TV ads, the model <em>underestimates</em> sales when both are high.",
                          "This is a <strong>synergy</strong> (marketing) or <strong>interaction</strong> (statistics) effect.",
                      ]),
                      notes="Visually: the residual plot against a 3D surface of TV × radio shows clear non-random structure when both channels are moderate."),
                slide("Adding an interaction term",
                      bullets([
                          "Interaction model: sales = β₀ + β₁·TV + β₂·radio + β₃·(TV × radio) + ε",
                          "β₃ captures how the effect of TV on sales <em>changes</em> as radio increases.",
                          "The effective slope for TV is: β̂₁ + β̂₃ × radio.",
                          "An extra $1 000 on TV → (19 + 1.1 × radio) additional units sold.",
                      ]),
                      notes="This is the key insight: the interaction term makes the slope of one predictor a function of another."),
                slide("Interaction model: results",
                      '<table style="font-size:0.88em;margin:0.3em auto;">'
                      '<tr><th></th><th>Coef.</th><th>SE</th><th>t</th><th>p-value</th></tr>'
                      '<tr><td>Intercept</td><td>6.750</td><td>0.248</td><td>27.23</td><td>&lt;0.0001</td></tr>'
                      '<tr><td>TV</td><td>0.019</td><td>0.002</td><td>12.70</td><td>&lt;0.0001</td></tr>'
                      '<tr><td>radio</td><td>0.029</td><td>0.009</td><td>3.24</td><td>0.0014</td></tr>'
                      '<tr><td>TV×radio</td><td>0.0011</td><td>0.000</td><td>20.73</td><td>&lt;0.0001</td></tr>'
                      '</table>'
                      '<p class="muted" style="font-size:0.85em;margin-top:0.4em;">R² jumps from 89.7 % (additive) to <strong>96.8 %</strong>. The interaction term explains 69 % of the remaining variance.</p>',
                      notes="R² increase: (96.8 − 89.7) / (100 − 89.7) = 69 %. This is massive — the interaction is the dominant signal."),
                slide("The hierarchy principle",
                      bullets([
                          "If an interaction term is included, <em>always</em> include the main effects too — even if their p-values are not significant.",
                          "Reason: without main effects, the interaction term also absorbs them — its coefficient changes meaning.",
                          "Rule of thumb: <strong>interaction in → main effects in</strong>.",
                          "Applies equally to qualitative × quantitative interactions (e.g., student × income).",
                      ]),
                      notes="This is a modelling convention, not a statistical test. Violating it leads to uninterpretable interaction coefficients."),
                slide("Qualitative × quantitative: student example",
                      '<div class="two-col">'
                      '<div><img src="img/ch3_student_parallel.svg" style="width:100%;height:38vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;text-align:center;">No interaction — parallel lines (same slope)</p></div>'
                      '<div><img src="img/ch3_student_interact.svg" style="width:100%;height:38vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.8em;text-align:center;">With interaction — different slopes</p></div>'
                      '</div>',
                      notes="The interaction term allows the income–balance slope to differ between students and non-students."),
                slide("Non-linearity: polynomial regression",
                      '<img src="img/ch3_polynomial_fits.svg" style="width:100%;max-height:50vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.85em;margin-top:0.3em;">'
                      'Linear under-fits (misses curvature). Quadratic (degree 2) fits well. '
                      'Degree 5 overfits — wiggles at the extremes. sklearn: <code>PolynomialFeatures(degree=2) + Pipeline</code>.</p>',
                      notes="Polynomial regression is still linear in the coefficients — it's multiple linear regression with engineered features x, x², x³, ..."),
                slide("Residual diagnostics: linear vs quadratic",
                      '<img src="img/ch3_residuals_poly.svg" style="width:100%;max-height:50vh;object-fit:contain;">'
                      '<p class="muted" style="font-size:0.85em;margin-top:0.3em;">'
                      'Left: linear residuals show a clear arch — the model is mis-specified. '
                      'Right: quadratic residuals are random — the curvature has been captured. '
                      'Cross-validation would select degree 2.</p>',
                      notes="Horsepower² coefficient = 0.0012 with t = 10.1 — very significant. Higher degrees give diminishing returns and eventually overfit."),
            ],
        },
    ],
    "recap_items": [
        "<strong>OLS</strong> minimises RSS to produce β̂₀ and β̂₁; statsmodels gives you SE, t, p, CI in one <code>.summary()</code> call.",
        "<strong>R² and RSE</strong> measure how much variance is explained and what the typical error is — always report both.",
        "<strong>MLR, dummies, interactions, and polynomial terms</strong> all fit inside the same linear-regression framework — just with different X columns.",
    ],
    "recap_callout": "Next: Classification — when Y is categorical. The same ideas (loss, coefficients, regularisation) reappear in logistic regression.",
}


W3_CV = {
    "title": "Cross-Validation and the Bootstrap",
    "kicker": "Week 3 · Course 3",
    "subtitle": "Estimating test error via hold-out sets, K-fold CV, LOOCV, and the bootstrap",
    "parts_summary": [
        ("Part 1 · 0:00–0:30", "Why training error lies", "The overfitting gap, validation sets, and their drawbacks."),
        ("Part 2 · 0:30–1:15", "Cross-validation", "K-fold, LOOCV, the right vs wrong way."),
        ("Part 3 · 1:15–1:45", "The Bootstrap", "SE estimation, confidence intervals, and limits."),
    ],
    "callout": "Cross-validation and the bootstrap are the two most important tools for assessing statistical learning methods. Everything downstream — model selection, hyperparameter tuning, uncertainty quantification — rests on these ideas.",
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Why Training Error Lies",
            "subtitle": "The gap between training and test performance",
            "slides": [
                slide("Training error vs test error",
                      two_col(
                          bullets([
                              "<strong>Test error</strong>: average error on new observations not used to train the model.",
                              "<strong>Training error</strong>: error on the observations the model was fitted on — easy to calculate.",
                              "Training error <em>dramatically underestimates</em> test error for flexible models.",
                              "More flexibility → training error always falls, but test error forms a U-shape.",
                          ], fragments=False),
                          '<img src="img/ch5_bias_variance_curve.svg" style="width:100%;max-height:52vh;object-fit:contain;">',
                      ),
                      "The core motivation for resampling: we care about how the model performs on fresh data, not on the same data it memorised."),
                slide("The bias-variance trade-off curve",
                      two_col(
                          '<p>As model complexity increases:</p>'
                          + bullets([
                              "Training error decreases monotonically.",
                              "Test error decreases, then <em>rises</em> again.",
                              "Minimum of test error = sweet spot.",
                              "Left of minimum: high bias (underfitting).",
                              "Right of minimum: high variance (overfitting).",
                          ], fragments=False),
                          '<img src="img/ch5_bias_variance_curve.svg" style="width:100%;max-height:55vh;object-fit:contain;">',
                      ),
                      "The cyan training curve goes down forever. The red test curve turns back up. We want to find the minimum of the red curve without ever having the true test data."),
                slide("How to estimate test error",
                      bullets([
                          "<strong>Best solution:</strong> a large designated test set — often not available.",
                          "<strong>Mathematical adjustment:</strong> C<sub>p</sub>, AIC, BIC — adjust training error upward by a penalty for model complexity.",
                          "<strong>Resampling methods (our focus):</strong> hold out a subset of training data, fit on the rest, evaluate on the held-out portion.",
                          "Resampling is model-agnostic — it works for any learning method, not just linear models.",
                      ])),
                slide("The validation-set approach",
                      '<img src="img/ch5_validation_split.svg" style="width:100%;max-height:28vh;object-fit:contain;margin-bottom:0.5em;">'
                      + bullets([
                          "Randomly split n observations into a <strong>training set</strong> and a <strong>validation (hold-out) set</strong>.",
                          "Fit the model on the training set only.",
                          "Evaluate on the validation set: <strong>MSE</strong> for regression, <strong>misclassification rate</strong> for classification.",
                          "The validation error estimates the test error.",
                      ]),
                      "Blue cells = training set; orange cells = validation set. The split is random, which is both the approach's strength (simple) and weakness (variable)."),
                slide("Drawbacks of validation set",
                      two_col(
                          bullets([
                              "<strong>High variance:</strong> the validation error depends heavily on <em>which</em> observations land in each half.",
                              "10 random splits of the same Auto data → 10 different MSE curves (see right).",
                              "<strong>Overestimates test error:</strong> only half the data trains the model.",
                              "The model fit on n/2 has more bias than the model deployed on all n.",
                          ], fragments=False),
                          '<img src="img/ch5_auto_multi_split.svg" style="width:100%;max-height:55vh;object-fit:contain;">',
                      ),
                      "This motivates K-fold cross-validation: use the data more efficiently by rotating which portion is held out."),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:15",
            "title": "Cross-Validation",
            "subtitle": "K-fold, LOOCV, the right and wrong way",
            "slides": [
                slide("K-fold cross-validation",
                      bullets([
                          "Randomly divide data into <strong>K equal-sized parts</strong> C<sub>1</sub>, C<sub>2</sub>, …, C<sub>K</sub>.",
                          "Leave out part k. Fit on the other K−1 parts combined. Predict on part k. Compute MSE<sub>k</sub>.",
                          "Repeat for each k = 1, 2, …, K. Combine the K estimates.",
                          "CV<sub>(K)</sub> = Σ (n<sub>k</sub>/n) · MSE<sub>k</sub>",
                          "Estimates can also be used to <em>select</em> the best model (degree, hyperparameter, etc.).",
                      ])),
                slide("5-fold CV — the diagram",
                      two_col(
                          '<table style="font-size:0.75em;border-collapse:collapse;">'
                          '<tr><th>Fold</th><th>Part 1</th><th>Part 2</th><th>Part 3</th><th>Part 4</th><th>Part 5</th></tr>'
                          '<tr><td>1</td><td style="background:#fdd;color:#900;">Valid.</td><td>Train</td><td>Train</td><td>Train</td><td>Train</td></tr>'
                          '<tr><td>2</td><td>Train</td><td style="background:#fdd;color:#900;">Valid.</td><td>Train</td><td>Train</td><td>Train</td></tr>'
                          '<tr><td>3</td><td>Train</td><td>Train</td><td style="background:#fdd;color:#900;">Valid.</td><td>Train</td><td>Train</td></tr>'
                          '<tr><td>4</td><td>Train</td><td>Train</td><td>Train</td><td style="background:#fdd;color:#900;">Valid.</td><td>Train</td></tr>'
                          '<tr><td>5</td><td>Train</td><td>Train</td><td>Train</td><td>Train</td><td style="background:#fdd;color:#900;">Valid.</td></tr>'
                          '</table>',
                          '<p class="muted" style="font-size:0.9em;">Each row is one fit. Each red cell contributes its MSE to CV<sub>(5)</sub>. Every observation is held out exactly once.</p>',
                      ),
                      "The key advantage over a single validation set: every observation is used for both training and validation across the K fits."),
                slide("The CV formula in detail",
                      '<p style="text-align:center;font-size:1.15em;">CV<sub>(K)</sub> = &Sigma;<sub>k=1</sub><sup>K</sup> (n<sub>k</sub>/n) &middot; MSE<sub>k</sub></p>'
                      + '<p style="text-align:center;font-size:1.15em;">MSE<sub>k</sub> = &Sigma;<sub>i &isin; C<sub>k</sub></sub> (y<sub>i</sub> &minus; ŷ<sub>i</sub>)<sup>2</sup> / n<sub>k</sub></p>'
                      + bullets([
                          "n<sub>k</sub> = n/K when n is a multiple of K.",
                          "ŷ<sub>i</sub> is the prediction for obs i from the model <em>trained without part k</em>.",
                          "Setting K = n gives <strong>Leave-One-Out CV (LOOCV)</strong>.",
                      ], fragments=False),
                      "The weight n_k/n is just 1/K when folds are equal-sized. For LOOCV each fold has one observation."),
                slide("LOOCV — a nice shortcut",
                      '<p>For <strong>least-squares linear or polynomial regression</strong>:</p>'
                      + '<p style="text-align:center;font-size:1.1em;">CV<sub>(n)</sub> = (1/n) &Sigma;<sub>i=1</sub><sup>n</sup> [(y<sub>i</sub> &minus; ŷ<sub>i</sub>) / (1 &minus; h<sub>i</sub>)]<sup>2</sup></p>'
                      + bullets([
                          "ŷ<sub>i</sub> = fitted value from a <em>single</em> full-data OLS fit.",
                          "h<sub>i</sub> = leverage of observation i — diagonal of the hat matrix H = X(X<sup>T</sup>X)<sup>&minus;1</sup>X<sup>T</sup>.",
                          "One model fit computes LOOCV for free. No K refits needed.",
                          "Observations with high leverage h<sub>i</sub> get their residual inflated more.",
                      ]),
                      "This formula is a classic result in linear algebra. It shows that LOOCV is implicitly a form of influence analysis — high-leverage points dominate."),
                slide("LOOCV vs K = 5 or 10",
                      two_col(
                          bullets([
                              "LOOCV is nearly <em>unbiased</em> — trains on n−1 observations.",
                              "But LOOCV has <strong>high variance</strong>: K=n estimates are highly correlated.",
                              "K = 5 or K = 10 provides a better <strong>bias-variance trade-off</strong>.",
                              "Each fold uses (K−1)/K of the data → some upward bias, controlled variance.",
                              "<strong>Practical rule of thumb: use K = 10.</strong>",
                          ], fragments=False),
                          '<img src="img/ch5_auto_loocv_vs_10fold.svg" style="width:100%;max-height:54vh;object-fit:contain;">',
                      ),
                      "The analogy is averaging correlated vs uncorrelated estimators. LOOCV averages n nearly identical estimates; 10-fold averages 10 more diverse ones."),
                slide("Auto data: LOOCV vs 10-fold CV",
                      '<img src="img/ch5_auto_loocv_vs_10fold.svg" style="width:100%;max-height:52vh;object-fit:contain;">'
                      + '<p class="muted" style="font-size:0.8em;margin-top:0.4em;"><strong>Left:</strong> LOOCV — single smooth curve, no randomness, minimum at degree 2. <strong>Right:</strong> 10-fold CV (10 runs) — slight variation across seeds, but minimum is consistently at degree 2.</p>',
                      "Both methods correctly identify that quadratic (degree 2) is sufficient. LOOCV gives one answer; 10-fold is slightly noisy but gets the same answer."),
                slide("True vs estimated test MSE",
                      '<img src="img/ch5_true_vs_estimated_mse.svg" style="width:100%;max-height:50vh;object-fit:contain;">'
                      + '<p class="muted" style="font-size:0.8em;margin-top:0.3em;">Grey = training MSE. <strong style="color:#4878d0;">Blue</strong> = true test MSE. <strong style="color:#ee854a;">Orange dashed</strong> = 10-fold CV estimate. CV reliably finds the same minimum as the true test curve even when the absolute values differ.</p>',
                      "The practical take: CV is reliable for model selection (finding the minimum) even if the absolute CV error is slightly off the true test error."),
                slide("Bias in K-fold CV",
                      bullets([
                          "Each fold trains on only (K−1)/K of the full data.",
                          "Smaller training set → model is slightly worse → <strong>upward bias</strong> in error estimate.",
                          "K = n (LOOCV) minimises this bias — trains on n−1 points, nearly the full dataset.",
                          "But LOOCV has the highest variance (correlated fold estimates).",
                          "<strong>K = 5 or 10 balances bias and variance.</strong> The standard choice.",
                      ]),
                      "This is exactly the bias-variance trade-off appearing at the meta-level: bias vs variance of the CV estimator itself."),
                slide("CV for classification",
                      '<p>Replace MSE with misclassification rate:</p>'
                      + '<p style="text-align:center;">CV<sub>K</sub> = &Sigma;<sub>k</sub> (n<sub>k</sub>/n) Err<sub>k</sub>, &nbsp;&nbsp; Err<sub>k</sub> = &Sigma;<sub>i &isin; C<sub>k</sub></sub> I(y<sub>i</sub> &ne; ŷ<sub>i</sub>) / n<sub>k</sub></p>'
                      + '<p>Estimated SE of CV<sub>K</sub>:</p>'
                      + '<p style="text-align:center;">SE&#772;(CV<sub>K</sub>) = &radic;[ (1/K) &Sigma;<sub>k</sub> (Err<sub>k</sub> &minus; Err&#772;<sub>k</sub>)<sup>2</sup> / (K&minus;1) ]</p>'
                      + '<p class="muted" style="font-size:0.85em;">This SE estimate is useful but <em>not strictly valid</em> — the K fold errors are correlated (they share training data), violating the independence assumption of the SE formula.</p>',
                      "Despite the violation, the SE estimate gives a practical sense of uncertainty. In practice, running CV multiple times and averaging gives a better stability estimate."),
                slide("CV: the right and the wrong way",
                      two_col(
                          '<p><strong>Wrong:</strong></p>'
                          + bullets([
                              "Step 1: find top-100 predictors by correlation with labels (using ALL data).",
                              "Step 2: apply CV to logistic regression on those 100 predictors.",
                              "→ CV error ≈ 0%, but true error = 50%.",
                          ], fragments=False),
                          '<p><strong>Right:</strong></p>'
                          + bullets([
                              "CV folds wrap ALL steps.",
                              "Inside each fold: select predictors from training fold only, then fit classifier.",
                              "→ CV error correctly reflects true performance.",
                          ], fragments=False),
                      ),
                      "This mistake was made in many genomics papers (Ambroise & McLachlan 2002). The 5000 predictors are noise; their correlations with labels are spurious but large enough to separate classes."),
                slide("Why the wrong way is wrong",
                      bullets([
                          "Step 1 (feature selection) <em>has already seen the labels</em>.",
                          "The selected features are chosen to correlate with labels in this specific sample — noise that happens to look like signal.",
                          "The classifier in step 2 is guaranteed to look good on these features even if they are purely random.",
                          "<strong>The rule:</strong> everything that touches labels must be inside the CV loop.",
                          "In scikit-learn: use <code>Pipeline</code> — it enforces this automatically.",
                      ])),
                slide("sklearn Pipeline enforces the right way",
                      code_block(
                          "from sklearn.pipeline import Pipeline\n"
                          "from sklearn.feature_selection import SelectKBest, f_classif\n"
                          "from sklearn.linear_model import LogisticRegression\n"
                          "from sklearn.model_selection import cross_val_score\n\n"
                          "# RIGHT: selection is inside the pipeline, inside each fold\n"
                          "pipe = Pipeline([\n"
                          "    ('select', SelectKBest(f_classif, k=100)),\n"
                          "    ('clf',    LogisticRegression()),\n"
                          "])\n"
                          "cv_error = 1 - cross_val_score(pipe, X, y, cv=5).mean()\n"
                          "# cv_error ≈ 0.50 for random labels — honest"
                      ),
                      "The Pipeline passes each fold's training data through SelectKBest before fitting the classifier. The held-out fold is evaluated on features selected without it."),
            ],
        },
        {
            "kicker": "Part 3 · 1:15 – 1:45",
            "title": "The Bootstrap",
            "subtitle": "Quantifying uncertainty by resampling",
            "slides": [
                slide("What is the bootstrap?",
                      bullets([
                          "A flexible tool to quantify <strong>uncertainty</strong> of any estimator or statistical learning method.",
                          "Provides estimates of <strong>standard error</strong> and <strong>confidence intervals</strong> without needing a new study.",
                          'Name from Baron Munchausen: <em>"pulled himself up by his own bootstraps"</em>.',
                          "Key idea: treat the observed sample as a stand-in for the population; repeatedly resample from it.",
                      ])),
                slide("The investment example",
                      '<p>Invest a fraction α in asset X and 1−α in asset Y. Minimise Var(αX + (1−α)Y).</p>'
                      + '<p style="text-align:center;font-size:1.1em;">&alpha;<sup>*</sup> = (&sigma;<sub>Y</sub><sup>2</sup> &minus; &sigma;<sub>XY</sub>) / (&sigma;<sub>X</sub><sup>2</sup> + &sigma;<sub>Y</sub><sup>2</sup> &minus; 2&sigma;<sub>XY</sub>)</p>'
                      + bullets([
                          "&sigma;<sub>X</sub><sup>2</sup> = Var(X), &sigma;<sub>Y</sub><sup>2</sup> = Var(Y), &sigma;<sub>XY</sub> = Cov(X,Y) are unknown.",
                          "Estimate them from a sample → get &alpha;&#770;.",
                          "Problem: how accurate is &alpha;&#770;? What is SE(&alpha;&#770;)?",
                      ], fragments=False),
                      "With known population parameters σ_X²=1, σ_Y²=1.25, σ_XY=0.5, the true α = 0.6."),
                slide("Simulating from the true population",
                      bullets([
                              "If we could repeatedly draw samples of n=100 from the true population, we could estimate SE(&alpha;&#770;) directly.",
                              "Draw 1000 datasets → compute &alpha;&#770; for each → histogram of &alpha;&#770;<sub>1</sub>, …, &alpha;&#770;<sub>1000</sub>.",
                              "Mean ≈ 0.5996 (very close to true α = 0.6).",
                              "SD ≈ 0.083 → SE(&alpha;&#770;) ≈ 0.083.",
                              "This is the <em>gold standard</em> — but requires knowing the population.",
                          ]),
                      "In practice we have one sample, not 1000. The bootstrap mimics this process using only that one sample."),
                slide("Bootstrap: resample from your one dataset",
                      bullets([
                              "We cannot generate new data from the population.",
                              "Instead: treat the observed sample Z = (z<sub>1</sub>,…,z<sub>n</sub>) as the estimated population P&#770;.",
                              "Draw bootstrap datasets Z*<sup>1</sup>, Z*<sup>2</sup>, …, Z*<sup>B</sup> by sampling <strong>n observations with replacement</strong> from Z.",
                              "Some observations appear multiple times; some not at all.",
                              "Compute &alpha;&#770;*<sup>1</sup>, …, &alpha;&#770;*<sup>B</sup> on each bootstrap dataset.",
                          ])),
                slide("Bootstrap standard error",
                      two_col(
                          '<p>Estimate SE using the bootstrap estimates:</p>'
                          + '<p style="text-align:center;font-size:1em;">SE<sub>B</sub>(&alpha;&#770;) = &radic;[ 1/(B&minus;1) &Sigma;<sub>r=1</sub><sup>B</sup> (&alpha;&#770;*<sup>r</sup> &minus; &#x101;*)<sup>2</sup> ]</p>'
                          + bullets([
                              "Investment example: SE<sub>B</sub>(&alpha;&#770;) ≈ 0.087, true SE = 0.083.",
                              "B = 1000 resamples is typically enough.",
                              "Works for <em>any</em> estimator — OLS, medians, ML models.",
                          ], fragments=False),
                          '<img src="img/ch5_bootstrap_alpha.svg" style="width:100%;max-height:55vh;object-fit:contain;">',
                      ),
                      "The bootstrap distribution of α̂* closely tracks the true distribution from 1000 simulated datasets. This is the remarkable fact that makes bootstrap work."),
                slide("Bootstrap percentile confidence interval",
                      bullets([
                              "Sort the B bootstrap estimates &alpha;&#770;*<sup>1</sup>, …, &alpha;&#770;*<sup>B</sup>.",
                              "The 5th and 95th percentiles form an approximate <strong>90% CI</strong>.",
                              "For the investment example: 90% CI ≈ (0.43, 0.72). True α = 0.6 is well inside.",
                              "This is the <strong>Bootstrap Percentile interval</strong> — the simplest CI from the bootstrap.",
                              "More sophisticated variants (BCa, studentised bootstrap) correct for skew and bias.",
                          ]),
                      "Interpretation: 90% of the time, the interval we construct this way contains the true α. This is the standard frequentist CI interpretation."),
                slide("Bootstrap is NOT suitable for prediction error",
                      two_col(
                          bullets([
                              "Attempt: use Z*<sup>b</sup> as training set, original Z as validation.",
                              "Problem: ~2/3 of obs appear in each bootstrap sample.",
                              "Model has already 'seen' ~63% of the validation set.",
                              "Result: bootstrap <em>severely underestimates</em> test error.",
                              "<strong>Use CV for prediction error. Use bootstrap for SE and CI.</strong>",
                          ], fragments=False),
                          '<img src="img/ch5_bootstrap_overlap.svg" style="width:100%;max-height:55vh;object-fit:contain;">',
                      ),
                      "Fraction out-of-bag ≈ 1 − (1 − 1/n)^n → 1 − 1/e ≈ 36.8% as n→∞. The other 63.2% were seen during training."),
                slide("Bootstrap for regression coefficients",
                      code_block(
                          "import numpy as np\n"
                          "rng = np.random.default_rng(0)\n\n"
                          "# One bootstrap iteration\n"
                          "n = len(y)\n"
                          "idx = rng.choice(n, size=n, replace=True)\n"
                          "X_boot, y_boot = X[idx], y[idx]\n"
                          "coef_boot = np.linalg.lstsq(X_boot, y_boot, rcond=None)[0]\n\n"
                          "# Repeat B times, collect SE\n"
                          "coefs = [fit_once(rng) for _ in range(1000)]\n"
                          "se_boot = np.std(coefs, axis=0)  # compare to statsmodels .bse"
                      ),
                      "Bootstrap SE of OLS coefficients matches statsmodels .bse closely. But bootstrap works for any model, not just OLS."),
                slide("scipy.stats.bootstrap — the modern API",
                      code_block(
                          "from scipy.stats import bootstrap\n\n"
                          "# Bootstrap CI for the median of a 1-D sample\n"
                          "result = bootstrap(\n"
                          "    (sample,),          # data as tuple of arrays\n"
                          "    statistic=np.median,\n"
                          "    n_resamples=1000,\n"
                          "    confidence_level=0.95,\n"
                          "    random_state=0,\n"
                          ")\n"
                          "print(result.confidence_interval)  # ConfidenceInterval(low=..., high=...)"
                      ),
                      "scipy.stats.bootstrap was added in SciPy 1.7. It handles any statistic — just pass a function. Supports both percentile and BCa (bias-corrected accelerated) intervals."),
                slide("Bootstrap vs permutation tests",
                      two_col(
                          '<p><strong>Bootstrap</strong></p>'
                          + bullets([
                              "Samples from the <em>estimated population</em> P&#770;.",
                              "Estimates SE and CI for any estimator.",
                              "Answers: how variable is my estimate?",
                          ], fragments=False),
                          '<p><strong>Permutation test</strong></p>'
                          + bullets([
                              "Samples from the <em>null distribution</em> (shuffle labels).",
                              "Estimates p-values and False Discovery Rates.",
                              "Answers: is there any effect at all?",
                          ], fragments=False),
                      ),
                      "Bootstrap can test H₀: θ=0 by checking if the CI contains zero. But permutation tests are generally more powerful for hypothesis testing. Use each for what it's designed for."),
            ],
        },
    ],
    "recap_items": [
        "<strong>Cross-validate everything — including preprocessing.</strong> Use sklearn's Pipeline so that feature selection and scaling happen inside each fold, not outside.",
        "<strong>K = 5 or 10 is the practical default.</strong> LOOCV is nearly unbiased but has high variance; large K finds the right minimum with less computation.",
        "<strong>Bootstrap gives SE and CI for any estimator.</strong> Use scipy.stats.bootstrap; avoid using bootstrap for prediction error — use CV instead.",
    ],
    "recap_callout": "Next: Classification — when Y is categorical. The same ideas of regularisation and model selection reappear, now with logistic loss.",
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
# WEEK 3 · COURSE 4 — Model Selection & Regularization
# ============================================================================

# ── SVG helpers ──────────────────────────────────────────────────────────────

_SVG_SUBSET_FRONTIER = svg_diagram("""
<svg class="diagram" viewBox="0 0 640 300" width="620" height="290">
  <defs>
    <marker id="axArr" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <line x1="60" y1="250" x2="600" y2="250" stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr)"/>
  <line x1="60" y1="250" x2="60"  y2="20"  stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr)"/>
  <text x="320" y="278" text-anchor="middle" font-size="13" fill="#0f172a">Number of Predictors</text>
  <text x="20"  y="140" text-anchor="middle" font-size="13" fill="#0f172a" transform="rotate(-90 20 140)">RSS</text>
  <circle cx="110" cy="215" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="180" cy="185" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="180" cy="170" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="180" cy="200" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="250" cy="150" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="250" cy="135" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="250" cy="165" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="250" cy="175" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="320" cy="120" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="320" cy="108" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="320" cy="140" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="390" cy="95"  r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="390" cy="82"  r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="390" cy="110" r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="460" cy="78"  r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="460" cy="70"  r="4" fill="#94a3b8" opacity="0.6"/>
  <circle cx="530" cy="65"  r="4" fill="#94a3b8" opacity="0.6"/>
  <polyline points="110,215 180,170 250,135 320,108 390,82 460,70 530,65"
            fill="none" stroke="#dc2626" stroke-width="2.5"/>
  <circle cx="110" cy="215" r="6" fill="#dc2626"/>
  <circle cx="180" cy="170" r="6" fill="#dc2626"/>
  <circle cx="250" cy="135" r="6" fill="#dc2626"/>
  <circle cx="320" cy="108" r="6" fill="#dc2626"/>
  <circle cx="390" cy="82"  r="6" fill="#dc2626"/>
  <circle cx="460" cy="70"  r="6" fill="#dc2626"/>
  <circle cx="530" cy="65"  r="6" fill="#dc2626"/>
  <text x="110" y="265" text-anchor="middle" font-size="11" fill="#64748b">1</text>
  <text x="180" y="265" text-anchor="middle" font-size="11" fill="#64748b">2</text>
  <text x="250" y="265" text-anchor="middle" font-size="11" fill="#64748b">3</text>
  <text x="320" y="265" text-anchor="middle" font-size="11" fill="#64748b">4</text>
  <text x="390" y="265" text-anchor="middle" font-size="11" fill="#64748b">5</text>
  <text x="460" y="265" text-anchor="middle" font-size="11" fill="#64748b">6</text>
  <text x="530" y="265" text-anchor="middle" font-size="11" fill="#64748b">p</text>
  <circle cx="400" cy="40" r="5" fill="#94a3b8" opacity="0.6"/>
  <text x="412" y="44" font-size="11" fill="#64748b">all 2ᵖ models</text>
  <circle cx="400" cy="58" r="6" fill="#dc2626"/>
  <text x="412" y="62" font-size="11" fill="#dc2626">best for each k (frontier)</text>
</svg>
""", "margin:0 auto; display:block;")

_SVG_RIDGE_PATHS = svg_diagram("""
<svg class="diagram" viewBox="0 0 620 280" width="600" height="270">
  <defs>
    <marker id="axArr2" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <line x1="60" y1="230" x2="570" y2="230" stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr2)"/>
  <line x1="60" y1="230" x2="60"  y2="20"  stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr2)"/>
  <line x1="60" y1="130" x2="568" y2="130" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="315" y="258" text-anchor="middle" font-size="12" fill="#0f172a">λ (regularization strength) →</text>
  <text x="18"  y="130" text-anchor="middle" font-size="12" fill="#0f172a" transform="rotate(-90 18 130)">Coefficient</text>
  <text x="65"  y="245" font-size="10" fill="#64748b">small λ</text>
  <text x="510" y="245" font-size="10" fill="#64748b">large λ</text>
  <text x="67" y="18" font-size="10" fill="#64748b">← OLS estimates</text>
  <text x="575" y="133" font-size="10" fill="#64748b">0</text>
  <path d="M70,200 C150,195 280,160 560,128" fill="none" stroke="#0f172a" stroke-width="2.2"/>
  <text x="62" y="204" text-anchor="end" font-size="10" fill="#0f172a">Income</text>
  <path d="M70,55 C150,60 280,90 560,129" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="6,3"/>
  <text x="62" y="58" text-anchor="end" font-size="10" fill="#dc2626">Limit</text>
  <path d="M70,72 C160,78 290,100 560,130" fill="none" stroke="#2563eb" stroke-width="2.2" stroke-dasharray="4,2"/>
  <text x="62" y="90" text-anchor="end" font-size="10" fill="#2563eb">Rating</text>
  <path d="M70,100 C160,105 290,118 560,130" fill="none" stroke="#d97706" stroke-width="2.2" stroke-dasharray="2,2"/>
  <text x="62" y="118" text-anchor="end" font-size="10" fill="#d97706">Student</text>
  <text x="560" y="120" font-size="10" fill="#64748b">→ 0</text>
  <text x="310" y="22" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Ridge: coefficients shrink toward 0 as λ grows</text>
</svg>
""", "margin:0 auto; display:block;")

_SVG_BV_CURVE = svg_diagram("""
<svg class="diagram" viewBox="0 0 600 280" width="580" height="270">
  <defs>
    <marker id="axArr3" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <line x1="60" y1="230" x2="560" y2="230" stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr3)"/>
  <line x1="60" y1="230" x2="60"  y2="20"  stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr3)"/>
  <text x="310" y="258" text-anchor="middle" font-size="12" fill="#0f172a">Regularization strength λ →</text>
  <text x="18"  y="130" text-anchor="middle" font-size="12" fill="#0f172a" transform="rotate(-90 18 130)">Error</text>
  <line x1="60" y1="150" x2="550" y2="150" stroke="#64748b" stroke-width="1" stroke-dasharray="5,4"/>
  <text x="555" y="153" font-size="10" fill="#64748b">σ²</text>
  <path d="M70,148 C120,148 200,150 300,165 C380,178 460,200 540,220"
        fill="none" stroke="#0f172a" stroke-width="2.2"/>
  <path d="M70,60 C120,70 200,95 300,130 C380,155 460,175 540,190"
        fill="none" stroke="#16a34a" stroke-width="2.2"/>
  <path d="M70,90 C100,75 150,62 220,58 C280,56 330,65 380,85 C430,106 480,135 540,165"
        fill="none" stroke="#7c3aed" stroke-width="2.5"/>
  <line x1="220" y1="230" x2="220" y2="20" stroke="#7c3aed" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="225" y="240" font-size="10" fill="#7c3aed">optimal λ</text>
  <text x="215" y="62" font-size="14" fill="#7c3aed">×</text>
  <line x1="370" y1="35" x2="400" y2="35" stroke="#0f172a" stroke-width="2"/>
  <text x="406" y="39" font-size="11" fill="#0f172a">Bias²</text>
  <line x1="370" y1="52" x2="400" y2="52" stroke="#16a34a" stroke-width="2"/>
  <text x="406" y="56" font-size="11" fill="#16a34a">Variance</text>
  <line x1="370" y1="69" x2="400" y2="69" stroke="#7c3aed" stroke-width="2.5"/>
  <text x="406" y="73" font-size="11" fill="#7c3aed">Test MSE</text>
  <text x="310" y="22" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">Ridge: bias–variance trade-off</text>
</svg>
""", "margin:0 auto; display:block;")

_SVG_LASSO_CONSTRAINT = svg_diagram("""
<svg class="diagram" viewBox="0 0 640 300" width="620" height="290">
  <text x="155" y="22" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Lasso (L1 — diamond)</text>
  <polygon points="155,70 210,145 155,220 100,145" fill="#06b6d4" opacity="0.25" stroke="#06b6d4" stroke-width="2"/>
  <ellipse cx="220" cy="90" rx="85" ry="50" fill="none" stroke="#dc2626" stroke-width="1.8" opacity="0.7"/>
  <ellipse cx="220" cy="90" rx="60" ry="36" fill="none" stroke="#dc2626" stroke-width="1.8" opacity="0.7"/>
  <ellipse cx="220" cy="90" rx="40" ry="24" fill="none" stroke="#dc2626" stroke-width="1.8" opacity="0.7"/>
  <circle cx="220" cy="90" r="5" fill="#dc2626"/>
  <text x="228" y="88" font-size="10" fill="#dc2626">β̂ (OLS)</text>
  <circle cx="100" cy="145" r="6" fill="#0f172a"/>
  <text x="60" y="148" font-size="10" fill="#0f172a">contact</text>
  <text x="60" y="160" font-size="10" fill="#0f172a">at corner</text>
  <text x="60" y="172" font-size="10" fill="#0f172a">→ β₁=0</text>
  <text x="155" y="240" text-anchor="middle" font-size="11" fill="#64748b">β₁</text>
  <text x="86"  y="148" text-anchor="end"    font-size="11" fill="#64748b">β₂</text>
  <text x="465" y="22" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">Ridge (L2 — circle)</text>
  <circle cx="465" cy="145" r="75" fill="#06b6d4" opacity="0.25" stroke="#06b6d4" stroke-width="2"/>
  <ellipse cx="535" cy="90" rx="85" ry="50" fill="none" stroke="#dc2626" stroke-width="1.8" opacity="0.7"/>
  <ellipse cx="535" cy="90" rx="60" ry="36" fill="none" stroke="#dc2626" stroke-width="1.8" opacity="0.7"/>
  <ellipse cx="535" cy="90" rx="40" ry="24" fill="none" stroke="#dc2626" stroke-width="1.8" opacity="0.7"/>
  <circle cx="535" cy="90" r="5" fill="#dc2626"/>
  <text x="543" y="88" font-size="10" fill="#dc2626">β̂ (OLS)</text>
  <circle cx="415" cy="110" r="6" fill="#0f172a"/>
  <text x="350" y="108" font-size="10" fill="#0f172a">contact on</text>
  <text x="350" y="120" font-size="10" fill="#0f172a">smooth arc</text>
  <text x="350" y="132" font-size="10" fill="#0f172a">→ β≠ 0</text>
  <text x="465" y="240" text-anchor="middle" font-size="11" fill="#64748b">β₁</text>
  <text x="385" y="148" text-anchor="end"    font-size="11" fill="#64748b">β₂</text>
  <line x1="320" y1="15" x2="320" y2="285" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="5,4"/>
</svg>
""", "margin:0 auto; display:block;")

_SVG_LASSO_PATHS = svg_diagram("""
<svg class="diagram" viewBox="0 0 620 280" width="600" height="270">
  <defs>
    <marker id="axArr4" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <line x1="60" y1="230" x2="570" y2="230" stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr4)"/>
  <line x1="60" y1="230" x2="60"  y2="20"  stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr4)"/>
  <line x1="60" y1="130" x2="568" y2="130" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="315" y="258" text-anchor="middle" font-size="12" fill="#0f172a">λ →  (L1 penalty grows)</text>
  <text x="18"  y="130" text-anchor="middle" font-size="12" fill="#0f172a" transform="rotate(-90 18 130)">Coefficient</text>
  <text x="568" y="133" font-size="10" fill="#64748b">0</text>
  <path d="M70,200 C140,196 220,165 340,130 L555,130" fill="none" stroke="#0f172a" stroke-width="2.2"/>
  <text x="62" y="204" text-anchor="end" font-size="10" fill="#0f172a">Income</text>
  <path d="M70,55 C150,60 260,85 390,130 L555,130" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="6,3"/>
  <text x="62" y="58" text-anchor="end" font-size="10" fill="#dc2626">Limit</text>
  <path d="M70,72 C170,79 290,103 430,130 L555,130" fill="none" stroke="#2563eb" stroke-width="2.2" stroke-dasharray="4,2"/>
  <text x="62" y="90" text-anchor="end" font-size="10" fill="#2563eb">Rating</text>
  <path d="M70,100 C130,105 210,123 295,130 L555,130" fill="none" stroke="#d97706" stroke-width="2.2" stroke-dasharray="2,2"/>
  <text x="62" y="118" text-anchor="end" font-size="10" fill="#d97706">Student</text>
  <text x="300" y="22" text-anchor="middle" font-size="11" fill="#0f172a" font-weight="bold">Lasso: coefficients hit exactly zero (sparsity!)</text>
  <text x="298" y="120" font-size="10" fill="#d97706">↑ Student zeroed first</text>
  <line x1="340" y1="130" x2="340" y2="240" stroke="#0f172a" stroke-width="1" stroke-dasharray="3,3"/>
  <text x="344" y="245" font-size="9" fill="#0f172a">Income=0</text>
</svg>
""", "margin:0 auto; display:block;")

_SVG_PCR_SCREE = svg_diagram("""
<svg class="diagram" viewBox="0 0 580 270" width="560" height="260">
  <defs>
    <marker id="axArr5" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <line x1="60" y1="220" x2="530" y2="220" stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr5)"/>
  <line x1="60" y1="220" x2="60"  y2="20"  stroke="#64748b" stroke-width="1.5" marker-end="url(#axArr5)"/>
  <text x="295" y="248" text-anchor="middle" font-size="12" fill="#0f172a">Number of components M</text>
  <text x="16"  y="125" text-anchor="middle" font-size="12" fill="#0f172a" transform="rotate(-90 16 125)">CV MSE</text>
  <polyline points="100,190 160,155 220,120 280,90 340,75 400,72 460,71 510,70"
            fill="none" stroke="#2563eb" stroke-width="2.5"/>
  <polyline points="100,190 160,140 220,95 280,72 340,68 400,67 460,66 510,66"
            fill="none" stroke="#16a34a" stroke-width="2.5" stroke-dasharray="6,3"/>
  <line x1="60" y1="68" x2="525" y2="68" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="535" y="71" font-size="10" fill="#dc2626">OLS</text>
  <circle cx="340" cy="75" r="6" fill="#2563eb"/>
  <text x="344" y="65" font-size="10" fill="#2563eb">PCR opt M=5</text>
  <circle cx="280" cy="72" r="6" fill="#16a34a"/>
  <text x="284" y="60" font-size="10" fill="#16a34a">PLS opt M=4</text>
  <text x="100" y="234" text-anchor="middle" font-size="11" fill="#64748b">1</text>
  <text x="160" y="234" text-anchor="middle" font-size="11" fill="#64748b">2</text>
  <text x="220" y="234" text-anchor="middle" font-size="11" fill="#64748b">3</text>
  <text x="280" y="234" text-anchor="middle" font-size="11" fill="#64748b">4</text>
  <text x="340" y="234" text-anchor="middle" font-size="11" fill="#64748b">5</text>
  <text x="400" y="234" text-anchor="middle" font-size="11" fill="#64748b">6</text>
  <text x="460" y="234" text-anchor="middle" font-size="11" fill="#64748b">7</text>
  <line x1="370" y1="30" x2="400" y2="30" stroke="#2563eb" stroke-width="2.5"/>
  <text x="406" y="34" font-size="11" fill="#2563eb">PCR</text>
  <line x1="370" y1="47" x2="400" y2="47" stroke="#16a34a" stroke-width="2.5" stroke-dasharray="6,3"/>
  <text x="406" y="51" font-size="11" fill="#16a34a">PLS</text>
  <text x="295" y="18" text-anchor="middle" font-size="12" font-weight="bold" fill="#0f172a">PCR vs PLS: cross-validation MSE by M</text>
</svg>
""", "margin:0 auto; display:block;")

# ── Runnable example code strings ────────────────────────────────────────────

_CODE_BEST_SUBSET = """\
import numpy as np
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from itertools import combinations
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(42)
n, p = 100, 5
X = rng.normal(size=(n, p))
beta = np.array([3, 1.5, 0, 0, -2])
y = X @ beta + rng.normal(size=n)
names = [f'X{i+1}' for i in range(p)]

best = {}
for k in range(1, p + 1):
    best_rss, best_combo = np.inf, None
    for combo in combinations(range(p), k):
        Xk = X[:, combo]
        lr = LinearRegression().fit(Xk, y)
        rss = np.sum((y - lr.predict(Xk))**2)
        if rss < best_rss:
            best_rss, best_combo = rss, combo
    best[k] = (best_rss, best_combo)
    print(f'k={k}: predictors={[names[i] for i in best_combo]}, RSS={best_rss:.2f}')

ks = list(best.keys())
rss_vals = [best[k][0] for k in ks]
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(ks, rss_vals, 'ro-', ms=8, label='best-of-k frontier')
ax.set_xlabel('# predictors'); ax.set_ylabel('RSS')
ax.set_title('Best Subset — RSS frontier')
ax.legend(); plt.tight_layout(); plt.show()
"""

_CODE_AIC_BIC = """\
import numpy as np
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import pandas as pd
from itertools import combinations

rng = np.random.default_rng(0)
n = 200
df = pd.DataFrame({
    'x1': rng.normal(size=n), 'x2': rng.normal(size=n),
    'x3': rng.normal(size=n), 'x4': rng.normal(size=n),
})
df['y'] = 2*df['x1'] - 1.5*df['x2'] + rng.normal(size=n)

rows = []
for k in range(1, 5):
    for combo in combinations(['x1','x2','x3','x4'], k):
        m = smf.ols(f"y ~ {' + '.join(combo)}", data=df).fit()
        rows.append({'k': k, 'preds': combo,
                     'AIC': m.aic, 'BIC': m.bic, 'AdjR2': m.rsquared_adj})
res = pd.DataFrame(rows)

for col in ['AIC','BIC','AdjR2']:
    best = res.loc[res[col].idxmin() if col != 'AdjR2' else res[col].idxmax()]
    print(f'Best by {col}: {list(best.preds)}')

fig, axes = plt.subplots(1, 3, figsize=(11, 3))
for ax, col, low_good in zip(axes, ['AIC','BIC','AdjR2'], [True, True, False]):
    ax.scatter(res['k'], res[col], alpha=0.6)
    best_row = res.loc[res[col].idxmin() if low_good else res[col].idxmax()]
    ax.scatter(best_row['k'], best_row[col], color='red', s=80, zorder=5)
    ax.set_xlabel('# predictors'); ax.set_title(col)
plt.tight_layout(); plt.show()
"""

_CODE_RIDGE = """\
import numpy as np
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)
scaler = StandardScaler()
Xs = scaler.fit_transform(X)
feature_names = load_diabetes().feature_names

alphas = np.logspace(-2, 4, 200)
coefs = np.array([Ridge(alpha=a).fit(Xs, y).coef_ for a in alphas])

fig, ax = plt.subplots(figsize=(8, 4))
for i, name in enumerate(feature_names):
    ax.plot(np.log10(alphas), coefs[:, i], label=name, lw=1.6)
ax.axhline(0, color='k', lw=0.8, ls='--')
ax.set_xlabel('log10(lambda)'); ax.set_ylabel('Standardised coefficient')
ax.set_title('Ridge regression - coefficient paths')
ax.legend(fontsize=8, ncol=2, loc='upper right')
plt.tight_layout(); plt.show()

rcv = RidgeCV(alphas=alphas, cv=10).fit(Xs, y)
print(f'RidgeCV best alpha = {rcv.alpha_:.3f}')
print(f'All {len(rcv.coef_)} coefficients non-zero (Ridge never zeros out)')
"""

_CODE_LASSO = """\
import numpy as np
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)
scaler = StandardScaler()
Xs = scaler.fit_transform(X)
feature_names = load_diabetes().feature_names

alphas = np.logspace(-2, 1, 200)
coefs = np.array([
    Lasso(alpha=a, max_iter=5000).fit(Xs, y).coef_ for a in alphas
])

fig, ax = plt.subplots(figsize=(8, 4))
for i, name in enumerate(feature_names):
    ax.plot(np.log10(alphas), coefs[:, i], label=name, lw=1.6)
ax.axhline(0, color='k', lw=0.8, ls='--')
ax.set_xlabel('log10(lambda)'); ax.set_ylabel('Standardised coefficient')
ax.set_title('Lasso - coefficient paths (exact zeros!)')
ax.legend(fontsize=8, ncol=2, loc='lower right')
plt.tight_layout(); plt.show()

lcv = LassoCV(cv=10, max_iter=10000, random_state=0).fit(Xs, y)
print(f'LassoCV best alpha = {lcv.alpha_:.4f}')
zeroed = [n for n, c in zip(feature_names, lcv.coef_) if c == 0]
kept   = [n for n, c in zip(feature_names, lcv.coef_) if c != 0]
print(f'Zeroed out: {zeroed}')
print(f'Kept: {kept}')
"""

_CODE_PCR_PLS = """\
import numpy as np
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)
Xs = StandardScaler().fit_transform(X)

pcr_mse, pls_mse = [], []
Ms = range(1, 11)
for M in Ms:
    pcr = Pipeline([('pca', PCA(n_components=M)), ('lr', LinearRegression())])
    pcr_mse.append(-cross_val_score(pcr, Xs, y, cv=10,
                   scoring='neg_mean_squared_error').mean())
    pls = PLSRegression(n_components=M)
    pls_mse.append(-cross_val_score(pls, Xs, y, cv=10,
                   scoring='neg_mean_squared_error').mean())

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(Ms, pcr_mse, 'b-o', label='PCR (unsupervised PCA)', ms=7)
ax.plot(Ms, pls_mse, 'g--s', label='PLS (supervised)', ms=7)
ols_mse = -cross_val_score(LinearRegression(), Xs, y, cv=10,
                           scoring='neg_mean_squared_error').mean()
ax.axhline(ols_mse, color='red', ls=':', label=f'OLS ({ols_mse:.0f})')
ax.set_xlabel('M (components)'); ax.set_ylabel('CV MSE')
ax.set_title('PCR vs PLS on Diabetes data')
ax.legend(); plt.tight_layout(); plt.show()

best_M_pcr = int(np.argmin(pcr_mse)) + 1
best_M_pls = int(np.argmin(pls_mse)) + 1
print(f'Best PCR: M={best_M_pcr}, CV-MSE={pcr_mse[best_M_pcr-1]:.1f}')
print(f'Best PLS: M={best_M_pls}, CV-MSE={pls_mse[best_M_pls-1]:.1f}')
print(f'OLS CV-MSE: {ols_mse:.1f}')
"""

# ── Slide spec ────────────────────────────────────────────────────────────────

W3_MS = {
    "title": "Model Selection and Regularization",
    "kicker": "Week 3 · Course 4",
    "subtitle": "Subset selection, shrinkage (Ridge & Lasso), and dimension reduction",
    "parts_summary": [
        ("Part 1 · 0:00–0:30", "Subset Selection",
         "Best subset, forward & backward stepwise, comparison."),
        ("Part 2 · 0:30–1:00", "Choosing the Optimal Model",
         "Cp, AIC, BIC, Adj-R², validation set, CV, one-SE rule."),
        ("Part 3 · 1:00–1:20", "Ridge Regression",
         "L2 shrinkage, coefficient paths, bias-variance, scaling."),
        ("Part 4 · 1:20–1:40", "The Lasso",
         "L1 sparsity, geometric picture, Lasso vs Ridge."),
        ("Part 5 · 1:40–2:00", "Dimension Reduction",
         "PCR (unsupervised PCA) and PLS (supervised)."),
    ],
    "callout": (
        "Least squares is not the only way. Regularization and selection give you models "
        "that <em>generalise</em> better — trading a little bias for a large drop in variance."
    ),
    "parts": [
        {
            "kicker": "Part 1 · 0:00 – 0:30",
            "title": "Subset Selection",
            "subtitle": "Best subset, forward stepwise, backward stepwise",
            "slides": [
                slide(
                    "Why replace least squares?",
                    bullets([
                        "<strong>Prediction accuracy:</strong> OLS has low bias but can have high variance, especially when p is large relative to n.",
                        "<strong>Model interpretability:</strong> setting irrelevant coefficients to zero yields a simpler, more interpretable model.",
                        "Two families of fix: <em>subset selection</em> (keep only some predictors) and <em>shrinkage</em> (shrink all coefficients toward zero).",
                        "A third approach — <em>dimension reduction</em> — projects predictors into a lower-dimensional subspace.",
                    ]),
                    "The key tension: OLS minimises training error; we care about test error. Adding variables always reduces training RSS but may increase test error.",
                ),
                slide(
                    "Best Subset Selection",
                    two_col(
                        bullets([
                            "Fit all <strong>2<sup>p</sup></strong> possible models (one per predictor subset).",
                            "For each size k, keep the model with smallest RSS — call it M<sub>k</sub>.",
                            "Finally choose the single best M<sub>k</sub> using an external criterion (CV, AIC, BIC).",
                            "Guaranteed to find the globally best subset — but <strong>2<sup>40</sup> ≈ 10<sup>12</sup></strong> models for p=40!",
                        ], fragments=False),
                        _SVG_SUBSET_FRONTIER,
                    ),
                    "Grey dots = all possible models. Red frontier = best model at each size k. RSS always decreases as k grows, so we cannot use RSS alone to pick k.",
                ),
                slide(
                    "Forward Stepwise Selection",
                    bullets([
                        "Start with M<sub>0</sub>: the null model (intercept only).",
                        "For k = 0, …, p−1: add the <em>one predictor</em> that most improves fit (smallest RSS / largest R²).",
                        "Produces a nested sequence M<sub>0</sub> ⊂ M<sub>1</sub> ⊂ … ⊂ M<sub>p</sub>.",
                        "Considers only <strong>1 + p(p+1)/2</strong> models vs 2<sup>p</sup> — computationally feasible for large p.",
                        "<strong>Caveat:</strong> not guaranteed to find the globally best subset.",
                    ]),
                    "Forward stepwise is greedy: once a variable is added it stays. This can miss the optimal model if two variables together explain Y but neither alone does.",
                ),
                slide(
                    "Backward Stepwise Selection",
                    bullets([
                        "Start with M<sub>p</sub>: the full model with all p predictors.",
                        "At each step remove the <em>least useful</em> predictor (largest p-value / smallest |t-statistic|).",
                        "Requires <strong>n &gt; p</strong> so the full model can be fit — forward stepwise can handle n &lt; p.",
                        "Also searches only 1 + p(p+1)/2 models.",
                        "Neither forward nor backward stepwise is universally better — use CV to choose.",
                    ]),
                    "Backward stepwise starts from the opposite end. It can also miss the optimal subset.",
                ),
                slide(
                    "Forward vs. Best Subset — Credit data",
                    two_col(
                        """<table style="font-size:0.85em; border-collapse:collapse; width:100%;">
<tr style="background:#f1f5f9;">
  <th style="padding:4px 8px; border:1px solid #cbd5e1;"># Vars</th>
  <th style="padding:4px 8px; border:1px solid #cbd5e1;">Best Subset</th>
  <th style="padding:4px 8px; border:1px solid #cbd5e1;">Forward Stepwise</th>
</tr>
<tr><td style="padding:4px 8px; border:1px solid #cbd5e1; text-align:center;">1</td>
    <td style="padding:4px 8px; border:1px solid #cbd5e1;">rating</td>
    <td style="padding:4px 8px; border:1px solid #cbd5e1;">rating</td></tr>
<tr style="background:#f8fafc;"><td style="padding:4px 8px; border:1px solid #cbd5e1; text-align:center;">2</td>
    <td style="padding:4px 8px; border:1px solid #cbd5e1;">rating, income</td>
    <td style="padding:4px 8px; border:1px solid #cbd5e1;">rating, income</td></tr>
<tr><td style="padding:4px 8px; border:1px solid #cbd5e1; text-align:center;">3</td>
    <td style="padding:4px 8px; border:1px solid #cbd5e1;">rating, income, student</td>
    <td style="padding:4px 8px; border:1px solid #cbd5e1;">rating, income, student</td></tr>
<tr style="background:#fef2f2;"><td style="padding:4px 8px; border:1px solid #cbd5e1; text-align:center;">4</td>
    <td style="padding:4px 8px; border:1px solid #cbd5e1;"><strong>cards, income,<br/>student, limit</strong></td>
    <td style="padding:4px 8px; border:1px solid #cbd5e1;"><strong>rating, income,<br/>student, limit</strong></td></tr>
</table>""",
                        bullets([
                            "First three models identical.",
                            "4-variable models <strong>differ</strong> — forward selection is greedy.",
                            "In practice the difference rarely matters for prediction.",
                            "Always validate with CV, not just training RSS.",
                        ], fragments=False),
                    ),
                    "The takeaway: stepwise methods are practical approximations that work well in practice.",
                ),
                example_slide(
                    "Best subset selection — live",
                    "Enumerate all 2ᵖ models on a simulated dataset. Plot the RSS frontier and print the best predictor set for each size k.",
                    _CODE_BEST_SUBSET,
                    packages="numpy,matplotlib,sklearn",
                ),
            ],
        },
        {
            "kicker": "Part 2 · 0:30 – 1:00",
            "title": "Choosing the Optimal Model",
            "subtitle": "Cp, AIC, BIC, Adj-R², validation, and cross-validation",
            "slides": [
                slide(
                    "Training error is a bad guide",
                    bullets([
                        "The full model (all p predictors) always has the <strong>smallest RSS</strong> and <strong>largest R²</strong> on the training set.",
                        "But training error <em>underestimates</em> test error — it does not account for overfitting.",
                        "RSS and R² cannot compare models with <em>different numbers of predictors</em>.",
                        "We need an honest estimate of test error: either by <strong>adjusting</strong> training error upward, or by <strong>directly estimating</strong> it via held-out data.",
                    ]),
                    "This is the core tension: training error rewards complexity; test error punishes it.",
                ),
                slide(
                    "Mallow’s Cₚ and AIC",
                    two_col(
                        """<p style="font-size:0.9em;">
<strong>Mallow’s C<sub>p</sub></strong><br/>
<code>C<sub>p</sub> = (RSS + 2dσ̂²) / n</code><br/>
<span class="muted">d = # parameters, σ̂² = estimated error variance.<br/>
Adds a penalty of 2σ̂² per parameter. Select <strong>smallest C<sub>p</sub></strong>.</span>
</p>
<hr style="margin:0.5em 0; border-color:#e2e8f0;"/>
<p style="font-size:0.9em;">
<strong>AIC</strong><br/>
<code>AIC = −2 log L + 2d</code><br/>
<span class="muted">For Gaussian OLS: <strong>AIC and C<sub>p</sub> are equivalent</strong>.</span>
</p>""",
                        bullets([
                            "Both add a <strong>complexity penalty</strong> proportional to d.",
                            "Select the model that <strong>minimises</strong> C<sub>p</sub> or AIC.",
                            "σ̂² is estimated from the full model.",
                            "AIC generalises to any maximum-likelihood model.",
                        ], fragments=False),
                    ),
                    "AIC generalises Cp to non-Gaussian models. The penalty 2d is the same.",
                ),
                slide(
                    "BIC and Adjusted R²",
                    two_col(
                        """<p style="font-size:0.9em;">
<strong>BIC</strong><br/>
<code>BIC = (RSS + log(n)·d·σ̂²) / n</code><br/>
<span class="muted">Replaces 2 with log(n). Since log(n) &gt; 2 for n &gt; 7, BIC <strong>penalises more</strong> and picks smaller models.</span>
</p>
<hr style="margin:0.5em 0; border-color:#e2e8f0;"/>
<p style="font-size:0.9em;">
<strong>Adjusted R²</strong><br/>
<code>Adj R² = 1 − RSS/(n−d−1) / TSS/(n−1)</code><br/>
<span class="muted">Can <em>decrease</em> when an unhelpful predictor is added. <strong>Maximise</strong> Adj R².</span>
</p>""",
                        bullets([
                            "BIC tends to select <strong>smaller</strong> models than AIC.",
                            "Adj R² penalises by (n−d−1) in denominator.",
                            "All four adjust for model complexity.",
                            "In practice BIC and CV often agree.",
                        ], fragments=False),
                    ),
                    "BIC has a Bayesian justification and consistently selects the true model for large n.",
                ),
                slide(
                    "Validation set and cross-validation",
                    bullets([
                        "<strong>Validation set:</strong> reserve 20–30% of data. Fit on the rest; pick model with smallest held-out MSE.",
                        "<strong>K-fold CV:</strong> rotate the hold-out set K times; average the MSE estimates. More stable.",
                        "Advantage over AIC/BIC: <strong>no estimate of σ² needed</strong> — works for any loss and any method.",
                        "Use <code>cross_val_score</code> from sklearn with <code>scoring='neg_mean_squared_error'</code>.",
                    ]),
                    "CV is the most widely recommended approach for model selection today.",
                ),
                slide(
                    "The one-standard-error rule",
                    bullets([
                        "CV picks the model with the <em>absolute</em> minimum CV error.",
                        "Neighbouring model sizes often have CV errors <strong>within one SE</strong> — statistically indistinguishable.",
                        "<strong>One-SE rule:</strong> pick the <em>simplest</em> model whose CV error is within one SE of the minimum.",
                        "Rationale: prefer fewer predictors when the predictive gain is within noise.",
                    ]),
                    "The one-SE rule is a practical heuristic for preferring parsimony.",
                ),
                example_slide(
                    "AIC, BIC, Adj-R² — live comparison",
                    "Enumerate all subset models on simulated data. Compare AIC, BIC, and Adj-R². Red dot = best model per criterion.",
                    _CODE_AIC_BIC,
                    packages="numpy,matplotlib,sklearn,statsmodels",
                ),
            ],
        },
        {
            "kicker": "Part 3 · 1:00 – 1:20",
            "title": "Ridge Regression",
            "subtitle": "L2 shrinkage, coefficient paths, and the bias–variance trade-off",
            "slides": [
                slide(
                    "Ridge regression — the objective",
                    two_col(
                        """<p style="font-size:0.88em;">
<strong>OLS objective:</strong><br/>
<code>minimise  RSS = Σ(yᵢ − β₀ − Σβⱼxᵢⱼ)²</code>
</p>
<hr style="margin:0.5em 0; border-color:#e2e8f0;"/>
<p style="font-size:0.88em;">
<strong>Ridge objective:</strong><br/>
<code>minimise  RSS + λ Σβⱼ²</code><br/>
<span class="muted">λ ≥ 0 is the <em>tuning parameter</em>.<br/>
λΣβⱼ² is the <strong>L2 shrinkage penalty</strong>.</span>
</p>
<p class="callout" style="font-size:0.85em; margin-top:0.6em;">β̂₀ is <em>not</em> penalised — only slope coefficients are shrunk.</p>""",
                        bullets([
                            "λ = 0 → <strong>OLS</strong> (no penalty).",
                            "λ → ∞ → all coefficients → <strong>zero</strong>.",
                            "Intermediate λ → coefficients shrunk <em>toward</em> zero but not exactly zero.",
                            "Ridge <strong>never performs variable selection</strong> — all p predictors remain.",
                            "Selecting λ is critical; use <strong>cross-validation</strong>.",
                        ], fragments=False),
                    ),
                    "The ridge penalty has a Bayesian interpretation: it corresponds to a Gaussian prior on the coefficients centered at zero.",
                ),
                slide(
                    "Coefficient paths and the need to standardise",
                    two_col(
                        _SVG_RIDGE_PATHS,
                        bullets([
                            "Each curve = one coefficient as λ increases from left (OLS) to right (zero).",
                            "All shrink smoothly — none reaches exactly zero.",
                            "<strong>Must standardise predictors</strong> before fitting ridge: the L2 penalty is not scale-equivariant.",
                            "Use <code>StandardScaler</code> (zero mean, unit variance).",
                        ], fragments=False),
                    ),
                    "Without standardisation a predictor in millions is penalised more than one in single digits.",
                ),
                slide(
                    "Why ridge improves over OLS: bias–variance trade-off",
                    two_col(
                        _SVG_BV_CURVE,
                        bullets([
                            "OLS: zero bias, but <strong>high variance</strong> when p is large.",
                            "As λ grows, bias increases slightly but <strong>variance drops sharply</strong>.",
                            "Test MSE = Bias² + Variance + σ² has a <strong>U-shape</strong> — minimum at optimal λ.",
                            "Ridge wins when variance reduction outweighs bias increase.",
                            "Especially helpful when p is close to n or predictors are correlated.",
                        ], fragments=False),
                    ),
                    "Ridge adds a spring that pulls all coefficients toward zero, reducing wild swinging from multicollinearity.",
                ),
                slide(
                    "Selecting λ by cross-validation",
                    bullets([
                        "Try a grid of λ values (log-spaced from very small to very large).",
                        "For each λ, compute the <strong>K-fold CV error</strong>.",
                        "Select the λ that minimises CV error (or one-SE rule).",
                        "Re-fit the final model on <em>all</em> training data using the selected λ.",
                        "<code>sklearn.linear_model.RidgeCV</code> does this automatically and efficiently.",
                    ]),
                    "RidgeCV uses an efficient leave-one-out formula (GCV) so it is much faster than running Ridge K times per lambda.",
                ),
                example_slide(
                    "Ridge regression — coefficient paths & CV",
                    "Fit Ridge on the Diabetes dataset. Plot how each coefficient shrinks as λ grows. Use RidgeCV to pick the optimal λ.",
                    _CODE_RIDGE,
                    packages="numpy,matplotlib,sklearn",
                ),
            ],
        },
        {
            "kicker": "Part 4 · 1:20 – 1:40",
            "title": "The Lasso",
            "subtitle": "L1 sparsity, variable selection, and the geometric picture",
            "slides": [
                slide(
                    "The Lasso objective",
                    two_col(
                        """<p style="font-size:0.88em;">
<strong>Lasso objective:</strong><br/>
<code>minimise  RSS + λ Σ|βⱼ|</code><br/>
<span class="muted">Uses the <em>L1 norm</em> (sum of absolute values).<br/>
When λ is large enough, some coefficients are forced to be <strong>exactly zero</strong>.</span>
</p>
<p class="callout" style="font-size:0.85em; margin-top:0.6em;">
The lasso performs <em>variable selection</em> — the kink at zero in |β| is what causes exact zeros.
</p>""",
                        bullets([
                            "λ = 0 → OLS (no penalty).",
                            "λ → ∞ → null model (all slopes = 0).",
                            "Intermediate λ → some coefficients are <strong>exactly zero</strong>.",
                            "Lasso gives a <strong>sparse model</strong> — interpretable like best subset.",
                            "Also called LASSO: <em>Least Absolute Shrinkage and Selection Operator</em>.",
                        ], fragments=False),
                    ),
                    "The lasso was proposed by Tibshirani in 1996.",
                ),
                slide(
                    "Why the lasso produces exact zeros — geometry",
                    two_col(
                        _SVG_LASSO_CONSTRAINT,
                        bullets([
                            "Lasso: <code>min RSS  s.t.  Σ|βⱼ| ≤ s</code>",
                            "Ridge: <code>min RSS  s.t.  Σβⱼ² ≤ s</code>",
                            "RSS ellipses expand outward from β̂ (OLS minimum).",
                            "Lasso constraint is a <strong>diamond</strong> with corners on axes.",
                            "Ellipse hits the corner first → coefficient is <strong>exactly zero</strong>.",
                            "Ridge constraint is a <strong>sphere</strong> — smooth, no corners → never exactly zero.",
                        ], fragments=False),
                    ),
                    "The corners of the L1 diamond lie on the coordinate axes. The expanding ellipse contacts a corner instead of a smooth edge.",
                ),
                slide(
                    "Lasso coefficient paths",
                    two_col(
                        _SVG_LASSO_PATHS,
                        bullets([
                            "As λ grows, coefficients are driven to exactly zero <strong>one by one</strong>.",
                            "The order of zeroing reflects predictor importance.",
                            "Contrast with ridge: all approach zero but <em>never reach it</em>.",
                            "LassoCV selects the λ minimising CV error.",
                            "Always standardise predictors before fitting lasso.",
                        ], fragments=False),
                    ),
                    "Reading the path: at small lambda all coefficients equal OLS. As lambda grows, the least important predictors are zeroed first.",
                ),
                slide(
                    "Lasso vs Ridge — when to choose which",
                    two_col(
                        """<div>
<h3 style="color:#2563eb; margin:0 0 0.3em;">Lasso</h3>
<ul style="font-size:0.88em; margin:0; padding-left:1.2em;">
  <li>Sparse models (exact zeros).</li>
  <li>Automatic <strong>variable selection</strong>.</li>
  <li>Best when <strong>few predictors</strong> truly matter.</li>
  <li>More interpretable output.</li>
</ul>
</div>""",
                        """<div>
<h3 style="color:#dc2626; margin:0 0 0.3em;">Ridge</h3>
<ul style="font-size:0.88em; margin:0; padding-left:1.2em;">
  <li>Keeps all predictors (shrinks but never zeros).</li>
  <li>Best when <strong>many predictors</strong> all contribute a little.</li>
  <li>Handles multicollinearity well.</li>
  <li>Slightly better MSE when signal is diffuse.</li>
</ul>
</div>""",
                    ),
                    "Cross-validation can tell you which is better for your dataset. Elastic Net interpolates between the two.",
                ),
                example_slide(
                    "Lasso — sparsity and variable selection",
                    "Plot Lasso coefficient paths on the Diabetes dataset. Use LassoCV to find optimal λ and report which features are zeroed out.",
                    _CODE_LASSO,
                    packages="numpy,matplotlib,sklearn",
                ),
            ],
        },
        {
            "kicker": "Part 5 · 1:40 – 2:00",
            "title": "Dimension Reduction",
            "subtitle": "Principal Components Regression and Partial Least Squares",
            "slides": [
                slide(
                    "Dimension reduction — the idea",
                    bullets([
                        "Rather than selecting or shrinking the original p predictors, <strong>transform</strong> them into M &lt; p new features Z₁, …, Z<sub>M</sub>.",
                        "Each Z<sub>m</sub> = Σ φ<sub>mj</sub> X<sub>j</sub> — a <em>linear combination</em> of the originals.",
                        "Then fit OLS of Y on Z₁, …, Z<sub>M</sub>.",
                        "Constraints on the coefficient space → <strong>variance reduction</strong>.",
                        "Key question: <em>how do we choose the linear combinations?</em>",
                    ]),
                    "Dimension reduction can be seen as a form of regularisation: it constrains coefficients to lie in a lower-dimensional subspace.",
                ),
                slide(
                    "Principal Components Regression (PCR)",
                    two_col(
                        bullets([
                            "<strong>Step 1:</strong> compute the first M principal components (PCA) of X — directions of maximum variance.",
                            "<strong>Step 2:</strong> regress Y on these M PCs using OLS.",
                            "PCA is <em>unsupervised</em> — the response Y is not used to determine the directions.",
                            "Assumption: highest-variance directions in X are also most relevant to Y.",
                            "Choose M by cross-validation.",
                        ], fragments=False),
                        bullets([
                            "M = p → OLS (no reduction).",
                            "M = 1 → regress on single direction of most variance.",
                            "Works well when a few PCs capture most variation in X.",
                            "Drawback: PC directions may not correlate with Y.",
                        ], fragments=False),
                    ),
                    "PCR was proposed by Hotelling in the 1930s. It is the simplest dimension reduction method and still widely used.",
                ),
                slide(
                    "Partial Least Squares (PLS)",
                    bullets([
                        "PLS also finds M &lt; p linear combinations — but in a <strong>supervised</strong> way.",
                        "Z₁ is the linear combination of X most correlated with Y.",
                        "Subsequent directions are orthogonalised against previous ones.",
                        "PLS uses the response to <em>guide</em> direction choice → often better directions than PCR.",
                        "In practice PLS and PCR often give similar results with CV tuning.",
                    ]),
                    "PLS was developed by Herman Wold for chemometrics in the 1970s. It is especially popular in genomics where p >> n.",
                ),
                slide(
                    "PCR vs PLS — choosing M",
                    two_col(
                        _SVG_PCR_SCREE,
                        bullets([
                            "Choose M by <strong>K-fold CV</strong> — plot CV-MSE vs number of components.",
                            "PLS often needs fewer components than PCR.",
                            "Both typically outperform OLS when p is large relative to n.",
                            "sklearn: <code>PCA + LinearRegression</code> pipeline for PCR; <code>PLSRegression</code> for PLS.",
                        ], fragments=False),
                    ),
                    "PLS reaches its minimum CV-MSE with fewer components because its directions are guided by the response.",
                ),
                slide(
                    "Comparing all methods — practical guide",
                    """<table style="font-size:0.82em; border-collapse:collapse; width:100%;">
<tr style="background:#f1f5f9;">
  <th style="padding:5px 8px; border:1px solid #cbd5e1;">Method</th>
  <th style="padding:5px 8px; border:1px solid #cbd5e1;">Variable selection?</th>
  <th style="padding:5px 8px; border:1px solid #cbd5e1;">Best when…</th>
  <th style="padding:5px 8px; border:1px solid #cbd5e1;">Key parameter</th>
</tr>
<tr><td style="padding:5px 8px; border:1px solid #cbd5e1;"><strong>Best Subset</strong></td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">Yes (exact)</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">p ≤ 30, computation OK</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">k (# predictors)</td></tr>
<tr style="background:#f8fafc;"><td style="padding:5px 8px; border:1px solid #cbd5e1;"><strong>Forward/Backward</strong></td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">Yes (greedy)</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">Large p, fast needed</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">k (stop criterion)</td></tr>
<tr><td style="padding:5px 8px; border:1px solid #cbd5e1;"><strong>Ridge</strong></td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">No (shrinks all)</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">Many small effects, multicollinearity</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">λ</td></tr>
<tr style="background:#f8fafc;"><td style="padding:5px 8px; border:1px solid #cbd5e1;"><strong>Lasso</strong></td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">Yes (exact zeros)</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">Few true predictors, interpretability</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">λ</td></tr>
<tr><td style="padding:5px 8px; border:1px solid #cbd5e1;"><strong>PCR</strong></td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">No</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">Highly correlated X, p &gt; n</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">M (# components)</td></tr>
<tr style="background:#f8fafc;"><td style="padding:5px 8px; border:1px solid #cbd5e1;"><strong>PLS</strong></td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">No</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">p &gt; n, Y-relevant structure</td>
    <td style="padding:5px 8px; border:1px solid #cbd5e1;">M (# components)</td></tr>
</table>
<p class="muted" style="margin-top:0.5em; font-size:0.88em;">Always use cross-validation to select the key parameter. No method universally dominates.</p>""",
                    "The right method depends on whether you believe the true model is sparse (Lasso) or dense (Ridge/PCR/PLS).",
                ),
                example_slide(
                    "PCR vs PLS — live comparison",
                    "Fit PCR and PLS on the Diabetes dataset. Plot 10-fold CV-MSE vs number of components M. Find the optimal M for each and compare to OLS.",
                    _CODE_PCR_PLS,
                    packages="numpy,matplotlib,sklearn",
                ),
            ],
        },
    ],
    "recap_items": [
        "<strong>Subset selection</strong> (best subset, forward, backward) identifies which predictors to include. CV or BIC chooses the model size.",
        "<strong>Ridge (L2) and Lasso (L1)</strong> shrink coefficients toward zero. Lasso creates exact zeros — variable selection. CV picks λ.",
        "<strong>PCR and PLS</strong> reduce dimension first, then regress. PCR is unsupervised; PLS uses the response to guide directions.",
    ],
    "recap_callout": (
        "No single method wins everywhere. Use cross-validation to compare them on your data. "
        "Lasso is usually the first choice when you want sparsity; Ridge when you expect many small effects."
    ),
}


# ============================================================================
# WEEK 3 · COURSE 5 — Moving Beyond Linearity
# ============================================================================

_CODE_POLYNOMIAL = """\
import numpy as np
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(42)
x = np.linspace(18, 80, 200)
wage = 110 - 0.015*(x-49)**2 + 0.3*(x-49) + rng.normal(0, 20, 200)

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
x_rng = np.linspace(18, 80, 300).reshape(-1, 1)

for deg, ax, color in zip([1, 4], axes, ['tab:blue', 'tab:orange']):
    pipe = Pipeline([
        ('poly', PolynomialFeatures(degree=deg, include_bias=False)),
        ('lr', LinearRegression())
    ])
    pipe.fit(x.reshape(-1,1), wage)
    ax.scatter(x, wage, alpha=0.4, s=20, color='steelblue')
    ax.plot(x_rng, pipe.predict(x_rng), color=color, lw=2.5,
            label=f'Degree {deg}')
    ax.set_xlabel('Age'); ax.set_ylabel('Wage')
    ax.set_title(f'Degree-{deg} Polynomial')
    ax.legend()

plt.tight_layout()
plt.show()
"""

_CODE_STEP_SPLINE = """\
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

rng = np.random.default_rng(42)
age = np.sort(rng.integers(18, 81, 300).astype(float))
wage = 110 - 0.015*(age-49)**2 + 0.3*(age-49) + rng.normal(0, 20, 300)

# Step function via pd.cut
cuts = [18, 33.5, 49, 64.5, 80]
labels = ['18-33', '33-49', '49-65', '65-80']
cat = pd.cut(age, bins=cuts, labels=labels, include_lowest=True)
D = pd.get_dummies(cat).values.astype(float)
m = LinearRegression(fit_intercept=True).fit(D, wage)

x_rng = np.linspace(18, 80, 400)
cat_rng = pd.cut(x_rng, bins=cuts, labels=labels, include_lowest=True)
D_rng = pd.get_dummies(cat_rng).values.astype(float)

fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(age, wage, alpha=0.35, s=20, color='steelblue')
ax.step(x_rng, m.predict(D_rng), where='mid',
        color='darkorange', lw=2.5, label='Step function')
for c in cuts[1:-1]:
    ax.axvline(c, color='grey', lw=0.8, linestyle='--', alpha=0.6)
ax.set_xlabel('Age'); ax.set_ylabel('Wage')
ax.set_title('Step Function (Piecewise Constant)')
ax.legend(); plt.tight_layout(); plt.show()
"""

_CODE_CUBIC_SPLINE = """\
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy.interpolate import UnivariateSpline

rng = np.random.default_rng(42)
age = np.sort(rng.integers(18, 81, 300).astype(float))
wage = 110 - 0.015*(age-49)**2 + 0.3*(age-49) + rng.normal(0, 20, 300)
x_rng = np.linspace(18, 80, 300)

def trunc_power_basis(x, knots, d=3):
    cols = [x**k for k in range(1, d+1)]
    for kn in knots:
        cols.append(np.maximum(x - kn, 0)**d)
    return np.column_stack(cols)

knots = np.quantile(age, [0.25, 0.5, 0.75])
X = trunc_power_basis(age, knots)
m = LinearRegression(fit_intercept=True).fit(X, wage)
y_cubic = m.predict(trunc_power_basis(x_rng, knots))

# Smoothing spline via scipy
spl = UnivariateSpline(age, wage, k=3, s=len(age)*200)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, (y_hat, label, color) in zip(axes, [
    (y_cubic, 'Cubic Spline (3 knots)', 'tab:orange'),
    (spl(x_rng), 'Smoothing Spline', 'tab:red'),
]):
    ax.scatter(age, wage, alpha=0.3, s=20, color='steelblue')
    ax.plot(x_rng, y_hat, color=color, lw=2.5, label=label)
    ax.set_xlabel('Age'); ax.set_ylabel('Wage'); ax.legend()
    ax.set_title(label)

plt.tight_layout(); plt.show()
"""

_CODE_SMOOTHING_SPLINE = """\
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

rng = np.random.default_rng(42)
age = np.sort(rng.integers(18, 81, 300).astype(float))
wage = 110 - 0.015*(age-49)**2 + 0.3*(age-49) + rng.normal(0, 20, 300)
x_rng = np.linspace(18, 80, 300)

smoothing_levels = [
    (age.size * 20,   '16 df  (wiggly)',  'tab:red'),
    (age.size * 200,  '6.8 df (LOOCV)',   'tab:blue'),
    (age.size * 2000, '~2 df  (linear)',  'tab:green'),
]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.scatter(age, wage, alpha=0.25, s=20, color='grey')
for s, label, color in smoothing_levels:
    spl = UnivariateSpline(age, wage, k=3, s=s)
    ax.plot(x_rng, spl(x_rng), lw=2.5, color=color, label=label)

ax.set_xlabel('Age'); ax.set_ylabel('Wage')
ax.set_title('Smoothing Spline — Effect of lambda (s parameter)')
ax.legend(); plt.tight_layout(); plt.show()
"""

_CODE_LOESS = """\
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

rng = np.random.default_rng(42)
age = np.sort(rng.integers(18, 81, 300).astype(float))
wage = 110 - 0.015*(age-49)**2 + 0.3*(age-49) + rng.normal(0, 20, 300)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.scatter(age, wage, alpha=0.3, s=20, color='steelblue', label='Data')

for frac, color, label in [
    (0.2, 'tab:orange', 'span = 0.2 (wiggly)'),
    (0.5, 'tab:red',    'span = 0.5'),
    (0.8, 'tab:green',  'span = 0.8 (smooth)'),
]:
    smooth = lowess(wage, age, frac=frac, return_sorted=True)
    ax.plot(smooth[:, 0], smooth[:, 1], lw=2.5, color=color, label=label)

ax.set_xlabel('Age'); ax.set_ylabel('Wage')
ax.set_title('Local Regression (LOESS) — Different Span Values')
ax.legend(); plt.tight_layout(); plt.show()
"""

_CODE_GAM = """\
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy.interpolate import UnivariateSpline

rng = np.random.default_rng(42)
n = 500
age  = rng.integers(18, 81, n).astype(float)
year = rng.integers(2003, 2010, n).astype(float)
edu  = rng.choice(['HS', 'College', 'Grad'], n, p=[0.4, 0.4, 0.2])
wage = (110
        - 0.015*(age-49)**2 + 0.3*(age-49)
        + 1.5*(year-2006)
        + np.where(edu=='HS', 0, np.where(edu=='College', 15, 30))
        + rng.normal(0, 18, n))

# Build feature matrix: spline on age + linear year + dummies for edu
def spline_cols(x, knots, k=3):
    cols = [x**d for d in range(1, k+1)]
    for kn in knots: cols.append(np.maximum(x - kn, 0)**k)
    return np.column_stack(cols)

knots_age = np.quantile(age, [0.25, 0.5, 0.75])
X_age  = spline_cols(age, knots_age)
X_year = (year - year.mean()).reshape(-1, 1)
X_edu  = pd.get_dummies(edu, drop_first=True).values.astype(float)
X = np.column_stack([X_year, X_age, X_edu])
m = LinearRegression(fit_intercept=True).fit(X, wage)

print(f"GAM R² = {m.score(X, wage):.3f}")

# Plot age component
age_rng = np.linspace(age.min(), age.max(), 200)
X_age_rng = spline_cols(age_rng, knots_age)
n_age = X_age.shape[1]
f_age = X_age_rng @ m.coef_[1:1+n_age]
f_age -= f_age.mean()

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(age_rng, f_age, color='tab:red', lw=2.5)
ax.axhline(0, color='grey', lw=0.7, linestyle='--')
ax.set_xlabel('Age'); ax.set_ylabel('f(age)')
ax.set_title('GAM: Partial Effect of Age')
plt.tight_layout(); plt.show()
"""

W3_BL = {
    "title": "Moving Beyond Linearity",
    "kicker": "Week 3 · Course 5",
    "subtitle": "Polynomials, splines, local regression, and generalized additive models",
    "parts_summary": [
        ("Part 1 · 0:00–0:20", "Polynomial Regression",
         "Degree-d models, fitted curves, logistic extension, tail caveats."),
        ("Part 2 · 0:20–0:35", "Step Functions & Piecewise Polynomials",
         "Piecewise constant fits, dummy encoding, path from steps to splines."),
        ("Part 3 · 0:35–1:00", "Splines",
         "Linear, cubic, and natural cubic splines; knot placement, df trade-offs."),
        ("Part 4 · 1:00–1:20", "Smoothing Splines",
         "Roughness-penalised fit, effective df, LOOCV lambda selection."),
        ("Part 5 · 1:20–1:40", "Local Regression",
         "Sliding weighted window, span parameter, loess()."),
        ("Part 6 · 1:40–2:00", "Generalized Additive Models",
         "Additive structure, GAM components, GAM for classification."),
    ],
    "callout": (
        "Linear models are a starting point, not the end. "
        "These methods let you capture <em>any</em> smooth nonlinear relationship "
        "while staying interpretable."
    ),
    "parts": [
        # ------------------------------------------------------------------ #
        # Part 1 — Polynomial Regression                                      #
        # ------------------------------------------------------------------ #
        {
            "kicker": "Part 1 · 0:00 – 0:20",
            "title": "Polynomial Regression",
            "subtitle": "Extending the linear model with higher-degree terms",
            "slides": [
                slide(
                    "Why go beyond linearity?",
                    bullets([
                        "Linear models are easy to fit and interpret — but the world is rarely linear.",
                        "We want methods that are <em>flexible</em> yet still <em>interpretable</em>, unlike black-box models.",
                        "Key insight: we can enrich the linear model by <strong>transforming the predictors</strong>, while keeping the same least-squares machinery.",
                        "Five families: <strong>polynomials</strong>, step functions, splines, local regression, and GAMs — each a different way to bend the line.",
                    ]),
                    "The beauty of these methods: they all fit into the standard linear model framework — you create new input columns and run lm() or LinearRegression() as usual.",
                ),
                slide(
                    "The Polynomial Model",
                    two_col(
                        bullets([
                            "Replace the single linear predictor X with <strong>X, X², X³, …, Xᵈ</strong>.",
                            "y<sub>i</sub> = β₀ + β₁x<sub>i</sub> + β₂x<sub>i</sub>² + β₃x<sub>i</sub>³ + … + βₐx<sub>i</sub>ᵈ + ε<sub>i</sub>",
                            "Treat X<sub>k</sub> = x<sup>k</sup> as a new variable — then it's just <strong>multiple linear regression</strong>.",
                            "Degree d is a hyperparameter: choose by CV or fix at a small value (d ≤ 5).",
                            "<strong>Caveat:</strong> polynomials have notorious tail behaviour — they oscillate wildly outside the training range.",
                        ], fragments=False),
                        f'<img src="img/ch7_polynomial_fit.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "The coefficients themselves are hard to interpret, but the fitted curve f̂(x) is the object of interest.",
                ),
                slide(
                    "Fitted values and confidence bands",
                    bullets([
                        "We care about <strong>ŷ(x₀) = β̂₀ + β̂₁x₀ + β̂₂x₀² + β̂₃x₀³ + β̂₄x₀⁴</strong> at any test point x₀.",
                        "Since ŷ(x₀) is a linear function of β̂, we get a simple expression for its variance — use OLS standard error formula.",
                        "Plot ŷ(x₀) ± 2·se[ŷ(x₀)] as a <strong>pointwise confidence band</strong>.",
                        "In Python: fit with <code>PolynomialFeatures + LinearRegression</code>, or <code>np.polyfit</code>; CIs via <code>statsmodels.OLS</code>.",
                        "In R: <code>y ~ poly(x, degree=3)</code> — orthogonal polynomials are numerically more stable.",
                    ]),
                    "Pointwise CI != simultaneous CI — the band tells you the uncertainty at each individual x₀, not jointly across all x₀.",
                ),
                slide(
                    "Logistic polynomial extension",
                    two_col(
                        bullets([
                            "Polynomial features work seamlessly inside <strong>logistic regression</strong>.",
                            "Example: Pr(wage > 250 | age) modelled as a logistic function of age<sup>1</sup>…age<sup>4</sup>.",
                            "Compute CIs on the <em>logit scale</em>, then invert with σ(·) to get CI on the probability scale.",
                            "The rug plot at the bottom shows the (rare) high-earner observations.",
                        ], fragments=False),
                        f'<img src="img/ch7_polynomial_logistic.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "Computing CIs on logit scale and then transforming avoids probabilities outside [0,1].",
                ),
                example_slide(
                    "Polynomial regression — live",
                    "Fit degree-1 and degree-4 polynomials on simulated wage data. Plot both fits side by side.",
                    _CODE_POLYNOMIAL,
                    packages="numpy,matplotlib,sklearn",
                ),
            ],
        },
        # ------------------------------------------------------------------ #
        # Part 2 — Step Functions & Piecewise Polynomials                     #
        # ------------------------------------------------------------------ #
        {
            "kicker": "Part 2 · 0:20 – 0:35",
            "title": "Step Functions & Piecewise Polynomials",
            "subtitle": "Breaking the range into regions — constant or polynomial per region",
            "slides": [
                slide(
                    "Step Functions",
                    two_col(
                        bullets([
                            "Divide X into K+1 contiguous regions via <em>cut points</em> c₁ < c₂ < … < cₖ.",
                            "Create indicator (dummy) variables: C₁(X)=I(X<c₁), C₂(X)=I(c₁≤X<c₂), …",
                            "Fit a <strong>constant within each region</strong> — effectively a histogram regression.",
                            "Easy to implement: <code>pd.cut()</code> → <code>get_dummies()</code> → <code>LinearRegression</code>.",
                            "Useful for creating <strong>interpretable interactions</strong>, e.g. I(year<2005)·Age allows a different slope before/after 2005.",
                        ], fragments=False),
                        f'<img src="img/ch7_step_function.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "Step functions are popular in biostatistics and economics where region-based effects are natural. They miss smooth trends within each region.",
                ),
                slide(
                    "From steps to piecewise polynomials",
                    bullets([
                        "Instead of a constant in each region, fit a <strong>separate polynomial</strong>.",
                        "A piecewise cubic with K knots fits a degree-3 polynomial in each of the K+1 intervals — that's 4(K+1) parameters.",
                        "<strong>Problem:</strong> the polynomials need not join smoothly — there can be jumps and kinks at the knots.",
                        "Adding <em>continuity constraints</em> reduces the parameter count but keeps the fit smooth.",
                        "<em>Splines</em> have the <strong>maximum</strong> continuity: the function and its first d−1 derivatives are continuous at every knot.",
                    ]),
                    "4 panels: piecewise cubic → continuous → cubic spline → linear spline. Each step adds a smoothness constraint.",
                ),
                slide(
                    "Four levels of smoothness",
                    f'<img src="img/ch7_piecewise_comparison.svg" style="width:100%;border-radius:8px;">',
                    "Top-left: piecewise cubic — jumps at the knot. Top-right: continuous but kink visible. Bottom-left: cubic spline — smooth. Bottom-right: linear spline — V-shape at knot.",
                ),
                example_slide(
                    "Step function — live",
                    "Fit a piecewise-constant step function on simulated wage~age data using pd.cut() and LinearRegression.",
                    _CODE_STEP_SPLINE,
                    packages="numpy,pandas,matplotlib,sklearn",
                ),
            ],
        },
        # ------------------------------------------------------------------ #
        # Part 3 — Splines                                                    #
        # ------------------------------------------------------------------ #
        {
            "kicker": "Part 3 · 0:35 – 1:00",
            "title": "Splines",
            "subtitle": "Linear, cubic, and natural cubic splines; basis functions and degrees of freedom",
            "slides": [
                slide(
                    "Linear Splines — basis functions",
                    two_col(
                        bullets([
                            "A <strong>linear spline</strong> with knots ξ₁,…,ξₖ is a piecewise linear function that is <em>continuous</em> at each knot.",
                            "Represented as: y = β₀ + β₁x + β₂(x−ξ₁)₊ + … + βₖ₊₁(x−ξₖ)₊",
                            "<strong>Truncated positive part</strong>: (x−ξ)₊ = max(x−ξ, 0)",
                            "Each basis function is 0 to the left of its knot, then grows linearly — it 'turns on' at ξ.",
                            "K knots → K+2 parameters (intercept + slope + K kink terms).",
                        ], fragments=False),
                        f'<img src="img/ch7_linear_spline_basis.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "The truncated power basis is elegant: adding one term per knot is all it takes to create a new kink while keeping continuity.",
                ),
                slide(
                    "Cubic Splines — the workhorse",
                    two_col(
                        bullets([
                            "A <strong>cubic spline</strong> with K knots has continuous first and second derivatives at every knot — the curve looks <em>visually smooth</em>.",
                            "Truncated cubic basis: b₁=x, b₂=x², b₃=x³, bₖ₊₃=(x−ξₖ)³₊",
                            "K knots → <strong>K+4 parameters</strong> (3 polynomial terms + K truncated cubics + intercept).",
                            "Fitted with ordinary least squares — no special algorithm needed.",
                            "In R: <code>bs(x, knots=c(25,40,60))</code>; in Python: build the truncated basis manually or use <code>patsy.cr()</code>.",
                        ], fragments=False),
                        f'<img src="img/ch7_cubic_spline_basis.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "Cubic splines are the sweet spot: smooth enough to look natural, yet not too wiggly. Higher degrees rarely help.",
                ),
                slide(
                    "Natural Cubic Splines",
                    two_col(
                        bullets([
                            "Cubic splines can behave badly in the <em>tails</em> (beyond the boundary knots) — high variance, wild extrapolation.",
                            "A <strong>natural cubic spline</strong> adds the constraint that f(x) is <em>linear</em> beyond the boundary knots.",
                            "This adds 4 constraints (2 per boundary) → reduces df by 4 vs a regular cubic spline.",
                            "With the same df, we can place <strong>more internal knots</strong> → better fit in the interior.",
                            "In Python: <code>scipy.interpolate.UnivariateSpline</code> with boundary conditions.",
                        ], fragments=False),
                        f'<img src="img/ch7_natural_spline_compare.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "The natural spline (red) stays sensible near the boundaries. The cubic spline (blue) has wider CI bands at the edges.",
                ),
                slide(
                    "Knot placement and degrees of freedom",
                    two_col(
                        bullets([
                            "Strategy: pick K (number of knots), then place them at uniform <strong>quantiles</strong> of X — this puts more knots where the data is dense.",
                            "Cubic spline: <strong>K+4 df</strong>; Natural spline: <strong>K df</strong>.",
                            "More df = more flexibility = more variance. Choose K by cross-validation.",
                            "At the same df, natural splines almost always beat polynomials in the tails.",
                        ], fragments=False),
                        f'<img src="img/ch7_knot_df_compare.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "Degree-14 polynomial (15 df) goes haywire near the edges. Natural cubic spline (15 df) stays sensible throughout.",
                ),
                example_slide(
                    "Cubic & smoothing splines — live",
                    "Build a truncated power basis cubic spline and compare to scipy's UnivariateSpline on the same data.",
                    _CODE_CUBIC_SPLINE,
                    packages="numpy,matplotlib,sklearn,scipy",
                ),
            ],
        },
        # ------------------------------------------------------------------ #
        # Part 4 — Smoothing Splines                                          #
        # ------------------------------------------------------------------ #
        {
            "kicker": "Part 4 · 1:00 – 1:20",
            "title": "Smoothing Splines",
            "subtitle": "Roughness-penalised fitting — no knot placement needed",
            "slides": [
                slide(
                    "The smoothing spline criterion",
                    bullets([
                        "Minimise over all smooth functions g: <strong>Σ(yᵢ − g(xᵢ))² + λ ∫ g″(t)² dt</strong>",
                        "First term = RSS — fits the data.",
                        "Second term = <em>roughness penalty</em> — penalises curvature (g″ large ≡ wiggly).",
                        "λ ≥ 0 controls the trade-off: <strong>λ=0</strong> → interpolating spline (zero training RSS), <strong>λ→∞</strong> → linear fit.",
                        "The solution is always a <em>natural cubic spline</em> with a knot at every unique xᵢ — but λ controls effective smoothness.",
                    ]),
                    "The roughness penalty λ∫g''² is the second derivative integrated over the whole domain — large g'' means rapid change in slope, i.e. wiggliness.",
                ),
                slide(
                    "Effective degrees of freedom",
                    two_col(
                        bullets([
                            "Fitted values: ĝ<sub>λ</sub> = <strong>S<sub>λ</sub> y</strong>, where S<sub>λ</sub> is an n×n smoother matrix.",
                            "Effective df: df<sub>λ</sub> = Σᵢ {S<sub>λ</sub>}ᵢᵢ — the trace of the smoother matrix.",
                            "Convenient to specify <strong>df instead of λ</strong> — the algorithm finds the λ that gives the target df.",
                            "LOOCV: RSS<sub>CV</sub>(λ) = Σ [(yᵢ − ĝ<sub>λ</sub>(xᵢ)) / (1 − {S<sub>λ</sub>}ᵢᵢ)]² — computed from a single fit!",
                        ], fragments=False),
                        f'<img src="img/ch7_smoothing_spline.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "The LOOCV formula for smoothing splines is free — unlike k-fold CV which requires k refits, LOOCV here is just a diagonal division.",
                ),
                slide(
                    "Smoothing splines in Python",
                    bullets([
                        "<code>scipy.interpolate.UnivariateSpline(x, y, k=3, s=smoothing_factor)</code>",
                        "The <code>s</code> parameter controls smoothing: s=0 → interpolating, s large → very smooth.",
                        "Set s ≈ n × σ² as a rule of thumb; use CV to tune.",
                        "<code>spl.get_residual()</code> returns RSS; effective df via <code>spl.get_knots()</code> count.",
                        "No need to choose knot locations — the algorithm places them automatically at the data points.",
                    ]),
                    "In R: smooth.spline(x, y, df=10) specifies df directly; smooth.spline(x, y) uses LOOCV automatically.",
                ),
                example_slide(
                    "Smoothing spline — live",
                    "Fit smoothing splines with different s values (λ proxy). See how the smoothing parameter controls wiggliness.",
                    _CODE_SMOOTHING_SPLINE,
                    packages="numpy,matplotlib,scipy",
                ),
            ],
        },
        # ------------------------------------------------------------------ #
        # Part 5 — Local Regression                                           #
        # ------------------------------------------------------------------ #
        {
            "kicker": "Part 5 · 1:20 – 1:40",
            "title": "Local Regression",
            "subtitle": "Fit a local model at each query point using nearby observations",
            "slides": [
                slide(
                    "The local regression idea",
                    two_col(
                        bullets([
                            "At each query point x₀, fit a <strong>weighted linear regression</strong> using only nearby observations.",
                            "<strong>Algorithm:</strong> (1) find s·n nearest neighbours of x₀; (2) assign weights Kλ(x₀, xᵢ) — highest at x₀, zero beyond the window; (3) fit weighted OLS; (4) use ŷ = β̂₀ + β̂₁x₀.",
                            "The <strong>span s</strong> controls smoothness: small s → wiggly, large s → smooth (like a global fit).",
                            "In Python: <code>statsmodels.nonparametric.smoothers_lowess.lowess(y, x, frac=0.5)</code>.",
                            "In R: <code>loess(wage ~ age, span=0.5)</code>.",
                        ], fragments=False),
                        f'<img src="img/ch7_local_regression.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "Local regression is sometimes called LOESS (locally estimated scatterplot smoothing) or LOWESS (locally weighted scatterplot smoothing).",
                ),
                slide(
                    "Weight functions and span choice",
                    bullets([
                        "<strong>Epanechnikov kernel</strong>: K(u) = 0.75(1−u²) for |u|≤1 — optimal in MSE sense.",
                        "<strong>Tricube kernel</strong>: w = (1 − |d/dₘₐₓ|³)³ — the most common default in loess.",
                        "Can fit higher-degree local polynomials (not just linear) inside each window.",
                        "Span = proportion of data used per fit: span 0.2 = 20% of points per window.",
                        "Choose span by <strong>cross-validation</strong>; LOOCV is cheap for fixed span.",
                        "<strong>Caveat:</strong> boundary effects — fewer points available at the edges of X.",
                    ]),
                    "Span is analogous to k in KNN regression: small span = high variance, large span = high bias.",
                ),
                example_slide(
                    "LOESS — live",
                    "Fit local regression with three different span values using statsmodels.lowess. Compare smoothness.",
                    _CODE_LOESS,
                    packages="numpy,matplotlib,statsmodels",
                ),
            ],
        },
        # ------------------------------------------------------------------ #
        # Part 6 — Generalized Additive Models                               #
        # ------------------------------------------------------------------ #
        {
            "kicker": "Part 6 · 1:40 – 2:00",
            "title": "Generalized Additive Models",
            "subtitle": "Flexible nonlinear models that stay interpretable — one component per predictor",
            "slides": [
                slide(
                    "The GAM idea",
                    bullets([
                        "Replace each linear term β<sub>j</sub>x<sub>ij</sub> with a <em>smooth function</em> f<sub>j</sub>(x<sub>ij</sub>):",
                        "y<sub>i</sub> = β₀ + f₁(x<sub>i1</sub>) + f₂(x<sub>i2</sub>) + … + f<sub>p</sub>(x<sub>ip</sub>) + ε<sub>i</sub>",
                        "Each f<sub>j</sub> can be a <strong>spline, polynomial, step function, or LOESS fit</strong> — independently chosen.",
                        "<strong>Additive structure</strong> is the key: effects are summed, so each component is interpretable in isolation.",
                        "Fit by <em>backfitting</em>: iteratively update each f<sub>j</sub> while keeping the others fixed, until convergence.",
                    ]),
                    "GAMs are a sweet spot between linear models (interpretable, low variance) and fully nonparametric models (flexible, high variance).",
                ),
                slide(
                    "GAM components — wage example",
                    f'<img src="img/ch7_gam_components.svg" style="width:100%;border-radius:8px;">',
                    "Three component plots: f1(year) is nearly linear (small effect). f2(age) is a smooth hump peaking around 45. f3(education) shows a strong positive step for advanced degrees.",
                ),
                slide(
                    "GAMs for classification",
                    two_col(
                        bullets([
                            "GAMs extend naturally to <strong>logistic regression</strong>:",
                            "log[p(X) / (1−p(X))] = β₀ + f₁(X₁) + f₂(X₂) + … + f<sub>p</sub>(X<sub>p</sub>)",
                            "Each component is now a contribution to the <em>log-odds</em>.",
                            "In Python: build spline features, then pass to <code>LogisticRegression</code> — same trick as before.",
                        ], fragments=False),
                        f'<img src="img/ch7_gam_classification.svg" style="width:100%;border-radius:8px;">',
                    ),
                    "The GAM for classification shows that education has by far the strongest effect on being a high earner — much more than year or age.",
                ),
                slide(
                    "Pros, cons, and extensions",
                    two_col(
                        f"""<strong style="color:var(--bc-success)">Advantages</strong>
{bullets([
    "Automatically models nonlinear effects — no manual feature engineering.",
    "Each f<sub>j</sub> is interpretable via a component plot.",
    "Can mix: some terms linear, some spline, some factor.",
    "Use <code>anova()</code> to test linearity of each term.",
], fragments=False)}""",
                        f"""<strong style="color:var(--bc-danger)">Limitations</strong>
{bullets([
    "Additive assumption can miss <em>interaction effects</em>.",
    "Can add low-order interactions: <code>ns(age,df=5):ns(year,df=5)</code>.",
    "Backfitting may be slow for large n and many predictors.",
    "In Python: <code>pygam</code> library provides a full GAM implementation with automatic smoothing.",
], fragments=False)}""",
                    ),
                    "GAMs are popular in environmental science, health research, and economics where smooth nonlinear effects are expected.",
                ),
                example_slide(
                    "GAM — live",
                    "Build an additive model for wage using spline on age, linear year, and dummy education. Print R² and plot the age component.",
                    _CODE_GAM,
                    packages="numpy,pandas,matplotlib,sklearn,scipy",
                ),
            ],
        },
    ],
    "recap_items": [
        "<strong>Polynomial regression</strong>: replace X with X, X², …, Xᵈ — standard OLS, but watch the tails.",
        "<strong>Step functions</strong>: cut X into regions, create dummies — piecewise constant, easy interaction terms.",
        "<strong>Splines</strong>: piecewise polynomials with continuity constraints — cubic splines (K+4 df) are the workhorse; natural cubic splines add linear tails (K df).",
        "<strong>Smoothing splines</strong>: penalise curvature with λ∫g″²; effective df replaces knot selection; LOOCV chooses λ for free.",
        "<strong>Local regression</strong>: fit a weighted local polynomial at each query point — span controls bias-variance trade-off.",
        "<strong>GAMs</strong>: y = β₀ + f₁(X₁) + … + fₚ(Xₚ); each component is interpretable; extends to logistic GAMs.",
    ],
    "recap_callout": (
        "All six methods fit into the <strong>linear model framework</strong> — you transform the predictors, then run OLS or logistic regression as usual. "
        "Splines and GAMs are the most used in practice: they balance flexibility, interpretability, and statistical efficiency."
    ),
}

# ============================================================================
# DRIVER
# ============================================================================

DECKS = [
    # Week 3
    (WEEK3 / "course-01-what-is-statistical-learning" / "slides" / "index.html", W3_SL),
    (WEEK3 / "course-02-linear-regression" / "slides" / "index.html", W3_LR),
    (WEEK3 / "course-03-resampling-methods" / "slides" / "index.html", W3_CV),
    (WEEK3 / "course-04-model-selection-regularization" / "slides" / "index.html", W3_MS),
    (WEEK3 / "course-05-moving-beyond-linearity" / "slides" / "index.html", W3_BL),
    # Week 4
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
