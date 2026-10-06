import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts.sync_drive import (
    CATEGORIES,
    SyncError,
    build_reports_index,
    classify_drive_file,
    extract_report_title,
    main,
    render_markdown_file_to_html,
    resolve_doc_sources,
    resolve_folder_ids,
    sync_native_google_docs,
    sync_reports,
)
from scripts.storage_adapter import (
    MemoryStorageAdapter,
    RemoteFile,
    StorageError,
    StorageNotFoundError,
    StoragePermissionError,
)
from scripts.report_ingestion import IngestionResult, IngestionStatus


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
        # Accessible, empty sources are different from missing/unreadable sources.
        available_docs = {source["document_id"]: "" for source in self.doc_sources.values()}
        available_docs.update(docs or {})
        return FakeDrive(self.folders, contents or {}, available_docs, list_error)

    def test_required_doc_fetch_failures_are_aggregated_and_classified(self):
        class FailingAdapter(MemoryStorageAdapter):
            def export_doc_text(self, doc_id, mime_type="text/plain"):
                errors = {
                    "doc-daily-1": StorageNotFoundError("not found or not visible"),
                    "doc-ew-1": StoragePermissionError("permission denied"),
                    "doc-weekly-1": StorageError("transport failure"),
                }
                raise errors[doc_id]

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SyncError) as caught:
            sync_native_google_docs(FailingAdapter(), self.root, self.doc_sources)
        diagnostic = stderr.getvalue()
        self.assertIn("SOURCE_DOC_NOT_FOUND_OR_NOT_VISIBLE: daily", diagnostic)
        self.assertIn("SOURCE_DOC_PERMISSION_DENIED: early-warning", diagnostic)
        self.assertIn("SOURCE_DOC_FETCH_FAILED: weekly", diagnostic)
        self.assertNotIn("SOURCE_DOC_PERMISSION_DENIED: daily", diagnostic)
        for source in self.doc_sources.values():
            self.assertIn(source["document_id"], str(caught.exception))

    def test_cli_fails_when_all_required_docs_fail_despite_unchanged_folder_reports(self):
        legacy = b"<html><h1>Existing daily report</h1></html>"
        remote = drive_file("one", "Daily_2026-08-28.html", legacy)
        self.folders[self.folder_ids["daily"]] = [remote]
        service = self._service({"one": legacy})
        sync_reports(service, self.root, self.folder_ids, enable_native_docs=False)
        service.files_api.docs.clear()
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        stdout, stderr = io.StringIO(), io.StringIO()
        environment = {"DRIVE_FOLDER_" + c.upper().replace("-", "_"): fid for c, fid in self.folder_ids.items()}
        with patch.dict("os.environ", environment, clear=True), \
             patch("scripts.sync_drive.create_drive_service", return_value=service), \
             patch("scripts.sync_drive.resolve_doc_sources", return_value=self.doc_sources), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(["--repo-root", str(self.root)])
        self.assertEqual(status, 1)
        self.assertNotIn("Sync complete", stdout.getvalue())
        self.assertNotIn("BUILD_SUCCEEDED", stdout.getvalue())
        diagnostics = stderr.getvalue().splitlines()
        self.assertEqual(sum(line.startswith("SOURCE_DOC_NOT_FOUND_OR_NOT_VISIBLE:") for line in diagnostics), 3)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_one_failed_source_does_not_hide_valid_source_or_allow_success(self):
        service = self._service(docs={
            "doc-daily-1": make_sample_doc(),
            "doc-weekly-1": RuntimeError("file not found"),
        })
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), self.assertRaises(SyncError):
            sync_reports(service, self.root, self.folder_ids, self.doc_sources)
        self.assertEqual(len(service.files_api.doc_exports), 3)
        self.assertTrue((self.root / "reports/daily/Global_Daily_Brief_2026-09-03.html").is_file())
        self.assertNotIn("BUILD_SUCCEEDED", stdout.getvalue())

    def test_invalid_canonical_block_fails_sync_without_replacing_existing_reports(self):
        service = self._service(docs={"doc-daily-1": make_sample_doc().replace("research_status: COMPLETE", "research_status: INCOMPLETE")})
        legacy_path = self.root / "reports/daily/Existing_2026-08-28.html"
        legacy_path.parent.mkdir(parents=True)
        legacy_path.write_bytes(b"existing report")
        with self.assertRaisesRegex(SyncError, "CANONICAL_BLOCK_INVALID"):
            sync_reports(service, self.root, self.folder_ids, self.doc_sources)
        self.assertEqual(legacy_path.read_bytes(), b"existing report")

    def test_ingestion_error_result_fails_sync(self):
        with patch("scripts.sync_drive.ingest_report_content", return_value=IngestionResult(status=IngestionStatus.FAILED, error="render failed")), \
             self.assertRaisesRegex(SyncError, "INGESTION_FAILED"):
            sync_native_google_docs(self._service(), self.root, self.doc_sources)

    def test_ingestion_exception_is_reported_as_sync_failure(self):
        with patch("scripts.sync_drive.ingest_report_content", side_effect=OSError("disk write failed")), \
             self.assertRaisesRegex(SyncError, "INGESTION_FAILED"):
            sync_native_google_docs(self._service(), self.root, self.doc_sources)

    def test_folder_replay_preserves_verified_journal_artifacts(self):
        source = make_sample_doc()
        service = self._service(docs={"doc-daily-1": source})
        sync_reports(service, self.root, self.folder_ids, self.doc_sources)
        report = self.root / "reports/daily/Global_Daily_Brief_2026-09-03.md"
        html = report.with_suffix(".html")
        runs = self.root / "data/report_runs.json"
        before = [p.read_bytes() for p in (report, html, runs)]
        raw = ("\ufeff" + source.replace("\n\n", "\n\n\n\n")).encode()
        service.files_api.folders[self.folder_ids["daily"]] = [drive_file("replay", report.name, raw)]
        service.files_api.contents["replay"] = raw
        for _ in range(2):
            sync_reports(service, self.root, self.folder_ids, self.doc_sources)
            self.assertEqual([p.read_bytes() for p in (report, html, runs)], before)
        self.assertIn("replay", service.files_api.downloads)

        # A valid download must not heal or hide a corrupted recorded artifact.
        report.write_bytes(b"corrupted snapshot")
        with self.assertRaisesRegex(SyncError, "checksum mismatch"):
            sync_reports(service, self.root, self.folder_ids, self.doc_sources)
        self.assertEqual(report.read_bytes(), b"corrupted snapshot")
        self.assertEqual(html.read_bytes(), before[1])
        self.assertEqual(runs.read_bytes(), before[2])

    def test_text_download_keeps_original_and_does_not_redownload(self):
        name = "Global_Daily_Brief_2026-10-04.txt"
        raw = b"# Daily report\n\nReport body.\n"
        self.folders[self.folder_ids["daily"]] = [drive_file("text-report", name, raw)]
        service = self._service(contents={"text-report": raw})
        sync_reports(service, self.root, self.folder_ids, enable_native_docs=False)
        self.assertEqual((self.root / "reports/daily" / name).read_bytes(), raw)
        self.assertTrue((self.root / "reports/daily" / name.replace(".txt", ".html")).is_file())
        result = sync_reports(service, self.root, self.folder_ids, enable_native_docs=False)
        self.assertEqual(result.updated, 0)
        self.assertEqual(service.files_api.downloads, ["text-report"])

    def test_missing_processed_artifact_is_required_source_failure(self):
        service = self._service(docs={"doc-daily-1": make_sample_doc()})
        sync_reports(service, self.root, self.folder_ids, self.doc_sources)
        html = self.root / "reports/daily/Global_Daily_Brief_2026-09-03.html"
        html.unlink()
        with self.assertRaisesRegex(SyncError, "missing recorded html artifact"):
            sync_reports(service, self.root, self.folder_ids, self.doc_sources)

    def test_folder_renderer_does_not_silently_ignore_ingestion_failure(self):
        with patch("scripts.sync_drive.ingest_report_file", return_value=IngestionResult(status=IngestionStatus.FAILED, error="artifact missing")), \
             self.assertRaisesRegex(SyncError, "folder report ingestion failed"):
            render_markdown_file_to_html(self.root / "reports/weekly/weekly.md", "weekly", self.root / "data/report_runs.json")

    def test_accessible_docs_without_complete_block_remain_valid_noop(self):
        service = self._service(docs={"doc-daily-1": "Report is being prepared. <<<REPORT_BEGIN>>>"})
        result = sync_reports(service, self.root, self.folder_ids, self.doc_sources)
        self.assertEqual(result.updated, 0)
        self.assertEqual(result.unchanged, 0)

    def test_explicit_folder_only_sync_does_not_export_docs(self):
        service = self._service()
        service.files_api.docs.clear()
        sync_reports(service, self.root, self.folder_ids, enable_native_docs=False)
        self.assertEqual(service.files_api.doc_exports, [])

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
        self.assertIn('class="table-scroll wide-content"', html_content)
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

    def test_sync_reports_powered_by_memory_storage_adapter(self):
        adapter = MemoryStorageAdapter()
        # Add a daily report HTML
        daily_content = b"<html><h1>Daily Global Brief</h1></html>"
        f1 = RemoteFile(
            id="mem-1",
            name="Global_Daily_Brief_2026-09-02.html",
            size=len(daily_content),
            modified_time="2026-09-02T08:00:00Z",
            md5_checksum=md5(daily_content),
        )
        adapter.add_file(self.folder_ids["daily"], f1, daily_content)

        # Add a native Google Doc
        doc_payload = make_sample_doc(run_id="GDB-20260903-0730", title="Daily Memory Brief")
        adapter.add_doc("doc-daily-1", doc_payload)
        adapter.add_doc("doc-ew-1", "")
        adapter.add_doc("doc-weekly-1", "")

        # First sync
        first = sync_reports(adapter, self.root, self.folder_ids, self.doc_sources, enable_native_docs=True)
        self.assertEqual(first.updated, 2)  # 1 folder file + 1 canonical doc

        # File exists on disk
        self.assertTrue((self.root / "reports" / "daily" / "Global_Daily_Brief_2026-09-02.html").is_file())
        self.assertTrue((self.root / "reports" / "daily" / "Global_Daily_Brief_2026-09-03.html").is_file())
        self.assertTrue((self.root / "data" / "reports.json").is_file())

        # Second sync is idempotent
        second = sync_reports(adapter, self.root, self.folder_ids, self.doc_sources, enable_native_docs=True)
        self.assertEqual(second.updated, 0)
        self.assertEqual(second.unchanged, 2)


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

    def test_extract_report_title_from_html_and_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            html_file = root / "Weekly_Strategy_2026-09-27.html"
            html_file.write_text("<!doctype html><html><body><h1>Weekly Global Macro Strategy &amp; Outlook</h1></body></html>", encoding="utf-8")
            self.assertEqual(extract_report_title(html_file), "Weekly Global Macro Strategy & Outlook")

            # With companion markdown title frontmatter
            md_file = root / "Weekly_Strategy_2026-09-27.md"
            md_file.write_text("---\ntitle: Rich Markdown Frontmatter Title\n---\n# Ignored\n", encoding="utf-8")
            self.assertEqual(extract_report_title(html_file), "Rich Markdown Frontmatter Title")

    def test_build_reports_index_extracts_weekly_title_automatically(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            weekly_dir = root / "reports" / "weekly"
            weekly_dir.mkdir(parents=True)
            html_file = weekly_dir / "Weekly_Strategy_2026-09-27.html"
            html_file.write_text(
                "<!doctype html><html><head><title>Ignored</title></head><body>"
                "<h1>Weekly Global Macro &amp; Investment Strategy｜AI獲利動能撐住風險資產</h1>"
                "</body></html>",
                encoding="utf-8",
            )

            index = build_reports_index(root, {})
            self.assertEqual(len(index["reports"]), 1)
            expected_title = "Weekly Global Macro & Investment Strategy｜AI獲利動能撐住風險資產"
            self.assertEqual(index["reports"][0]["title"], expected_title)
            self.assertEqual(index["latest"]["weekly"]["title"], expected_title)



if __name__ == "__main__":
    unittest.main()
