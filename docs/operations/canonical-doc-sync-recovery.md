# Canonical Google Docs sync recovery — 2026-10-02

## Verified diagnosis

The production path is Drive/Docs → GitHub Actions → static GitHub Pages.
The sync and Pages workflows do not depend on Cloud Run. The intentionally
configured Google Cloud monthly $0 cap was not changed or used as an explanation.
The separate global-macro-publisher incident is outside this repair.

Runs [36977406550](https://github.com/NeoChuang-git/global-macro-research/actions/runs/36977406550)
and [36988500821](https://github.com/NeoChuang-git/global-macro-research/actions/runs/36988500821)
were read back from GitHub. Both ran main commit
`dc0c80beb8ea06e2c429ad4836752b67035bbb96`, exported all three configured
canonical Docs with HTTP 404, and nevertheless finished successfully with
`updated=0 unchanged=154 ignored=0`.

`sync_native_google_docs()` caught every export exception, printed
`SOURCE_DOC_PERMISSION_DENIED`, and continued. Invalid canonical blocks and
ingestion failure results also only logged an error. None of those paths raised
`SyncError`, so the CLI printed `BUILD_SUCCEEDED`, returned zero, and allowed the
success-dependent Pages workflow to proceed.

The non-secret Actions variables identify the CI reader as
`global-macro-drive-reader@global-macro-research.iam.gserviceaccount.com`, using
Workload Identity Federation. Drive connector metadata confirmed all three
configured IDs are the intended native Google Docs. Permission metadata on
each showed only its owner; it did not include the CI reader. All three
`text/plain` exports succeeded through the connected user's Drive identity:
Daily 509,258 bytes, Macro 2,163,630 bytes, Weekly 124,160 bytes. The export
method, MIME type, and `drive.readonly` scope are supported by the
[Drive export reference](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/export)
and [export formats](https://developers.google.com/workspace/drive/api/guides/ref-export-formats).

This is evidence of a document-specific CI visibility/access gap, rather than
an invalid ID or unsupported export format. It is not a live re-test under the
CI service-account identity. No credentials were read, replaced, or used for
impersonation. HTTP 404 alone cannot distinguish an absent file from a file
the caller cannot read; see the [Drive error guide](https://developers.google.com/workspace/drive/api/guides/handle-errors).

## Folder sources and canonical contract

The existing folder route already archived the latest valid Daily and Macro
run IDs (`GDB-20261002-0728` and
`MTW-20261002-0756-fed-hawkish-rates-energy`). The manifest has no canonical
source document ID for those runs. This explains why reports can appear while
the canonical exports fail; it does not justify removing the canonical sources.

The latest Weekly block is `WKS-20260927-2000`, format version 2. Its seven
Chinese headings were not recognized by the validator. Its corresponding
sections are present: Regime 轉換矩陣, 每週總經訊號板, 訊號持續性評分,
總經資料與政策深度分析, 全球跨資產傳導, 情境矩陣與風險燈號,
下週催化劑行事曆. Explicit aliases now apply only to Weekly v2. All required
sections remain mandatory, and v1 behavior is unchanged.

The folder route is currently sufficient to show recent Daily/Macro reports;
it is not verified as a complete substitute for the canonical contract. The
Weekly canonical run was not in the manifest. An offline integration archived
it as a separate rerun snapshot rather than overwriting the existing weekly
report.

## Repair and validation

Configured canonical fetch, validation, and ingestion failures now accumulate
and raise `SyncError`. Diagnostics distinguish 404/not-visible, 401/403, and
other fetch failures. Successful sources are still attempted after another
source fails. Accessible documents without complete blocks and already
archived valid runs remain normal no-ops.

Validation used an isolated Python 3.12 venv and no Google authentication:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_site.py
git diff --check
```

All 108 tests passed after the independent review corrections. Regression tests
first reproduced five assertion failures
and one ingestion exception for the swallowed-error behavior, plus failures for
HTTP status misclassification and the unrecognized Weekly headings. New tests
cover aggregate failure diagnostics, CLI status 1 despite unchanged folder
reports, historical report preservation, mixed success/failure, invalid blocks,
ingestion failures, intentional folder-only mode, Weekly Chinese equivalents,
missing sections, and the unchanged v1 contract.

A fresh independent Codex reviewer inspected the original diff and workflows,
reran the original 98 tests, and performed additional negative/scoping and
failure-injection probes. The review found no new blocker in the initial patch,
but identified three existing preservation/idempotency defects relevant to
enabling canonical ingestion: an HTML-only legacy report could be overwritten;
different same-minute run IDs could overwrite the previous rerun snapshot; and
a recorded run with missing artifacts could still be skipped as complete.
Those defects were reproduced, corrected locally, and independently rechecked.

Native snapshot naming now reserves both artifacts and chooses incrementing
suffixes for occupied rerun names. Processed run artifacts require safe paths,
existence, and matching checksums. Actual Daily/Macro folder Markdown contains
CRLF and source text outside canonical markers; the validated normalized block
hash matches its manifest even though the raw file hash differs. The checker
accepts that exact equivalence while rejecting changed canonical content with
the same run ID. Folder ingestion failure results now also propagate as
`SyncError`. Rendering occurs before writes, preventing renderer failures from
leaving an orphan Markdown snapshot. Ten additional persistent tests cover
these preservation and compatibility cases.

All three actual connector exports passed the repaired parser. In a temporary
offline mirror with those exports supplied through `MemoryStorageAdapter`, the
first sync returned `updated=1 unchanged=2`, the repeat returned
`updated=0 unchanged=3`, and the site built successfully. SHA256 comparison
confirmed all 269 existing report files stayed byte-for-byte identical.
Only `Weekly_Strategy_2026-09-27_rerun_2000.md` and `.html` were added in that
temporary mirror. No generated reports or index/state changes are included in
this patch.

The sync is not transactional across sources: some valid local files may be
written before a later failure. The existing Actions commit step is skipped
when the CLI fails, and the Pages workflow gates on sync success, so failed
runs do not publish those partial local changes. Previously deployed reports
stay available.

Residual limitation: failure while writing the second artifact or the manifest
can still leave local unregistered artifacts. There is no rollback across the
pair or across sources. A retry in the same local mirror can retain an
unregistered pair alongside a new safely named snapshot. GitHub Actions starts
each sync from a fresh checkout and does not commit/deploy a failed sync, so
failed runner artifacts do not enter the next production attempt. Do not
manually publish partial files from a failed local run.

## Isolation and remaining approval

The confirmed source checkout is
`/Volumes/VM-Data/Agent/Global-macro-research`, branch
`feat/gmr-pub-cloud-001` at `bc2086b395ee2cebb91106a3e8db91947d368de9`.
It had three untracked publisher work-order items and live Antigravity/publisher
processes. It was left untouched.

The repair is in
`/Users/neochuang/Documents/Codex/2026-10-02/task-6/global-macro-research-fix`,
branch `fix/required-canonical-source-health`, based on the fetched production
main commit `dc0c80beb8ea06e2c429ad4836752b67035bbb96`.
TWSEMCPserver CAP01/EVD-01 and Harness were not modified. No external model,
Notion scheduler, push, merge to remote main, deployment, or sharing mutation
was used.

The minimum permission proposal is Viewer access on only the three canonical
Docs listed in [enable-automation.md](enable-automation.md), granted to the
existing CI reader. Per the user's boundary, owner approval is required before
making that change. Do not create public sharing, new credentials, editor
permissions, or broader parent-folder access.

The reader identity was freshly read back during review from the non-secret
`GCP_SERVICE_ACCOUNT` repository variable (last updated 2026-08-28), and the
current main workflow explicitly passes `${{ vars.GCP_SERVICE_ACCOUNT }}` to
the existing authentication action. There is no sync-step `continue-on-error`
or commit-step `always()` override. The proposed recipient is the existing
production reader, not a new publisher identity.

After permission approval and code review, an authorized maintainer can apply
the patch to current main, rerun the tests, publish the code, and run the normal
sync. Verify all three `SOURCE_DOC_FETCHED` outcomes, valid/previously archived
run IDs, the commit behavior, and Pages artifact/deployment. Expect an
intentional weekly rerun snapshot if this run is still absent. Local passing
tests and user-identity exports are not production recovery evidence.

## Authorized rollout

At 2026-10-02 10:13 UTC the owner explicitly approved Viewer access on only
the three exact canonical Docs for the existing CI reader, and publication of
the independently reviewed repair to main followed by sync and Pages
verification. Pre-write permission readback showed no existing reader grant.
The three file-scoped grants were then applied through the existing Drive
connector and read back as `type=user`, `role=reader` for the approved email.
No parent-folder or public sharing was added, and no credentials or billing
cap were changed. Production rollout results are recorded separately after
observing the actual sync and deployment runs.
