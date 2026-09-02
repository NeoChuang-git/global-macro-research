#!/usr/bin/env python3
"""
Comprehensive Modernizer and Content Beautifier for Legacy Global Macro Reports.
Normalizes structure, hero headers, table scrolling, semantic direction badges,
risk lights, state transition chips, and embeds the unified institutional design system.
"""

import hashlib
import html
import json
import re
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from bs4 import BeautifulSoup
from scripts.markdown_renderer import (
    get_embedded_css,
    _enrich_text_html,
    _process_element_contents,
)
from scripts.sync_drive import build_reports_index, _atomic_write_if_changed, _hash_file

# Enhanced institutional stylesheet with legacy compatibility
UNIFIED_CSS = get_embedded_css() + """
/* Legacy Card & Layout Compatibility */
main {
  max-width: 1240px;
  margin: 0 auto;
}

.card, .panel, .box, .risk-card, .sec {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px 28px;
  margin: 24px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.callout, .note {
  background: var(--accent-glow);
  border-left: 4px solid var(--accent);
  border-radius: 0 8px 8px 0;
  padding: 16px 20px;
  margin: 18px 0;
  color: var(--text-primary);
  font-size: 0.98rem;
  line-height: 1.68;
}

.chain, .node {
  background: var(--bg-surface-raised);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
  margin: 18px 0;
  font-weight: 600;
  text-align: center;
  color: var(--text-primary);
  line-height: 1.6;
}

.small, small, .footer-note {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 24px;
  display: block;
}

/* Legacy Color & Badge utilities */
.green, .g, .badge-green { color: var(--success); font-weight: 700; }
.yellow, .y, .badge-yellow { color: var(--warning); font-weight: 700; }
.orange, .o, .badge-orange { color: var(--orange); font-weight: 700; }
.red, .r, .badge-red { color: var(--danger); font-weight: 700; }

.pill, .tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1;
  background: var(--bg-surface-raised);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.metric, .metric-down {
  font-weight: 600;
  font-feature-settings: "tnum" 1;
}

.arrow {
  font-weight: 700;
}

.muted {
  color: var(--text-muted);
}

.table-wrap, .scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin: 18px 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-surface);
}
"""


def detect_report_type_badge(category: str, filename: str) -> str:
    if category == "early-warning" or "early_warning" in filename.lower() or "risk" in filename.lower():
        return "MACRO_TAIWAN_EARLY_WARNING"
    elif category == "weekly" or "weekly" in filename.lower():
        return "WEEKLY_STRATEGY"
    return "GLOBAL_DAILY_BRIEF"


def detect_risk_light(text: str) -> str:
    upper = text.upper()
    if "🔴" in text or "RISK: RED" in upper or "RED LIGHT" in upper or "AGGREGATE RISK: RED" in upper:
        return '<span class="badge risk-red">🔴 Risk: RED</span>'
    elif "🟠" in text or "RISK: ORANGE" in upper or "ORANGE LIGHT" in upper or "AGGREGATE RISK: ORANGE" in upper or "ORANGE" in upper:
        return '<span class="badge risk-orange">🟠 Risk: ORANGE</span>'
    elif "🟡" in text or "RISK: YELLOW" in upper or "YELLOW LIGHT" in upper or "YELLOW" in upper:
        return '<span class="badge risk-yellow">🟡 Risk: YELLOW</span>'
    elif "🟢" in text or "RISK: GREEN" in upper or "GREEN LIGHT" in upper or "GREEN" in upper:
        return '<span class="badge risk-green">🟢 Risk: GREEN</span>'
    return '<span class="badge risk-yellow">🟡 Risk: YELLOW</span>'


def extract_clean_title(soup: BeautifulSoup, filename: str) -> str:
    # 1. Try finding first H1
    h1 = soup.find("h1")
    if h1:
        text = h1.get_text(strip=True)
        if text:
            # Clean up common prefixes like "Global Macro Early Warning｜"
            cleaned = re.sub(r"^Global Macro (?:Early Warning|Daily Brief|Morning|Weekly Strategy)\s*[｜|—–-]\s*", "", text)
            return cleaned or text

    # 2. Try title tag
    if soup.title and soup.title.string:
        text = soup.title.string.strip()
        cleaned = re.sub(r"^Global Macro (?:Early Warning|Daily Brief|Morning|Weekly Strategy)\s*[｜|—–-]\s*", "", text)
        return cleaned or text

    # 3. Fallback to filename
    name = Path(filename).stem
    name = re.sub(r"^(?:Global_Macro_|Global_Daily_Brief_|Weekly_Strategy_)", "", name)
    name = re.sub(r"_\d{4}-\d{2}-\d{2}(?:_\w+)?", "", name)
    return name.replace("_", " ").title()


def beautify_legacy_report(file_path: Path, category: str) -> bool:
    raw_content = file_path.read_text(encoding="utf-8")
    
    # Skip reports already generated by new markdown renderer
    if "<!-- canonical-markdown-rendered -->" in raw_content or (
        "hero-header" in raw_content and "report-container" in raw_content and "report_type" in raw_content
    ):
        return False

    soup = BeautifulSoup(raw_content, "html.parser")

    # 1. Extract metadata
    filename = file_path.name
    report_type = detect_report_type_badge(category, filename)
    clean_title = extract_clean_title(soup, filename)
    risk_badge = detect_risk_light(soup.get_text())

    # 2. Remove legacy header/hero elements to avoid duplicate headers
    for old_hero in list(soup.find_all(["section", "div", "header"], class_=["hero", "header", "site-header"])):
        old_hero.decompose()
    for h in list(soup.find_all("h1")):
        h.decompose()

    # 3. Apply semantic enrichment across all text nodes (Directions, Risk lights, Transitions, Grades)
    for el in soup.find_all(["td", "th", "p", "li", "div", "span", "blockquote"]):
        if el.find(["table", "pre"]):
            continue
        _process_element_contents(soup, el)

    # 4. Wrap all tables in <div class="table-scroll">
    for table in soup.find_all("table"):
        parent = table.parent
        if parent and parent.name == "div" and any(c in parent.get("class", []) for c in ["table-scroll", "table-wrap", "scroll"]):
            continue
        wrapper = soup.new_tag("div", attrs={"class": "table-scroll"})
        table.wrap(wrapper)

    # 5. Extract main body content
    main_el = soup.find("main")
    if main_el:
        body_content = "".join(str(c) for c in main_el.contents if str(c).strip())
    elif soup.body:
        body_content = "".join(str(c) for c in soup.body.contents if str(c).strip())
    else:
        body_content = str(soup)

    # 6. Build modernized HTML document
    hero_header_html = f"""<header class="hero-header">
  <div class="hero-top">
    <div class="hero-type-row">
      <span class="badge badge-type">{html.escape(report_type)}</span>
      {risk_badge}
    </div>
  </div>
  <h1 class="hero-title">{html.escape(clean_title)}</h1>
</header>"""

    document_html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(clean_title)} · Global Macro Signal Report</title>
<style>
{UNIFIED_CSS}
</style>
</head>
<body>
<div class="report-container">
{hero_header_html}
<main class="report-content">
{body_content}
</main>
<footer>
  Global Macro Signal Report · Archive · Generated Deterministically
</footer>
</div>
</body>
</html>
"""

    file_path.write_text(document_html, encoding="utf-8")
    return True


def main():
    reports_dir = repo_root / "reports"
    updated_count = 0

    for cat_dir in ["early-warning", "daily", "weekly"]:
        target_dir = reports_dir / cat_dir
        if not target_dir.exists():
            continue
        for html_file in sorted(target_dir.glob("**/*.html")):
            if html_file.name == "Global_Macro_Early_Warning_2026-09-03_0003_labor_rates_divergence.html":
                continue
            if beautify_legacy_report(html_file, cat_dir):
                updated_count += 1
                print(f"Beautified: {html_file.relative_to(repo_root)}")

    print(f"\nTotal beautified legacy reports: {updated_count}")

    # Rebuild reports.json index with updated sha256 checksums
    state_file = repo_root / "data/drive-sync-state.json"
    state_data = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {"files": {}}
    
    runs_file = repo_root / "data/report_runs.json"
    runs_data = json.loads(runs_file.read_text(encoding="utf-8")) if runs_file.exists() else None

    index = build_reports_index(repo_root, state_data.get("files", {}), runs_data=runs_data)
    _atomic_write_if_changed(repo_root / "data/reports.json", (json.dumps(index, ensure_ascii=False, indent=2, default=str) + "\n").encode("utf-8"))
    print("Updated data/reports.json with new SHA256 checksums.")


if __name__ == "__main__":
    main()
