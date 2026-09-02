#!/usr/bin/env python3

"""Deterministic Markdown & Semantic Presentation Renderer for Research Reports.

Converts canonical Markdown research blocks into standalone, beautifully-styled,
zero-token HTML documents with Institutional aesthetic and full semantic styling.
"""

import html
import re
import warnings
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from markdown_it import MarkdownIt

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


DIRECTION_MAP = {
    "↑": "上升",
    "↓": "下降",
    "→": "持平",
    "↗": "改善",
    "↘": "惡化",
}

RISK_LIGHT_CLASSES = {
    "green": ("risk-green", "🟢", "Green"),
    "yellow": ("risk-yellow", "🟡", "Yellow"),
    "orange": ("risk-orange", "🟠", "Orange"),
    "red": ("risk-red", "🔴", "Red"),
}


def _create_markdown_parser() -> MarkdownIt:
    """Create a secured CommonMark parser with table support and raw HTML disabled."""
    md = MarkdownIt("commonmark", {"html": False})
    md.enable("table")
    return md


MD_PARSER = _create_markdown_parser()


def _format_datetime(iso_str: Optional[str]) -> str:
    if not iso_str:
        return "N/A"
    s = str(iso_str).replace("T", " ")
    if len(s) > 19:
        s = s[:19]
    return s


def _render_hero_header(metadata: Dict[str, Any]) -> str:
    title = html.escape(str(metadata.get("title", "Global Macro Report")))
    report_type = html.escape(str(metadata.get("report_type", "")))
    run_id = html.escape(str(metadata.get("run_id", "")))
    risk_light = str(metadata.get("risk_light", "")).upper()
    topic = metadata.get("topic")

    risk_class = "risk-yellow"
    risk_icon = "🟡"
    risk_label = "YELLOW"
    if "GREEN" in risk_light:
        risk_class, risk_icon, risk_label = "risk-green", "🟢", "GREEN"
    elif "ORANGE" in risk_light:
        risk_class, risk_icon, risk_label = "risk-orange", "🟠", "ORANGE"
    elif "RED" in risk_light:
        risk_class, risk_icon, risk_label = "risk-red", "🔴", "RED"
    elif "YELLOW" in risk_light:
        risk_class, risk_icon, risk_label = "risk-yellow", "🟡", "YELLOW"

    topic_badge = f'<span class="badge badge-topic">{html.escape(str(topic))}</span>' if topic else ""

    return f"""
<header class="hero-header">
  <div class="hero-top">
    <div class="hero-type-row">
      <span class="badge badge-type">{report_type}</span>
      <span class="badge {risk_class}">{risk_icon} Risk: {risk_label}</span>
      {topic_badge}
    </div>
    <div class="hero-run-id">RUN_ID: <code>{run_id}</code></div>
  </div>
  <h1 class="hero-title">{title}</h1>
</header>
"""


def clean_markdown_body(text: str) -> str:
    """Clean markdown body by stripping any canonical markers, front matter, and footer markers."""
    if not text:
        return ""

    # 1. Remove <<<REPORT_BEGIN>>> and <<<REPORT_END>>> markers
    text = re.sub(r"^\s*<<<REPORT_BEGIN>>>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*<<<REPORT_END>>>\s*", "", text, flags=re.MULTILINE)

    # 2. Remove front matter block if present
    text = re.sub(r"^\s*---\s*\n.*?\n---\s*\n", "", text, flags=re.DOTALL)

    # 3. Remove trailing current doc markers like __GLOBAL_DAILY_BRIEF_CURRENT__
    text = re.sub(r"__\w+__\s*$", "", text.strip())

    # 4. Remove any remaining raw frontmatter lines at the top of the body
    lines = text.splitlines()
    filtered_lines = []
    in_raw_header = True
    header_keys = (
        "research_status:",
        "generated_at_taipei:",
        "coverage_start_taipei:",
        "coverage_end_taipei:",
        "us_market_status:",
        "run_id:",
        "report_type:",
        "report_name:",
        "format_version:",
        "risk_light:",
        "slug:",
        "trigger_status:",
        "classification:",
        "title:",
    )
    for line in lines:
        stripped = line.strip()
        if in_raw_header:
            if any(stripped.startswith(k) for k in header_keys) or stripped == "---" or stripped.startswith("<<<"):
                continue
            if stripped == "":
                continue
            in_raw_header = False
        filtered_lines.append(line)

    return "\n".join(filtered_lines).strip()


def _postprocess_soup(soup: BeautifulSoup) -> None:
    """Apply deterministic semantic post-processing to HTML elements."""

    # 0. Strip any elements containing canonical markers or raw frontmatter
    for tag in list(soup.find_all(["h1", "h2", "h3", "h4", "p", "pre", "div"])):
        t = tag.get_text()
        if "<<<REPORT_BEGIN>>>" in t or "<<<REPORT_END>>>" in t:
            tag.decompose()
        elif "research_status:" in t and "format_version:" in t:
            tag.decompose()

    # 1. Remove redundant top-level H1 from markdown body (the canonical title is rendered in hero-header)
    first_h1 = soup.find("h1")
    if first_h1:
        first_h1.decompose()

    # 2. Tables: wrap in <div class="table-scroll">
    for table in soup.find_all("table"):
        # Ensure proper wrapper if not already wrapped
        if table.parent and table.parent.name == "div" and "table-scroll" in table.parent.get("class", []):
            continue
        wrapper = soup.new_tag("div", attrs={"class": "table-scroll"})
        table.wrap(wrapper)

    # 3. Links: sanitize and enforce target="_blank" rel="noopener noreferrer"
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if not href.startswith("http://") and not href.startswith("https://") and not href.startswith("#"):
            a["href"] = "#"
        elif href.startswith("http://") or href.startswith("https://"):
            a["target"] = "_blank"
            a["rel"] = "noopener noreferrer"

    # 3. Text replacements for Directions, Risk lights, Evidence Grades, and State transitions in table cells and paragraphs
    text_targets = soup.find_all(["td", "th", "p", "li"])

    # Regex patterns
    # Direction arrows: ↑, ↓, →, ↗, ↘
    # Risk icons: 🟢, 🟡, 🟠, 🔴
    # Transitions: e.g. "Yellow → Orange", "Neutral → Positive"
    
    for element in text_targets:
        if element.find(["table", "div", "pre"]):
            continue
        
        # Process child string nodes carefully to preserve terminology verbatim
        _process_element_contents(soup, element)


def _process_element_contents(soup: BeautifulSoup, element: Any) -> None:
    """Process child text nodes of an element for semantic badges and directions."""
    is_table_cell = element.name in ("td", "th")
    for text_node in list(element.find_all(string=True)):
        if text_node.parent and text_node.parent.name in ("code", "pre", "script", "style"):
            continue
        text = str(text_node)
        if not text.strip():
            continue

        # Check if any semantic replacement is needed
        replaced_html = _enrich_text_html(text, is_table_cell=is_table_cell)
        if replaced_html != text:
            parsed_frag = BeautifulSoup(replaced_html, "html.parser")
            text_node.replace_with(*parsed_frag.contents)


def _enrich_text_html(text: str, is_table_cell: bool = False) -> str:
    """Enrich text with semantic HTML spans while strictly preserving original text terms."""
    # Escape HTML characters first
    escaped = html.escape(text)

    placeholders = {}
    p_counter = 0

    def _token(html_snippet: str) -> str:
        nonlocal p_counter
        p_counter += 1
        key = f"___SEMANTIC_TOKEN_{p_counter}___"
        placeholders[key] = html_snippet
        return key

    # 1. State transitions with Risk Light names: e.g. "ORANGE → ORANGE", "Yellow → Orange"
    def _replace_risk_transition(m):
        p, c = m.group(1), m.group(2)
        p_u, c_u = p.upper(), c.upper()
        p_class = f"risk-{p.lower()}"
        c_class = f"risk-{c.lower()}"
        p_icon = "🟢" if p_u == "GREEN" else "🟡" if p_u == "YELLOW" else "🟠" if p_u == "ORANGE" else "🔴"
        c_icon = "🟢" if c_u == "GREEN" else "🟡" if c_u == "YELLOW" else "🟠" if c_u == "ORANGE" else "🔴"
        snippet = f'<span class="state-transition"><span class="risk {p_class}">{p_icon} {p}</span> <span class="transition-arrow">→</span> <span class="risk {c_class}">{c_icon} {c}</span></span>'
        return _token(snippet)

    escaped = re.sub(
        r"\b(GREEN|YELLOW|ORANGE|RED|Green|Yellow|Orange|Red)\s*→\s*(GREEN|YELLOW|ORANGE|RED|Green|Yellow|Orange|Red)\b",
        _replace_risk_transition,
        escaped,
    )

    # 2. General State transitions: e.g. "4.18% → 4.31%", "Neutral → Positive", "60% → 72%", "$88.5 → $91.2"
    def _replace_general_transition(m):
        prior, current = m.group(1), m.group(2)
        snippet = f'<span class="state-transition"><span class="state-prior">{prior}</span><span class="transition-arrow">→</span><span class="state-current">{current}</span></span>'
        return _token(snippet)

    escaped = re.sub(
        r"(?<!\S)([\$\+A-Za-z0-9.%🟢🟡🟠🔴-]+(?:\s+[\$\+A-Za-z0-9.%🟢🟡🟠🔴-]+)?)\s*→\s*([\$\+A-Za-z0-9.%🟢🟡🟠🔴-]+(?:\s+[\$\+A-Za-z0-9.%🟢🟡🟠🔴-]+)?)(?!\S)",
        _replace_general_transition,
        escaped,
    )

    # 3. Direction arrows
    escaped = re.sub(
        r"↑(?:\s*(?:上升|增加))?",
        lambda _: _token('<span class="direction direction-up">↑ 上升</span>'),
        escaped,
    )
    escaped = re.sub(
        r"↓(?:\s*(?:下降|減少))?",
        lambda _: _token('<span class="direction direction-down">↓ 下降</span>'),
        escaped,
    )
    escaped = re.sub(
        r"↗(?:\s*(?:改善|加速))?",
        lambda _: _token('<span class="direction direction-improving">↗ 改善</span>'),
        escaped,
    )
    escaped = re.sub(
        r"↘(?:\s*(?:惡化|減速))?",
        lambda _: _token('<span class="direction direction-worsening">↘ 惡化</span>'),
        escaped,
    )
    escaped = re.sub(
        r"(?<!\w)→(?!\w)(?:\s*(?:持平|無明顯變化))?",
        lambda _: _token('<span class="direction direction-flat">→ 持平</span>'),
        escaped,
    )

    # 4. Risk Lights (Emoji)
    if is_table_cell:
        escaped = re.sub(r"🟢(?:\s*Green)?", lambda _: _token('<span class="risk risk-green">🟢</span>'), escaped)
        escaped = re.sub(r"🟡(?:\s*Yellow)?", lambda _: _token('<span class="risk risk-yellow">🟡</span>'), escaped)
        escaped = re.sub(r"🟠(?:\s*Orange)?", lambda _: _token('<span class="risk risk-orange">🟠</span>'), escaped)
        escaped = re.sub(r"🔴(?:\s*Red)?", lambda _: _token('<span class="risk risk-red">🔴</span>'), escaped)
    else:
        escaped = re.sub(r"🟢(?:\s*Green)?", lambda _: _token('<span class="risk risk-green">🟢 Green</span>'), escaped)
        escaped = re.sub(r"🟡(?:\s*Yellow)?", lambda _: _token('<span class="risk risk-yellow">🟡 Yellow</span>'), escaped)
        escaped = re.sub(r"🟠(?:\s*Orange)?", lambda _: _token('<span class="risk risk-orange">🟠 Orange</span>'), escaped)
        escaped = re.sub(r"🔴(?:\s*Red)?", lambda _: _token('<span class="risk risk-red">🔴 Red</span>'), escaped)

    # 5. Risk Lights following "Risk Light:" or "Risk:"
    def _replace_named_risk_light(m):
        prefix = m.group(1)
        val = m.group(2)
        val_upper = val.upper()
        icon = "🟢" if val_upper == "GREEN" else "🟡" if val_upper == "YELLOW" else "🟠" if val_upper == "ORANGE" else "🔴"
        cls = f"risk-{val.lower()}"
        return prefix + _token(f'<span class="risk {cls}">{icon} {val}</span>')

    escaped = re.sub(
        r"((?:Risk\s*Light|Risk|燈號)[：:]\s*)(GREEN|YELLOW|ORANGE|RED|Green|Yellow|Orange|Red)\b",
        _replace_named_risk_light,
        escaped,
    )

    # 6. Standalone uppercase risk light words in table cells (e.g. "ORANGE", "YELLOW", "RED", "GREEN") -> icon only
    if is_table_cell:
        def _replace_cell_risk_word(m):
            w = m.group(1)
            icon = "🟢" if w == "GREEN" else "🟡" if w == "YELLOW" else "🟠" if w == "ORANGE" else "🔴"
            cls = f"risk-{w.lower()}"
            return _token(f'<span class="risk {cls}">{icon}</span>')

        escaped = re.sub(r"^\s*(GREEN|YELLOW|ORANGE|RED)\s*$", _replace_cell_risk_word, escaped)

    # 7. Evidence Grades
    escaped = re.sub(r"\bGrade\s+([A-D])\b", lambda m: _token(f'<span class="badge badge-grade-{m.group(1)}">Grade {m.group(1)}</span>'), escaped)

    # Expand all tokens
    for k, v in placeholders.items():
        escaped = escaped.replace(k, v)

    return escaped


def get_embedded_css() -> str:
    """Return self-contained institutional CSS stylesheet."""
    return """
:root {
  --bg-primary: #0f172a;
  --bg-surface: #1e293b;
  --bg-surface-raised: #334155;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --border: #334155;
  --border-light: #475569;
  --accent: #38bdf8;
  --accent-glow: rgba(56, 189, 248, 0.15);
  --success: #10b981;
  --warning: #f59e0b;
  --orange: #f97316;
  --danger: #ef4444;
  --table-zebra: rgba(255, 255, 255, 0.02);
  --table-hover: rgba(56, 189, 248, 0.06);
}

@media (prefers-color-scheme: light) {
  :root {
    --bg-primary: #f8fafc;
    --bg-surface: #ffffff;
    --bg-surface-raised: #f1f5f9;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --border: #e2e8f0;
    --border-light: #cbd5e1;
    --accent: #0284c7;
    --accent-glow: rgba(2, 132, 199, 0.08);
    --table-zebra: #f8fafc;
    --table-hover: rgba(2, 132, 199, 0.05);
  }
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.68;
  font-size: 15px;
  font-feature-settings: "tnum" 1, "cv02" 1, "cv03" 1, "cv04" 1;
  -webkit-font-smoothing: antialiased;
  padding: 24px 16px;
}

.report-container {
  max-width: 1240px;
  margin: 0 auto;
}

/* Hero Header */
.hero-header {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 28px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.hero-type-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hero-run-id {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.hero-run-id code {
  background: var(--bg-surface-raised);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--accent);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.hero-title {
  font-size: 1.85rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  line-height: 1.28;
}

/* Typography & Headings */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary);
  font-weight: 600;
  line-height: 1.35;
}

h2 {
  font-size: 1.35rem;
  margin: 36px 0 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--accent);
  display: flex;
  align-items: center;
  gap: 8px;
}

h3 {
  font-size: 1.15rem;
  margin: 24px 0 12px;
  color: var(--text-primary);
}

p {
  margin-bottom: 14px;
  color: var(--text-primary);
}

ul, ol {
  margin: 12px 0 16px 24px;
  color: var(--text-primary);
}

li {
  margin-bottom: 6px;
}

/* Blockquotes / Callout boxes */
blockquote {
  background: var(--accent-glow);
  border-left: 4px solid var(--accent);
  border-radius: 0 8px 8px 0;
  padding: 14px 18px;
  margin: 18px 0;
  color: var(--text-primary);
  font-size: 0.98rem;
}

blockquote p:last-child {
  margin-bottom: 0;
}

/* Tables */
.table-scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin: 20px 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-surface);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
  text-align: left;
}

th, td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

th {
  background: var(--bg-surface-raised);
  color: var(--text-primary);
  font-weight: 600;
  position: sticky;
  top: 0;
  white-space: nowrap;
  letter-spacing: 0.02em;
}

tr:nth-child(even) td {
  background: var(--table-zebra);
}

tr:hover td {
  background: var(--table-hover);
}

/* Badges */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  line-height: 1;
}

.badge-type {
  background: rgba(56, 189, 248, 0.15);
  color: var(--accent);
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.badge-topic {
  background: var(--bg-surface-raised);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.badge-grade-A { background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-grade-B { background: rgba(56, 189, 248, 0.15); color: var(--accent); border: 1px solid rgba(56, 189, 248, 0.3); }
.badge-grade-C { background: rgba(245, 158, 11, 0.15); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-grade-D { background: rgba(239, 68, 68, 0.15); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.3); }

/* Direction Indicators */
.direction {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-weight: 600;
  font-size: 0.88rem;
}

.direction-up { color: #38bdf8; }
.direction-down { color: #a855f7; }
.direction-improving { color: var(--success); }
.direction-worsening { color: var(--danger); }
.direction-flat { color: var(--text-muted); }

/* Risk Lights */
.risk {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.82rem;
  line-height: 1.2;
}

.risk-green { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.risk-yellow { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.risk-orange { background: rgba(249, 115, 22, 0.15); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); }
.risk-red { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

/* State Transition */
.state-transition {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--bg-surface-raised);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.state-prior { color: var(--text-muted); }
.transition-arrow { color: var(--accent); font-weight: bold; }
.state-current { color: var(--text-primary); font-weight: 600; }

/* Links */
a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px dotted rgba(56, 189, 248, 0.5);
}

a:hover {
  border-bottom-style: solid;
}

/* Code */
code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background: var(--bg-surface-raised);
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 0.88em;
}

pre {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  overflow-x: auto;
  margin: 16px 0;
}

pre code {
  background: transparent;
  padding: 0;
}

/* Footer */
footer {
  margin-top: 48px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-muted);
}
"""


def render_markdown_to_html(markdown_body: str, metadata: Dict[str, Any]) -> str:
    """
    Render canonical markdown body and front matter metadata into complete standalone HTML.
    """
    metadata = dict(metadata)
    h1_match = re.search(r"^\s*#\s+(.+)$", markdown_body, flags=re.MULTILINE)
    if h1_match:
        h1_text = h1_match.group(1).strip()
        if "｜" in h1_text or "|" in h1_text or len(h1_text) > len(str(metadata.get("title", ""))):
            metadata["title"] = h1_text

    cleaned_body = clean_markdown_body(markdown_body)
    raw_html = MD_PARSER.render(cleaned_body)
    soup = BeautifulSoup(raw_html, "html.parser")
    _postprocess_soup(soup)
    content_html = str(soup)

    hero_html = _render_hero_header(metadata)
    css = get_embedded_css()
    title = html.escape(str(metadata.get("title", "Global Macro Signal Report")))
    date_str = _format_datetime(metadata.get("generated_at_taipei"))

    document_html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {date_str}</title>
<style>
{css}
</style>
</head>
<body>
<div class="report-container">
{hero_html}
<main class="report-content">
{content_html}
</main>
<footer>
  Global Macro Signal Report · {date_str} · Generated Deterministically
</footer>
</div>
</body>
</html>
"""
    return document_html
