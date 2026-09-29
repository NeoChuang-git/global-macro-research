"""
Report Catalog Module (Deep Module).

Encapsulates report discovery, metadata extraction, index construction,
and querying behind a high-leverage interface:
- Scans report filesystem trees safely
- Extracts titles from companion Markdown frontmatter, H1 tags, or HTML titles
- Correlates with report_runs.json manifests
- Produces deterministic, sorted catalog entries
- Atomically persists data/reports.json (Schema Version 1)
- Exposes typed query interfaces for downstream consumers
"""

from __future__ import annotations

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
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from scripts.report_runs import RUNS_STATE_PATH, load_report_runs

CATEGORIES = ("early-warning", "daily", "weekly")
INDEX_PATH = Path("data/reports.json")
DATE_PATTERN = re.compile(r"(?<!\d)(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)(?!\d)")

GENERIC_TITLES: Set[str] = {
    "global daily brief",
    "global macro morning",
    "weekly strategy",
    "weekly global macro strategy",
    "global macro early warning",
    "untitled report",
}


class CatalogError(RuntimeError):
    """Failure discovering, validating, or serializing the report catalog."""


@dataclass(frozen=True)
class CatalogEntry:
    category: str
    date: Optional[str]
    file: str
    title: str
    sha256: str
    modified_time: Optional[str] = None
    run_id: Optional[str] = None
    report_type: Optional[str] = None
    source_kind: Optional[str] = None
    source_document_id: Optional[str] = None
    generated_at_taipei: Optional[str] = None
    coverage_start_taipei: Optional[str] = None
    coverage_end_taipei: Optional[str] = None
    risk_light: Optional[str] = None
    topic: Optional[str] = None
    slug: Optional[str] = None
    markdown_path: Optional[str] = None
    markdown_sha256: Optional[str] = None
    html_path: Optional[str] = None

    @property
    def is_canonical(self) -> bool:
        return bool(self.run_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry into Schema Version 1 dictionary representation."""
        if self.run_id:
            return {
                "category": self.category,
                "coverage_end_taipei": self.coverage_end_taipei or "",
                "coverage_start_taipei": self.coverage_start_taipei or "",
                "date": self.date,
                "file": self.file,
                "generated_at_taipei": self.generated_at_taipei or "",
                "html_path": self.html_path or self.file,
                "markdown_path": self.markdown_path,
                "markdown_sha256": self.markdown_sha256,
                "modified_time": self.modified_time or "",
                "report_type": self.report_type,
                "risk_light": self.risk_light,
                "run_id": self.run_id,
                "sha256": self.sha256,
                "slug": self.slug,
                "source_document_id": self.source_document_id,
                "source_kind": self.source_kind or "google_doc_markdown",
                "title": self.title,
                "topic": self.topic,
            }
        return {
            "category": self.category,
            "date": self.date,
            "file": self.file,
            "modified_time": self.modified_time if self.modified_time else None,
            "sha256": self.sha256,
            "title": self.title,
        }


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


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    ).encode("utf-8")


def is_safe_parent_and_path(repo_root: Path, category: str, local_path: Path) -> bool:
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


def valid_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return value


def date_from_name(name: str) -> Optional[str]:
    match = DATE_PATTERN.search(name)
    if not match:
        return None
    return valid_date("-".join(match.groups()))


def date_from_modified_time(modified_time: Optional[str]) -> Optional[str]:
    if not modified_time or len(modified_time) < 10:
        return None
    return valid_date(modified_time[:10])


def display_title(name: str) -> str:
    stem = Path(name).stem
    stem = DATE_PATTERN.sub(" ", stem)
    title = re.sub(r"[_-]+", " ", stem)
    title = " ".join(title.split()) or "Untitled report"
    if title == "Global Macro Morning" or re.match(r"^Global Daily Brief(?:\s+\d{4})?$", title):
        return "Global Daily Brief"
    return title


def is_generic_title(title: Optional[str]) -> bool:
    if not title:
        return True
    t = title.strip().lower()
    return t in GENERIC_TITLES


def extract_report_title(path: Path) -> Optional[str]:
    """Extract a descriptive title from companion markdown or HTML content."""
    md_path = path.with_suffix(".md")
    if not md_path.is_file():
        txt_path = path.with_suffix(".txt")
        if txt_path.is_file():
            md_path = txt_path

    if md_path.is_file():
        try:
            raw_md = md_path.read_text(encoding="utf-8", errors="replace")
            fm_match = re.search(r"^\s*title:\s*(.+)$", raw_md, re.MULTILINE)
            if fm_match:
                val = fm_match.group(1).strip().strip("'\"")
                if val:
                    return val
            h1_match = re.search(r"^\s*\\?#\s+(.+)$", raw_md, re.MULTILINE)
            if h1_match:
                val = h1_match.group(1).strip()
                if val:
                    return val
        except Exception:
            pass

    try:
        raw_html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    m_h1 = re.search(r"<h1[^>]*>(.*?)</h1>", raw_html, re.IGNORECASE | re.DOTALL)
    if m_h1:
        clean = html.unescape(re.sub(r"<[^>]+>", "", m_h1.group(1))).strip()
        clean = " ".join(clean.split())
        if clean:
            return clean

    m_title = re.search(r"<title[^>]*>(.*?)</title>", raw_html, re.IGNORECASE | re.DOTALL)
    if m_title:
        clean = html.unescape(re.sub(r"<[^>]+>", "", m_title.group(1))).strip()
        clean = re.sub(r"\s*[·•|-]\s*N/A\s*$", "", clean, flags=re.IGNORECASE)
        clean = " ".join(clean.split())
        if clean:
            return clean

    return None


def classify_drive_file(
    category: str, name: str, modified_time: Optional[str]
) -> Dict[str, Any]:
    file_date = date_from_name(name) or date_from_modified_time(modified_time)
    title = display_title(name)
    return {
        "category": category,
        "date": file_date,
        "title": title,
    }


class ReportCatalog:
    """Centralized report catalog providing indexing, querying, and serialization."""

    def __init__(
        self,
        reports: Sequence[CatalogEntry],
        latest: Mapping[str, Optional[CatalogEntry]],
        schema_version: int = 1,
    ) -> None:
        self._reports: List[CatalogEntry] = list(reports)
        self._latest: Dict[str, Optional[CatalogEntry]] = dict(latest)
        self._schema_version = schema_version

    @property
    def reports(self) -> List[CatalogEntry]:
        return list(self._reports)

    @property
    def latest(self) -> Dict[str, Optional[CatalogEntry]]:
        return dict(self._latest)

    def get_reports(self, category: Optional[str] = None) -> List[CatalogEntry]:
        """Return all reports, optionally filtered by category."""
        if category:
            return [r for r in self._reports if r.category == category]
        return list(self._reports)

    def get_latest(self, category: str) -> Optional[CatalogEntry]:
        """Return the latest report for the given category."""
        return self._latest.get(category)

    def get_entry_by_file(self, relative_path: str) -> Optional[CatalogEntry]:
        """Lookup an entry by its relative posix file path."""
        for r in self._reports:
            if r.file == relative_path:
                return r
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete catalog index to schema version 1 dictionary."""
        return {
            "schema_version": self._schema_version,
            "reports": [r.to_dict() for r in self._reports],
            "latest": {
                category: self._latest[category].to_dict() if self._latest.get(category) else None
                for category in CATEGORIES
            },
        }

    def save(self, repo_root: Path, target_path: Optional[Path] = None) -> bool:
        """Atomically persist data/reports.json if content changed."""
        dest = target_path or (Path(repo_root) / INDEX_PATH)
        dest.parent.mkdir(parents=True, exist_ok=True)
        return atomic_write_if_changed(dest, json_bytes(self.to_dict()))

    @classmethod
    def load_from_disk(cls, repo_root: Path, index_path: Optional[Path] = None) -> ReportCatalog:
        """Load catalog from an existing data/reports.json file."""
        path = index_path or (Path(repo_root) / INDEX_PATH)
        if not path.is_file():
            raise CatalogError(f"reports index file not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CatalogError(f"invalid reports index JSON: {exc}") from exc

        if data.get("schema_version") != 1 or not isinstance(data.get("reports"), list):
            raise CatalogError(f"unsupported reports index schema in {path}")

        raw_latest = data.get("latest")
        if not isinstance(raw_latest, dict) or set(raw_latest.keys()) != set(CATEGORIES):
            raise CatalogError(f"invalid latest-report index in {path}")

        entries: List[CatalogEntry] = []
        for r in data["reports"]:
            if not isinstance(r, dict):
                raise CatalogError(f"invalid non-object report entry in {path}")
            if "category" not in r or "file" not in r or "title" not in r or "sha256" not in r:
                raise CatalogError(f"missing required report entry fields in {path}")
            entries.append(
                CatalogEntry(
                    category=r["category"],
                    date=r.get("date"),
                    file=r["file"],
                    title=r["title"],
                    sha256=r["sha256"],
                    modified_time=r.get("modified_time"),
                    run_id=r.get("run_id"),
                    report_type=r.get("report_type"),
                    source_kind=r.get("source_kind"),
                    source_document_id=r.get("source_document_id"),
                    generated_at_taipei=r.get("generated_at_taipei"),
                    coverage_start_taipei=r.get("coverage_start_taipei"),
                    coverage_end_taipei=r.get("coverage_end_taipei"),
                    risk_light=r.get("risk_light"),
                    topic=r.get("topic"),
                    slug=r.get("slug"),
                    markdown_path=r.get("markdown_path"),
                    markdown_sha256=r.get("markdown_sha256"),
                    html_path=r.get("html_path"),
                )
            )

        latest: Dict[str, Optional[CatalogEntry]] = {c: None for c in CATEGORIES}
        raw_latest = data.get("latest", {})
        for cat in CATEGORIES:
            raw_entry = raw_latest.get(cat)
            if raw_entry:
                latest[cat] = CatalogEntry(
                    category=raw_entry["category"],
                    date=raw_entry.get("date"),
                    file=raw_entry["file"],
                    title=raw_entry["title"],
                    sha256=raw_entry["sha256"],
                    modified_time=raw_entry.get("modified_time"),
                    run_id=raw_entry.get("run_id"),
                    report_type=raw_entry.get("report_type"),
                    source_kind=raw_entry.get("source_kind"),
                    source_document_id=raw_entry.get("source_document_id"),
                    generated_at_taipei=raw_entry.get("generated_at_taipei"),
                    coverage_start_taipei=raw_entry.get("coverage_start_taipei"),
                    coverage_end_taipei=raw_entry.get("coverage_end_taipei"),
                    risk_light=raw_entry.get("risk_light"),
                    topic=raw_entry.get("topic"),
                    slug=raw_entry.get("slug"),
                    markdown_path=raw_entry.get("markdown_path"),
                    markdown_sha256=raw_entry.get("markdown_sha256"),
                    html_path=raw_entry.get("html_path"),
                )

        return cls(reports=entries, latest=latest, schema_version=data.get("schema_version", 1))

    @classmethod
    def build_from_scan(
        cls,
        repo_root: Path,
        state_files: Optional[Dict[str, Any]] = None,
        runs_data: Optional[Dict[str, Any]] = None,
    ) -> ReportCatalog:
        """Scan report trees, extract metadata, sort, and construct catalog."""
        repo_root = Path(repo_root).resolve()
        state = state_files or {}
        
        runs_by_html: Dict[str, Dict[str, Any]] = {}
        if runs_data and isinstance(runs_data.get("runs"), dict):
            for run_rec in runs_data["runs"].values():
                html_p = run_rec.get("html_path")
                if html_p:
                    runs_by_html[html_p] = run_rec

        entries: List[CatalogEntry] = []

        for category in CATEGORIES:
            category_root = repo_root / "reports" / category
            if not category_root.exists():
                continue
            for path in sorted(category_root.rglob("*")):
                if not path.is_file() or path.is_symlink() or not path.name.lower().endswith(".html"):
                    continue
                if not is_safe_parent_and_path(repo_root, category, path):
                    continue
                relative = path.relative_to(repo_root).as_posix()
                metadata = state.get(relative, {})
                classification = classify_drive_file(
                    category, path.name, metadata.get("modified_time")
                )
                file_sha256 = hash_file(path, "sha256")

                extracted_title = extract_report_title(path)
                run_rec = runs_by_html.get(relative)

                if run_rec:
                    date_val = str(classification["date"] or str(run_rec.get("generated_at_taipei", ""))[:10])
                    resolved_title = (
                        run_rec.get("title")
                        if (run_rec.get("title") and not is_generic_title(run_rec.get("title")))
                        else (extracted_title or run_rec.get("title") or classification["title"])
                    )
                    entry = CatalogEntry(
                        category=category,
                        date=date_val,
                        file=relative,
                        title=resolved_title,
                        sha256=file_sha256,
                        modified_time=str(metadata.get("modified_time") or run_rec.get("generated_at_taipei") or ""),
                        run_id=run_rec.get("run_id"),
                        report_type=run_rec.get("report_type"),
                        source_kind="google_doc_markdown",
                        source_document_id=run_rec.get("source_document_id"),
                        generated_at_taipei=str(run_rec.get("generated_at_taipei") or ""),
                        coverage_start_taipei=str(run_rec.get("coverage_start_taipei") or ""),
                        coverage_end_taipei=str(run_rec.get("coverage_end_taipei") or ""),
                        risk_light=run_rec.get("risk_light"),
                        topic=run_rec.get("topic"),
                        slug=run_rec.get("slug"),
                        markdown_path=run_rec.get("markdown_path"),
                        markdown_sha256=run_rec.get("markdown_sha256"),
                        html_path=relative,
                    )
                else:
                    # Legacy HTML report
                    entry = CatalogEntry(
                        category=category,
                        date=classification["date"],
                        file=relative,
                        title=extracted_title or classification["title"],
                        sha256=file_sha256,
                        modified_time=str(metadata.get("modified_time") or "") if metadata.get("modified_time") else None,
                    )

                entries.append(entry)

        # Deterministic multi-key sorting
        entries.sort(key=lambda item: (item.title.casefold(), item.file))
        entries.sort(key=lambda item: CATEGORIES.index(item.category))
        entries.sort(key=lambda item: str(item.modified_time or ""), reverse=True)
        entries.sort(key=lambda item: str(item.date or ""), reverse=True)

        latest: Dict[str, Optional[CatalogEntry]] = {c: None for c in CATEGORIES}
        for item in entries:
            if latest[item.category] is None:
                latest[item.category] = item

        return cls(reports=entries, latest=latest)
