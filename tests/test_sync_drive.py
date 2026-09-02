import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.sync_drive import (
    CATEGORIES,
    SyncError,
    build_reports_index,
    classify_drive_file,
    resolve_doc_sources,
    resolve_folder_ids,
    sync_native_google_docs,
    sync_reports,
)


def md5(content):
    return hashlib.md5(content).hexdigest()


def sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


class FakeRequest:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def execute(self):
        if self.error:
            raise self.error
        return self.value


class FakeFiles:
    def __init__(self, folders, contents, docs=None, list_error=None):
        self.folders = folders
        self.contents = contents
        self.docs = docs or {}
        self.list_error = list_error
        self.downloads = []
        self.doc_exports = []
        self.write_calls = []

    def list(self, **kwargs):
        if self.list_error:
            return FakeRequest(error=self.list_error)

        query = kwargs["q"]
        folder_id = next(
            folder_id for folder_id in self.folders if f"'{folder_id}' in parents" in query
        )
        return FakeRequest({"files": self.folders[folder_id]})

    def get_media(self, fileId, **kwargs):
        self.downloads.append(fileId)
        value = self.contents[fileId]
        if isinstance(value, Exception):
            return FakeRequest(error=value)
        return FakeRequest(value=value)

    def export_media(self, fileId, mimeType="text/plain", **kwargs):
        self.doc_exports.append((fileId, mimeType))
        if fileId not in self.docs:
            return FakeRequest(error=RuntimeError(f"file {fileId} not found"))
        value = self.docs[fileId]
        if isinstance(value, Exception):
            return FakeRequest(error=value)
        if isinstance(value, str):
            value = value.encode("utf-8")
        return FakeRequest(value=value)

    def create(self, **kwargs):
        self.write_calls.append(("create", kwargs))
        return FakeRequest({"id": "created"})

    def update(self, **kwargs):
        self.write_calls.append(("update", kwargs))
        return FakeRequest({"id": "updated"})


class FakeDrive:
    def __init__(self, folders, contents, docs=None, list_error=None):
        self.files_api = FakeFiles(folders, contents, docs, list_error)

    def files(self):
        return self.files_api


def drive_file(file_id, name, content, modified="2026-08-28T01:02:03Z"):
    return {
        "id": file_id,
        "name": name,
        "modifiedTime": modified,
        "md5Checksum": md5(content),
        "size": str(len(content)),
    }


def make_sample_doc(run_id="GDB-20260903-0730", title="Global Daily Brief"):
    return f"""<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
report_type: GLOBAL_DAILY_BRIEF
run_id: {run_id}
generated_at_taipei: 2026-09-03T07:30:00+08:00
coverage_start_taipei: 2026-09-02T07:30:00+08:00
coverage_end_taipei: 2026-09-03T07:30:00+08:00
title: {title}
format_version: 1
risk_light: YELLOW
slug: global_daily_brief
---
# {title}

## 1. Executive Intelligence Summary
Overview of today's macro conditions...

## 2. Daily Signal Board
| 指標 | 方向 | 燈號 |
|---|:---:|:---:|
| 10Y Yield | ↑ | 🔴 |

## 3. Top 3 Daily Themes
Theme 1, Theme 2, Theme 3.

## 4. Macro Data & Policy Detail
Data details...

## 5. Cross-Asset Confirmation
Confirmation analysis...

## 6. Causal Chain Audit
Causal link...

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
<<<REPORT_END>>>
"""


class SyncDriveTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.folder_ids = {category: f"folder-{category}" for category in CATEGORIES}
        self.folders = {folder_id: [] for folder_id in self.folder_ids.values()}
        self.doc_sources = {
            "GLOBAL_DAILY_BRIEF": {
                "document_id": "doc-daily-1",
                "category": "daily",
                "report_type": "GLOBAL_DAILY_BRIEF",
            },
            "MACRO_TAIWAN_EARLY_WARNING": {
                "document_id": "doc-ew-1",
                "category": "early-warning",
                "report_type": "MACRO_TAIWAN_EARLY_WARNING",
            },
            "WEEKLY_STRATEGY": {
                "document_id": "doc-weekly-1",
                "category": "weekly",
                "report_type": "WEEKLY_STRATEGY",
            },
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def _service(self, contents=None, docs=None, list_error=None):
        return FakeDrive(self.folders, contents or {}, docs or {}, list_error)

    def test_classifies_html_filename_and_extracts_date_without_trusting_paths(self):
        report = classify_drive_file(
            "early-warning",
            "Global_Macro_Early_Warning_2026-08-28.html",
            "2026-08-29T03:04:05Z",
        )

        self.assertEqual(report["category"], "early-warning")
        self.assertEqual(report["date"], "2026-08-28")
        self.assertEqual(report["title"], "Global Macro Early Warning")
        self.assertIsNone(classify_drive_file("daily", "notes.pdf", "2026-08-29T00:00:00Z"))

        with self.assertRaises(SyncError):
            classify_drive_file("weekly", "../escape.html", "2026-08-29T00:00:00Z")

    def test_repeated_sync_is_idempotent_and_does_not_download_unchanged_file(self):
        content = b"<html><title>Daily</title></html>"
        remote = drive_file("one", "Global_Daily_Brief_2026-08-28.html", content)
        self.folders[self.folder_ids["daily"]] = [remote]
        service = self._service({"one": content})

        first = sync_reports(service, self.root, self.folder_ids, enable_native_docs=False)
        second = sync_reports(service, self.root, self.folder_ids, enable_native_docs=False)

        self.assertEqual(first.updated, 1)
        self.assertEqual(second.updated, 0)
        self.assertEqual(service.files_api.downloads, ["one"])

    def test_updates_existing_file_when_drive_checksum_changes(self):
        old = b"<html>old</html>"
        new = b"<html>new</html>"
        name = "Global_Macro_Weekly_2026-08-28.html"
        self.folders[self.folder_ids["weekly"]] = [drive_file("weekly-1", name, old)]
        service = self._service({"weekly-1": old})
        sync_reports(service, self.root, self.folder_ids, enable_native_docs=False)

        self.folders[self.folder_ids["weekly"]] = [
            drive_file("weekly-1", name, new, "2026-08-28T09:00:00Z")
        ]
        service.files_api.contents["weekly-1"] = new
        result = sync_reports(service, self.root, self.folder_ids, enable_native_docs=False)

        self.assertEqual(result.updated, 1)
        self.assertEqual((self.root / "reports" / "weekly" / name).read_bytes(), new)

    def test_builds_sorted_index_and_latest_report_per_category(self):
        reports = {
            "early-warning": [
                ("ew-new", "Risk_2026-08-28.html", b"new", "2026-08-28T08:00:00Z"),
                ("ew-old", "Risk_2026-08-27.html", b"old", "2026-08-27T08:00:00Z"),
            ],
            "daily": [
                ("am", "Daily_20260828.html", b"daily", "2026-08-28T06:00:00Z")
            ],
            "weekly": [],
        }
        contents = {}
        for category, items in reports.items():
            for file_id, name, content, modified in items:
                self.folders[self.folder_ids[category]].append(
                    drive_file(file_id, name, content, modified)
                )
                contents[file_id] = content

        sync_reports(self._service(contents), self.root, self.folder_ids, enable_native_docs=False)
        index = json.loads((self.root / "data" / "reports.json").read_text())

        self.assertEqual(
            [item["file"] for item in index["reports"]],
            [
                "reports/early-warning/Risk_2026-08-28.html",
                "reports/daily/Daily_20260828.html",
                "reports/early-warning/Risk_2026-08-27.html",
            ],
        )
        self.assertEqual(index["latest"]["early-warning"]["date"], "2026-08-28")
        self.assertEqual(index["latest"]["daily"]["date"], "2026-08-28")
        self.assertIsNone(index["latest"]["weekly"])

    def test_native_google_doc_syncs_archives_markdown_and_renders_html(self):
        doc_content = make_sample_doc(run_id="GDB-20260903-0730")
        docs = {"doc-daily-1": doc_content}
        service = self._service(docs=docs)

        # 1. First sync run
        result = sync_reports(
            service=service,
            repo_root=self.root,
            folder_ids=self.folder_ids,
            doc_sources=self.doc_sources,
            enable_native_docs=True,
        )

        self.assertEqual(result.updated, 1)

        # Verify archived markdown exists
        md_path = self.root / "reports" / "daily" / "Global_Daily_Brief_2026-09-03.md"
        self.assertTrue(md_path.exists())
        self.assertIn("<<<REPORT_BEGIN>>>", md_path.read_text())

        # Verify rendered HTML exists and contains tables and semantic classes
        html_path = self.root / "reports" / "daily" / "Global_Daily_Brief_2026-09-03.html"
        self.assertTrue(html_path.exists())
        html_content = html_path.read_text()
        self.assertIn('<div class="table-scroll', html_content)
        self.assertIn("direction-up", html_content)
        self.assertIn("risk-red", html_content)

        # Verify reports.json was updated with rich metadata
        index = json.loads((self.root / "data" / "reports.json").read_text())
        daily_rep = next(r for r in index["reports"] if r["file"] == "reports/daily/Global_Daily_Brief_2026-09-03.html")
        self.assertEqual(daily_rep["run_id"], "GDB-20260903-0730")
        self.assertEqual(daily_rep["source_kind"], "google_doc_markdown")
        self.assertEqual(daily_rep["markdown_path"], "reports/daily/Global_Daily_Brief_2026-09-03.md")

        # 2. Second sync run with same RUN_ID (Idempotency)
        second_result = sync_reports(
            service=service,
            repo_root=self.root,
            folder_ids=self.folder_ids,
            doc_sources=self.doc_sources,
            enable_native_docs=True,
        )
        self.assertEqual(second_result.updated, 0)
        self.assertEqual(second_result.unchanged, 1)

    def test_prepending_new_run_id_creates_new_snapshot_and_preserves_old(self):
        doc_old = make_sample_doc(run_id="GDB-20260902-0730", title="Daily Brief Sept 2")
        docs = {"doc-daily-1": doc_old}
        service = self._service(docs=docs)

        sync_reports(
            service=service,
            repo_root=self.root,
            folder_ids=self.folder_ids,
            doc_sources=self.doc_sources,
            enable_native_docs=True,
        )
        old_md = self.root / "reports" / "daily" / "Global_Daily_Brief_2026-09-03.md"
        self.assertTrue(old_md.exists())

        # Prepend new run_id
        doc_new = make_sample_doc(run_id="GDB-20260903-0730", title="Daily Brief Sept 3") + "\n\n" + doc_old
        service.files_api.docs["doc-daily-1"] = doc_new

        sync_reports(
            service=service,
            repo_root=self.root,
            folder_ids=self.folder_ids,
            doc_sources=self.doc_sources,
            enable_native_docs=True,
        )

        # Both runs tracked in report_runs.json
        runs_data = json.loads((self.root / "data" / "report_runs.json").read_text())
        self.assertIn("GDB-20260902-0730", runs_data["runs"])
        self.assertIn("GDB-20260903-0730", runs_data["runs"])

    def test_legacy_html_reports_remain_byte_for_byte_untouched(self):
        legacy_bytes = b"<!doctype html><html><head><title>Legacy</title></head><body>Legacy 100% untouched</body></html>"
        legacy_path = self.root / "reports" / "daily" / "Legacy_Report_2026-08-01.html"
        legacy_path.parent.mkdir(parents=True, exist_ok=True)
        legacy_path.write_bytes(legacy_bytes)
        sha_before = sha256_bytes(legacy_bytes)

        # Sync native docs
        doc_content = make_sample_doc(run_id="GDB-20260903-0730")
        docs = {"doc-daily-1": doc_content}
        service = self._service(docs=docs)

        sync_reports(
            service=service,
            repo_root=self.root,
            folder_ids=self.folder_ids,
            doc_sources=self.doc_sources,
            enable_native_docs=True,
        )

        sha_after = sha256_bytes(legacy_path.read_bytes())
        self.assertEqual(sha_before, sha_after)
        self.assertEqual(legacy_path.read_bytes(), legacy_bytes)

    def test_never_calls_drive_upload_or_update_for_generated_html(self):
        doc_content = make_sample_doc(run_id="GDB-20260903-0730")
        docs = {"doc-daily-1": doc_content}
        service = self._service(docs=docs)

        sync_reports(
            service=service,
            repo_root=self.root,
            folder_ids=self.folder_ids,
            doc_sources=self.doc_sources,
            enable_native_docs=True,
        )

        # Ensure no write operations (create/update) were invoked on Drive API
        self.assertEqual(service.files_api.write_calls, [])


class ReportsIndexTests(unittest.TestCase):
    def test_index_includes_preexisting_nested_html_and_ignores_non_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            nested = root / "reports" / "early-warning" / "2026" / "08"
            nested.mkdir(parents=True)
            (nested / "Risk_2026-08-20.html").write_text("<html></html>")
            (nested / "Risk_2026-08-20.metadata.json").write_text("{}")

            index = build_reports_index(root, {})

            self.assertEqual(len(index["reports"]), 1)
            self.assertEqual(index["reports"][0]["date"], "2026-08-20")

    def test_index_ignores_reports_behind_parent_symlink(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outside = root.parent / "outside_ew"
            outside.mkdir(parents=True, exist_ok=True)
            (outside / "Risk_2026-08-20.html").write_text("<html></html>")

            (root / "reports").mkdir(parents=True, exist_ok=True)
            (root / "reports" / "early-warning").symlink_to(outside)

            index = build_reports_index(root, {})
            self.assertEqual(len(index["reports"]), 0)


if __name__ == "__main__":
    unittest.main()
