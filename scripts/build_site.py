#!/usr/bin/env python3

"""Build the minimal static artifact deployed to GitHub Pages."""

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
STATIC_FILES = (
    "index.html",
    "archive.html",
    "report.html",
    ".nojekyll",
    "assets/favicon.svg",
    "assets/css/app.css",
    "assets/js/app.js",
    "assets/js/archive.js",
    "assets/js/report.js",
    "data/reports.json",
)


class BuildError(RuntimeError):
    """The static site cannot be built safely."""


def _validated_report_path(repo_root, value):
    if not isinstance(value, str):
        raise BuildError("unsafe non-string report path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or len(pure.parts) < 3:
        raise BuildError(f"unsafe report path: {value}")
    if pure.parts[0] != "reports" or pure.parts[1] not in {
        "early-warning",
        "morning",
        "weekly",
    }:
        raise BuildError(f"unsafe report path: {value}")
    if pure.suffix.lower() != ".html":
        raise BuildError(f"unsafe report extension: {value}")
    source = repo_root.joinpath(*pure.parts)
    if not source.is_file() or source.is_symlink():
        raise BuildError(f"missing indexed report: {value}")
    
    resolved_root = repo_root.resolve()
    category_root = (resolved_root / "reports" / pure.parts[1]).resolve()
    try:
        source.resolve().relative_to(category_root)
    except (ValueError, RuntimeError):
        raise BuildError(f"unsafe report path resolves outside report root: {value}")

    current = source.absolute()
    while True:
        if current.resolve() == resolved_root:
            break
        if current.is_symlink():
            raise BuildError(f"unsafe symlink ancestor in report path: {value}")
        parent = current.parent
        if parent == current:
            break
        current = parent

    return pure, source


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_site(repo_root, output):
    repo_root = Path(repo_root).resolve()
    output = Path(output).resolve()
    if output.parent != repo_root or output.name != "_site":
        raise BuildError("output must be the repository's _site directory")

    index_path = repo_root / "data" / "reports.json"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError(f"invalid reports index: {exc}") from exc
    if index.get("schema_version") != 1 or not isinstance(index.get("reports"), list):
        raise BuildError("unsupported reports index schema")
    latest = index.get("latest")
    categories = {"early-warning", "morning", "weekly"}
    if not isinstance(latest, dict) or set(latest) != categories:
        raise BuildError("invalid latest-report index")

    validated_reports = []
    indexed_files = set()
    for report in index["reports"]:
        if not isinstance(report, dict):
            raise BuildError("invalid non-object report entry")
        relative, source = _validated_report_path(repo_root, report.get("file"))
        if relative.as_posix() in indexed_files:
            raise BuildError(f"duplicate indexed report: {relative.as_posix()}")
        expected_sha256 = report.get("sha256")
        if (
            not isinstance(expected_sha256, str)
            or len(expected_sha256) != 64
            or any(character not in "0123456789abcdef" for character in expected_sha256)
        ):
            raise BuildError(f"invalid report checksum: {relative.as_posix()}")
        if _sha256(source) != expected_sha256:
            raise BuildError(f"report checksum mismatch: {relative.as_posix()}")
        indexed_files.add(relative.as_posix())
        validated_reports.append((relative, source))

    for category, report in latest.items():
        if report is None:
            continue
        if not isinstance(report, dict) or report.get("category") != category:
            raise BuildError(f"invalid latest report for {category}")
        if report.get("file") not in indexed_files:
            raise BuildError(f"latest report is not indexed for {category}")

    temporary = Path(tempfile.mkdtemp(prefix=".site-build-", dir=repo_root))
    try:
        for relative_text in STATIC_FILES:
            source = repo_root / relative_text
            if not source.is_file() or source.is_symlink():
                raise BuildError(f"missing static site file: {relative_text}")
            destination = temporary / relative_text
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        for relative, source in validated_reports:
            destination = temporary.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        if output.is_symlink():
            raise BuildError("output cannot be a symlink")
        if output.exists():
            shutil.rmtree(output)
        temporary.replace(output)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the GitHub Pages artifact")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args(argv)
    try:
        output = build_site(args.repo_root, args.output)
    except BuildError as exc:
        parser.error(str(exc))
    print(f"Built static site: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
