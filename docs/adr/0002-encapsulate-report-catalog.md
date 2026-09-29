# 0002. Encapsulate Report Catalog

## Context
Previously, report discovery, classification, and index generation were embedded inside `scripts/sync_drive.py` across multiple functions (`build_reports_index`, `extract_report_title`, `classify_drive_file`). Furthermore, downstream consumers like `scripts/build_site.py` had to directly read and validate raw JSON schemas from `data/reports.json`. This tightly coupled file indexing with Drive synchronization, leaked companion file inspection rules, and duplicated report path safety verification.

## Decision
We encapsulated report metadata inspection, indexing, and querying behind a deep module: `scripts/report_catalog.py`.
- **Unified Producer/Consumer Seam**: `ReportCatalog` serves both `sync_drive.py` (which triggers `build_and_save_index()`) and `build_site.py` (which queries `get_all_reports()` and `get_latest_reports()`), eliminating raw JSON schema parsing from consumer scripts.
- **Typed Representation**: Reports are represented as typed `CatalogEntry` dataclasses with dictionary serialization preserving 100% backward compatibility for `data/reports.json`.
- **Encapsulated Metadata Extraction**: Title extraction from HTML headers, companion markdown frontmatter, and filename heuristics are kept local to the catalog module.
- **Legacy Compatibility**: Full backwards compatibility is preserved for pre-existing legacy HTML reports lacking companion markdown or run manifests.
