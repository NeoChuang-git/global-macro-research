#!/usr/bin/env python3
"""
Modernize legacy HTML reports to match the new institutional design system.
Replaces legacy inline <style> tags with the unified design system stylesheet,
wraps unwrapped <table> elements in <div class="table-scroll">, and re-indexes reports.json.
"""

import hashlib
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from bs4 import BeautifulSoup
from scripts.markdown_renderer import get_embedded_css
from scripts.sync_drive import build_reports_index, _atomic_write_if_changed, _hash_file

# Enhanced institutional stylesheet covering modern markdown classes + all legacy report classes
LEGACY_UNIFIED_CSS = get_embedded_css() + """
/* Legacy Report Compatibility Classes */
main {
  max-width: 1240px;
  margin: 0 auto;
}

.card, .panel, .box, .risk-card, .sec {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 22px 26px;
  margin: 20px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.hero {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.hero h1 {
  margin: 0 0 12px;
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.28;
}

.hero p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 1.05rem;
}

.callout, .note {
  background: var(--accent-glow);
  border-left: 4px solid var(--accent);
  border-radius: 0 8px 8px 0;
  padding: 14px 18px;
  margin: 16px 0;
  color: var(--text-primary);
  font-size: 0.98rem;
}

.chain, .node {
  background: var(--bg-surface-raised);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
  margin: 16px 0;
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


def modernize_html_file(file_path: Path) -> bool:
    """Modernize a single legacy HTML file with the unified stylesheet and table scrolling."""
    # Skip new markdown-rendered reports
    raw_content = file_path.read_text(encoding="utf-8")
    if "report-container" in raw_content and "hero-header" in raw_content:
        return False

    soup = BeautifulSoup(raw_content, "html.parser")

    # 1. Update or inject <style> tag
    style_tag = soup.find("style")
    if style_tag:
        style_tag.string = LEGACY_UNIFIED_CSS
    else:
        new_style = soup.new_tag("style")
        new_style.string = LEGACY_UNIFIED_CSS
        if soup.head:
            soup.head.append(new_style)
        else:
            soup.insert(0, new_style)

    # 2. Wrap all tables in <div class="table-scroll"> if not already wrapped
    for table in soup.find_all("table"):
        parent = table.parent
        if parent and parent.name == "div" and any(c in parent.get("class", []) for c in ["table-scroll", "table-wrap", "scroll"]):
            continue
        wrapper = soup.new_tag("div", attrs={"class": "table-scroll"})
        table.wrap(wrapper)

    # 3. Write back modernized HTML
    modernized_html = str(soup)
    file_path.write_text(modernized_html, encoding="utf-8")
    return True


def main():
    repo_root = Path(__file__).resolve().parent.parent
    reports_dir = repo_root / "reports"
    updated_count = 0

    for html_file in sorted(reports_dir.glob("**/*.html")):
        if modernize_html_file(html_file):
            updated_count += 1
            print(f"Modernized: {html_file.relative_to(repo_root)}")

    print(f"\nTotal modernized files: {updated_count}")

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
