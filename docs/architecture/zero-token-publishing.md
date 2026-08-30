# Zero-Token Report Publishing Architecture

## Objective, invariants, evidence, and trade-off

**Objective:** publish three classes of HTML macro report with no LLM in the
maintenance path and no always-on Mac dependency.

**Invariants:** Google Drive is read-only; only `.html` files from the three
configured folders enter the mirror; every public report is indexed; sync is
idempotent; credentials never enter Git; and old ingestion queues cannot run as
the active path.

**Evidence:** unit tests cover filename classification, repeat synchronization,
content updates, missing local files, remote/API errors, index ordering/latest
selection, and Pages artifact path validation. The deployment workflow builds a
minimal artifact before Pages receives it.

**Core trade-off:** the mirror is additive. A report removed from Drive remains
in Git history and the local report tree. This intentionally prefers archive
retention and recovery over destructive source mirroring. Removing an archived
report therefore requires an explicit reviewed Git change.

## Modules and boundaries

| Module | Public interface | Responsibility |
| --- | --- | --- |
| Drive adapter | Google Drive API v3 read-only scope | List and download binary HTML from three folder IDs |
| Synchronizer | `scripts/sync-drive.py` | Validate names/sizes, detect changes, verify checksum, atomically update mirrors |
| Sync state | `data/drive-sync-state.json` | Stable Drive metadata/checksums used for idempotency; contains no credential |
| Indexer | `build_reports_index()` | Scan the three local mirrors, sort reports, select latest per category |
| Website | `index.html`, `archive.html`, `report.html` | Read only `data/reports.json`; render cards, filters, and a sandboxed local HTML reader |
| Artifact builder | `scripts/build_site.py` | Fail on unsafe/missing references and copy only public assets into `_site/` |
| Sync automation | `.github/workflows/sync-reports.yml` | Authenticate by OIDC, sync, and commit/push changed mirror/index files |
| Pages automation | `.github/workflows/deploy-pages.yml` | Verify, build, upload, and deploy the static artifact |

## Deterministic sync contract

1. Folder classification comes from the configured folder ID, never filename
   guesswork.
2. Only safe basename filenames ending in `.html` (case-insensitive) are
   candidates. Directory separators and traversal are rejected.
3. Duplicate case-insensitive HTML names in a category are ambiguous and abort
   the run before any report is written.
4. A matching Drive MD5 and local MD5 skips download. A missing or changed local
   file is downloaded and verified against Drive MD5 when available.
5. Every changed file is written through a same-directory temporary file and
   atomic replacement.
6. Remote listing/download must complete before staged files are applied. An API
   error exits non-zero and prevents index/state publication.
7. `data/reports.json` is emitted with sorted keys and stable indentation. It has
   no wall-clock `generated_at`, so an unchanged tree produces identical bytes.

Default maximum report size is 25 MiB and can be lowered with
`MAX_REPORT_BYTES`. To protect the runner from resource exhaustion, batch limits
enforce at most 200 total Drive files (`DEFAULT_MAX_BATCH_FILES`), 100 MiB total
Drive bytes (`DEFAULT_MAX_BATCH_BYTES`), and 50 MiB staged changes per run
(`DEFAULT_MAX_STAGED_BYTES`). Parent symlink checking ensures no ancestor path
can escape the report directory root. The sync never uploads, edits, trashes, or
changes Drive permissions.

Source reports must be self-contained HTML. Relative companion assets are not
mirrored because the source contract intentionally admits only `.html` files.

## Index schema

```json
{
  "schema_version": 1,
  "reports": [
    {
      "category": "daily",
      "date": "2026-08-28",
      "file": "reports/daily/Global_Daily_Brief_2026-08-28.html",
      "modified_time": "2026-08-28T01:00:00Z",
      "sha256": "...",
      "title": "Global Daily Brief"
    }
  ],
  "latest": {
    "early-warning": null,
    "daily": {},
    "weekly": null
  }
}
```

Reports sort by report date descending, Drive modified time descending, category
order (`early-warning`, `daily`, `weekly`), title, and path. A filename date in
`YYYY-MM-DD` or `YYYYMMDD` form wins; otherwise Drive `modifiedTime` supplies the
date. Pre-existing reports without either remain indexed with a null date.

## Website trust boundary

Drive HTML is untrusted content. `report.html` accepts only a path already found
in `reports.json`, restricts it to the three report roots, and loads it in a
strictly sandboxed iframe (`sandbox=""`) without `allow-same-origin`,
`allow-scripts`, `allow-popups`, or `allow-popups-to-escape-sandbox`. No raw
same-origin opening mechanism is provided. The site build rejects symlinks,
parent symlink ancestors, traversal, missing index files, and non-HTML report references.

## Actions supply-chain and workflow chaining

All GitHub Actions are pinned to full 40-character immutable commit SHAs. In
`sync-reports.yml`, dependency installation and unit testing occur strictly
before Google Cloud authentication is initiated. `deploy-pages.yml` listens to
both direct pushes to `main` and `workflow_run` completion of the sync workflow,
ensuring bot commits from GITHUB_TOKEN reliably trigger deployment.

## Zero-token statement

The ongoing flow runs deterministic Python, Google Drive API calls, Git/GitHub
Actions, browser JavaScript, and GitHub Pages. It contains no model endpoint,
agent, prompt, embedding, or inference call. This makes AI-token maintenance
cost zero. Report authoring upstream is a separate concern and is not claimed to
be token-free by this repository.
