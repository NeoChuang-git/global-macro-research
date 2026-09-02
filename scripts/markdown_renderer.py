#!/usr/bin/env python3

"""Deterministic Markdown & Semantic Presentation Renderer for Research Reports.

Converts canonical Markdown research blocks into standalone, beautifully-styled,
zero-token HTML documents with Institutional aesthetic and full semantic styling.
"""

import html
import re
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt


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


def _postprocess_soup(soup: BeautifulSoup) -> None:
    """Apply deterministic semantic post-processing to HTML elements."""

    # 1. Tables: wrap in <div class="table-scroll">
    for table in soup.find_all("table"):
        # Ensure proper wrapper if not already wrapped
        if table.parent and table.parent.name == "div" and "table-scroll" in table.parent.get("class", []):
            continue
        wrapper = soup.new_tag("div", attrs={"class": "table-scroll"})
        table.wrap(wrapper)

    # 2. Links: sanitize and enforce target="_blank" rel="noopener noreferrer"
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
    for child in list(element.contents):
        if isinstance(child, str):
            text = str(child)
            if not text.strip():
                continue
            
            # Check if any semantic replacement is needed
            replaced_html = _enrich_text_html(text)
            if replaced_html != text:
                parsed_frag = BeautifulSoup(replaced_html, "html.parser")
                child.replace_with(*parsed_frag.contents)


def _enrich_text_html(text: str) -> str:
    """Enrich text with semantic HTML spans while strictly preserving original text terms."""
    # Escape HTML characters first
    escaped = html.escape(text)

    # State transitions: e.g. "Yellow → Orange", "Neutral → Positive", "60% → 72%"
    transition_pattern = re.compile(
        r"\b([A-Za-z0-9%]+(?:\s+[A-Za-z0-9%]+)?)\s+→\s+([A-Za-z0-9%]+(?:\s+[A-Za-z0-9%]+)?)\b"
    )
    def _replace_transition(m):
        prior, current = m.group(1), m.group(2)
        return f'<span class="state-transition"><span class="state-prior">{prior}</span><span class="transition-arrow">__TRANS_ARROW__</span><span class="state-current">{current}</span></span>'

    escaped = transition_pattern.sub(_replace_transition, escaped)

    # Direction arrows
    escaped = re.sub(
        r"↑(?:\s*(?:上升|增加))?",
        r'<span class="direction direction-up">↑ 上升</span>',
        escaped,
    )
    escaped = re.sub(
        r"↓(?:\s*(?:下降|減少))?",
        r'<span class="direction direction-down">↓ 下降</span>',
        escaped,
    )
    escaped = re.sub(
        r"↗(?:\s*(?:改善|加速))?",
        r'<span class="direction direction-improving">↗ 改善</span>',
        escaped,
    )
    escaped = re.sub(
        r"↘(?:\s*(?:惡化|減速))?",
        r'<span class="direction direction-worsening">↘ 惡化</span>',
        escaped,
    )
    # Standalone → (not part of transition)
    escaped = re.sub(
        r"(?<!\w)→(?!\w)(?:\s*(?:持平|無明顯變化))?",
        r'<span class="direction direction-flat">→ 持平</span>',
        escaped,
    )

    # Restore transition arrow
    escaped = escaped.replace("__TRANS_ARROW__", "→")

    # Risk Lights
    escaped = re.sub(r"🟢(?:\s*Green)?", r'<span class="risk risk-green">🟢 Green</span>', escaped)
    escaped = re.sub(r"🟡(?:\s*Yellow)?", r'<span class="risk risk-yellow">🟡 Yellow</span>', escaped)
    escaped = re.sub(r"🟠(?:\s*Orange)?", r'<span class="risk risk-orange">🟠 Orange</span>', escaped)
    escaped = re.sub(r"🔴(?:\s*Red)?", r'<span class="risk risk-red">🔴 Red</span>', escaped)

    # Evidence Grades (standalone in cells or tokens like "Grade A", "Grade B", etc.)
    escaped = re.sub(r"\bGrade\s+([A-D])\b", r'<span class="badge badge-grade-\1">Grade \1</span>', escaped)

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
    raw_html = MD_PARSER.render(markdown_body)
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
