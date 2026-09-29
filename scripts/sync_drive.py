#!/usr/bin/env python3

"""Deterministically mirror reports from Google Docs and Google Drive folders."""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Tuple

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from scripts.report_ingestion import (
    IngestionResult,
    IngestionStatus,
    ingest_report_content,
    ingest_report_file,
)
from scripts.report_runs import (
    RUNS_STATE_PATH,
    load_report_runs,
)
from scripts.report_catalog import (
    ReportCatalog,
    date_from_modified_time as _date_from_modified_time,
    date_from_name as _date_from_name,
    display_title as _display_title,
    extract_report_title,
    is_generic_title as _is_generic_title,
    is_safe_parent_and_path as _is_safe_parent_and_path,
)


ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("early-warning", "daily", "weekly")
CATEGORY_ENV_VARS = {
    "early-warning": ("DRIVE_FOLDER_EARLY_WARNING",),
    "daily": ("DRIVE_FOLDER_DAILY", "DRIVE_FOLDER_MORNING"),
    "weekly": ("DRIVE_FOLDER_WEEKLY",),
}
STATE_PATH = Path("data/drive-sync-state.json")
INDEX_PATH = Path("data/reports.json")
DEFAULT_MAX_REPORT_BYTES = 25 * 1024 * 1024
DEFAULT_MAX_BATCH_FILES = 200
DEFAULT_MAX_BATCH_BYTES = 100 * 1024 * 1024
DEFAULT_MAX_STAGED_BYTES = 50 * 1024 * 1024
DATE_PATTERN = re.compile(r"(?<!\d)(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)(?!\d)")

DEFAULT_DOC_SOURCES = {
    "GLOBAL_DAILY_BRIEF": {
        "document_id": "1NvDE2s4vqPERGOToh9sZHrp7y0_gmGEd4LjKNWfTVoM",
        "category": "daily",
        "report_type": "GLOBAL_DAILY_BRIEF",
    },
    "MACRO_TAIWAN_EARLY_WARNING": {
        "document_id": "1OudDZrY4Xdk3IKAtT-xvvUBwvkotU08ZwO6b-9OjRyk",
        "category": "early-warning",
        "report_type": "MACRO_TAIWAN_EARLY_WARNING",
    },
    "WEEKLY_STRATEGY": {
        "document_id": "15ZME47m_BAc3W7Z5Gcg97pHxiICULd-NRxe9Ox2NQrI",
        "category": "weekly",
        "report_type": "WEEKLY_STRATEGY",
    },
}


class SyncError(RuntimeError):
    """A user-actionable synchronization failure."""


@dataclass(frozen=True)
class SyncResult:
    updated: int
    unchanged: int
    ignored: int


ALLOWED_EXTENSIONS = (".html", ".md", ".txt")


def classify_drive_file(category, name, modified_time):
    if category not in CATEGORIES:
        raise SyncError(f"unknown report category: {category}")
    if not isinstance(name, str) or not name:
        raise SyncError(f"invalid Drive filename in {category}")
    if Path(name).name != name or "/" in name or "\\" in name:
        raise SyncError(f"unsafe Drive filename in {category}: {name}")
    lower_name = name.lower()
    if not any(lower_name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return None
    return {
        "category": category,
        "title": _display_title(name),
        "date": _date_from_name(name) or _date_from_modified_time(modified_time),
    }


def resolve_folder_ids(environment):
    folder_ids = {}
    for category, variables in CATEGORY_ENV_VARS.items():
        value = ""
        matched_var = None
        for variable in variables:
            val = environment.get(variable, "").strip()
            if val:
                value = val
                matched_var = variable
                break
        if not value:
            raise SyncError(f"missing required environment variable: {variables[0]}")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
            raise SyncError(f"invalid Drive folder ID in {matched_var or variables[0]}")
        folder_ids[category] = value
    if len(set(folder_ids.values())) != len(CATEGORIES):
        raise SyncError("the three Drive folder IDs must be distinct")
    return folder_ids


def resolve_doc_sources(environment: Optional[Mapping[str, str]] = None) -> Dict[str, Dict[str, str]]:
    env = environment or {}
    sources = {}
    for key, default_info in DEFAULT_DOC_SOURCES.items():
        env_keys = [f"DOC_ID_{default_info['category'].upper().replace('-', '_')}"]
        if default_info["category"] == "daily":
            env_keys.append("DOC_ID_MORNING")

        doc_id = ""
        for ek in env_keys:
            val = env.get(ek, "").strip()
            if val:
                doc_id = val
                break
        if not doc_id:
            doc_id = default_info["document_id"]

        sources[key] = {
            "document_id": doc_id,
            "category": default_info["category"],
            "report_type": default_info["report_type"],
        }
    return sources


def _hash_bytes(content, algorithm):
    digest = hashlib.new(algorithm)
    digest.update(content)
    return digest.hexdigest()


def _hash_file(path, algorithm):
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"invalid JSON file {path}: {exc}") from exc


def _json_bytes(value):
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    ).encode("utf-8")


def _atomic_write_if_changed(path, content):
    if path.exists() and path.read_bytes() == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return True


def _list_folder_files(service, category, folder_id):
    files = []
    page_token = None
    try:
        while True:
            response = (
                service.files()
                .list(
                    q=f"'{folder_id}' in parents and trashed = false",
                    fields="nextPageToken,files(id,name,modifiedTime,md5Checksum,size)",
                    orderBy="name",
                    pageSize=1000,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
    except Exception as exc:
        raise SyncError(f"Drive API list failed for {category}: {exc}") from exc
    return sorted(files, key=lambda item: (item.get("name", "").casefold(), item.get("id", "")))


def _download_file(service, remote, category, max_report_bytes):
    try:
        declared_size = int(remote.get("size", 0))
    except (TypeError, ValueError) as exc:
        raise SyncError(f"invalid Drive size for {category}/{remote.get('name')}") from exc
    if declared_size < 0:
        raise SyncError(f"invalid Drive size for {category}/{remote.get('name')}")
    if declared_size > max_report_bytes:
        raise SyncError(
            f"report exceeds {max_report_bytes} bytes: {category}/{remote.get('name')}"
        )
    try:
        content = service.files().get_media(
            fileId=remote["id"], supportsAllDrives=True
        ).execute()
    except Exception as exc:
        raise SyncError(
            f"Drive API download failed for {category}/{remote.get('name')}: {exc}"
        ) from exc
    if not isinstance(content, bytes):
        raise SyncError(f"Drive returned non-binary content for {category}/{remote.get('name')}")
    if len(content) > max_report_bytes:
        raise SyncError(
            f"downloaded report exceeds {max_report_bytes} bytes: {category}/{remote.get('name')}"
        )
    expected_md5 = remote.get("md5Checksum")
    if expected_md5 and _hash_bytes(content, "md5") != expected_md5:
        raise SyncError(f"checksum mismatch for {category}/{remote.get('name')}")
    return content


def _state_entry(remote, relative_path, content_sha256):
    return {
        "category": relative_path.parts[1],
        "drive_file_id": remote["id"],
        "md5_checksum": remote.get("md5Checksum"),
        "modified_time": remote.get("modifiedTime"),
        "name": remote["name"],
        "sha256": content_sha256,
        "size": int(remote.get("size", 0)),
    }


def sync_native_google_docs(
    service,
    repo_root: Path,
    doc_sources: Optional[Dict[str, Dict[str, str]]] = None,
    runs_file: Optional[Path] = None,
) -> Tuple[int, int]:
    """
    Sync native Google Docs by exporting plain text, extracting latest canonical block,
    validating metadata/sections, checking idempotency, archiving markdown, and rendering HTML.
    Returns (archived_count, skipped_count).
    """
    repo_root = Path(repo_root)
    sources = doc_sources or resolve_doc_sources(os.environ)
    runs_path = runs_file or (repo_root / RUNS_STATE_PATH)

    archived_count = 0
    skipped_count = 0

    for name, source_info in sources.items():
        category = source_info["category"]
        doc_id = source_info["document_id"]
        expected_type = source_info["report_type"]

        # 1. Fetch text from Google Doc via export_media
        try:
            raw_content = service.files().export_media(
                fileId=doc_id, mimeType="text/plain"
            ).execute()
            if isinstance(raw_content, bytes):
                text = raw_content.decode("utf-8", errors="replace")
            else:
                text = str(raw_content)
            print(f"SOURCE_DOC_FETCHED: {category} ({doc_id})")
        except Exception as exc:
            print(f"SOURCE_DOC_PERMISSION_DENIED: {category} ({doc_id}): {exc}", file=sys.stderr)
            continue

        result = ingest_report_content(
            content=text,
            category=category,
            repo_root=repo_root,
            source_document_id=doc_id,
            expected_type=expected_type,
            runs_path=runs_path,
            allow_fallback=False,
        )

        if result.status == IngestionStatus.ARCHIVED_CANONICAL:
            print(f"CANONICAL_BLOCK_FOUND: {result.run_id} ({category})")
            print(f"MARKDOWN_ARCHIVED: {result.markdown_rel} ({result.markdown_sha256[:8]})")
            print(f"MARKDOWN_RENDERED: {result.html_rel} ({result.html_sha256[:8]})")
            archived_count += 1
        elif result.status == IngestionStatus.SKIPPED_EXISTING:
            print(f"CANONICAL_BLOCK_FOUND: {result.run_id} ({category})")
            print(f"RUN_ID_PREEXISTING: {result.run_id}")
            skipped_count += 1
        elif result.status == IngestionStatus.NO_CANONICAL_BLOCK:
            print(f"NO_CANONICAL_BLOCK_YET: {category}")
        elif result.status == IngestionStatus.CANONICAL_BLOCK_INVALID:
            print(f"CANONICAL_BLOCK_INVALID: {category}: {result.error}", file=sys.stderr)
        else:
            print(f"INGESTION_FAILED: {category} ({doc_id}): {result.error}", file=sys.stderr)

    return archived_count, skipped_count


def render_markdown_file_to_html(md_path: Path, category: str, runs_path: Path) -> Path:
    """Render a downloaded .md / .txt file to companion .html with institutional styling."""
    repo_root_dir = runs_path.parent.parent if runs_path.parent.name == "data" else runs_path.parent
    result = ingest_report_file(
        file_path=md_path,
        category=category,
        repo_root=repo_root_dir,
        runs_path=runs_path,
        allow_fallback=True,
    )
    if result.status == IngestionStatus.ARCHIVED_CANONICAL:
        print(f"MARKDOWN_RENDERED: {result.html_path.name}")
    elif result.status == IngestionStatus.ARCHIVED_FALLBACK:
        print(f"MARKDOWN_RENDERED_FALLBACK: {result.html_path.name}")
    return result.html_path or md_path.with_suffix(".html")



def sync_reports(
    service,
    repo_root,
    folder_ids=None,
    doc_sources=None,
    max_report_bytes=DEFAULT_MAX_REPORT_BYTES,
    max_batch_files=DEFAULT_MAX_BATCH_FILES,
    max_batch_bytes=DEFAULT_MAX_BATCH_BYTES,
    max_staged_bytes=DEFAULT_MAX_STAGED_BYTES,
    enable_native_docs=True,
):
    repo_root = Path(repo_root)

    state_file = repo_root / STATE_PATH
    state = _load_json(state_file, {"schema_version": 1, "files": {}})
    if state.get("schema_version") != 1 or not isinstance(state.get("files"), dict):
        raise SyncError(f"unsupported sync state schema: {state_file}")

    next_files = dict(state["files"])
    staged = {}
    total_remote_files = 0
    total_remote_bytes = 0
    total_staged_bytes = 0
    updated = 0
    unchanged = 0
    ignored = 0

    # 1. Sync legacy Drive folder files (if folder_ids provided)
    if folder_ids:
        if set(folder_ids) != set(CATEGORIES):
            missing = sorted(set(CATEGORIES) - set(folder_ids))
            raise SyncError(f"missing Drive folder mapping: {', '.join(missing)}")

        for category in CATEGORIES:
            category_remotes = {}
            for remote in _list_folder_files(service, category, folder_ids[category]):
                if not isinstance(remote.get("id"), str) or not remote["id"]:
                    raise SyncError(f"Drive file is missing an ID in {category}")
                name = remote.get("name")
                classification = classify_drive_file(category, name, remote.get("modifiedTime"))
                if classification is None:
                    ignored += 1
                    continue
                folded = name.casefold()
                if folded in category_remotes:
                    prev_remote = category_remotes[folded]
                    prev_time = prev_remote.get("modifiedTime") or ""
                    curr_time = remote.get("modifiedTime") or ""
                    if curr_time > prev_time or (
                        curr_time == prev_time and remote.get("id", "") > prev_remote.get("id", "")
                    ):
                        category_remotes[folded] = remote
                else:
                    category_remotes[folded] = remote

            for remote in category_remotes.values():
                name = remote.get("name")
                total_remote_files += 1
                if total_remote_files > max_batch_files:
                    raise SyncError(
                        f"total Drive reports exceed batch limit of {max_batch_files} files"
                    )

                try:
                    declared_size = int(remote.get("size", 0))
                except (TypeError, ValueError):
                    declared_size = 0
                total_remote_bytes += max(0, declared_size)
                if total_remote_bytes > max_batch_bytes:
                    raise SyncError(
                        f"total Drive reports size exceeds batch limit of {max_batch_bytes} bytes"
                    )

                relative = PurePosixPath("reports", category, name)
                relative_text = relative.as_posix()
                local_path = repo_root.joinpath(*relative.parts)

                if not _is_safe_parent_and_path(repo_root, category, local_path):
                    raise SyncError(f"unsafe report path or symlink ancestor: {relative_text}")

                previous = next_files.get(relative_text, {})
                remote_md5 = remote.get("md5Checksum")
                local_matches = False
                if local_path.is_file() and not local_path.is_symlink():
                    if remote_md5:
                        local_matches = _hash_file(local_path, "md5") == remote_md5
                    elif previous.get("sha256"):
                        local_matches = _hash_file(local_path, "sha256") == previous["sha256"]

                if local_matches:
                    content_sha256 = _hash_file(local_path, "sha256")
                    unchanged += 1
                else:
                    content = _download_file(service, remote, category, max_report_bytes)
                    content_sha256 = _hash_bytes(content, "sha256")
                    if local_path.is_file() and _hash_file(local_path, "sha256") == content_sha256:
                        unchanged += 1
                    else:
                        total_staged_bytes += len(content)
                        if total_staged_bytes > max_staged_bytes:
                            raise SyncError(
                                f"staged updates exceed batch limit of {max_staged_bytes} bytes"
                            )
                        staged[relative_text] = content
                        updated += 1

                next_files[relative_text] = _state_entry(remote, relative, content_sha256)

        for relative_text in sorted(staged):
            written_path = repo_root / relative_text
            _atomic_write_if_changed(written_path, staged[relative_text])
            if relative_text.lower().endswith((".md", ".txt")):
                runs_file = repo_root / RUNS_STATE_PATH
                render_markdown_file_to_html(written_path, written_path.parent.name, runs_file)

        next_state = {"schema_version": 1, "files": dict(sorted(next_files.items()))}
        _atomic_write_if_changed(state_file, _json_bytes(next_state))

    # 2. Sync Native Google Docs Markdown blocks
    if enable_native_docs:
        doc_updated, doc_skipped = sync_native_google_docs(
            service=service, repo_root=repo_root, doc_sources=doc_sources
        )
        updated += doc_updated
        unchanged += doc_skipped

    # 3. Build & update reports.json index
    runs_file = repo_root / RUNS_STATE_PATH
    runs_data = load_report_runs(runs_file)
    catalog = ReportCatalog.build_from_scan(repo_root, next_files, runs_data=runs_data)
    catalog.save(repo_root)
    print("REPORT_INDEX_UPDATED")
    print("BUILD_SUCCEEDED")

    return SyncResult(updated=updated, unchanged=unchanged, ignored=ignored)


def build_reports_index(repo_root, state_files, runs_data=None):
    return ReportCatalog.build_from_scan(repo_root, state_files, runs_data=runs_data).to_dict()


def create_drive_service():
    try:
        import google.auth
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise SyncError(
            "Google Drive dependencies are missing; install requirements-sync.txt"
        ) from exc
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Mirror reports from Google Docs and Google Drive folders"
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "--max-report-bytes",
        type=int,
        default=int(os.environ.get("MAX_REPORT_BYTES", DEFAULT_MAX_REPORT_BYTES)),
    )
    parser.add_argument(
        "--disable-native-docs",
        action="store_true",
        default=os.environ.get("ENABLE_NATIVE_GOOGLE_DOC_MARKDOWN", "true").lower()
        not in ("true", "1", "yes"),
        help="Disable native Google Docs canonical Markdown sync",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.max_report_bytes <= 0:
            raise SyncError("--max-report-bytes must be positive")
        folder_ids = resolve_folder_ids(os.environ)
        doc_sources = resolve_doc_sources(os.environ)
        result = sync_reports(
            service=create_drive_service(),
            repo_root=args.repo_root,
            folder_ids=folder_ids,
            doc_sources=doc_sources,
            max_report_bytes=args.max_report_bytes,
            enable_native_docs=not args.disable_native_docs,
        )
    except SyncError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"Sync complete: updated={result.updated} unchanged={result.unchanged} ignored={result.ignored}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
