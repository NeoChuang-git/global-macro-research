# Global Macro Research Publishing

Zero-token static publishing pipeline that syncs, validates, renders, and serves institutional macro research reports.

## Language

**Macro Report**:
An institutional research document covering global macro developments, asset allocations, or early warning signals.
_Avoid_: Article, post, blog

**Canonical Report Block**:
The delimited institutional markdown payload (delimited by `<<<REPORT_BEGIN>>>` and `<<<REPORT_END>>>`) containing mandatory metadata headers and sectioned analysis.
_Avoid_: Raw block, text payload

**Report Ingestion**:
The end-to-end process of consuming raw document content, validating canonical structure, rendering institutional HTML/Markdown artifacts, and recording run state.
_Avoid_: File saving, download processing

**Report Run**:
An idempotent record identified by a unique `run_id` tracking processed report artifacts, SHA256 hashes, and metadata timestamps.
_Avoid_: Log entry, sync record

**Report Fallback**:
The secondary parsing and rendering mechanism applied when a document lacks canonical delimiters but represents valid research content.
_Avoid_: Error handler, default template

**Report Catalog**:
The centralized index and query module that discovers, classifies, and exposes metadata for all published reports across categories.
_Avoid_: Report list, file scanner

**Catalog Entry**:
The canonical, structured metadata record representing a single published macro report in the catalog.
_Avoid_: Index dict, report row

**Storage Adapter**:
The decoupled persistence and retrieval boundary that abstracts remote cloud storage (Google Drive) and in-memory mock storage behind a unified interface.
_Avoid_: Drive client, API helper

**Remote File**:
The typed metadata representation of an asset residing in a storage adapter, encapsulating ID, name, size, timestamps, and checksums.
_Avoid_: Drive item, file dict

**Memory Storage Adapter**:
An in-memory, zero-dependency implementation of the Storage Adapter used for deterministic, blazing-fast unit testing without mocking Google SDK internals.
_Avoid_: Fake drive, mock client


