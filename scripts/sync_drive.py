#!/usr/bin/env python3

"""Deterministically mirror HTML reports from three Google Drive folders."""

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
from typing import Dict, Mapping, Optional


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
    if title == "Global Macro Morning":
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
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


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


def sync_reports(
    service,
    repo_root,
    folder_ids,
    max_report_bytes=DEFAULT_MAX_REPORT_BYTES,
    max_batch_files=DEFAULT_MAX_BATCH_FILES,
    max_batch_bytes=DEFAULT_MAX_BATCH_BYTES,
    max_staged_bytes=DEFAULT_MAX_STAGED_BYTES,
):
    repo_root = Path(repo_root)
    if set(folder_ids) != set(CATEGORIES):
        missing = sorted(set(CATEGORIES) - set(folder_ids))
        raise SyncError(f"missing Drive folder mapping: {', '.join(missing)}")

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

    for category in CATEGORIES:
        seen_names = {}
        for remote in _list_folder_files(service, category, folder_ids[category]):
            if not isinstance(remote.get("id"), str) or not remote["id"]:
                raise SyncError(f"Drive file is missing an ID in {category}")
            name = remote.get("name")
            classification = classify_drive_file(category, name, remote.get("modifiedTime"))
            if classification is None:
                ignored += 1
                continue
            folded = name.casefold()
            if folded in seen_names:
                raise SyncError(
                    f"duplicate Drive HTML filename in {category}: {seen_names[folded]} / {name}"
                )
            seen_names[folded] = name

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
    index = build_reports_index(repo_root, next_state["files"])
    _atomic_write_if_changed(repo_root / INDEX_PATH, _json_bytes(index))
    return SyncResult(updated=updated, unchanged=unchanged, ignored=ignored)


def build_reports_index(repo_root, state_files):
    repo_root = Path(repo_root)
    reports = []
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
            reports.append(
                {
                    "category": category,
                    "date": classification["date"],
                    "file": relative,
                    "modified_time": metadata.get("modified_time"),
                    "sha256": metadata.get("sha256") or _hash_file(path, "sha256"),
                    "title": classification["title"],
                }
            )

    reports.sort(key=lambda item: (item["title"].casefold(), item["file"]))
    reports.sort(key=lambda item: CATEGORIES.index(item["category"]))
    reports.sort(key=lambda item: item["modified_time"] or "", reverse=True)
    reports.sort(key=lambda item: item["date"] or "", reverse=True)
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
        description="Mirror HTML reports from the three configured Google Drive folders"
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument(
        "--max-report-bytes",
        type=int,
        default=int(os.environ.get("MAX_REPORT_BYTES", DEFAULT_MAX_REPORT_BYTES)),
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.max_report_bytes <= 0:
            raise SyncError("--max-report-bytes must be positive")
        folder_ids = resolve_folder_ids(os.environ)
        result = sync_reports(
            create_drive_service(), args.repo_root, folder_ids, args.max_report_bytes
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
