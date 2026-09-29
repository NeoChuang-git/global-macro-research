# 0003. Decouple Google Drive Storage Adapter

## Context
Previously, `scripts/sync_drive.py` was directly coupled to the low-level Google Drive Python SDK client (`googleapiclient.discovery.Resource`). Network calls, pagination queries, binary stream downloads, plain text exports, and credential handling were tightly bound to the synchronization pipeline. This coupling forced unit tests in `tests/test_sync_drive.py` to maintain brittle, complex mock hierarchies (`FakeDrive`, `FakeFiles`, `FakeRequest`) mimicking Google SDK internal method call chains (`service.files().list().execute()`), while making it difficult to test edge cases, network failures, or support alternate storage backends.

## Decision
We decouple cloud storage operations behind a dedicated deep module: `scripts/storage_adapter.py`.
- **Protocol & Typed Seam**: Define a clean `StorageAdapter` protocol and immutable `RemoteFile` dataclass providing high-level operations: `list_folder_files(folder_id)`, `read_file_bytes(file_id)`, and `export_doc_text(doc_id, mime_type)`.
- **Dual Implementations**:
  - `GoogleDriveStorageAdapter`: Production adapter wrapping Google Drive API client, encapsulating pagination, query construction, and media transfers.
  - `MemoryStorageAdapter`: Zero-dependency, in-memory implementation for blazing-fast unit tests and offline testing without mock SDK chains.
- **Domain Exception Translation**: Wrap and translate SDK HTTP and network errors into explicit domain exceptions: `StorageError`, `StoragePermissionError`, and `StorageNotFoundError`.
- **Backward-Compatible Seam**: Provide an adapter bridge in `scripts/sync_drive.py` enabling `sync_reports` and `sync_native_google_docs` to accept either a `StorageAdapter` or a legacy Google API client `service` (automatically wrapped).
