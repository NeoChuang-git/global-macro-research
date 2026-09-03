#!/usr/bin/env python3

"""Deterministic Markdown & Semantic Presentation Renderer for Research Reports.

Converts canonical Markdown research blocks into standalone, beautifully-styled,
zero-token HTML documents with Medium-style narrow narrative, wide breakout tables,
and full semantic institutional styling.
"""

import html
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

    # 2. Semantic enhancements
    _enhance_callouts(soup)
    _enhance_analysis_cards(soup)
    _enhance_meta_chips(soup)
    _enhance_executive_summary(soup)
    _enhance_tables(soup)
    _sanitize_links(soup)

    # 3. Text replacements for Directions, Risk lights, Evidence Grades, and State transitions
    text_targets = soup.find_all(["td", "th", "p", "li"])
    for element in text_targets:
        if element.find(["table", "div", "pre"]):
            continue
        _process_element_contents(soup, element)


def get_embedded_css() -> str:
    """Return self-contained Medium-style institutional CSS stylesheet."""
    return """
:root {
  color-scheme: light;
  --bg-primary: #f8fafc;
  --bg-surface: #ffffff;
  --bg-surface-raised: #f1f5f9;
  --bg-surface-hover: #e2e8f0;
  --text-primary: #0f172a;
  --text-secondary: #334155;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --border-subtle: #cbd5e1;
  --accent: #0284c7;
  --accent-light: #e0f2fe;
  --accent-glow: rgba(2, 132, 199, 0.08);

  /* Callout Colors */
  --callout-bg: #f8fafc;
  --callout-thesis-border: #0284c7;
  --callout-thesis-bg: #f0f9ff;
  --callout-risk-border: #f97316;
  --callout-risk-bg: #fff7ed;
  --callout-strategy-border: #8b5cf6;
  --callout-strategy-bg: #f5f3ff;
  --callout-catalyst-border: #10b981;
  --callout-catalyst-bg: #ecfdf5;

  /* Card & Chips */
  --card-bg: #ffffff;
  --card-border: #e2e8f0;
  --chip-bg: #f1f5f9;
  --chip-text: #334155;
  --chip-border: #cbd5e1;

  /* Risk Lights */
  --risk-green-bg: #ecfdf5; --risk-green-text: #059669; --risk-green-border: #a7f3d0;
  --risk-yellow-bg: #fefce8; --risk-yellow-text: #d97706; --risk-yellow-border: #fef08a;
  --risk-orange-bg: #fff7ed; --risk-orange-text: #ea580c; --risk-orange-border: #fed7aa;
  --risk-red-bg: #fef2f2; --risk-red-text: #dc2626; --risk-red-border: #fecaca;

  /* Table */
  --table-zebra: #f8fafc;
  --table-hover: #f1f5f9;
  --table-header-bg: #f1f5f9;
}

@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --bg-primary: #0f172a;
    --bg-surface: #1e293b;
    --bg-surface-raised: #334155;
    --bg-surface-hover: #475569;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border: #334155;
    --border-subtle: #475569;
    --accent: #38bdf8;
    --accent-light: rgba(56, 189, 248, 0.15);
    --accent-glow: rgba(56, 189, 248, 0.12);

    --callout-bg: #1e293b;
    --callout-thesis-border: #38bdf8;
    --callout-thesis-bg: rgba(56, 189, 248, 0.08);
    --callout-risk-border: #fb923c;
    --callout-risk-bg: rgba(249, 115, 22, 0.08);
    --callout-strategy-border: #a78bfa;
    --callout-strategy-bg: rgba(167, 139, 250, 0.08);
    --callout-catalyst-border: #34d399;
    --callout-catalyst-bg: rgba(52, 211, 153, 0.08);

    --card-bg: #1e293b;
    --card-border: #334155;
    --chip-bg: #334155;
    --chip-text: #cbd5e1;
    --chip-border: #475569;

    --risk-green-bg: rgba(16, 185, 129, 0.15); --risk-green-text: #34d399; --risk-green-border: rgba(16, 185, 129, 0.3);
    --risk-yellow-bg: rgba(245, 158, 11, 0.15); --risk-yellow-text: #fbbf24; --risk-yellow-border: rgba(245, 158, 11, 0.3);
    --risk-orange-bg: rgba(249, 115, 22, 0.15); --risk-orange-text: #fb923c; --risk-orange-border: rgba(249, 115, 22, 0.3);
    --risk-red-bg: rgba(239, 68, 68, 0.15); --risk-red-text: #f87171; --risk-red-border: rgba(239, 68, 68, 0.3);

    --table-zebra: rgba(255, 255, 255, 0.02);
    --table-hover: rgba(56, 189, 248, 0.06);
    --table-header-bg: #334155;
  }
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.8;
  font-size: 17px;
  font-feature-settings: "tnum" 1, "cv02" 1, "cv03" 1, "cv04" 1;
  -webkit-font-smoothing: antialiased;
  padding: 24px 16px;
  overflow-x: hidden;
}

/* Layout Containers: Narrative & Content Presentation */
.report-container {
  width: 100%;
  max-width: 1120px;
  margin: 0 auto;
  padding: 24px 20px 48px;
  position: relative;
}

.report-narrative {
  width: 100%;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
}

/* Wide Content Presentation */
.wide-content {
  width: 100%;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
}

/* Hero Header */
.hero-header {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px 28px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 14px;
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
  font-size: 1.75rem;
  font-weight: 750;
  letter-spacing: -0.025em;
  color: var(--text-primary);
  line-height: 1.32;
  margin-bottom: 12px;
}

.hero-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 10px;
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  background: var(--bg-surface-raised);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* Typography & Headings */
.report-narrative p {
  margin: 0 0 1.25rem;
  line-height: 1.8;
  color: var(--text-primary);
}

strong {
  font-weight: 650;
  color: var(--text-primary);
}

h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary);
  line-height: 1.35;
  letter-spacing: -0.015em;
}

h2 {
  font-size: 1.45rem;
  font-weight: 700;
  margin: 3.5rem 0 1.2rem;
  padding-bottom: 0.6rem;
  border-bottom: 2px solid var(--accent);
}

h3 {
  font-size: 1.22rem;
  font-weight: 700;
  margin: 2.5rem 0 1rem;
}

h4 {
  font-size: 1.05rem;
  font-weight: 650;
  margin: 1.8rem 0 0.6rem;
  color: var(--accent);
}

hr {
  border: 0;
  border-top: 1px solid var(--border);
  margin: 3rem auto;
  width: 100%;
}

ul, ol {
  margin: 1rem 0 1.5rem 1.5rem;
  padding: 0;
}

li {
  margin-bottom: 0.65rem;
  line-height: 1.7;
}

/* Callouts */
.callout {
  margin: 1.8rem 0;
  padding: 1.1rem 1.35rem;
  border-left: 4px solid var(--accent);
  border-radius: 0 10px 10px 0;
  background: var(--callout-bg);
  border-top: 1px solid var(--border);
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.callout p {
  margin: 0;
  line-height: 1.75;
}

.callout-thesis {
  border-left-color: var(--callout-thesis-border);
  background: var(--callout-thesis-bg);
}

.callout-risk {
  border-left-color: var(--callout-risk-border);
  background: var(--callout-risk-bg);
}

.callout-strategy {
  border-left-color: var(--callout-strategy-border);
  background: var(--callout-strategy-bg);
}

.callout-catalyst {
  border-left-color: var(--callout-catalyst-border);
  background: var(--callout-catalyst-bg);
}

/* Analysis Cards */
.analysis-card {
  margin: 2.2rem 0;
  padding: 1.5rem 1.6rem;
  border: 1px solid var(--card-border);
  border-radius: 14px;
  background: var(--card-bg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.analysis-card > h3:first-child {
  margin-top: 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}

/* Meta Chips */
.meta-chips {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: 1rem 0 1.25rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  background: var(--chip-bg);
  color: var(--chip-text);
  border: 1px solid var(--chip-border);
  line-height: 1.35;
}

.chip-score {
  font-weight: 700;
  color: var(--accent);
  background: var(--accent-light);
  border-color: var(--accent);
}

.chip-evidence, .chip-confidence, .chip-severity, .chip-persistence {
  color: var(--text-secondary);
}

/* Direction Indicators */
.direction {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-weight: 600;
  font-size: 0.85rem;
}

.direction-up { color: #0284c7; }
.direction-down { color: #7c3aed; }
.direction-improving { color: #059669; }
.direction-worsening { color: #dc2626; }
.direction-flat { color: var(--text-muted); }

/* Risk Lights */
.risk-chip, .risk {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.82rem;
  line-height: 1.3;
}

.risk-green { background: var(--risk-green-bg); color: var(--risk-green-text); border: 1px solid var(--risk-green-border); }
.risk-yellow { background: var(--risk-yellow-bg); color: var(--risk-yellow-text); border: 1px solid var(--risk-yellow-border); }
.risk-orange { background: var(--risk-orange-bg); color: var(--risk-orange-text); border: 1px solid var(--risk-orange-border); }
.risk-red { background: var(--risk-red-bg); color: var(--risk-red-text); border: 1px solid var(--risk-red-border); }

/* State Transitions */
.state-transition {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--bg-surface-raised);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid var(--border);
}

.state-prior { color: var(--text-muted); }
.transition-arrow { color: var(--accent); font-weight: bold; }
.state-current { color: var(--text-primary); font-weight: 600; }

/* Tables */
.table-scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin-top: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg-surface);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.92rem;
  text-align: left;
  min-width: 680px;
}

th {
  background: var(--table-header-bg);
  color: var(--text-primary);
  font-weight: 650;
  position: sticky;
  top: 0;
  z-index: 2;
  padding: 11px 15px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  letter-spacing: 0.01em;
}

td {
  padding: 11px 15px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
  line-height: 1.55;
}

tr:last-child td {
  border-bottom: none;
}

tr:nth-child(even) td {
  background: var(--table-zebra);
}

tr:hover td {
  background: var(--table-hover);
}

.numeric {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* Executive Summary Grid */
.executive-points {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  list-style: none;
  margin: 1.25rem 0 1.75rem 0;
  padding: 0;
}

.executive-points > li {
  margin: 0;
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  line-height: 1.6;
  font-size: 0.92rem;
}

@media (max-width: 768px) {
  .executive-points {
    grid-template-columns: 1fr;
  }
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
  background: var(--accent-light);
  color: var(--accent);
  border: 1px solid var(--accent);
}

.badge-topic {
  background: var(--bg-surface-raised);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.badge-grade-A { background: var(--risk-green-bg); color: var(--risk-green-text); border: 1px solid var(--risk-green-border); }
.badge-grade-B { background: var(--accent-light); color: var(--accent); border: 1px solid var(--accent); }
.badge-grade-C { background: var(--risk-yellow-bg); color: var(--risk-yellow-text); border: 1px solid var(--risk-yellow-border); }
.badge-grade-D { background: var(--risk-red-bg); color: var(--risk-red-text); border: 1px solid var(--risk-red-border); }

/* Links */
a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px dotted rgba(2, 132, 199, 0.4);
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

/* Responsive Overrides */
@media (max-width: 768px) {
  body {
    padding: 16px 12px;
    font-size: 16px;
  }
  .report-narrative p {
    font-size: 16px;
  }
  h1.hero-title { font-size: 1.45rem; }
  h2 { font-size: 1.25rem; margin-top: 2.2rem; }
  h3 { font-size: 1.1rem; margin-top: 1.8rem; }
  h4 { font-size: 1rem; }
  .analysis-card {
    padding: 1.1rem 1rem;
    border-radius: 10px;
  }
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
