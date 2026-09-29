"""
Storage Adapter Module (Deep Module).

Decouples cloud storage operations (Google Drive, In-Memory) behind a clean,
typed interface:
- RemoteFile: immutable dataclass encapsulating remote file metadata
- StorageAdapter: protocol defining folder listing, binary read, and doc export
- GoogleDriveStorageAdapter: production adapter wrapping Google Drive API client
- MemoryStorageAdapter: zero-dependency in-memory adapter for deterministic unit tests
- Error translation: maps Google API/network exceptions to domain-specific StorageErrors
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence, Tuple, Union, runtime_checkable

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))


class StorageError(RuntimeError):
    """Base exception for all storage adapter operations."""


class StorageNotFoundError(StorageError):
    """Requested remote file or folder does not exist."""


class StoragePermissionError(StorageError):
    """Access denied, permission error, or quota exceeded for the storage resource."""


@dataclass(frozen=True)
class RemoteFile:
    """Immutable representation of a file in remote storage."""

    id: str
    name: str
    size: int = 0
    modified_time: Optional[str] = None
    md5_checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to Google Drive API compatible dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "size": str(self.size),
            "modifiedTime": self.modified_time,
            "md5Checksum": self.md5_checksum,
        }


@runtime_checkable
class StorageAdapter(Protocol):
    """Storage adapter interface for listing and transferring remote files."""

    def list_folder_files(self, folder_id: str) -> List[RemoteFile]:
        """List active (non-trashed) files in the remote folder."""
        ...

    def read_file_bytes(self, file_id: str) -> bytes:
        """Download binary contents of a remote file."""
        ...

    def export_doc_text(self, doc_id: str, mime_type: str = "text/plain") -> str:
        """Export text representation of a remote document."""
        ...


class MemoryStorageAdapter:
    """Zero-dependency, in-memory storage adapter for deterministic testing and offline use."""

    def __init__(
        self,
        folders: Optional[Dict[str, Sequence[RemoteFile]]] = None,
        files: Optional[Dict[str, bytes]] = None,
        docs: Optional[Dict[str, str]] = None,
    ) -> None:
        self._folders: Dict[str, List[RemoteFile]] = {}
        if folders:
            for fid, f_list in folders.items():
                self._folders[fid] = list(f_list)
        self._files: Dict[str, bytes] = dict(files) if files else {}
        self._docs: Dict[str, str] = dict(docs) if docs else {}

    def add_file(self, folder_id: str, remote_file: RemoteFile, content: bytes) -> None:
        """Register a remote file under a folder with its binary payload."""
        self._folders.setdefault(folder_id, []).append(remote_file)
        self._files[remote_file.id] = content

    def add_doc(self, doc_id: str, text: str) -> None:
        """Register a document with its text payload."""
        self._docs[doc_id] = text

    def list_folder_files(self, folder_id: str) -> List[RemoteFile]:
        if folder_id not in self._folders:
            return []
        return sorted(self._folders[folder_id], key=lambda f: (f.name.casefold(), f.id))

    def read_file_bytes(self, file_id: str) -> bytes:
        if file_id not in self._files:
            raise StorageNotFoundError(f"file not found in memory storage: {file_id}")
        return self._files[file_id]

    def export_doc_text(self, doc_id: str, mime_type: str = "text/plain") -> str:
        if doc_id not in self._docs:
            raise StorageNotFoundError(f"document not found in memory storage: {doc_id}")
        return self._docs[doc_id]


class GoogleDriveStorageAdapter:
    """Production storage adapter wrapping Google Drive API client resource."""

    def __init__(self, service: Any) -> None:
        self._service = service

    def list_folder_files(self, folder_id: str) -> List[RemoteFile]:
        query = f"'{folder_id}' in parents and trashed = false"
        files: List[RemoteFile] = []
        page_token = None
        try:
            while True:
                request = self._service.files().list(
                    q=query,
                    fields="nextPageToken, files(id, name, modifiedTime, md5Checksum, size)",
                    pageSize=1000,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                response = request.execute()
                for item in response.get("files", []):
                    f_id = item.get("id")
                    name = item.get("name")
                    if not f_id or not name:
                        continue
                    try:
                        declared_size = int(item.get("size", 0))
                    except (TypeError, ValueError):
                        declared_size = 0
                    files.append(
                        RemoteFile(
                            id=f_id,
                            name=name,
                            size=declared_size,
                            modified_time=item.get("modifiedTime"),
                            md5_checksum=item.get("md5Checksum"),
                        )
                    )
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
        except StorageError:
            raise
        except Exception as exc:
            self._translate_and_raise(exc, f"list folder {folder_id}")

        return sorted(files, key=lambda f: (f.name.casefold(), f.id))

    def read_file_bytes(self, file_id: str) -> bytes:
        try:
            request = self._service.files().get_media(
                fileId=file_id, supportsAllDrives=True
            )
            content = request.execute()
            if not isinstance(content, bytes):
                raise StorageError(f"expected binary content, got {type(content).__name__}")
            return content
        except StorageError:
            raise
        except Exception as exc:
            self._translate_and_raise(exc, f"read file {file_id}")
            raise  # pragma: no cover

    def export_doc_text(self, doc_id: str, mime_type: str = "text/plain") -> str:
        try:
            request = self._service.files().export_media(
                fileId=doc_id, mimeType=mime_type
            )
            content = request.execute()
            if isinstance(content, bytes):
                return content.decode("utf-8", errors="replace")
            return str(content)
        except StorageError:
            raise
        except Exception as exc:
            self._translate_and_raise(exc, f"export doc {doc_id}")
            raise  # pragma: no cover

    def _translate_and_raise(self, exc: Exception, action: str) -> None:
        err_msg = str(exc)
        status_code = getattr(getattr(exc, "resp", None), "status", None)
        if status_code in (401, 403) or "permission" in err_msg.lower() or "quota" in err_msg.lower():
            raise StoragePermissionError(f"Drive permission error during {action}: {exc}") from exc
        if status_code == 404 or "not found" in err_msg.lower():
            raise StorageNotFoundError(f"Drive resource not found during {action}: {exc}") from exc
        raise StorageError(f"Drive operation failed during {action}: {exc}") from exc


def create_storage_adapter(service: Optional[Any] = None) -> StorageAdapter:
    """Resolve or construct an appropriate StorageAdapter."""
    if service is not None:
        if isinstance(service, StorageAdapter):
            return service
        return GoogleDriveStorageAdapter(service)
    try:
        from scripts.sync_drive import create_drive_service
        return GoogleDriveStorageAdapter(create_drive_service())
    except Exception as exc:
        raise StorageError(f"failed to initialize Drive service: {exc}") from exc
