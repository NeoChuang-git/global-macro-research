"""
Report Ingestion Module (Deep Module).

Consolidates document ingestion behind a unified, high-leverage interface:
- Extracts canonical blocks or detects plain markdown/text
- Validates canonical structure (metadata headers, required sections)
- Evaluates idempotency against report_runs.json
- Determines archive paths
- Atomically archives canonical/fallback markdown snapshot
- Renders institutional HTML
- Atomically archives HTML artifact
- Records run manifest entry
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Optional, Union

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

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


class IngestionStatus(str, Enum):
    ARCHIVED_CANONICAL = "ARCHIVED_CANONICAL"
    ARCHIVED_FALLBACK = "ARCHIVED_FALLBACK"
    SKIPPED_EXISTING = "SKIPPED_EXISTING"
    NO_CANONICAL_BLOCK = "NO_CANONICAL_BLOCK"
    CANONICAL_BLOCK_INVALID = "CANONICAL_BLOCK_INVALID"
    FAILED = "FAILED"


@dataclass(frozen=True)
class IngestionResult:
    status: IngestionStatus
    run_id: Optional[str] = None
    title: Optional[str] = None
    report_type: Optional[str] = None
    category: str = ""
    markdown_path: Optional[Path] = None
    html_path: Optional[Path] = None
    markdown_rel: Optional[str] = None
    html_rel: Optional[str] = None
    markdown_sha256: Optional[str] = None
    html_sha256: Optional[str] = None
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status in (
            IngestionStatus.ARCHIVED_CANONICAL,
            IngestionStatus.ARCHIVED_FALLBACK,
        )

    @property
    def is_skipped(self) -> bool:
        return self.status == IngestionStatus.SKIPPED_EXISTING


def hash_bytes(content: bytes, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    digest.update(content)
    return digest.hexdigest()


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_if_changed(path: Path, content: bytes) -> bool:
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
            try:
                temporary.unlink()
            except OSError:
                pass
    return True


def _iso_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


def infer_expected_type(category: str) -> Optional[str]:
    if category == "early-warning":
        return "MACRO_TAIWAN_EARLY_WARNING"
    if category == "daily":
        return "GLOBAL_DAILY_BRIEF"
    if category == "weekly":
        return "WEEKLY_STRATEGY"
    return None


def extract_fallback_title(text: str, default_name: Optional[str] = None) -> str:
    fm_match = re.search(r"^\s*title:\s*(.+)$", text, re.MULTILINE)
    if fm_match:
        val = fm_match.group(1).strip().strip("'\"")
        if val:
            return val
    h1_match = re.search(r"^\s*\\?#\s+(.+)$", text, flags=re.MULTILINE)
    if h1_match:
        val = h1_match.group(1).strip()
        if val:
            return val
    if default_name:
        stem = Path(default_name).stem
        clean = re.sub(r"[_-]+", " ", stem).strip()
        if clean:
            return clean
    return "Untitled report"


def ingest_report_content(
    content: Union[str, bytes],
    category: str,
    repo_root: Path,
    source_document_id: Optional[str] = None,
    original_filename: Optional[str] = None,
    expected_type: Optional[str] = None,
    runs_path: Optional[Path] = None,
    force: bool = False,
    allow_fallback: bool = True,
) -> IngestionResult:
    """
    Ingest document content (raw string or bytes) into repository artifacts.

    Handles canonical extraction, metadata parsing, idempotency check,
    markdown archiving, HTML rendering, and run manifest tracking.
    """
    repo_root = Path(repo_root).resolve()
    runs_file = runs_path or (repo_root / RUNS_STATE_PATH)
    runs_data = load_report_runs(runs_file)
    expected_report_type = expected_type or infer_expected_type(category)

    if isinstance(content, bytes):
        text = content.decode("utf-8", errors="replace")
    else:
        text = str(content)

    category_dir = repo_root / "reports" / category
    category_dir.mkdir(parents=True, exist_ok=True)
    existing_filenames = {p.name for p in category_dir.iterdir() if p.is_file()}

    # 1. Try canonical report block extraction
    block = extract_latest_complete_report_block(text)
    canonical_metadata: Optional[Dict[str, Any]] = None
    canonical_body: Optional[str] = None
    canonical_error: Optional[Exception] = None

    if block:
        try:
            canonical_metadata, canonical_body = parse_and_validate_canonical_block(
                block, expected_report_type
            )
        except CanonicalBlockError as exc:
            canonical_error = exc
    else:
        if not allow_fallback:
            return IngestionResult(
                status=IngestionStatus.NO_CANONICAL_BLOCK,
                category=category,
            )

    if canonical_error and not allow_fallback:
        return IngestionResult(
            status=IngestionStatus.CANONICAL_BLOCK_INVALID,
            category=category,
            error=str(canonical_error),
        )

    # Path A: Valid Canonical Report Block
    if canonical_metadata and canonical_body is not None and block:
        run_id = canonical_metadata["run_id"]

        if not force and is_run_id_processed(runs_data, run_id):
            return IngestionResult(
                status=IngestionStatus.SKIPPED_EXISTING,
                run_id=run_id,
                title=canonical_metadata.get("title"),
                report_type=canonical_metadata.get("report_type"),
                category=category,
            )

        if original_filename:
            md_filename = Path(original_filename).with_suffix(".md").name
        else:
            md_filename = determine_archive_filename(canonical_metadata, existing_filenames)

        html_filename = Path(md_filename).with_suffix(".html").name
        md_rel = PurePosixPath("reports", category, md_filename)
        html_rel = PurePosixPath("reports", category, html_filename)
        md_full = repo_root.joinpath(*md_rel.parts)
        html_full = repo_root.joinpath(*html_rel.parts)

        # Archive canonical Markdown snapshot
        md_bytes = (f"<<<REPORT_BEGIN>>>\n{block}\n<<<REPORT_END>>>\n").encode("utf-8")
        atomic_write_if_changed(md_full, md_bytes)
        md_sha256 = hash_bytes(md_bytes, "sha256")

        # Render HTML
        html_content = render_markdown_to_html(canonical_body, canonical_metadata)
        html_bytes = html_content.encode("utf-8")
        atomic_write_if_changed(html_full, html_bytes)
        html_sha256 = hash_bytes(html_bytes, "sha256")

        # Record run in manifest
        run_record = {
            "run_id": run_id,
            "report_type": canonical_metadata["report_type"],
            "title": canonical_metadata["title"],
            "generated_at_taipei": _iso_str(canonical_metadata.get("generated_at_taipei")),
            "coverage_start_taipei": _iso_str(canonical_metadata.get("coverage_start_taipei")),
            "coverage_end_taipei": _iso_str(canonical_metadata.get("coverage_end_taipei")),
            "risk_light": canonical_metadata.get("risk_light"),
            "topic": canonical_metadata.get("topic"),
            "slug": canonical_metadata.get("slug"),
            "source_document_id": source_document_id,
            "markdown_path": md_rel.as_posix(),
            "markdown_sha256": md_sha256,
            "html_path": html_rel.as_posix(),
            "html_sha256": html_sha256,
        }
        record_report_run(runs_file, run_record)

        return IngestionResult(
            status=IngestionStatus.ARCHIVED_CANONICAL,
            run_id=run_id,
            title=canonical_metadata["title"],
            report_type=canonical_metadata["report_type"],
            category=category,
            markdown_path=md_full,
            html_path=html_full,
            markdown_rel=md_rel.as_posix(),
            html_rel=html_rel.as_posix(),
            markdown_sha256=md_sha256,
            html_sha256=html_sha256,
        )

    # Path B: Fallback Markdown Report
    title = extract_fallback_title(text, original_filename)
    report_type = expected_report_type or "GLOBAL_DAILY_BRIEF"
    
    stem = Path(original_filename).stem if original_filename else f"{category}_{datetime.now().strftime('%Y-%m-%d')}"
    run_id = f"{category.upper()}-{stem}"

    if not force and is_run_id_processed(runs_data, run_id):
        return IngestionResult(
            status=IngestionStatus.SKIPPED_EXISTING,
            run_id=run_id,
            title=title,
            report_type=report_type,
            category=category,
        )

    md_filename = Path(stem).with_suffix(".md").name
    html_filename = Path(stem).with_suffix(".html").name
    md_rel = PurePosixPath("reports", category, md_filename)
    html_rel = PurePosixPath("reports", category, html_filename)
    md_full = repo_root.joinpath(*md_rel.parts)
    html_full = repo_root.joinpath(*html_rel.parts)

    md_bytes = text.encode("utf-8")
    atomic_write_if_changed(md_full, md_bytes)
    md_sha256 = hash_bytes(md_bytes, "sha256")

    meta = {
        "title": title,
        "report_type": report_type,
        "run_id": run_id,
    }
    html_content = render_markdown_to_html(text, meta)
    html_bytes = html_content.encode("utf-8")
    atomic_write_if_changed(html_full, html_bytes)
    html_sha256 = hash_bytes(html_bytes, "sha256")

    run_record = {
        "run_id": run_id,
        "report_type": report_type,
        "title": title,
        "generated_at_taipei": None,
        "coverage_start_taipei": None,
        "coverage_end_taipei": None,
        "risk_light": None,
        "topic": None,
        "slug": None,
        "source_document_id": source_document_id,
        "markdown_path": md_rel.as_posix(),
        "markdown_sha256": md_sha256,
        "html_path": html_rel.as_posix(),
        "html_sha256": html_sha256,
    }
    record_report_run(runs_file, run_record)

    return IngestionResult(
        status=IngestionStatus.ARCHIVED_FALLBACK,
        run_id=run_id,
        title=title,
        report_type=report_type,
        category=category,
        markdown_path=md_full,
        html_path=html_full,
        markdown_rel=md_rel.as_posix(),
        html_rel=html_rel.as_posix(),
        markdown_sha256=md_sha256,
        html_sha256=html_sha256,
    )


def ingest_report_file(
    file_path: Path,
    category: str,
    repo_root: Path,
    runs_path: Optional[Path] = None,
    force: bool = False,
    allow_fallback: bool = True,
) -> IngestionResult:
    """
    Ingest a local report file on disk (.md or .txt), rendering companion .html
    and updating report_runs.json.
    """
    file_path = Path(file_path).resolve()
    raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    return ingest_report_content(
        content=raw_text,
        category=category,
        repo_root=repo_root,
        original_filename=file_path.name,
        runs_path=runs_path,
        force=force,
        allow_fallback=allow_fallback,
    )
