#!/usr/bin/env python3

import unittest
from scripts.markdown_renderer import render_markdown_to_html


class MarkdownRendererTests(unittest.TestCase):
    def test_renders_markdown_pipe_tables_into_scrollable_table_structure(self):
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

        self.assertIn('<div class="table-scroll">', rendered)
        self.assertIn("<table>", rendered)
        self.assertIn("<thead>", rendered)
        self.assertIn("<tbody>", rendered)
        self.assertIn("<th>", rendered)
        self.assertIn("<td>", rendered)
        self.assertIn("10Y 殖利率（Yield）", rendered)

    def test_semantic_direction_and_risk_light_mapping(self):
        md = """
- Direction Up: ↑
- Direction Down: ↓
- Risk Lights: 🟢 Green, 🟡 Yellow, 🟠 Orange, 🔴 Red
- Grade: Grade A, Grade B
"""
        meta = {
            "title": "Daily Signal",
            "report_type": "GLOBAL_DAILY_BRIEF",
            "run_id": "TEST-2",
        }
        rendered = render_markdown_to_html(md, meta)

        self.assertIn("direction-up", rendered)
        self.assertIn("direction-down", rendered)
        self.assertIn("risk-green", rendered)
        self.assertIn("risk-yellow", rendered)
        self.assertIn("risk-orange", rendered)
        self.assertIn("risk-red", rendered)
        self.assertIn("badge-grade-A", rendered)
        self.assertIn("badge-grade-B", rendered)

    def test_semantic_state_transition_chips(self):
        md = "Transition check: Yellow → Orange and 60% → 72%"
        meta = {"title": "State Transition", "run_id": "TEST-3"}
        rendered = render_markdown_to_html(md, meta)

        self.assertIn("state-transition", rendered)
        self.assertIn("state-prior", rendered)
        self.assertIn("state-current", rendered)
        self.assertIn("Yellow", rendered)
        self.assertIn("Orange", rendered)

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
        meta = {"title": "Terminology Test", "run_id": "TEST-4"}
        rendered = render_markdown_to_html(md, meta)

        for term in terms:
            self.assertIn(term, rendered)

    def test_raw_html_in_markdown_is_escaped_and_safe(self):
        md = """
<script>alert('xss')</script>
<iframe src="http://evil.com"></iframe>
<object data="test"></object>
"""
        meta = {"title": "Security Test", "run_id": "TEST-5"}
        rendered = render_markdown_to_html(md, meta)

        # Ensure no unescaped script, iframe, object tags are rendered as active elements
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<iframe>", rendered)
        self.assertNotIn("<object>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_source_links_are_sanitized_with_target_blank(self):
        md = """
- Valid: [Fed Report](https://federalreserve.gov/report)
- Invalid: [Attack](javascript:alert(1))
"""
        meta = {"title": "Links Test", "run_id": "TEST-6"}
        rendered = render_markdown_to_html(md, meta)

        self.assertIn('target="_blank"', rendered)
        self.assertIn('rel="noopener noreferrer"', rendered)
        self.assertNotIn('href="javascript:', rendered)

    def test_html_output_is_standalone_with_no_external_dependencies(self):
        meta = {
            "title": "Standalone Test",
            "run_id": "TEST-7",
            "report_type": "GLOBAL_DAILY_BRIEF",
        }
        rendered = render_markdown_to_html("# Content", meta)

        self.assertIn("<!doctype html>", rendered)
        self.assertIn("<style>", rendered)
        self.assertNotIn('rel="stylesheet"', rendered)
        self.assertNotIn("googleapis.com", rendered)
        self.assertNotIn("cdnjs.cloudflare.com", rendered)


if __name__ == "__main__":
    unittest.main()
