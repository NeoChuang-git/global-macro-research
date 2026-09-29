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
