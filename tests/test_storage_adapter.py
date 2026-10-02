import unittest
from typing import Any, Dict, List, Optional

from scripts.storage_adapter import (
    GoogleDriveStorageAdapter,
    MemoryStorageAdapter,
    RemoteFile,
    StorageAdapter,
    StorageError,
    StorageNotFoundError,
    StoragePermissionError,
    create_storage_adapter,
)


class FakeRequest:
    def __init__(self, value: Any = None, error: Optional[Exception] = None):
        self.value = value
        self.error = error

    def execute(self) -> Any:
        if self.error:
            raise self.error
        return self.value


class FakeFilesAPI:
    def __init__(self) -> None:
        self.folders: Dict[str, List[Dict[str, Any]]] = {}
        self.files: Dict[str, bytes] = {}
        self.docs: Dict[str, Any] = {}
        self.list_error: Optional[Exception] = None
        self.get_error: Optional[Exception] = None
        self.export_error: Optional[Exception] = None

    def list(self, **kwargs) -> FakeRequest:
        if self.list_error:
            return FakeRequest(error=self.list_error)
        q = kwargs.get("q", "")
        page_token = kwargs.get("pageToken")
        # Extract folder_id from q="'folder_id' in parents"
        import re
        m = re.search(r"'([^']+)' in parents", q)
        fid = m.group(1) if m else ""
        all_files = self.folders.get(fid, [])

        # Simulate pagination: 2 items per page if page_token requested
        if page_token == "page2":
            return FakeRequest({"files": all_files[2:]})
        elif len(all_files) > 2 and page_token is None:
            return FakeRequest({"files": all_files[:2], "nextPageToken": "page2"})
        return FakeRequest({"files": all_files})

    def get_media(self, fileId: str, **kwargs) -> FakeRequest:
        if self.get_error:
            return FakeRequest(error=self.get_error)
        if fileId not in self.files:
            return FakeRequest(error=RuntimeError("file not found in fake"))
        return FakeRequest(value=self.files[fileId])

    def export_media(self, fileId: str, mimeType: str = "text/plain", **kwargs) -> FakeRequest:
        if self.export_error:
            return FakeRequest(error=self.export_error)
        if fileId not in self.docs:
            return FakeRequest(error=RuntimeError("doc not found in fake"))
        val = self.docs[fileId]
        if isinstance(val, str):
            val = val.encode("utf-8")
        return FakeRequest(value=val)


class FakeDriveService:
    def __init__(self) -> None:
        self.files_api = FakeFilesAPI()

    def files(self) -> FakeFilesAPI:
        return self.files_api


class TestRemoteFile(unittest.TestCase):
    def test_remote_file_immutability_and_dict(self):
        f = RemoteFile(
            id="file-123",
            name="Report_2026-09-03.html",
            size=1024,
            modified_time="2026-09-03T08:00:00Z",
            md5_checksum="abc123md5",
        )
        self.assertEqual(f.id, "file-123")
        self.assertEqual(f.name, "Report_2026-09-03.html")
        self.assertEqual(f.size, 1024)
        self.assertEqual(f.modified_time, "2026-09-03T08:00:00Z")
        self.assertEqual(f.md5_checksum, "abc123md5")

        with self.assertRaises(AttributeError):
            f.name = "new_name.html"  # type: ignore

        d = f.to_dict()
        self.assertEqual(d["id"], "file-123")
        self.assertEqual(d["name"], "Report_2026-09-03.html")
        self.assertEqual(d["size"], "1024")
        self.assertEqual(d["modifiedTime"], "2026-09-03T08:00:00Z")
        self.assertEqual(d["md5Checksum"], "abc123md5")


class TestMemoryStorageAdapter(unittest.TestCase):
    def test_memory_adapter_operations(self):
        adapter = MemoryStorageAdapter()
        self.assertIsInstance(adapter, StorageAdapter)

        # Empty folder
        self.assertEqual(adapter.list_folder_files("folder-daily"), [])

        # Add files
        f1 = RemoteFile("id-1", "b_report.html", 100)
        f2 = RemoteFile("id-2", "a_report.html", 200)
        adapter.add_file("folder-daily", f1, b"content-1")
        adapter.add_file("folder-daily", f2, b"content-2")

        # Sorted by name casefold
        listed = adapter.list_folder_files("folder-daily")
        self.assertEqual(len(listed), 2)
        self.assertEqual(listed[0].name, "a_report.html")
        self.assertEqual(listed[1].name, "b_report.html")

        # Read bytes
        self.assertEqual(adapter.read_file_bytes("id-1"), b"content-1")
        self.assertEqual(adapter.read_file_bytes("id-2"), b"content-2")
        with self.assertRaises(StorageNotFoundError):
            adapter.read_file_bytes("id-missing")

        # Add doc and export
        adapter.add_doc("doc-1", "# Canonical Doc Text")
        self.assertEqual(adapter.export_doc_text("doc-1"), "# Canonical Doc Text")
        with self.assertRaises(StorageNotFoundError):
            adapter.export_doc_text("doc-missing")


class TestGoogleDriveStorageAdapter(unittest.TestCase):
    def setUp(self):
        self.service = FakeDriveService()
        self.adapter = GoogleDriveStorageAdapter(self.service)

    def test_list_folder_files_with_pagination(self):
        self.service.files_api.folders["folder-1"] = [
            {"id": "id-1", "name": "Report_C.html", "size": "100", "modifiedTime": "2026-09-01T00:00:00Z"},
            {"id": "id-2", "name": "Report_A.html", "size": "200", "modifiedTime": "2026-09-02T00:00:00Z"},
            {"id": "id-3", "name": "Report_B.html", "size": "300", "modifiedTime": "2026-09-03T00:00:00Z"},
        ]

        files = self.adapter.list_folder_files("folder-1")
        self.assertEqual(len(files), 3)
        # Verify sorted by name
        self.assertEqual([f.name for f in files], ["Report_A.html", "Report_B.html", "Report_C.html"])
        self.assertEqual(files[0].size, 200)

    def test_read_file_bytes(self):
        self.service.files_api.files["file-1"] = b"binary-data"
        content = self.adapter.read_file_bytes("file-1")
        self.assertEqual(content, b"binary-data")

    def test_export_doc_text(self):
        self.service.files_api.docs["doc-1"] = "Exported Text Content"
        text = self.adapter.export_doc_text("doc-1")
        self.assertEqual(text, "Exported Text Content")

    def test_error_translation(self):
        # 1. Permission error
        class FakeHttpResp:
            status = 403
        class FakeHttpError(Exception):
            resp = FakeHttpResp()
            def __str__(self):
                return "The caller does not have permission"

        self.service.files_api.list_error = FakeHttpError()
        with self.assertRaises(StoragePermissionError):
            self.adapter.list_folder_files("folder-1")

        # 2. Not found error
        class FakeNotFoundResp:
            status = 404
        class FakeNotFoundError(Exception):
            resp = FakeNotFoundResp()
            def __str__(self):
                return "File not found"

        self.service.files_api.get_error = FakeNotFoundError()
        with self.assertRaises(StorageNotFoundError):
            self.adapter.read_file_bytes("missing-file")

        # 3. Generic error
        self.service.files_api.export_error = RuntimeError("Unexpected connection failure")
        with self.assertRaises(StorageError):
            self.adapter.export_doc_text("doc-err")

    def test_http_status_takes_priority_over_error_message(self):
        class HttpError(Exception):
            def __init__(self, status, message):
                super().__init__(message)
                self.resp = type("Response", (), {"status": status})()

        cases = (
            (404, "File not found or permission not visible", StorageNotFoundError),
            (401, "Not found", StoragePermissionError),
            (403, "Not found", StoragePermissionError),
            (500, "Unexpected permission backend error", StorageError),
        )
        for status, message, expected in cases:
            with self.subTest(status=status):
                self.service.files_api.export_error = HttpError(status, message)
                with self.assertRaises(expected) as caught:
                    self.adapter.export_doc_text("doc-1")
                self.assertIs(type(caught.exception), expected)


class TestFactoryFunction(unittest.TestCase):
    def test_create_storage_adapter(self):
        memory = MemoryStorageAdapter()
        self.assertIs(create_storage_adapter(memory), memory)

        fake_service = FakeDriveService()
        adapter = create_storage_adapter(fake_service)
        self.assertIsInstance(adapter, GoogleDriveStorageAdapter)


if __name__ == "__main__":
    unittest.main()
