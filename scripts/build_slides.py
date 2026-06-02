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
    # Week 3
    (WEEK3 / "course-01-what-is-statistical-learning" / "slides" / "index.html", W3_SL),
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
