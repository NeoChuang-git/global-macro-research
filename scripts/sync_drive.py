#!/usr/bin/env python3

"""Deterministically mirror reports from Google Docs and Google Drive folders."""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Tuple

from scripts.canonical_block import (
    CanonicalBlockError,
    determine_archive_filename,
    extract_latest_complete_report_block,
    parse_and_validate_canonical_block,
)
from scripts.markdown_renderer import render_markdown_to_html
from scripts.report_runs import (
    RUNS_STATE_PATH,
    is_run_id_processed,
    load_report_runs,
    record_report_run,
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


def _is_safe_parent_and_path(repo_root, category, local_path):
    repo_root = Path(repo_root).resolve()
    category_dir = repo_root / "reports" / category
    category_dir.mkdir(parents=True, exist_ok=True)
    category_root = category_dir.resolve()
    try:
        category_root.relative_to(repo_root)
    except (ValueError, RuntimeError):
        return False
    resolved_path = local_path.resolve()
    if not local_path.exists():
        resolved_parent = local_path.parent.resolve()
        try:
            resolved_parent.relative_to(category_root)
        except (ValueError, RuntimeError):
            return False
    else:
        try:
            resolved_path.relative_to(category_root)
        except (ValueError, RuntimeError):
            return False
    current = local_path.absolute()
    while True:
        if current.resolve() == repo_root:
            break
        if current.is_symlink():
            return False
        parent = current.parent
        if parent == current:
            break
        current = parent
    return True


def _valid_date(value):
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return value


def _date_from_name(name):
    match = DATE_PATTERN.search(name)
    if not match:
        return None
    return _valid_date("-".join(match.groups()))


def _date_from_modified_time(modified_time):
    if not modified_time or len(modified_time) < 10:
        return None
    return _valid_date(modified_time[:10])


def _display_title(name):
    stem = Path(name).stem
    stem = DATE_PATTERN.sub(" ", stem)
    title = re.sub(r"[_-]+", " ", stem)
    title = " ".join(title.split()) or "Untitled report"
    if title == "Global Macro Morning" or re.match(r"^Global Daily Brief(?:\s+\d{4})?$", title):
        return "Global Daily Brief"
    return title


def classify_drive_file(category, name, modified_time):
    if category not in CATEGORIES:
        raise SyncError(f"unknown report category: {category}")
    if not isinstance(name, str) or not name:
        raise SyncError(f"invalid Drive filename in {category}")
    if Path(name).name != name or "/" in name or "\\" in name:
        raise SyncError(f"unsafe Drive filename in {category}: {name}")
    if not name.lower().endswith(".html"):
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
    runs_data = load_report_runs(runs_path)

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

        # 2. Extract latest complete block
        block = extract_latest_complete_report_block(text)
        if not block:
            print(f"NO_CANONICAL_BLOCK_YET: {category}")
            continue

        # 3. Parse and validate
        try:
            metadata, body = parse_and_validate_canonical_block(block, expected_type)
            print(f"CANONICAL_BLOCK_FOUND: {metadata.get('run_id')} ({category})")
        except CanonicalBlockError as exc:
            print(f"CANONICAL_BLOCK_INVALID: {category}: {exc}", file=sys.stderr)
            continue

        run_id = metadata["run_id"]

        # 4. Check idempotency
        if is_run_id_processed(runs_data, run_id):
            print(f"RUN_ID_PREEXISTING: {run_id}")
            skipped_count += 1
            continue

        # 5. Determine filenames and paths
        category_dir = repo_root / "reports" / category
        category_dir.mkdir(parents=True, exist_ok=True)
        existing_filenames = {p.name for p in category_dir.iterdir() if p.is_file()}

        md_filename = determine_archive_filename(metadata, existing_filenames)
        html_filename = Path(md_filename).with_suffix(".html").name

        md_rel = PurePosixPath("reports", category, md_filename)
        html_rel = PurePosixPath("reports", category, html_filename)

        md_full = repo_root.joinpath(*md_rel.parts)
        html_full = repo_root.joinpath(*html_rel.parts)

        # 6. Archive canonical Markdown snapshot
        md_bytes = (f"<<<REPORT_BEGIN>>>\n{block}\n<<<REPORT_END>>>\n").encode("utf-8")
        _atomic_write_if_changed(md_full, md_bytes)
        md_sha256 = _hash_bytes(md_bytes, "sha256")
        print(f"MARKDOWN_ARCHIVED: {md_rel.as_posix()} ({md_sha256[:8]})")

        # 7. Render HTML
        html_content = render_markdown_to_html(body, metadata)
        html_bytes = html_content.encode("utf-8")
        _atomic_write_if_changed(html_full, html_bytes)
        html_sha256 = _hash_bytes(html_bytes, "sha256")
        print(f"MARKDOWN_RENDERED: {html_rel.as_posix()} ({html_sha256[:8]})")

        def _iso_str(val):
            if val is None:
                return None
            if hasattr(val, "isoformat"):
                return val.isoformat()
            return str(val)

        # 8. Update report runs manifest
        run_record = {
            "run_id": run_id,
            "report_type": metadata["report_type"],
            "title": metadata["title"],
            "generated_at_taipei": _iso_str(metadata.get("generated_at_taipei")),
            "coverage_start_taipei": _iso_str(metadata.get("coverage_start_taipei")),
            "coverage_end_taipei": _iso_str(metadata.get("coverage_end_taipei")),
            "risk_light": metadata.get("risk_light"),
            "topic": metadata.get("topic"),
            "slug": metadata.get("slug"),
            "source_document_id": doc_id,
            "markdown_path": md_rel.as_posix(),
            "markdown_sha256": md_sha256,
            "html_path": html_rel.as_posix(),
            "html_sha256": html_sha256,
        }
        runs_data = record_report_run(runs_path, run_record)
        archived_count += 1

    return archived_count, skipped_count


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
            _atomic_write_if_changed(repo_root / relative_text, staged[relative_text])

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
    index = build_reports_index(repo_root, next_files, runs_data=runs_data)
    _atomic_write_if_changed(repo_root / INDEX_PATH, _json_bytes(index))
    print("REPORT_INDEX_UPDATED")
    print("BUILD_SUCCEEDED")

    return SyncResult(updated=updated, unchanged=unchanged, ignored=ignored)


def build_reports_index(repo_root, state_files, runs_data=None):
    repo_root = Path(repo_root)
    reports = []
    
    # Map html_path to run_record if available
    runs_by_html = {}
    if runs_data and isinstance(runs_data.get("runs"), dict):
        for run_rec in runs_data["runs"].values():
            html_p = run_rec.get("html_path")
            if html_p:
                runs_by_html[html_p] = run_rec

    for category in CATEGORIES:
        category_root = repo_root / "reports" / category
        if not category_root.exists():
            continue
        for path in sorted(category_root.rglob("*")):
            if not path.is_file() or path.is_symlink() or not path.name.lower().endswith(".html"):
                continue
            if not _is_safe_parent_and_path(repo_root, category, path):
                continue
            relative = path.relative_to(repo_root).as_posix()
            metadata = state_files.get(relative, {})
            classification = classify_drive_file(
                category, path.name, metadata.get("modified_time")
            )
            file_sha256 = _hash_file(path, "sha256")

            # Check if this report was generated from a canonical Markdown run
            run_rec = runs_by_html.get(relative)
            if run_rec:
                date_val = str(classification["date"] or str(run_rec.get("generated_at_taipei", ""))[:10])
                entry = {
                    "category": category,
                    "date": date_val,
                    "file": relative,
                    "modified_time": str(metadata.get("modified_time") or run_rec.get("generated_at_taipei") or ""),
                    "sha256": file_sha256,
                    "title": run_rec.get("title") or classification["title"],
                    "run_id": run_rec.get("run_id"),
                    "report_type": run_rec.get("report_type"),
                    "source_kind": "google_doc_markdown",
                    "source_document_id": run_rec.get("source_document_id"),
                    "generated_at_taipei": str(run_rec.get("generated_at_taipei") or ""),
                    "coverage_start_taipei": str(run_rec.get("coverage_start_taipei") or ""),
                    "coverage_end_taipei": str(run_rec.get("coverage_end_taipei") or ""),
                    "risk_light": run_rec.get("risk_light"),
                    "topic": run_rec.get("topic"),
                    "slug": run_rec.get("slug"),
                    "markdown_path": run_rec.get("markdown_path"),
                    "markdown_sha256": run_rec.get("markdown_sha256"),
                    "html_path": relative,
                }
            else:
                # Legacy HTML report
                entry = {
                    "category": category,
                    "date": classification["date"],
                    "file": relative,
                    "modified_time": str(metadata.get("modified_time") or "") if metadata.get("modified_time") else None,
                    "sha256": file_sha256,
                    "title": classification["title"],
                }
                # Log preservation of legacy HTML
                # print(f"LEGACY_HTML_PRESERVED: {relative}")

            reports.append(entry)

    reports.sort(key=lambda item: (item["title"].casefold(), item["file"]))
    reports.sort(key=lambda item: CATEGORIES.index(item["category"]))
    reports.sort(key=lambda item: str(item.get("modified_time") or ""), reverse=True)
    reports.sort(key=lambda item: str(item.get("date") or ""), reverse=True)
    latest = {category: None for category in CATEGORIES}
    for report in reports:
        if latest[report["category"]] is None:
            latest[report["category"]] = report
    return {"schema_version": 1, "reports": reports, "latest": latest}


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
