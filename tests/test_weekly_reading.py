"""Scoped Weekly presentation and immutable-source contracts."""

from pathlib import Path
import re
import shutil
import tempfile
import unittest

from bs4 import BeautifulSoup

from scripts.canonical_block import extract_latest_complete_report_block, parse_and_validate_canonical_block
from scripts.markdown_renderer import render_markdown_to_html
from scripts.report_catalog import ReportCatalog
from scripts.report_ingestion import IngestionStatus, ingest_report_content
from scripts.report_runs import load_report_runs


ROOT = Path(__file__).resolve().parents[1]
WEEKLY = "weekly/Weekly_Strategy_2026-10-04"
OTHER_REPORTS = (
    "daily/Global_Daily_Brief_2026-10-04",
    "early-warning/Global_Macro_Early_Warning_2026-10-02_2159_us-jobs-cooling",
    "daily/Global_Daily_Brief_2026-10-05_rerun_1304",
    "early-warning/Global_Macro_Early_Warning_2026-10-05_2300_services-cost-pressure",
)
SCORES = [
    ["ai_fundamental_cycle", "91"], ["memory_cycle", "90"],
    ["energy_inflation", "88"], ["taiwan_leading_cycle", "86"],
    ["rates_shock", "83"], ["labor_market_cooling", "66"],
    ["fed_policy_tightening", "64"], ["semiconductor_relative_weakness", "28"],
]
POLICY = [
    ["FACT", "ISM 54.5、Prices 77.9\n非農+2.9萬、失業率4.2%\nPCE年增3.4%。"],
    ["MARKET EXPECTATION", "10月Fed暫停機率大升、12月仍可能行動。"],
    ["INFERENCE", "短端政策壓力改善、長端能源／財政壓力未改善，不等於全面金融條件放鬆。"],
]
SCENARIOS = [
    ["GREEN", "油價顯著回落、10Y<5%、信用穩定。"],
    ["YELLOW", "長端回落但估值仍高。"],
    ["RED", "能源再升、10Y創高、信用利差擴張且AI財測下修。"],
]


def source(stem=WEEKLY):
    raw = (ROOT / "reports" / f"{stem}.md").read_bytes()
    return parse_and_validate_canonical_block(extract_latest_complete_report_block(raw.decode()))


def render(stem=WEEKLY):
    metadata, body = source(stem)
    return BeautifulSoup(render_markdown_to_html(body, metadata), "html.parser")


def visible_rows(table):
    clone = BeautifulSoup(str(table), "html.parser")
    for icon in clone.select('[aria-hidden="true"]'):
        icon.decompose()
    return [[cell.get_text("\n", strip=True) for cell in row.find_all("td", recursive=False)]
            for row in clone.select("tbody tr")]


def paragraph(soup, heading):
    return soup.find("h2", string=heading).find_next_sibling("p").get_text()


def reconstructed_research(soup):
    """Reconstruct source punctuation from actual visible cells, never hidden text."""
    clone = BeautifulSoup(str(soup), "html.parser")
    for table in clone.select("table[data-weekly-schema]"):
        rows = visible_rows(table)
        schema = table["data-weekly-schema"]
        if schema == "signal-persistence-v1":
            text = "；".join(f"{key} {value}" for key, value in rows) + "。"
        elif schema == "policy-analysis-v1":
            text = "".join(key + "：" + value.replace("\n", "；") for key, value in rows)
        elif schema == "risk-scenarios-v1":
            text = "".join(key + "：" + value for key, value in rows)
        else:
            raise AssertionError(schema)
        replacement = clone.new_tag("p")
        replacement.string = text
        table.parent.replace_with(replacement)
    return re.sub(r"\s+", "", clone.select_one("main").get_text())


class WeeklyReadingTests(unittest.TestCase):
    def test_original_summary_layout_and_complete_chapters_without_directory(self):
        soup = render()
        self.assertIsNone(soup.select_one(".report-toc"))
        self.assertNotIn("章節導覽", soup.body.get_text())
        self.assertIsNone(soup.select_one(".executive-points"))
        summary = soup.find("h2", string="執行策略摘要（EXECUTIVE STRATEGY SUMMARY）").find_next_sibling("ul")
        self.assertEqual(len(summary.find_all("li", recursive=False)), 5)
        self.assertEqual(len(soup.select("main h2")), 24)
        self.assertEqual(soup.find(id="section-台灣股票-action-matrix").get_text(), "台灣股票 Action Matrix")
        self.assertFalse(soup.find_all("script"))

    def test_signal_table_preserves_exact_eight_values_without_scale(self):
        table = render().select_one('[data-weekly-schema="signal-persistence-v1"]')
        self.assertIsNotNone(table)
        self.assertEqual([h.get_text() for h in table.select("th")], ["訊號", "持續性評分"])
        self.assertEqual(visible_rows(table), SCORES)
        self.assertNotIn("/100", table.get_text())

    def test_policy_table_keeps_fact_groups_and_complete_qualifiers(self):
        table = render().select_one('[data-weekly-schema="policy-analysis-v1"]')
        self.assertIsNotNone(table)
        self.assertEqual([h.get_text() for h in table.select("th")], ["類別", "內容"])
        self.assertEqual(visible_rows(table), POLICY)
        self.assertEqual(len(table.select("br")), 2)

    def test_risk_scenarios_have_colored_visible_labels_and_separate_current_state(self):
        soup = render()
        table = soup.select_one('[data-weekly-schema="risk-scenarios-v1"]')
        self.assertIsNotNone(table)
        self.assertEqual([h.get_text() for h in table.select("th")], ["燈號", "觸發條件"])
        self.assertEqual(visible_rows(table), SCENARIOS)
        for label in ("GREEN", "YELLOW", "RED"):
            badge = table.select_one(".risk-" + label.lower())
            self.assertIsNotNone(badge)
            self.assertIn(label, badge.get_text())
        before = BeautifulSoup((ROOT / "reports" / (WEEKLY + ".html")).read_text(), "html.parser")
        old_badge = before.find("h2", string="情境矩陣與風險燈號").find_next_sibling("p").select_one(".risk-orange")
        current = soup.find("h2", string="情境矩陣與風險燈號").find_next_sibling("p")
        self.assertEqual(str(current.select_one(".risk-orange")), str(old_badge))
        self.assertNotIn("ORANGE", table.get_text())

    def test_visible_cells_reconstruct_each_exact_original_paragraph(self):
        soup = render()
        before = BeautifulSoup((ROOT / "reports" / (WEEKLY + ".html")).read_text(), "html.parser")
        scores = visible_rows(soup.select_one('[data-weekly-schema="signal-persistence-v1"]'))
        self.assertEqual("；".join(f"{k} {v}" for k, v in scores) + "。", paragraph(before, "訊號持續性評分"))
        policy = visible_rows(soup.select_one('[data-weekly-schema="policy-analysis-v1"]'))
        self.assertEqual("".join(k + "：" + v.replace("\n", "；") for k, v in policy), paragraph(before, "總經資料與政策深度分析"))
        risk = visible_rows(soup.select_one('[data-weekly-schema="risk-scenarios-v1"]'))
        self.assertEqual(paragraph(soup, "情境矩陣與風險燈號") + "".join(k + "：" + v for k, v in risk), paragraph(before, "情境矩陣與風險燈號"))

    def test_only_three_sections_change_and_original_two_tables_are_preserved(self):
        before = BeautifulSoup((ROOT / "reports" / (WEEKLY + ".html")).read_text(), "html.parser")
        after = render()
        self.assertEqual(len(after.select("table")), 5)
        self.assertEqual(reconstructed_research(before), reconstructed_research(after))
        self.assertEqual([visible_rows(t) for t in before.select("table")], [visible_rows(t) for t in after.select('table:not([data-weekly-schema])')])
        self.assertEqual([(a.get_text(), a.get("href")) for a in before.select("main a")], [(a.get_text(), a.get("href")) for a in after.select("main a")])

    def test_unknown_report_identity_never_receives_local_conversion(self):
        metadata, body = source()
        for change in ({"run_id": "WKS-OTHER"}, {"report_type": "GLOBAL_DAILY_BRIEF"}, {"report_type": "MACRO_TAIWAN_EARLY_WARNING"}):
            with self.subTest(change=change):
                soup = BeautifulSoup(render_markdown_to_html(body, dict(metadata, **change)), "html.parser")
                self.assertFalse(soup.select("[data-weekly-schema]"))
                self.assertIsNone(soup.select_one(".report-toc"))
                self.assertEqual(len(soup.select("table")), 2)

    def test_partial_or_formatted_source_fails_closed_without_consuming_text(self):
        metadata, body = source()
        changes = (
            ("## 訊號持續性評分", "## 訊號持續性評分（其他）", "signal-persistence-v1"),
            ("ai_fundamental_cycle 91；", "", "signal-persistence-v1"),
            ("ai_fundamental_cycle 91", "ai_fundamental_cycle 92", "signal-persistence-v1"),
            ("weakness 28。", "weakness 28；other 12。", "signal-persistence-v1"),
            ("ai_fundamental_cycle 91", "[ai_fundamental_cycle](https://example.com) 91", "signal-persistence-v1"),
            ("ai_fundamental_cycle 91", "**ai_fundamental_cycle** 91", "signal-persistence-v1"),
            ("weakness 28。", "weakness 28。\n\n另有條件。", "signal-persistence-v1"),
            ("MARKET EXPECTATION：", "OTHER EXPECTATION：", "policy-analysis-v1"),
            ("金融條件放鬆。", "金融條件放鬆。另有條件。", "policy-analysis-v1"),
            ("信用利差擴張且AI財測下修。", "信用利差擴張或AI財測下修。", "risk-scenarios-v1"),
        )
        for old, new, schema in changes:
            with self.subTest(schema=schema, new=new):
                changed = body.replace(old, new)
                self.assertNotEqual(changed, body)
                soup = BeautifulSoup(render_markdown_to_html(changed, metadata), "html.parser")
                self.assertIsNone(soup.select_one(f'[data-weekly-schema="{schema}"]'))
                if "https://example.com" in new:
                    self.assertIsNotNone(soup.select_one('a[href="https://example.com"]'))

    def test_other_reports_keep_original_research_tables_and_layout(self):
        for stem in OTHER_REPORTS:
            with self.subTest(report=stem):
                path = ROOT / "reports" / (stem + ".md")
                original_bytes = path.read_bytes()
                before = BeautifulSoup(path.with_suffix(".html").read_text(), "html.parser")
                after = render(stem)
                self.assertEqual(reconstructed_research(before), reconstructed_research(after))
                self.assertEqual([visible_rows(t) for t in before.select("table")], [visible_rows(t) for t in after.select("table")])
                self.assertIsNone(after.select_one(".report-toc"))
                self.assertEqual(len(before.select(".executive-points")), len(after.select(".executive-points")))
                self.assertEqual(original_bytes, path.read_bytes())

    def test_percentage_ranges_are_not_split_without_changing_their_text(self):
        soup = render()
        stock_table = soup.select('table:not([data-weekly-schema])')[1]
        ranges = [row.find_all("td")[4] for row in stock_table.select("tbody tr")]
        self.assertTrue(all("numeric" in cell.get("class", []) for cell in ranges))
        self.assertEqual(ranges[0].get_text(), "-6%～+9%")

    def test_duplicate_headings_keep_unique_stable_deep_links(self):
        body = "## 台灣 / AI\nA\n\n### 股票\nB\n\n## 台灣 / AI\nC"
        first = BeautifulSoup(render_markdown_to_html(body, {}), "html.parser")
        second = BeautifulSoup(render_markdown_to_html(body, {}), "html.parser")
        ids = [h.get("id") for h in first.select("main h2, main h3")]
        self.assertTrue(all(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [h["id"] for h in second.select("main h2, main h3")])

    def test_weekly_rerun_preserves_original_bytes_and_repeat_ingestion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            category = root / "reports/weekly"
            category.mkdir(parents=True)
            (root / "data").mkdir()
            shutil.copyfile(ROOT / "data/report_runs.json", root / "data/report_runs.json")
            originals = {}
            for suffix in (".md", ".html"):
                source_path = ROOT / "reports" / (WEEKLY + suffix)
                target = category / source_path.name
                target.write_bytes(source_path.read_bytes())
                originals[target] = target.read_bytes()
            raw = originals[category / "Weekly_Strategy_2026-10-04.md"]
            result = ingest_report_content(raw, "weekly", root, force=True, allow_fallback=False)
            self.assertEqual(result.status, IngestionStatus.ARCHIVED_CANONICAL)
            self.assertEqual(result.html_path.name, "Weekly_Strategy_2026-10-04_rerun_2045.html")
            self.assertEqual(result.markdown_path.read_bytes(), raw)
            for path, content in originals.items():
                self.assertEqual(path.read_bytes(), content)
            runs = load_report_runs(root / "data/report_runs.json")
            self.assertEqual(ReportCatalog.build_from_scan(root, runs_data=runs).get_latest("weekly").file, result.html_rel)
            self.assertEqual(ingest_report_content(raw, "weekly", root, allow_fallback=False).status, IngestionStatus.SKIPPED_EXISTING)
            self.assertEqual(len(list(category.iterdir())), 4)


if __name__ == "__main__":
    unittest.main()
