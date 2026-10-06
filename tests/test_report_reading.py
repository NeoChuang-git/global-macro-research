"""Reading behavior and preservation contracts for the shared report renderer."""

from pathlib import Path
import re
import shutil
import tempfile
import unittest

from bs4 import BeautifulSoup

from scripts.canonical_block import (
    extract_latest_complete_report_block,
    parse_and_validate_canonical_block,
)
from scripts.markdown_renderer import render_markdown_to_html
from scripts.report_catalog import ReportCatalog
from scripts.report_ingestion import IngestionStatus, ingest_report_content
from scripts.report_runs import load_report_runs


ROOT = Path(__file__).resolve().parents[1]
REPORTS = (
    "weekly/Weekly_Strategy_2026-10-04",
    "daily/Global_Daily_Brief_2026-10-04",
    "early-warning/Global_Macro_Early_Warning_2026-10-02_2159_us-jobs-cooling",
    "daily/Global_Daily_Brief_2026-10-05_rerun_1304",
    "early-warning/Global_Macro_Early_Warning_2026-10-05_2300_services-cost-pressure",
)


def render_snapshot(stem):
    source = (ROOT / "reports" / f"{stem}.md").read_bytes()
    block = extract_latest_complete_report_block(source.decode("utf-8"))
    metadata, body = parse_and_validate_canonical_block(block)
    return BeautifulSoup(render_markdown_to_html(body, metadata), "html.parser")


def research_text(soup):
    content = soup.select_one(".report-content")
    for hint in content.select(".table-scroll-hint"):
        hint.decompose()
    return re.sub(r"\s+", "", content.get_text())


class ReportReadingTests(unittest.TestCase):
    def test_weekly_summary_keeps_all_five_bullets(self):
        soup = render_snapshot(REPORTS[0])
        summary = soup.select_one("ul.executive-points")
        self.assertIsNotNone(summary)
        self.assertEqual(len(summary.find_all("li", recursive=False)), 5)

    def test_directory_reaches_every_chapter_without_scripts(self):
        soup = render_snapshot(REPORTS[0])
        directory = soup.select_one("details.report-toc")
        self.assertIsNotNone(directory)
        self.assertIsNotNone(directory.find("summary"))
        headings = soup.select("main h2")
        links = directory.select("nav a")
        self.assertEqual(len(headings), 24)
        self.assertEqual(len(links), len(headings))
        for heading, link in zip(headings, links):
            self.assertEqual(link["href"], "#" + heading["id"])
            self.assertEqual(link.get_text(), heading.get_text())
            self.assertEqual(heading["tabindex"], "-1")
        self.assertFalse(soup.find_all("script"))

    def test_duplicate_bilingual_headings_have_stable_unique_targets(self):
        md = "## 台灣 / AI\nA\n\n### 股票\nB\n\n## 台灣 / AI\nC\n\n## !!!\nD"
        first = BeautifulSoup(render_markdown_to_html(md, {}), "html.parser")
        second = BeautifulSoup(render_markdown_to_html(md, {}), "html.parser")
        ids = [h.get("id") for h in first.select("main h2, main h3")]
        self.assertTrue(all(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [h["id"] for h in second.select("main h2, main h3")])

    def test_tables_are_named_focusable_regions_with_visible_instructions(self):
        soup = render_snapshot(REPORTS[0])
        regions = soup.select(".table-scroll")
        self.assertEqual(len(regions), 2)
        for region in regions:
            self.assertEqual(region.get("tabindex"), "0")
            self.assertEqual(region.get("role"), "region")
            self.assertTrue(region.get("aria-label"))
            hint = soup.find(id=region.get("aria-describedby"))
            self.assertIsNotNone(hint)
            self.assertIn("方向鍵", hint.get_text())
            self.assertTrue(all(th.get("scope") == "col" for th in region.select("thead th")))

    def test_shared_reports_preserve_research_and_canonical_bytes(self):
        for stem in REPORTS:
            with self.subTest(report=stem):
                source = ROOT / "reports" / f"{stem}.md"
                before_bytes = source.read_bytes()
                before = BeautifulSoup((ROOT / "reports" / f"{stem}.html").read_text(), "html.parser")
                after = render_snapshot(stem)
                self.assertEqual(research_text(before), research_text(after))
                self.assertEqual(len(before.select("table")), len(after.select("table")))
                self.assertEqual(before_bytes, source.read_bytes())
                self.assertTrue(after.select(".report-toc nav a"))

    def test_reports_without_chapters_have_no_empty_directory(self):
        soup = BeautifulSoup(render_markdown_to_html("Only a paragraph.", {}), "html.parser")
        self.assertIsNone(soup.select_one(".report-toc"))

    def test_weekly_presentation_rerun_preserves_original_and_remains_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            category = root / "reports" / "weekly"
            category.mkdir(parents=True)
            (root / "data").mkdir()
            shutil.copyfile(ROOT / "data/report_runs.json", root / "data/report_runs.json")
            stem = "Weekly_Strategy_2026-10-04"
            original = {}
            for suffix in (".md", ".html"):
                path = category / (stem + suffix)
                shutil.copyfile(ROOT / "reports/weekly" / path.name, path)
                original[path] = path.read_bytes()
            source = original[category / (stem + ".md")]
            result = ingest_report_content(source, "weekly", root, force=True, allow_fallback=False)
            self.assertEqual(result.status, IngestionStatus.ARCHIVED_CANONICAL)
            self.assertEqual(result.html_path.name, stem + "_rerun_2045.html")
            self.assertEqual(result.markdown_path.read_bytes(), source)
            for path, content in original.items():
                self.assertEqual(path.read_bytes(), content)
            old = BeautifulSoup(original[category / (stem + ".html")], "html.parser")
            new = BeautifulSoup(result.html_path.read_text(), "html.parser")
            self.assertEqual(research_text(old), research_text(new))
            self.assertEqual(
                [(a.get_text(), a.get("href")) for a in old.select("main a")],
                [(a.get_text(), a.get("href")) for a in new.select("main a")],
            )
            self.assertEqual(
                [cell.get_text() for cell in old.select("th, td")],
                [cell.get_text() for cell in new.select("th, td")],
            )
            runs = load_report_runs(root / "data/report_runs.json")
            catalog = ReportCatalog.build_from_scan(root, runs_data=runs)
            self.assertEqual(catalog.get_latest("weekly").file, result.html_rel)
            repeat = ingest_report_content(source, "weekly", root, allow_fallback=False)
            self.assertEqual(repeat.status, IngestionStatus.SKIPPED_EXISTING)
            self.assertEqual(len(list(category.iterdir())), 4)

    def test_signed_percentage_ranges_are_kept_as_numeric_cells(self):
        soup = render_snapshot(REPORTS[0])
        stock_table = soup.select("table")[1]
        ranges = [row.find_all("td")[4] for row in stock_table.select("tbody tr")]
        self.assertTrue(all("numeric" in cell.get("class", []) for cell in ranges))
        self.assertEqual(ranges[0].get_text(), "-6%～+9%")


if __name__ == "__main__":
    unittest.main()
