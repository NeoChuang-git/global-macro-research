# 0001. Deep Report Ingestion Pipeline

## Context
Previously, report ingestion was orchestrated across four shallow modules (`canonical_block.py`, `markdown_renderer.py`, `report_runs.py`, and `sync_drive.py`). The caller in `sync_drive.py` had to manually extract canonical blocks, parse YAML frontmatter, check idempotency, invoke HTML rendering, determine archive paths, write files atomically, and append to the run manifest. This logic was duplicated between native Google Docs synchronization and local markdown file rendering, causing format-handling quirks and fallback heuristics to leak across the seam.

## Decision
We collapsed the entire document processing workflow behind a deep module: `scripts/report_ingestion.py`.
- **High-leverage Seam**: The module provides `ingest_report_content()` and `ingest_report_file()`, taking raw text or files along with the category, and returning an `IngestionResult` dataclass.
- **Encapsulated Internals**: Canonical block validation, markdown fallback heuristics, SHA256 hashing, atomic file writing, and `report_runs.json` manifest updates are all encapsulated behind the module interface.
- **Idempotency**: Idempotency checks are evaluated internally with an explicit `force: bool = False` override.
- **Locality**: Ingestion errors, format fallbacks, and storage updates are concentrated in one module, significantly improving testability and navigability.
