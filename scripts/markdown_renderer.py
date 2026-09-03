#!/usr/bin/env python3

"""Deterministic Markdown & Semantic Presentation Renderer for Research Reports.

Converts canonical Markdown research blocks into standalone, beautifully-styled,
zero-token HTML documents with Medium-style narrow narrative, wide breakout tables,
and full semantic institutional styling.
"""

import html
from pathlib import Path
import re
import warnings
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, Tag
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
    """Create a CommonMark parser with table support and raw HTML disabled."""
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
    gen_time = _format_datetime(metadata.get("generated_at_taipei"))
    cov_start = _format_datetime(metadata.get("coverage_start_taipei"))
    cov_end = _format_datetime(metadata.get("coverage_end_taipei"))

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
    cov_str = f"{cov_start} ~ {cov_end}" if (cov_start != "N/A" and cov_end != "N/A") else ""
    cov_badge = f'<span class="hero-chip hero-chip-cov">涵蓋：{cov_str}</span>' if cov_str else ""

    return f"""
<header class="hero-header">
  <div class="hero-top">
    <div class="hero-type-row">
      <span class="badge badge-type">{report_type}</span>
      <span class="risk-chip {risk_class}">{risk_icon} Risk: {risk_label}</span>
      {topic_badge}
    </div>
    <div class="hero-run-id">RUN_ID: <code>{run_id}</code></div>
  </div>
  <h1 class="hero-title">{title}</h1>
  <div class="hero-meta-row">
    <span class="hero-chip">發布時間：{gen_time}</span>
    {cov_badge}
  </div>
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


def _enhance_callouts(soup: BeautifulSoup) -> None:
    """Classify blockquotes into semantic callout boxes (Thesis, Risk, Strategy, Catalyst)."""
    thesis_pattern = re.compile(r"(?:一句話結論|核心判斷|核心結論|主要判斷|Thesis|One-line Conclusion)\s*[｜\|:：]", re.IGNORECASE)
    risk_pattern = re.compile(r"(?:風險提醒|核心風險|主要風險|市場風險|Risk|Risk Warning)\s*[｜\|:：]", re.IGNORECASE)
    strategy_pattern = re.compile(r"(?:投資含意|策略含意|交易含意|台灣外溢|資產配置|Investment Implications|Strategy)\s*[｜\|:：]", re.IGNORECASE)
    catalyst_pattern = re.compile(r"(?:下一驗證|下週驗證|下一催化劑|未來催化劑|Next Catalyst|Catalyst)\s*[｜\|:：]", re.IGNORECASE)

    for bq in soup.find_all("blockquote"):
        existing_classes = bq.get("class", [])
        if "callout" not in existing_classes:
            existing_classes.append("callout")

        text = bq.get_text()
        if thesis_pattern.search(text):
            existing_classes.append("callout-thesis")
        elif risk_pattern.search(text):
            existing_classes.append("callout-risk")
        elif strategy_pattern.search(text):
            existing_classes.append("callout-strategy")
        elif catalyst_pattern.search(text):
            existing_classes.append("callout-catalyst")

        bq["class"] = list(dict.fromkeys(existing_classes))


def _enhance_analysis_cards(soup: BeautifulSoup) -> None:
    """Package H3 sections matching #<number>｜, Signal #<number>｜, Theme #<number>｜ into cards."""
    card_title_pattern = re.compile(
        r"^\s*(?:#\d+\s*[｜\|]|Signal\s*#\d+\s*[｜\|]|Theme\s*#\d+\s*[｜\|]|Top\s*\d+\s*[｜\|]|#\d+\s*[-—–])",
        re.IGNORECASE,
    )

    h3_elements = soup.find_all("h3")
    for h3 in h3_elements:
        if not h3.parent or h3.find_parent("section", class_="analysis-card"):
            continue
        text = h3.get_text()
        if not card_title_pattern.search(text):
            continue

        # Create the analysis card section
        card_section = soup.new_tag("section", attrs={"class": "analysis-card"})
        h3.insert_before(card_section)

        # Collect siblings until next H2, H3, or end of container
        current = h3
        nodes_to_move = []
        while current:
            next_sibling = current.next_sibling
            nodes_to_move.append(current)
            if next_sibling is None:
                break
            if isinstance(next_sibling, Tag) and next_sibling.name in ("h2", "h3", "h1"):
                break
            current = next_sibling

        for node in nodes_to_move:
            card_section.append(node)


def _parse_chip_text_to_spans(soup: BeautifulSoup, raw_text: str) -> Optional[Tag]:
    """Parse raw text containing pipe-separated metrics into a styled meta-chips container."""
    parts = [p.strip() for p in re.split(r"\s*[｜\|]\s*", raw_text) if p.strip()]
    if not parts:
        return None

    label_keys = {"影響分數", "方向", "證據等級", "證據", "信心", "信心程度", "持續性", "嚴重度", "Severity", "Persistence", "Confidence", "Evidence", "Score"}
    normalized_items: List[str] = []
    
    i = 0
    while i < len(parts):
        current_part = parts[i]
        if current_part in label_keys and i + 1 < len(parts):
            val = parts[i + 1]
            normalized_items.append(f"{current_part} {val}")
            i += 2
        else:
            normalized_items.append(current_part)
            i += 1

    chips_container = soup.new_tag("div", attrs={"class": "meta-chips"})
    
    for item in normalized_items:
        chip_span = soup.new_tag("span", attrs={"class": "chip"})
        
        # Check classification
        if re.search(r"\b\d+/(?:100|5)\b", item) or item.startswith("影響分數") or item.startswith("Score"):
            chip_span["class"] = ["chip", "chip-score"]
        elif any(arrow in item for arrow in ("↗", "↘", "↑", "↓", "→")) or item.startswith("方向"):
            dir_cls = "direction-flat"
            if "↗" in item or "改善" in item or "加速" in item:
                dir_cls = "direction-improving"
            elif "↘" in item or "惡化" in item or "減速" in item:
                dir_cls = "direction-worsening"
            elif "↑" in item or "上升" in item:
                dir_cls = "direction-up"
            elif "↓" in item or "下降" in item:
                dir_cls = "direction-down"
            chip_span["class"] = ["chip", "direction", dir_cls]
        elif "證據" in item or "Grade" in item or "Evidence" in item:
            chip_span["class"] = ["chip", "chip-evidence"]
        elif "信心" in item or "Confidence" in item:
            chip_span["class"] = ["chip", "chip-confidence"]
        elif "Severity" in item or "嚴重度" in item:
            chip_span["class"] = ["chip", "chip-severity"]
        elif "Persistence" in item or "持續性" in item:
            chip_span["class"] = ["chip", "chip-persistence"]

        chip_span.string = item
        chips_container.append(chip_span)

    return chips_container


def _enhance_meta_chips(soup: BeautifulSoup) -> None:
    """Convert bold meta lines (e.g. 94/100｜↗ 改善｜證據 A｜信心 高) into meta-chips."""
    score_line_pattern = re.compile(
        r"(?:\d+/(?:100|5)|影響分數|證據|Grade|Confidence|信心|Severity|Persistence|方向|↗|↘|↑|↓)",
        re.IGNORECASE,
    )

    for p in soup.find_all("p"):
        text = p.get_text().strip()
        if ("｜" in text or "|" in text) and score_line_pattern.search(text):
            segments = [s.strip() for s in re.split(r"\s*[｜\|]\s*", text) if s.strip()]
            if len(segments) >= 2 and all(len(s) <= 40 for s in segments):
                chips_tag = _parse_chip_text_to_spans(soup, text)
                if chips_tag:
                    p.replace_with(chips_tag)


def _enhance_executive_summary(soup: BeautifulSoup) -> None:
    """Enhance executive summary bullets into responsive compact card grid."""
    for h2 in soup.find_all("h2"):
        t = h2.get_text()
        if "執行摘要" in t or "EXECUTIVE SUMMARY" in t.upper():
            current = h2.next_sibling
            while current:
                if isinstance(current, Tag):
                    if current.name in ("h2", "h1"):
                        break
                    if current.name == "ul":
                        existing_classes = current.get("class", [])
                        if "executive-points" not in existing_classes:
                            existing_classes.append("executive-points")
                            current["class"] = existing_classes
                        break
                current = current.next_sibling


def _enhance_tables(soup: BeautifulSoup) -> None:
    """Wrap tables with wide-content scrollable containers and auto-detect numeric columns."""
    for table in soup.find_all("table"):
        parent = table.parent
        if not (parent and parent.name == "div" and "table-scroll" in parent.get("class", [])):
            wrapper = soup.new_tag("div", attrs={"class": "table-scroll wide-content"})
            table.wrap(wrapper)
        elif "wide-content" not in parent.get("class", []):
            parent["class"] = list(dict.fromkeys(parent.get("class", []) + ["wide-content"]))

        rows = table.find_all("tr")
        if not rows:
            continue

        col_total: Dict[int, int] = {}
        col_numeric: Dict[int, int] = {}

        for tr in rows:
            tds = tr.find_all("td")
            for idx, td in enumerate(tds):
                val = td.get_text().strip()
                if not val:
                    continue
                col_total[idx] = col_total.get(idx, 0) + 1
                if re.match(r"^[\+\-]?\$?(?:US\$?)?[\d,\.]+(?:\s*(?:%|bp|bn|mn|k))?$", val, re.IGNORECASE) or \
                   re.match(r"^[\+\-]?\d+/\d+$", val) or \
                   re.match(r"^[↑↓→↗↘]?\s*[\+\-]?\d+(\.\d+)?(?:%|bp)?$", val):
                    col_numeric[idx] = col_numeric.get(idx, 0) + 1

        numeric_cols = set()
        for idx, total in col_total.items():
            if total > 0 and (col_numeric.get(idx, 0) / total) >= 0.6:
                numeric_cols.add(idx)

        for tr in rows:
            cells = tr.find_all(["th", "td"])
            for idx, cell in enumerate(cells):
                if idx in numeric_cols:
                    c_classes = cell.get("class", [])
                    if "numeric" not in c_classes:
                        c_classes.append("numeric")
                        cell["class"] = c_classes


def _sanitize_links(soup: BeautifulSoup) -> None:
    """Enforce safe target=_blank and rel=noopener noreferrer for links."""
    for a in soup.find_all("a"):
        href = a.get("href", "").strip()
        if not href.startswith("http://") and not href.startswith("https://") and not href.startswith("#"):
            a["href"] = "#"
        elif href.startswith("http://") or href.startswith("https://"):
            a["target"] = "_blank"
            a["rel"] = "noopener noreferrer"


def _process_element_contents(soup: BeautifulSoup, element: Any) -> None:
    """Process child text nodes of an element for semantic badges and directions."""
    is_table_cell = element.name in ("td", "th")
    for text_node in list(element.find_all(string=True)):
        if text_node.parent and text_node.parent.name in ("code", "pre", "script", "style"):
            continue
        text = str(text_node)
        if not text.strip():
            continue

        replaced_html = _enrich_text_html(text, is_table_cell=is_table_cell)
        if replaced_html != text:
            parsed_frag = BeautifulSoup(replaced_html, "html.parser")
            text_node.replace_with(*parsed_frag.contents)


def _enrich_text_html(text: str, is_table_cell: bool = False) -> str:
    """Enrich text with semantic HTML spans while strictly preserving original text terms."""
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

    # 5. Risk Lights following "Risk Light:" or "Risk:" or "風險燈號："
    def _replace_named_risk_light(m):
        prefix = m.group(1)
        val = m.group(2)
        val_upper = val.upper()
        icon = "🟢" if val_upper == "GREEN" else "🟡" if val_upper == "YELLOW" else "🟠" if val_upper == "ORANGE" else "🔴"
        cls = f"risk-{val.lower()}"
        return prefix + _token(f'<span class="risk {cls}">{icon} {val}</span>')

    escaped = re.sub(
        r"((?:Risk\s*Light|Risk|燈號|風險燈號)[：:]\s*)(GREEN|YELLOW|ORANGE|RED|Green|Yellow|Orange|Red)\b",
        _replace_named_risk_light,
        escaped,
    )

    # 6. Standalone uppercase risk light words in table cells
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


def enhance_html_elements(soup: BeautifulSoup, skip_h1_removal: bool = False) -> BeautifulSoup:
    """Apply deterministic institutional semantic enhancements across an HTML DOM tree.

    Transforms callout blockquotes, card groupings, score chips, executive grids,
    numeric table alignments, direction indicators, risk lights, and state transitions.
    """
    if not skip_h1_removal:
        first_h1 = soup.find("h1")
        if first_h1:
            first_h1.decompose()

    _enhance_callouts(soup)
    _enhance_analysis_cards(soup)
    _enhance_meta_chips(soup)
    _enhance_executive_summary(soup)
    _enhance_tables(soup)
    _sanitize_links(soup)

    text_targets = soup.find_all(["td", "th", "p", "li", "div", "span", "blockquote"])
    for element in text_targets:
        if element.find(["table", "pre"]):
            continue
        _process_element_contents(soup, element)

    return soup


def enhance_html_semantics(raw_html: str, skip_h1_removal: bool = True) -> str:
    """Parse HTML string, apply full institutional semantic enhancements, and return modernized HTML."""
    soup = BeautifulSoup(raw_html, "html.parser")
    enhance_html_elements(soup, skip_h1_removal=skip_h1_removal)
    return str(soup)


def _postprocess_soup(soup: BeautifulSoup) -> None:
    """Apply deterministic semantic post-processing to HTML elements."""

    # 0. Strip any elements containing canonical markers or raw frontmatter
    for tag in list(soup.find_all(["h1", "h2", "h3", "h4", "p", "pre", "div"])):
        t = tag.get_text()
        if "<<<REPORT_BEGIN>>>" in t or "<<<REPORT_END>>>" in t:
            tag.decompose()
        elif "research_status:" in t and "format_version:" in t:
            tag.decompose()

    enhance_html_elements(soup, skip_h1_removal=False)


EMBEDDED_CSS_PATH = Path(__file__).resolve().parent / "report-embedded.css"
_CACHED_EMBEDDED_CSS: Optional[str] = None


def get_embedded_css() -> str:
    """Return self-contained institutional CSS stylesheet loaded from report-embedded.css (cached in memory)."""
    global _CACHED_EMBEDDED_CSS
    if _CACHED_EMBEDDED_CSS is None:
        if EMBEDDED_CSS_PATH.is_file():
            _CACHED_EMBEDDED_CSS = EMBEDDED_CSS_PATH.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(f"Missing required embedded stylesheet: {EMBEDDED_CSS_PATH}")
    return _CACHED_EMBEDDED_CSS


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
  <div class="report-narrative">
    {hero_html}
    <main class="report-content">
      {content_html}
    </main>
    <footer>
      Global Macro Signal Report · {date_str} · Generated Deterministically
    </footer>
  </div>
</div>
</body>
</html>
"""
    return document_html
