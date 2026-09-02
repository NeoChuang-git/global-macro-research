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
    resolve_folder_ids,
    sync_reports,
)


def md5(content):
    return hashlib.md5(content).hexdigest()


class FakeRequest:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def execute(self):
        if self.error:
            raise self.error
        return self.value


class FakeFiles:
    def __init__(self, folders, contents, list_error=None):
        self.folders = folders
        self.contents = contents
        self.list_error = list_error
        self.downloads = []

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


class FakeDrive:
    def __init__(self, folders, contents, list_error=None):
        self.files_api = FakeFiles(folders, contents, list_error)

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


class SyncDriveTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.folder_ids = {category: f"folder-{category}" for category in CATEGORIES}
        self.folders = {folder_id: [] for folder_id in self.folder_ids.values()}

    def tearDown(self):
        self.temp_dir.cleanup()

    def _service(self, contents=None, list_error=None):
        return FakeDrive(self.folders, contents or {}, list_error)

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

        first = sync_reports(service, self.root, self.folder_ids)
        second = sync_reports(service, self.root, self.folder_ids)

        self.assertEqual(first.updated, 1)
        self.assertEqual(second.updated, 0)
        self.assertEqual(service.files_api.downloads, ["one"])

    def test_updates_existing_file_when_drive_checksum_changes(self):
        old = b"<html>old</html>"
        new = b"<html>new</html>"
        name = "Global_Macro_Weekly_2026-08-28.html"
        self.folders[self.folder_ids["weekly"]] = [drive_file("weekly-1", name, old)]
        service = self._service({"weekly-1": old})
        sync_reports(service, self.root, self.folder_ids)

        self.folders[self.folder_ids["weekly"]] = [
            drive_file("weekly-1", name, new, "2026-08-28T09:00:00Z")
        ]
        service.files_api.contents["weekly-1"] = new
        result = sync_reports(service, self.root, self.folder_ids)

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

        sync_reports(self._service(contents), self.root, self.folder_ids)
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

    def test_redownloads_missing_local_file_even_when_state_checksum_matches(self):
        content = b"<html>restore me</html>"
        remote = drive_file("missing", "Daily_2026-08-28.html", content)
        self.folders[self.folder_ids["daily"]] = [remote]
        service = self._service({"missing": content})
        sync_reports(service, self.root, self.folder_ids)
        local = self.root / "reports" / "daily" / remote["name"]
        local.unlink()

        result = sync_reports(service, self.root, self.folder_ids)

        self.assertEqual(result.updated, 1)
        self.assertEqual(local.read_bytes(), content)

    def test_deduplicates_identical_drive_names_by_latest_modified_time_and_fails_on_api_error(self):
        old_content = b"<html>old content</html>"
        new_content = b"<html>new content</html>"
        duplicate_name = "Weekly_2026-08-28.html"
        self.folders[self.folder_ids["weekly"]] = [
            drive_file("a", duplicate_name, old_content, "2026-08-28T08:00:00Z"),
            drive_file("b", duplicate_name, new_content, "2026-08-28T09:00:00Z"),
        ]

        result = sync_reports(
            self._service({"a": old_content, "b": new_content}), self.root, self.folder_ids
        )
        self.assertEqual(result.updated, 1)
        self.assertEqual((self.root / "reports" / "weekly" / duplicate_name).read_bytes(), new_content)

        with self.assertRaisesRegex(SyncError, "Drive API"):
            sync_reports(self._service(list_error=RuntimeError("offline")), self.root, self.folder_ids)

    def test_requires_all_three_folder_ids(self):
        with self.assertRaisesRegex(SyncError, "DRIVE_FOLDER_WEEKLY"):
            resolve_folder_ids(
                {
                    "DRIVE_FOLDER_EARLY_WARNING": "ew",
                    "DRIVE_FOLDER_DAILY": "am",
                }
            )

        with self.assertRaisesRegex(SyncError, "invalid Drive folder ID"):
            resolve_folder_ids(
                {
                    "DRIVE_FOLDER_EARLY_WARNING": "ew' or trashed = true",
                    "DRIVE_FOLDER_DAILY": "am",
                    "DRIVE_FOLDER_WEEKLY": "week",
                }
            )

        # Supports fallback from DRIVE_FOLDER_MORNING when DRIVE_FOLDER_DAILY is absent
        folder_ids = resolve_folder_ids(
            {
                "DRIVE_FOLDER_EARLY_WARNING": "ew",
                "DRIVE_FOLDER_MORNING": "am-fallback",
                "DRIVE_FOLDER_WEEKLY": "week",
            }
        )
        self.assertEqual(folder_ids["daily"], "am-fallback")

        # DRIVE_FOLDER_DAILY takes precedence over DRIVE_FOLDER_MORNING
        folder_ids_direct = resolve_folder_ids(
            {
                "DRIVE_FOLDER_EARLY_WARNING": "ew",
                "DRIVE_FOLDER_DAILY": "am-direct",
                "DRIVE_FOLDER_MORNING": "am-fallback",
                "DRIVE_FOLDER_WEEKLY": "week",
            }
        )
        self.assertEqual(folder_ids_direct["daily"], "am-direct")

    def test_rejects_exceeding_batch_limits(self):
        content = b"<html>report</html>"
        name = "Global_Daily_Brief_2026-08-28.html"
        self.folders[self.folder_ids["daily"]] = [
            drive_file("m1", name, content),
            drive_file("m2", "Global_Daily_Brief_2026-08-29.html", content),
        ]
        service = self._service({"m1": content, "m2": content})

        with self.assertRaisesRegex(SyncError, "batch limit of 1 files"):
            sync_reports(service, self.root, self.folder_ids, max_batch_files=1)

        with self.assertRaisesRegex(SyncError, "batch limit of 10 bytes"):
            sync_reports(service, self.root, self.folder_ids, max_batch_bytes=10)

        with self.assertRaisesRegex(SyncError, "batch limit of 5 bytes"):
            sync_reports(service, self.root, self.folder_ids, max_staged_bytes=5)

    def test_rejects_parent_symlink_in_sync_reports(self):
        content = b"<html>symlink target</html>"
        name = "Global_Daily_Brief_2026-08-28.html"
        self.folders[self.folder_ids["daily"]] = [drive_file("sym", name, content)]
        service = self._service({"sym": content})

        outside = self.root.parent / "outside_dir"
        outside.mkdir(parents=True, exist_ok=True)
        (self.root / "reports").mkdir(parents=True, exist_ok=True)
        (self.root / "reports" / "daily").symlink_to(outside)

        with self.assertRaisesRegex(SyncError, "unsafe report path or symlink ancestor"):
            sync_reports(service, self.root, self.folder_ids)


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
