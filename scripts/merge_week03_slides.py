"""Merge Week 3 interactive Reveal.js decks (rich HTML from git).

`build_slides.py` emits minimal outline decks. The student-facing Week 3 slides
are the full Pyodide interactive HTML that lived in the pre-merge course folders.
This script restores and merges them into the four post-merge course paths.

Usage:
    python3 scripts/merge_week03_slides.py

Requires git history containing the old six course slide paths (HEAD).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEK3 = ROOT / "weeks" / "week-03-machine-learning"

# Old git paths -> new output paths
RESTORE = {
    "weeks/week-03-machine-learning/course-03-feature-engineering/slides/index.html": (
        WEEK3 / "course-02-feature-engineering" / "slides" / "index.html",
        {"Week 3 · Course 3 · 1.5 hours": "Week 3 · Course 2 · 1.5 hours",
         "Course 6": "Course 4"},
    ),
    "weeks/week-03-machine-learning/course-04-cross-validation/slides/index.html": (
        WEEK3 / "course-03-cross-validation" / "slides" / "index.html",
        {"Week 3 · Course 4 · 1.5 hours": "Week 3 · Course 3 · 1.5 hours"},
    ),
}

MERGE_PAIRS = [
    (
        "weeks/week-03-machine-learning/course-01-linear-regression-i/slides/index.html",
        "weeks/week-03-machine-learning/course-02-linear-regression-ii/slides/index.html",
        WEEK3 / "course-01-linear-regression" / "slides" / "index.html",
        {
            "title": "Linear Regression",
            "kicker": "Week 3 · Course 1 · 3 hours",
            "subtitle": (
                "Part 1: simple LR on Boston · "
                "Part 2: multiple LR, diagnostics, categoricals"
            ),
            "callout": (
                "Every concept that appears later — loss, coefficients, R², residuals — "
                "shows up here in its cleanest form. Master simple LR and the rest of the "
                "course just adds knobs."
            ),
            "recap_callout": (
                "Next: feature engineering — scaling, polynomials, pipelines."
            ),
        },
    ),
    (
        "weeks/week-03-machine-learning/course-05-feature-selection-subset/slides/index.html",
        "weeks/week-03-machine-learning/course-06-feature-selection-shrinkage/slides/index.html",
        WEEK3 / "course-04-feature-selection" / "slides" / "index.html",
        {
            "title": "Feature Selection",
            "kicker": "Week 3 · Course 4 · 3 hours",
            "subtitle": (
                "Part 1: subset & stepwise · Part 2: Ridge, Lasso, Elastic Net"
            ),
            "callout": (
                "Too many predictors hurt prediction. Subset selection is the classical "
                "answer; shrinkage (Part 2) is the modern one."
            ),
            "recap_callout": "End of Week 3. Next week: from regression to classification.",
        },
    ),
]

PART_RETIME = [
    ("Part 1 · 0:00 – 0:30", "Part 4 · 1:30 – 2:00"),
    ("Part 2 · 0:30 – 1:00", "Part 5 · 2:00 – 2:30"),
    ("Part 3 · 1:00 – 1:30", "Part 6 · 2:30 – 3:00"),
    ("Part 1 · 0:00 - 0:30", "Part 4 · 1:30 - 2:00"),
    ("Part 2 · 0:30 - 1:00", "Part 5 · 2:00 - 2:30"),
    ("Part 3 · 1:00 - 1:30", "Part 6 · 2:30 - 3:00"),
]

WEEK3_COURSE_REFS = [
    ("Course 6", "Course 4"),
    ("Course 5", "Part 1"),
    ("in Course 6", "in Course 4"),
]


def git_show(path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def extract_slides_inner(html: str) -> str:
    start = html.index('<div class="slides">') + len('<div class="slides">')
    end = html.rindex("</div></div>")
    return html[start:end].strip()


def skip_title_and_roadmap(inner: str) -> str:
    inner = re.sub(
        r'^<section class="title-slide">.*?</section>\s*',
        "",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    inner = re.sub(
        r'^<section>\s*<span class="kicker">Roadmap</span>.*?</section>\s*',
        "",
        inner,
        count=1,
        flags=re.DOTALL,
    )
    return inner.strip()


def before_recap(inner: str) -> str:
    match = re.search(
        r'<section class="title-slide">\s*<span class="kicker">Recap</span>',
        inner,
    )
    if not match:
        raise ValueError("Recap section not found")
    return inner[: match.start()].strip()


def extract_recap_and_tail(html: str) -> tuple[str, str]:
    """Return (recap+references block, scripts+closing tags from first deck)."""
    inner = extract_slides_inner(html)
    match = re.search(
        r'(<section class="title-slide">\s*<span class="kicker">Recap</span>.*)',
        inner,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError("Recap section not found")
    tail_start = html.rindex("</div></div>")
    scripts = html[tail_start:]
    return match.group(1).strip(), scripts


def extract_recap_items(recap_block: str) -> list[str]:
    items = re.findall(
        r'<li class="fragment fade-up">(.*?)</li>',
        recap_block,
        flags=re.DOTALL,
    )
    return [re.sub(r"\s+", " ", it).strip() for it in items]


def retime_parts(body: str) -> str:
    for old, new in PART_RETIME:
        body = body.replace(old, new)
    return body


def apply_replacements(text: str, mapping: dict[str, str]) -> str:
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text


def build_roadmap(cards: list[tuple[str, str, str]], callout: str) -> str:
    card_html = ""
    for time_slot, name, desc in cards:
        card_html += (
            f'    <div class="card"><h4>{time_slot}</h4><strong>{name}</strong>\n'
            f'      <p class="muted" style="margin:0.3em 0 0;">{desc}</p></div>\n'
        )
    return f"""<section>
  <span class="kicker">Roadmap</span>
  <h2>Where we are heading</h2>
  <div class="three-col">
{card_html}  </div>
  <p class="callout" style="margin-top:1.2em;">{callout}</p>
</section>
"""


def build_title_slide(kicker: str, title: str, subtitle: str) -> str:
    return f"""<section class="title-slide">
  <span class="kicker">{kicker}</span>
  <h1>{title}</h1>
  <p class="muted" style="font-size:1.1em;">{subtitle}</p>
</section>
"""


def build_merged_recap(items: list[str], callout: str) -> str:
    lis = "\n".join(
        f'<li class="fragment fade-up">{item}</li>' for item in items
    )
    return f"""<section class="title-slide">
  <span class="kicker">Recap</span>
  <h2>Things to leave with</h2>
  <ol>
{lis}
  </ol>
  <p class="callout fragment fade-up">{callout}</p>
</section>
"""


def parse_roadmap_cards(html: str) -> list[tuple[str, str, str]]:
    inner = extract_slides_inner(html)
    roadmap_match = re.search(
        r'<span class="kicker">Roadmap</span>.*?<div class="three-col">(.*?)</div>\s*'
        r'<p class="callout"',
        inner,
        flags=re.DOTALL,
    )
    if not roadmap_match:
        raise ValueError("Roadmap not found")
    cards = []
    for card in re.finditer(
        r'<div class="card"><h4>(.*?)</h4><strong>(.*?)</strong>\s*'
        r'<p class="muted"[^>]*>(.*?)</p></div>',
        roadmap_match.group(1),
        flags=re.DOTALL,
    ):
        time_slot = re.sub(r"\s+", " ", card.group(1)).strip()
        name = re.sub(r"\s+", " ", card.group(2)).strip()
        desc = re.sub(r"\s+", " ", card.group(3)).strip()
        cards.append((time_slot, name, desc))
    return cards


def retime_roadmap_cards(cards: list[tuple[str, str, str]], offset_h: float = 1.5) -> list[tuple[str, str, str]]:
    out = []
    for slot, name, desc in cards:
        if " · " in slot:
            start, end = slot.split(" · ", 1)

            def add(t: str) -> str:
                h, m = (int(x) for x in t.split(":"))
                total = h * 60 + m + int(offset_h * 60)
                return f"{total // 60}:{total % 60:02d}"

            slot = f"{add(start.strip())} · {add(end.strip())}"
        out.append((slot, name, desc))
    return out


def head_from_template(html: str, title: str) -> str:
    return re.sub(
        r"<title>.*?</title>",
        f"<title>{title}</title>",
        html.split("<body>")[0],
        count=1,
        flags=re.DOTALL,
    )


def merge_pair(path_a: str, path_b: str, out_path: Path, meta: dict) -> None:
    html_a = git_show(path_a)
    html_b = git_show(path_b)

    cards_a = parse_roadmap_cards(html_a)
    cards_b = retime_roadmap_cards(parse_roadmap_cards(html_b))
    roadmap = build_roadmap(cards_a + cards_b, meta["callout"])

    body_a = before_recap(skip_title_and_roadmap(extract_slides_inner(html_a)))
    body_b = retime_parts(before_recap(skip_title_and_roadmap(extract_slides_inner(html_b))))
    for old, new in WEEK3_COURSE_REFS:
        body_b = body_b.replace(old, new)
    # LR II pointed at old course 3 (FE) for polynomials
    body_b = body_b.replace("Course 3 uses regularization", "Course 4 uses regularization")
    body_b = body_b.replace("Course 3 generalizes this", "Course 2 generalizes this")

    recap_a, tail = extract_recap_and_tail(html_a)
    recap_b, _ = extract_recap_and_tail(html_b)
    recap_items = extract_recap_items(recap_a) + extract_recap_items(recap_b)
    recap = build_merged_recap(recap_items, meta["recap_callout"])

    # Keep references from deck A only
    refs_match = re.search(
        r'(<section class="title-slide">\s*<span class="kicker">References</span>.*?</section>)',
        recap_a,
        flags=re.DOTALL,
    )
    references = refs_match.group(1) if refs_match else ""

    title_slide = build_title_slide(meta["kicker"], meta["title"], meta["subtitle"])
    inner = "\n".join([title_slide, roadmap, body_a, body_b, recap, references])

    doc = (
        head_from_template(html_a, meta["title"])
        + "<body>\n<div class=\"reveal\"><div class=\"slides\">\n"
        + inner
        + "\n"
        + tail
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc)
    n_sections = inner.count("<section")
    print(f"wrote {out_path.relative_to(ROOT)} ({n_sections} section tags)")


def restore_single(git_path: str, out_path: Path, replacements: dict[str, str]) -> None:
    html = git_show(git_path)
    html = apply_replacements(html, replacements)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)
    n_sections = extract_slides_inner(html).count("<section")
    print(f"wrote {out_path.relative_to(ROOT)} ({n_sections} section tags)")


def main() -> None:
    for path_a, path_b, out_path, meta in MERGE_PAIRS:
        merge_pair(path_a, path_b, out_path, meta)
    for git_path, (out_path, replacements) in RESTORE.items():
        restore_single(git_path, out_path, replacements)


if __name__ == "__main__":
    main()
