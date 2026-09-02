#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path
import unittest
from bs4 import BeautifulSoup
from scripts.markdown_renderer import render_markdown_to_html


class MarkdownRendererTests(unittest.TestCase):
    # --- 1. Markdown Fundamentals ---

    def test_blockquote_renders(self):
        md = "> 普通引用文字測試"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-1"})
        self.assertIn("<blockquote", rendered)
        self.assertIn("普通引用文字測試", rendered)

    def test_bold_leadin_renders(self):
        md = "**市場定價｜** 部分反映。"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-2"})
        self.assertIn("<strong>市場定價｜</strong>", rendered)
        self.assertIn("部分反映。", rendered)

    def test_horizontal_rule_renders(self):
        md = "段落一\n\n---\n\n段落二"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-3"})
        self.assertIn("<hr", rendered)

    def test_h3_h4_hierarchy(self):
        md = "### 一般標題 H3\n\n#### 市場解讀\n\n內文說明"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-4"})
        self.assertIn("<h3", rendered)
        self.assertIn("<h4", rendered)
        self.assertIn("一般標題 H3", rendered)
        self.assertIn("市場解讀", rendered)

    def test_pipe_table_renders(self):
        md = """
| 指標 | 前值 | 目前 | Delta |
|---|---:|---:|---:|
| 10Y 殖利率（Yield） | 4.18% | 4.26% | ↑ +8bp |
"""
        meta = {
            "title": "Daily Signal",
            "report_type": "GLOBAL_DAILY_BRIEF",
            "run_id": "TEST-1",
            "generated_at_taipei": "2026-09-03T07:30:00+08:00",
            "coverage_start_taipei": "2026-09-02T07:30:00+08:00",
            "coverage_end_taipei": "2026-09-03T07:30:00+08:00",
            "risk_light": "YELLOW",
        }
        rendered = render_markdown_to_html(md, meta)

        self.assertIn("table-scroll", rendered)
        self.assertIn("wide-content", rendered)
        self.assertIn("<table>", rendered)
        self.assertIn("<thead>", rendered)
        self.assertIn("<tbody>", rendered)
        self.assertIn("<th>", rendered)
        self.assertIn("<td>", rendered)
        self.assertIn("10Y 殖利率（Yield）", rendered)

    # --- 2. Semantic Callout Detection ---

    def test_thesis_callout_detection(self):
        md = "> **一句話結論｜** Dell 本輪上調的是全年獲利能力。\n\n> **核心判斷｜** AI 基建持續擴張。"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-5"})
        soup = BeautifulSoup(rendered, "html.parser")
        callouts = soup.find_all("blockquote", class_="callout-thesis")
        self.assertGreaterEqual(len(callouts), 2)

    def test_risk_callout_detection(self):
        md = "> **風險提醒｜** 高利率壓抑估值。\n\n> **核心風險｜** 融資成本上升。"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-6"})
        soup = BeautifulSoup(rendered, "html.parser")
        callouts = soup.find_all("blockquote", class_="callout-risk")
        self.assertGreaterEqual(len(callouts), 2)

    def test_strategy_callout_detection(self):
        md = "> **投資含意｜** 聚焦有指引證據的個股。\n\n> **策略含意｜** 逢低配置先進封裝。"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-7"})
        soup = BeautifulSoup(rendered, "html.parser")
        callouts = soup.find_all("blockquote", class_="callout-strategy")
        self.assertGreaterEqual(len(callouts), 2)

    def test_catalyst_callout_detection(self):
        md = "> **下一驗證｜** Broadcom 財報指引。\n\n> **下一催化劑｜** 美國非農就業報告。"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-8"})
        soup = BeautifulSoup(rendered, "html.parser")
        callouts = soup.find_all("blockquote", class_="callout-catalyst")
        self.assertGreaterEqual(len(callouts), 2)

    # --- 3. Event / Signal / Theme Card & Chips ---

    def test_event_card_detection(self):
        md = """
### #1｜Dell AI 伺服器需求推升訂單

**94/100｜↗ 改善｜證據 A｜信心 高**

- 事件說明內容。

### #2｜Palo Alto 估值調整

**82/100｜↘ 惡化｜證據 B｜信心 中**

- 第二張卡片內容。
"""
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-9"})
        soup = BeautifulSoup(rendered, "html.parser")
        cards = soup.find_all("section", class_="analysis-card")
        self.assertEqual(len(cards), 2)
        self.assertIn("Dell AI 伺服器需求推升訂單", cards[0].get_text())
        self.assertIn("Palo Alto 估值調整", cards[1].get_text())

    def test_signal_card_detection(self):
        md = """
### Signal #1｜AI 伺服器需求加速

- 訊號詳細內容。
"""
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-10"})
        soup = BeautifulSoup(rendered, "html.parser")
        cards = soup.find_all("section", class_="analysis-card")
        self.assertEqual(len(cards), 1)
        self.assertIn("AI 伺服器需求加速", cards[0].get_text())

    def test_theme_card_detection(self):
        md = """
### Theme #1｜全球半導體資本支出週期

- 主題分析內容。
"""
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-11"})
        soup = BeautifulSoup(rendered, "html.parser")
        cards = soup.find_all("section", class_="analysis-card")
        self.assertEqual(len(cards), 1)
        self.assertIn("全球半導體資本支出週期", cards[0].get_text())

    def test_score_chips(self):
        md = "**94/100｜↗ 改善｜證據 A｜信心 高**"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-12"})
        soup = BeautifulSoup(rendered, "html.parser")
        chips_div = soup.find("div", class_="meta-chips")
        self.assertIsNotNone(chips_div)
        chips = chips_div.find_all("span", class_="chip")
        self.assertGreaterEqual(len(chips), 3)
        self.assertIn("94/100", chips_div.get_text())
        self.assertIn("證據 A", chips_div.get_text())
        self.assertIn("信心 高", chips_div.get_text())

    def test_direction_chips(self):
        md = "- 上升: ↑\n- 下降: ↓\n- 持平: →\n- 改善: ↗\n- 惡化: ↘"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-13"})
        self.assertIn("direction-up", rendered)
        self.assertIn("direction-down", rendered)
        self.assertIn("direction-flat", rendered)
        self.assertIn("direction-improving", rendered)
        self.assertIn("direction-worsening", rendered)

    def test_risk_light_chips(self):
        md = "燈號檢查：🟢 Green, 🟡 Yellow, 🟠 Orange, 🔴 Red"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-14"})
        self.assertIn("risk-green", rendered)
        self.assertIn("risk-yellow", rendered)
        self.assertIn("risk-orange", rendered)
        self.assertIn("risk-red", rendered)

    def test_state_transition(self):
        md = "轉換檢驗：Yellow → Orange 以及 4.18% → 4.31%"
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-15"})
        self.assertIn("state-transition", rendered)
        self.assertIn("state-prior", rendered)
        self.assertIn("state-current", rendered)

    # --- 4. Tables & Layout ---

    def test_numeric_column_alignment(self):
        md = """
| 項目 | 數值 | 變動 | 說明 |
|---|---|---|---|
| 10Y Yield | 4.25% | +8bp | 美債殖利率 |
| 2Y Yield | 4.80% | +5bp | 短端利率 |
| Spread | 55bp | +3bp | 利差 |
"""
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-16"})
        soup = BeautifulSoup(rendered, "html.parser")
        tds = soup.find_all("td", class_="numeric")
        self.assertGreater(len(tds), 0)

    def test_executive_points_grid(self):
        md = """
## 執行摘要

> **一句話結論｜** 核心結論說明。

- **AI 基建｜↗** — 訂單持續強勁。
- **估值壓力｜↘** — 利率高檔壓抑本益比。
- **台灣供應鏈｜↗** — 外溢效應正向。
"""
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-17"})
        soup = BeautifulSoup(rendered, "html.parser")
        exec_list = soup.find("ul", class_="executive-points")
        self.assertIsNotNone(exec_list)

    def test_layout_narrative_and_wide_table(self):
        md = """
# 報告標題

一般段落文字。

| 欄位 A | 欄位 B |
|---|---|
| 內容 1 | 內容 2 |
"""
        rendered = render_markdown_to_html(md, {"title": "Test", "run_id": "T-18"})
        self.assertIn("report-narrative", rendered)
        self.assertIn("table-scroll", rendered)
        self.assertIn("wide-content", rendered)

    # --- 5. Security & Invariants ---

    def test_raw_html_disabled(self):
        md = """
<script>alert('xss')</script>
<iframe src="http://evil.com"></iframe>
<object data="test"></object>
"""
        rendered = render_markdown_to_html(md, {"title": "Security Test", "run_id": "TEST-5"})
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<iframe>", rendered)
        self.assertNotIn("<object>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_javascript_url_blocked(self):
        md = """
- Valid: [Fed Report](https://federalreserve.gov/report)
- Invalid: [Attack](javascript:alert(1))
"""
        rendered = render_markdown_to_html(md, {"title": "Links Test", "run_id": "TEST-6"})
        self.assertIn('target="_blank"', rendered)
        self.assertIn('rel="noopener noreferrer"', rendered)
        self.assertNotIn('href="javascript:', rendered)

    def test_preserves_bilingual_terminology_verbatim(self):
        terms = [
            "訂單（Order）",
            "新訂單（New Orders）",
            "外銷訂單（Export Orders）",
            "營收（Revenue）",
            "毛利率（Gross Margin）",
            "每股盈餘（EPS）",
            "資本支出（CapEx）",
            "庫存（Inventory）",
            "殖利率（Yield）",
            "實質殖利率（Real Yield）",
            "期限溢酬（Term Premium）",
            "信用利差（Credit Spread）",
            "流動性（Liquidity）",
            "資金流（Flow）",
            "部位（Positioning）",
            "估值（Valuation）",
            "前瞻指引（Guidance）",
            "市場定價（Market Pricing）",
            "市場週期（Market Cycle）",
            "基本面週期（Fundamental Cycle）",
        ]
        md = "\n".join(f"- {t}" for t in terms)
        rendered = render_markdown_to_html(md, {"title": "Terminology Test", "run_id": "TEST-4"})
        for term in terms:
            self.assertIn(term, rendered)

    def test_existing_html_byte_identical(self):
        """Verify that existing indexed HTML reports remain 100% byte-for-byte identical."""
        repo_root = Path(__file__).resolve().parents[1]
        index_path = repo_root / "data" / "reports.json"
        if not index_path.is_file():
            return
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for r in data.get("reports", []):
            rel_file = r.get("file")
            expected_sha = r.get("sha256")
            file_path = repo_root / rel_file
            if file_path.is_file():
                h = hashlib.sha256()
                with open(file_path, "rb") as f:
                    h.update(f.read())
                self.assertEqual(h.hexdigest(), expected_sha, f"Byte mismatch on existing report {rel_file}")


if __name__ == "__main__":
    unittest.main()

