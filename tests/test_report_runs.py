#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from scripts.report_runs import (
    ReportRunsError,
    get_run_record,
    is_run_id_processed,
    load_report_runs,
    record_report_run,
)


class ReportRunsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.runs_file = self.root / "data" / "report_runs.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_loads_empty_when_file_not_found(self):
        data = load_report_runs(self.runs_file)
        self.assertEqual(data, {"schema_version": 1, "runs": {}})
        self.assertFalse(is_run_id_processed(data, "RUN-1"))

    def test_same_run_id_is_not_archived_twice(self):
        record = {
            "run_id": "GDB-20260903-0730",
            "report_type": "GLOBAL_DAILY_BRIEF",
            "generated_at_taipei": "2026-09-03T07:30:00+08:00",
            "source_document_id": "doc-1",
            "markdown_sha256": "abc123",
            "markdown_path": "reports/daily/Global_Daily_Brief_2026-09-03.md",
            "html_path": "reports/daily/Global_Daily_Brief_2026-09-03.html",
        }
        record_report_run(self.runs_file, record)

        data = load_report_runs(self.runs_file)
        self.assertTrue(is_run_id_processed(data, "GDB-20260903-0730"))
        self.assertEqual(get_run_record(data, "GDB-20260903-0730")["markdown_sha256"], "abc123")

    def test_new_prepended_run_id_creates_new_snapshot(self):
        rec1 = {
            "run_id": "RUN-A",
            "report_type": "GLOBAL_DAILY_BRIEF",
            "markdown_sha256": "hash_a",
        }
        rec2 = {
            "run_id": "RUN-B",
            "report_type": "GLOBAL_DAILY_BRIEF",
            "markdown_sha256": "hash_b",
        }
        record_report_run(self.runs_file, rec1)
        record_report_run(self.runs_file, rec2)

        data = load_report_runs(self.runs_file)
        self.assertTrue(is_run_id_processed(data, "RUN-A"))
        self.assertTrue(is_run_id_processed(data, "RUN-B"))
        self.assertEqual(len(data["runs"]), 2)


if __name__ == "__main__":
    unittest.main()
