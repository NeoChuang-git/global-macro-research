import json
import tempfile
import unittest
from pathlib import Path

from scripts.report_catalog import (
    CATEGORIES,
    CatalogEntry,
    CatalogError,
    ReportCatalog,
    classify_drive_file,
    date_from_modified_time,
    date_from_name,
    display_title,
    extract_report_title,
    is_generic_title,
    is_safe_parent_and_path,
)


class TestReportCatalog(unittest.TestCase):
    def test_catalog_entry_to_dict_canonical(self):
        entry = CatalogEntry(
            category="daily",
            date="2026-09-03",
            file="reports/daily/Global_Daily_Brief_2026-09-03.html",
            title="Global Daily Brief: Taiwan Tech Momentum",
            sha256="abc123sha",
            modified_time="2026-09-03T08:00:00+08:00",
            run_id="GDB-20260903-0730",
            report_type="daily",
            source_kind="google_doc_markdown",
            source_document_id="doc-123",
            generated_at_taipei="2026-09-03 08:00:00",
            coverage_start_taipei="2026-09-02 07:00",
            coverage_end_taipei="2026-09-03 07:00",
            risk_light="yellow",
            topic="Macro & Tech",
            slug="global-daily-brief-2026-09-03",
            markdown_path="reports/daily/Global_Daily_Brief_2026-09-03.md",
            markdown_sha256="md123sha",
            html_path="reports/daily/Global_Daily_Brief_2026-09-03.html",
        )
        self.assertTrue(entry.is_canonical)
        data = entry.to_dict()
        self.assertEqual(data["category"], "daily")
        self.assertEqual(data["run_id"], "GDB-20260903-0730")
        self.assertEqual(data["title"], "Global Daily Brief: Taiwan Tech Momentum")
        self.assertEqual(data["risk_light"], "yellow")
        self.assertEqual(data["html_path"], "reports/daily/Global_Daily_Brief_2026-09-03.html")
        self.assertIn("coverage_start_taipei", data)

    def test_catalog_entry_to_dict_legacy(self):
        entry = CatalogEntry(
            category="weekly",
            date="2026-08-30",
            file="reports/weekly/Legacy_Weekly_2026-08-30.html",
            title="Weekly Strategy Outlook",
            sha256="def456sha",
            modified_time="2026-08-30T10:00:00+08:00",
        )
        self.assertFalse(entry.is_canonical)
        data = entry.to_dict()
        self.assertEqual(data["category"], "weekly")
        self.assertEqual(data["date"], "2026-08-30")
        self.assertEqual(data["file"], "reports/weekly/Legacy_Weekly_2026-08-30.html")
        self.assertEqual(data["title"], "Weekly Strategy Outlook")
        self.assertEqual(data["sha256"], "def456sha")
        self.assertNotIn("run_id", data)
        self.assertNotIn("markdown_path", data)

    def test_extract_report_title_precedence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)
            html_file = tmproot / "report.html"
            md_file = tmproot / "report.md"

            # 1. HTML only, title tag
            html_file.write_text("<html><head><title>HTML Title · N/A</title></head><body>Content</body></html>", encoding="utf-8")
            self.assertEqual(extract_report_title(html_file), "HTML Title")

            # 2. HTML only, h1 tag takes precedence over title tag
            html_file.write_text("<html><head><title>Title Tag</title></head><body><h1>H1 Header Title</h1></body></html>", encoding="utf-8")
            self.assertEqual(extract_report_title(html_file), "H1 Header Title")

            # 3. Companion MD with H1 takes precedence over HTML
            md_file.write_text("# Markdown H1 Title\n\nBody...", encoding="utf-8")
            self.assertEqual(extract_report_title(html_file), "Markdown H1 Title")

            # 4. Companion MD with frontmatter title takes highest precedence
            md_file.write_text('---\ntitle: "Frontmatter Title"\n---\n# Markdown H1\n', encoding="utf-8")
            self.assertEqual(extract_report_title(html_file), "Frontmatter Title")

    def test_date_and_classification_helpers(self):
        self.assertEqual(date_from_name("Global_Daily_Brief_2026-09-03.html"), "2026-09-03")
        self.assertEqual(date_from_name("Report_20260903.html"), "2026-09-03")
        self.assertIsNone(date_from_name("invalid_date_20269999.html"))
        self.assertIsNone(date_from_name("no_date.html"))

        self.assertEqual(date_from_modified_time("2026-09-03T12:00:00+08:00"), "2026-09-03")
        self.assertIsNone(date_from_modified_time(None))
        self.assertIsNone(date_from_modified_time("invalid"))

        classified = classify_drive_file("daily", "Global_Daily_Brief_2026-09-03.html", "2026-09-03T08:00:00")
        self.assertEqual(classified["category"], "daily")
        self.assertEqual(classified["date"], "2026-09-03")
        self.assertEqual(classified["title"], "Global Daily Brief")

        self.assertTrue(is_generic_title("global daily brief"))
        self.assertTrue(is_generic_title("Weekly Strategy"))
        self.assertFalse(is_generic_title("Semiconductor Supercycle Strategy"))

    def test_is_safe_parent_and_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)
            valid_path = tmproot / "reports" / "daily" / "2026-09-03.html"
            valid_path.parent.mkdir(parents=True, exist_ok=True)
            valid_path.write_text("content", encoding="utf-8")
            self.assertTrue(is_safe_parent_and_path(tmproot, "daily", valid_path))

            # Outside category
            wrong_cat_path = tmproot / "reports" / "weekly" / "2026-09-03.html"
            wrong_cat_path.parent.mkdir(parents=True, exist_ok=True)
            wrong_cat_path.write_text("content", encoding="utf-8")
            self.assertFalse(is_safe_parent_and_path(tmproot, "daily", wrong_cat_path))

            # Symlink rejection
            symlink_path = tmproot / "reports" / "daily" / "symlink.html"
            symlink_path.symlink_to(valid_path)
            self.assertFalse(is_safe_parent_and_path(tmproot, "daily", symlink_path))

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)
            reports_dir = tmproot / "reports" / "daily"
            reports_dir.mkdir(parents=True, exist_ok=True)
            report_file = reports_dir / "Global_Daily_Brief_2026-09-03.html"
            report_file.write_text("<h1>Daily Brief: Rates Focus</h1>", encoding="utf-8")

            catalog = ReportCatalog.build_from_scan(tmproot)
            self.assertEqual(len(catalog.reports), 1)
            self.assertEqual(catalog.reports[0].title, "Daily Brief: Rates Focus")

            # First save creates file and returns True
            changed = catalog.save(tmproot)
            self.assertTrue(changed)
            index_path = tmproot / "data" / "reports.json"
            self.assertTrue(index_path.is_file())

            # Second save without changes returns False
            changed_again = catalog.save(tmproot)
            self.assertFalse(changed_again)

            # Load from disk
            loaded = ReportCatalog.load_from_disk(tmproot)
            self.assertEqual(len(loaded.reports), 1)
            self.assertEqual(loaded.reports[0].file, "reports/daily/Global_Daily_Brief_2026-09-03.html")
            self.assertEqual(loaded.reports[0].title, "Daily Brief: Rates Focus")
            latest_daily = loaded.get_latest("daily")
            self.assertIsNotNone(latest_daily)
            self.assertEqual(latest_daily.date, "2026-09-03")

    def test_load_from_disk_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)
            # 1. Missing file
            with self.assertRaises(CatalogError):
                ReportCatalog.load_from_disk(tmproot)

            # 2. Corrupt JSON
            index_path = tmproot / "data" / "reports.json"
            index_path.parent.mkdir(parents=True, exist_ok=True)
            index_path.write_text("INVALID JSON", encoding="utf-8")
            with self.assertRaises(CatalogError):
                ReportCatalog.load_from_disk(tmproot)

            # 3. Invalid schema version
            index_path.write_text('{"schema_version": 99, "reports": []}', encoding="utf-8")
            with self.assertRaises(CatalogError):
                ReportCatalog.load_from_disk(tmproot)

            # 4. Invalid latest structure
            index_path.write_text('{"schema_version": 1, "reports": [], "latest": "not-a-dict"}', encoding="utf-8")
            with self.assertRaises(CatalogError):
                ReportCatalog.load_from_disk(tmproot)

            # 5. Invalid report entry (not a dict or missing fields)
            index_path.write_text('{"schema_version": 1, "reports": ["not-a-dict"], "latest": {"early-warning": null, "daily": null, "weekly": null}}', encoding="utf-8")
            with self.assertRaises(CatalogError):
                ReportCatalog.load_from_disk(tmproot)

            index_path.write_text('{"schema_version": 1, "reports": [{"category": "daily"}], "latest": {"early-warning": null, "daily": null, "weekly": null}}', encoding="utf-8")
            with self.assertRaises(CatalogError):
                ReportCatalog.load_from_disk(tmproot)

    def test_sorting_invariants(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)
            for cat in CATEGORIES:
                (tmproot / "reports" / cat).mkdir(parents=True, exist_ok=True)

            # Create reports across categories and dates
            (tmproot / "reports" / "daily" / "2026-09-01.html").write_text("<h1>Daily 1</h1>", encoding="utf-8")
            (tmproot / "reports" / "daily" / "2026-09-03.html").write_text("<h1>Daily 3</h1>", encoding="utf-8")
            (tmproot / "reports" / "early-warning" / "2026-09-03.html").write_text("<h1>EW 3</h1>", encoding="utf-8")
            (tmproot / "reports" / "weekly" / "2026-09-03.html").write_text("<h1>Weekly 3</h1>", encoding="utf-8")

            catalog = ReportCatalog.build_from_scan(tmproot)
            reports = catalog.reports
            # Date desc: 2026-09-03 before 2026-09-01
            # For same date 2026-09-03: category order is early-warning, daily, weekly
            self.assertEqual(reports[0].category, "early-warning")
            self.assertEqual(reports[0].date, "2026-09-03")
            self.assertEqual(reports[1].category, "daily")
            self.assertEqual(reports[1].date, "2026-09-03")
            self.assertEqual(reports[2].category, "weekly")
            self.assertEqual(reports[2].date, "2026-09-03")
            self.assertEqual(reports[3].category, "daily")
            self.assertEqual(reports[3].date, "2026-09-01")

    def test_query_methods(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmproot = Path(tmpdir)
            for cat in ("daily", "weekly"):
                (tmproot / "reports" / cat).mkdir(parents=True, exist_ok=True)
            (tmproot / "reports" / "daily" / "2026-09-03.html").write_text("<h1>Daily</h1>", encoding="utf-8")
            (tmproot / "reports" / "weekly" / "2026-09-01.html").write_text("<h1>Weekly</h1>", encoding="utf-8")

            catalog = ReportCatalog.build_from_scan(tmproot)
            self.assertEqual(len(catalog.get_reports()), 2)
            self.assertEqual(len(catalog.get_reports("daily")), 1)
            self.assertEqual(len(catalog.get_reports("weekly")), 1)
            self.assertEqual(len(catalog.get_reports("early-warning")), 0)

            self.assertIsNotNone(catalog.get_latest("daily"))
            self.assertIsNotNone(catalog.get_latest("weekly"))
            self.assertIsNone(catalog.get_latest("early-warning"))

            entry = catalog.get_entry_by_file("reports/daily/2026-09-03.html")
            self.assertIsNotNone(entry)
            self.assertEqual(entry.category, "daily")
            self.assertIsNone(catalog.get_entry_by_file("nonexistent.html"))


if __name__ == "__main__":
    unittest.main()
