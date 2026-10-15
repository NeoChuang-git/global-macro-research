"""Regression coverage for transfer budgets independent of archive size."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.sync_drive import CATEGORIES, SyncError, sync_reports
from tests.test_sync_drive import FakeDrive, FakeRequest, drive_file


class SyncTransferLimitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder_ids = {category: f"folder-{category}" for category in CATEGORIES}
        self.folders = {folder: [] for folder in self.folder_ids.values()}
        self.service = FakeDrive(self.folders, {})

    def add_reports(self, start, count, local=False):
        for number in range(start, start + count):
            category = CATEGORIES[number % len(CATEGORIES)]
            name = f"Report_2026-10-15_{number:04}.html"
            content = f"<html><h1>Report {number}</h1></html>".encode()
            remote = drive_file(str(number), name, content)
            self.folders[self.folder_ids[category]].append(remote)
            self.service.files_api.contents[str(number)] = content
            if local:
                path = self.root / "reports" / category / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)

    def sync(self, **limits):
        return sync_reports(self.service, self.root, self.folder_ids,
                            enable_native_docs=False, **limits)

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def test_200_and_201_verified_unchanged_reports_need_no_transfer_budget(self):
        self.add_reports(0, 200, local=True)
        for count in (200, 201):
            with self.subTest(count=count):
                result = self.sync()
                self.assertEqual((result.updated, result.unchanged), (0, count))
                before = self.snapshot()
                self.sync(max_batch_files=0, max_batch_bytes=0)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.service.files_api.downloads, [])
                self.assertEqual(len(json.loads(before["data/reports.json"])["reports"]), count)
                self.assertEqual(len(json.loads(before["data/drive-sync-state.json"])["files"]), count)
            if count == 200:
                self.add_reports(200, 1, local=True)

    def test_200_unchanged_plus_new_preserves_history_and_repeated_sync(self):
        self.add_reports(0, 200, local=True)
        self.sync()
        before = self.snapshot()
        self.add_reports(200, 1)
        result = self.sync(max_batch_bytes=len(self.service.files_api.contents["200"]))
        self.assertEqual((result.updated, result.unchanged), (1, 200))
        self.assertEqual(self.service.files_api.downloads, ["200"])
        after = self.snapshot()
        for path, content in before.items():
            if path.startswith("reports/"):
                self.assertEqual(after[path], content)
        old_state = json.loads(before["data/drive-sync-state.json"])["files"]
        new_state = json.loads(after["data/drive-sync-state.json"])["files"]
        self.assertEqual({key: new_state[key] for key in old_state}, old_state)
        old_index = json.loads(before["data/reports.json"])["reports"]
        new_index = json.loads(after["data/reports.json"])["reports"]
        self.assertEqual(len(new_index), 201)
        for entry in old_index:
            self.assertIn(entry, new_index)
        result = self.sync()
        self.assertEqual((result.updated, result.unchanged), (0, 201))
        self.assertEqual(self.snapshot(), after)
        self.assertEqual(self.service.files_api.downloads, ["200"])
        # Even reports no longer in Drive stay in the archive, index, and state.
        for folder in self.folders:
            self.folders[folder] = [r for r in self.folders[folder] if r["id"] != "0"]
        result = self.sync()
        self.assertEqual((result.updated, result.unchanged), (0, 200))
        self.assertEqual(self.snapshot(), after)
        self.assertEqual(self.service.files_api.downloads, ["200"])

    def test_200_transfers_succeed_but_201_fail_without_writes(self):
        self.add_reports(0, 200)
        self.assertEqual(self.sync().updated, 200)
        before = self.snapshot()
        # Change all 200 files, then add a 201st transfer in the last category.
        for remotes in self.folders.values():
            for index, remote in enumerate(remotes):
                content = b"<html>Changed report</html>"
                remotes[index] = drive_file(remote["id"], remote["name"], content)
                self.service.files_api.contents[remote["id"]] = content
        self.add_reports(200, 1)
        with self.assertRaisesRegex(SyncError, "transfer.*200 files"):
            self.sync()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.service.files_api.doc_exports, [])

    def test_multiple_pages_with_duplicates_keep_complete_history(self):
        self.add_reports(0, 201, local=True)
        self.add_reports(201, 1)
        original_list = self.service.files_api.list
        page_calls = []

        def paginated_list(**kwargs):
            remotes = original_list(**kwargs).execute()["files"]
            page_calls.append((kwargs["q"], kwargs["pageToken"]))
            if kwargs["pageToken"] is None:
                return FakeRequest({"files": remotes[:30], "nextPageToken": "second"})
            self.assertEqual(kwargs["pageToken"], "second")
            # Include a repeated ID and an older duplicate filename across pages.
            duplicate = dict(remotes[0], id="older-copy", modifiedTime="2020-01-01T00:00:00Z")
            return FakeRequest({"files": remotes[29:] + [duplicate]})

        self.service.files_api.list = paginated_list
        result = self.sync(max_batch_files=1)
        self.assertEqual((result.updated, result.unchanged), (1, 201))
        self.assertEqual(len(page_calls), 6)
        self.assertEqual(self.service.files_api.downloads, ["201"])
        state = json.loads((self.root / "data/drive-sync-state.json").read_text())["files"]
        self.assertEqual(len(state), 202)
        self.assertNotIn("older-copy", [entry["drive_file_id"] for entry in state.values()])
        self.assertEqual(len(json.loads((self.root / "data/reports.json").read_text())["reports"]), 202)

    def test_later_page_failure_cannot_publish_partial_listing(self):
        self.add_reports(0, 201, local=True)
        self.add_reports(201, 1)
        before = self.snapshot()
        original_list = self.service.files_api.list

        def failing_page(**kwargs):
            if kwargs["pageToken"]:
                return FakeRequest(error=RuntimeError("later page unavailable"))
            return FakeRequest({"files": original_list(**kwargs).execute()["files"],
                                "nextPageToken": "unavailable"})

        self.service.files_api.list = failing_page
        with self.assertRaisesRegex(SyncError, "later page unavailable"):
            self.sync()
        self.assertEqual(self.snapshot(), before)

    def test_declared_and_actual_transfer_bytes_remain_bounded(self):
        self.add_reports(0, 2)
        before = self.snapshot()
        for declared_size in (None, "0"):
            with self.subTest(declared_size=declared_size):
                if declared_size is not None:
                    for remotes in self.folders.values():
                        for remote in remotes:
                            remote["size"] = declared_size
                with self.assertRaisesRegex(SyncError, "transfer.*bytes"):
                    self.sync(max_batch_bytes=40)
                self.assertEqual(self.snapshot(), before)

    def test_unverified_local_content_still_consumes_transfer_budget(self):
        self.add_reports(0, 2, local=True)
        for remotes in self.folders.values():
            for remote in remotes:
                remote.pop("md5Checksum")
        before = self.snapshot()
        # With no remote checksum or prior state, identical bytes are only known
        # after download. The first download counts even though it is not staged.
        with self.assertRaisesRegex(SyncError, "transfer.*1 files"):
            self.sync(max_batch_files=1)
        self.assertEqual(self.service.files_api.downloads, ["0"])
        self.assertEqual(self.snapshot(), before)

    def test_matching_checksum_does_not_bypass_path_safety(self):
        self.add_reports(0, 1, local=True)
        directory = self.root / "reports/early-warning"
        outside = self.root / "outside"
        directory.rename(outside)
        directory.symlink_to(outside, target_is_directory=True)
        before = self.snapshot()
        with self.assertRaisesRegex(SyncError, "unsafe report path"):
            self.sync()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.service.files_api.downloads, [])

    def test_single_file_staging_and_checksum_guards_remain_active(self):
        self.add_reports(0, 1)
        before = self.snapshot()
        for limits, message in (({"max_report_bytes": 1}, "report exceeds"),
                                ({"max_staged_bytes": 1}, "staged updates")):
            with self.subTest(limits=limits), self.assertRaisesRegex(SyncError, message):
                self.sync(**limits)
            self.assertEqual(self.snapshot(), before)
        self.service.files_api.contents["0"] = b"bad checksum"
        with self.assertRaisesRegex(SyncError, "checksum mismatch"):
            self.sync()
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
