import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_site import BuildError, build_site


class BuildSiteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        for path in (
            "assets/css/app.css",
            "assets/favicon.svg",
            "assets/js/app.js",
            "assets/js/archive.js",
            "assets/js/report.js",
            "index.html",
            "archive.html",
            "report.html",
            ".nojekyll",
        ):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(path, encoding="utf-8")
        (self.root / "data").mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_index(self, reports):
        (self.root / "data" / "reports.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "reports": reports,
                    "latest": {
                        "early-warning": None,
                        "daily": None,
                        "weekly": None,
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_builds_minimal_site_and_copies_indexed_reports(self):
        report_path = self.root / "reports" / "daily" / "Daily_2026-08-28.html"
        report_path.parent.mkdir(parents=True)
        report_path.write_text("<html>report</html>", encoding="utf-8")
        self._write_index(
            [
                {
                    "category": "daily",
                    "title": "Daily",
                    "date": "2026-08-28",
                    "file": "reports/daily/Daily_2026-08-28.html",
                    "sha256": hashlib.sha256(b"<html>report</html>").hexdigest(),
                }
            ]
        )

        output = self.root / "_site"
        build_site(self.root, output)

        self.assertTrue((output / "index.html").is_file())
        self.assertTrue((output / "assets" / "js" / "app.js").is_file())
        self.assertEqual((output / "reports" / "daily" / report_path.name).read_text(), "<html>report</html>")
        self.assertFalse((output / "scripts").exists())

    def test_rejects_missing_or_escaping_report_reference(self):
        self._write_index(
            [
                {
                    "category": "weekly",
                    "title": "Missing",
                    "date": "2026-08-28",
                    "file": "reports/weekly/missing.html",
                    "sha256": "0" * 64,
                }
            ]
        )
        with self.assertRaisesRegex(BuildError, "missing"):
            build_site(self.root, self.root / "_site")

        self._write_index(
            [
                {
                    "category": "weekly",
                    "title": "Escape",
                    "date": "2026-08-28",
                    "file": "../secret.html",
                    "sha256": "0" * 64,
                }
            ]
        )
        with self.assertRaisesRegex(BuildError, "unsafe"):
            build_site(self.root, self.root / "_site")

    def test_rejects_report_content_that_does_not_match_index_checksum(self):
        report_path = self.root / "reports" / "weekly" / "Weekly_2026-08-28.html"
        report_path.parent.mkdir(parents=True)
        report_path.write_text("<html>changed</html>", encoding="utf-8")
        self._write_index(
            [
                {
                    "category": "weekly",
                    "title": "Weekly",
                    "date": "2026-08-28",
                    "file": "reports/weekly/Weekly_2026-08-28.html",
                    "sha256": "0" * 64,
                }
            ]
        )

        with self.assertRaisesRegex(BuildError, "checksum mismatch"):
            build_site(self.root, self.root / "_site")

    def test_rejects_parent_symlink_in_build_site(self):
        outside = self.root.parent / "outside_site"
        outside.mkdir(parents=True, exist_ok=True)
        (outside / "Daily_2026-08-28.html").write_text("<html>outside</html>", encoding="utf-8")

        (self.root / "reports").mkdir(parents=True, exist_ok=True)
        (self.root / "reports" / "daily").symlink_to(outside)

        self._write_index(
            [
                {
                    "category": "daily",
                    "title": "Daily",
                    "date": "2026-08-28",
                    "file": "reports/daily/Daily_2026-08-28.html",
                    "sha256": hashlib.sha256(b"<html>outside</html>").hexdigest(),
                }
            ]
        )

        with self.assertRaisesRegex(BuildError, "unsafe"):
            build_site(self.root, self.root / "_site")

    def test_report_reader_html_strictly_sandboxed_without_escape(self):
        report_html_path = Path(__file__).resolve().parents[1] / "report.html"
        content = report_html_path.read_text(encoding="utf-8")

        self.assertNotIn("open-original", content)
        self.assertNotIn("allow-popups-to-escape-sandbox", content)
        self.assertIn('sandbox=""', content)


if __name__ == "__main__":
    unittest.main()
