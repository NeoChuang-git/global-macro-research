import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts.report_ingestion import (
    IngestionResult,
    IngestionStatus,
    extract_fallback_title,
    ingest_report_content,
    ingest_report_file,
)

SAMPLE_DAILY_BODY = """
# Global Daily Brief

## 1. Executive Intelligence Summary
Overview of today's macro conditions...

## 2. Daily Signal Board
| Sector | Signal |
|---|---|
| Rates | 🔴 Up |

## 3. Top 3 Daily Themes
Theme 1, Theme 2, Theme 3.

## 4. Macro Data & Policy Detail
Data details...

## 5. Cross-Asset Confirmation
Confirmation analysis...

## 6. Causal Chain Audit
Causal link from Fed to Taiwan...

## 7. Global Tech / AI / Semiconductor / Memory / Server Transmission
Transmission into tech...

## 8. Taiwan Economy & Policy
Taiwan macro...

## 9. Taiwan Industry & Equity
Industry detail...

## 10. Market Cycle vs Fundamental Cycle
Cycle divergence...

## 11. Daily Taiwan Equity Action Delta
Actions...

## 12. Scenario Matrix
Scenario A / B / C...

## 13. Risk Lights
- Global 🟠
- Rates 🔴

## 14. Next 24–72h Catalysts
Upcoming catalysts...

## 15. Source Audit
| Claim | Source | URL | Grade |
|---|---|---|---|
| Data | Fed | https://example.com | A |

## 16. Bottom Line
Concluding summary.
"""

SAMPLE_CANONICAL_BLOCK = f"""<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
report_type: GLOBAL_DAILY_BRIEF
run_id: GDB-20260929-0730
generated_at_taipei: 2026-09-29T07:30:00+08:00
coverage_start_taipei: 2026-09-28T06:00:00+08:00
coverage_end_taipei: 2026-09-29T06:00:00+08:00
risk_light: YELLOW
topic: Global Macro Morning Brief
slug: gdb-20260929
title: Global Daily Brief 2026-09-29
format_version: 1
---
{SAMPLE_DAILY_BODY}
<<<REPORT_END>>>"""


class TestReportIngestion(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "data").mkdir(parents=True, exist_ok=True)
        (self.root / "reports").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ingest_canonical_report_success(self):
        res = ingest_report_content(
            content=SAMPLE_CANONICAL_BLOCK,
            category="daily",
            repo_root=self.root,
            source_document_id="doc-daily-123",
        )

        self.assertEqual(res.status, IngestionStatus.ARCHIVED_CANONICAL)
        self.assertTrue(res.is_success)
        self.assertFalse(res.is_skipped)
        self.assertEqual(res.run_id, "GDB-20260929-0730")
        self.assertEqual(res.title, "Global Daily Brief 2026-09-29")
        self.assertEqual(res.category, "daily")
        self.assertIsNotNone(res.markdown_path)
        self.assertIsNotNone(res.html_path)
        self.assertTrue(res.markdown_path.is_file())
        self.assertTrue(res.html_path.is_file())

        # Verify run was recorded in report_runs.json
        runs_file = self.root / "data" / "report_runs.json"
        self.assertTrue(runs_file.is_file())
        data = json.loads(runs_file.read_text(encoding="utf-8"))
        self.assertIn("GDB-20260929-0730", data.get("runs", {}))

    def test_canonical_snapshots_never_overwrite_html_only_legacy_report(self):
        directory = self.root / "reports/daily"
        directory.mkdir()
        legacy = directory / "Global_Daily_Brief_2026-09-29.html"
        legacy.write_bytes(b"legacy html only")
        result = ingest_report_content(SAMPLE_CANONICAL_BLOCK, "daily", self.root, allow_fallback=False)
        self.assertEqual(legacy.read_bytes(), b"legacy html only")
        self.assertNotEqual(result.html_path, legacy)

    def test_same_time_distinct_run_ids_keep_every_snapshot(self):
        snapshots = []
        for i in range(3):
            content = SAMPLE_CANONICAL_BLOCK.replace("GDB-20260929-0730", f"GDB-20260929-0730-{i}")
            result = ingest_report_content(content, "daily", self.root, allow_fallback=False)
            snapshots.append((result, result.markdown_path.read_bytes(), result.html_path.read_bytes()))
        self.assertEqual(len({r.markdown_path for r, _, _ in snapshots}), 3)
        for result, markdown, html in snapshots:
            self.assertEqual(result.markdown_path.read_bytes(), markdown)
            self.assertEqual(result.html_path.read_bytes(), html)

    def test_processed_canonical_run_with_missing_or_corrupt_artifacts_fails(self):
        result = ingest_report_content(SAMPLE_CANONICAL_BLOCK, "daily", self.root, allow_fallback=False)
        markdown, html = result.markdown_path.read_bytes(), result.html_path.read_bytes()
        for artifact, original in ((result.markdown_path, markdown), (result.html_path, html)):
            for damage in ("missing", "corrupt"):
                with self.subTest(artifact=artifact.suffix, damage=damage):
                    if damage == "missing":
                        artifact.unlink()
                    else:
                        artifact.write_bytes(b"changed bytes")
                    failed = ingest_report_content(SAMPLE_CANONICAL_BLOCK, "daily", self.root, allow_fallback=False)
                    self.assertEqual(failed.status, IngestionStatus.FAILED)
                    self.assertIn("artifact", failed.error)
                    artifact.write_bytes(original)

    def test_canonical_render_failure_writes_no_artifacts_or_manifest(self):
        with patch("scripts.report_ingestion.render_markdown_to_html", side_effect=RuntimeError("renderer failed")), \
             self.assertRaisesRegex(RuntimeError, "renderer failed"):
            ingest_report_content(SAMPLE_CANONICAL_BLOCK, "daily", self.root, allow_fallback=False)
        self.assertFalse(any(p.is_file() for p in self.root.rglob("*")))

    def test_processed_run_accepts_identical_raw_folder_block_and_crlf(self):
        result = ingest_report_content(SAMPLE_CANONICAL_BLOCK, "daily", self.root, allow_fallback=False)
        raw = ("Source note\r\n" + SAMPLE_CANONICAL_BLOCK.replace("\n", "\r\n") + "\r\nFooter").encode()
        result.markdown_path.write_bytes(raw)
        repeat = ingest_report_content(SAMPLE_CANONICAL_BLOCK, "daily", self.root, allow_fallback=False)
        self.assertEqual(repeat.status, IngestionStatus.SKIPPED_EXISTING)
        self.assertEqual(result.markdown_path.read_bytes(), raw)

    def test_processed_run_does_not_accept_changed_body_with_same_run_id(self):
        result = ingest_report_content(SAMPLE_CANONICAL_BLOCK, "daily", self.root, allow_fallback=False)
        result.markdown_path.write_text(SAMPLE_CANONICAL_BLOCK.replace("Concluding summary.", "Changed conclusion."))
        repeat = ingest_report_content(SAMPLE_CANONICAL_BLOCK, "daily", self.root, allow_fallback=False)
        self.assertEqual(repeat.status, IngestionStatus.FAILED)
        self.assertIn("checksum mismatch", repeat.error)

    def test_processed_fallback_run_with_missing_html_fails(self):
        result = ingest_report_content("# Weekly Strategy\nDetails", "weekly", self.root, original_filename="weekly.md")
        result.html_path.unlink()
        repeat = ingest_report_content("# Weekly Strategy\nDetails", "weekly", self.root, original_filename="weekly.md")
        self.assertEqual(repeat.status, IngestionStatus.FAILED)
        self.assertIn("missing recorded html artifact", repeat.error)

    def test_ingest_canonical_report_idempotency_and_force(self):
        # First ingestion
        res1 = ingest_report_content(
            content=SAMPLE_CANONICAL_BLOCK,
            category="daily",
            repo_root=self.root,
        )
        self.assertEqual(res1.status, IngestionStatus.ARCHIVED_CANONICAL)

        # Second ingestion without force -> SKIPPED_EXISTING
        res2 = ingest_report_content(
            content=SAMPLE_CANONICAL_BLOCK,
            category="daily",
            repo_root=self.root,
            force=False,
        )
        self.assertEqual(res2.status, IngestionStatus.SKIPPED_EXISTING)
        self.assertTrue(res2.is_skipped)
        self.assertFalse(res2.is_success)

        # Third ingestion with force=True -> re-archives
        res3 = ingest_report_content(
            content=SAMPLE_CANONICAL_BLOCK,
            category="daily",
            repo_root=self.root,
            force=True,
        )
        self.assertEqual(res3.status, IngestionStatus.ARCHIVED_CANONICAL)
        self.assertTrue(res3.is_success)

    def test_ingest_fallback_markdown_with_frontmatter(self):
        plain_md = """---
title: Weekly Macro Investment Strategy
---
# Ignored Header
Weekly review of bond markets and foreign exchange.
"""
        res = ingest_report_content(
            content=plain_md,
            category="weekly",
            repo_root=self.root,
            original_filename="Weekly_Strategy_2026-09-27.md",
        )

        self.assertEqual(res.status, IngestionStatus.ARCHIVED_FALLBACK)
        self.assertTrue(res.is_success)
        self.assertEqual(res.title, "Weekly Macro Investment Strategy")
        self.assertEqual(res.run_id, "WEEKLY-Weekly_Strategy_2026-09-27")
        self.assertTrue(res.html_path.is_file())

        runs_file = self.root / "data" / "report_runs.json"
        data = json.loads(runs_file.read_text(encoding="utf-8"))
        self.assertIn("WEEKLY-Weekly_Strategy_2026-09-27", data.get("runs", {}))

    def test_ingest_fallback_markdown_with_h1(self):
        plain_md = """
# Taiwan Tech Supply Chain Warning

Supply chain lead times extended by 3 weeks.
"""
        res = ingest_report_content(
            content=plain_md,
            category="early-warning",
            repo_root=self.root,
            original_filename="Risk_2026-09-15.md",
        )

        self.assertEqual(res.status, IngestionStatus.ARCHIVED_FALLBACK)
        self.assertEqual(res.title, "Taiwan Tech Supply Chain Warning")
        self.assertEqual(res.run_id, "EARLY-WARNING-Risk_2026-09-15")

    def test_ingest_corrupted_canonical_block_falls_back_gracefully(self):
        # Missing required sections according to canonical block spec
        bad_canonical = """<<<REPORT_BEGIN>>>
---
report_type: GLOBAL_DAILY_BRIEF
run_id: GDB-CORRUPT-001
title: Incomplete Daily Brief
---
## Only One Section Here
Missing Executive Summary and Risk Lights.
<<<REPORT_END>>>"""

        res = ingest_report_content(
            content=bad_canonical,
            category="daily",
            repo_root=self.root,
            original_filename="Global_Daily_Brief_2026-09-28.md",
        )

        # Should fall back to ARCHIVED_FALLBACK without crashing
        self.assertEqual(res.status, IngestionStatus.ARCHIVED_FALLBACK)
        self.assertTrue(res.is_success)
        self.assertTrue(res.html_path.is_file())

    def test_ingest_report_file(self):
        weekly_dir = self.root / "reports" / "weekly"
        weekly_dir.mkdir(parents=True, exist_ok=True)
        local_file = weekly_dir / "Weekly_Strategy_2026-09-28.md"
        local_file.write_text("# Weekly Strategy Update\nDetails here.", encoding="utf-8")

        res = ingest_report_file(
            file_path=local_file,
            category="weekly",
            repo_root=self.root,
        )

        self.assertEqual(res.status, IngestionStatus.ARCHIVED_FALLBACK)
        self.assertTrue(res.is_success)
        self.assertEqual(res.title, "Weekly Strategy Update")
        self.assertTrue((weekly_dir / "Weekly_Strategy_2026-09-28.html").is_file())

    def test_extract_fallback_title_heuristics(self):
        self.assertEqual(extract_fallback_title("title: Hello World\n# Ignored"), "Hello World")
        self.assertEqual(extract_fallback_title("# Main Header\nBody"), "Main Header")
        self.assertEqual(extract_fallback_title("Just body", default_name="Global_Daily_Brief_2026.md"), "Global Daily Brief 2026")

    def test_strict_canonical_mode_without_fallback(self):
        # When allow_fallback=False and no block is found
        res_no_block = ingest_report_content(
            content="Plain text without canonical blocks",
            category="daily",
            repo_root=self.root,
            allow_fallback=False,
        )
        self.assertEqual(res_no_block.status, IngestionStatus.NO_CANONICAL_BLOCK)
        self.assertFalse(res_no_block.is_success)

        # When allow_fallback=False and block is invalid
        bad_canonical = """<<<REPORT_BEGIN>>>
---
report_type: GLOBAL_DAILY_BRIEF
run_id: GDB-BAD
---
Invalid body without sections
<<<REPORT_END>>>"""
        res_bad_block = ingest_report_content(
            content=bad_canonical,
            category="daily",
            repo_root=self.root,
            allow_fallback=False,
        )
        self.assertEqual(res_bad_block.status, IngestionStatus.CANONICAL_BLOCK_INVALID)
        self.assertFalse(res_bad_block.is_success)
        self.assertIsNotNone(res_bad_block.error)

    def test_ingest_escaped_canonical_document(self):
        escaped_doc = f"""
\\<\\<\\<REPORT\\_BEGIN\\>\\>\\>
\\---
research\\_status: COMPLETE
report\\_type: GLOBAL\\_DAILY\\_BRIEF
run\\_id: GDB-20260929-ESCAPED
generated\\_at\\_taipei: 2026-09-29T07:30:00+08:00
coverage\\_start\\_taipei: 2026-09-28T07:30:00+08:00
coverage\\_end\\_taipei: 2026-09-29T07:30:00+08:00
title: Global Daily Brief Escaped Ingestion Test
format\\_version: 1
risk\\_light: GREEN
\\---
{SAMPLE_DAILY_BODY}
\\<\\<\\<REPORT\\_END\\>\\>\\>
"""
        res = ingest_report_content(
            content=escaped_doc,
            category="daily",
            repo_root=self.root,
            allow_fallback=False,
        )
        self.assertEqual(res.status, IngestionStatus.ARCHIVED_CANONICAL)
        self.assertTrue(res.is_success)
        self.assertEqual(res.run_id, "GDB-20260929-ESCAPED")
        self.assertIsNotNone(res.html_path)
        html_text = res.html_path.read_text(encoding="utf-8")
        self.assertIn("<h2", html_text)
        self.assertNotIn("\\#\\#", html_text)


if __name__ == "__main__":
    unittest.main()
