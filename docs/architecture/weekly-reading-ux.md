# Weekly reading interface — phase 1

## Scope and acceptance

Improve the existing deterministic report presentation without changing research,
canonical Markdown content, prompts, or iframe permissions. The original
2026-10-04 preview scope excluded publication and changes to report snapshots or
manifests. The authorized 2026-10-06 release continuation below uses the existing
versioned rerun path while preserving every original report snapshot.

- Recognize the bilingual Weekly executive strategy summary; retain every bullet.
- Give H2/H3 headings stable, unique anchors and offer a keyboard-operable chapter
  directory. Retain the complete heading text and section order.
- Limit narrative width to 800px while tables can use the 1080px content width.
- At 375/390px, preserve readable text and every table column, keep the first
  column visible during horizontal scrolling, and explain keyboard/touch scrolling.
- Keep headers attached to the table scrollport for long tables. Short tables
  remain in normal page flow; do not promise page-sticky headers inside an
  overflow wrapper. Use native, bounded two-axis scrolling only when necessary.
- Work without JavaScript inside the existing sandboxed report iframe.
- Verify 1440px desktop and 375/390px mobile, direct and iframe, keyboard/anchors,
  long-table header behavior, and Daily/Macro renderer regressions.
- Compare all existing research text before/after; hash canonical inputs and
  verify tracked reports/data remain unchanged. Deliver real local screenshots.

## Decisions

Use native details/summary for a compact chapter directory, ordinary
fragment links, and focusable named table regions. The header and first column
stick within each table's scrollport. The scrollport grows naturally up to a
viewport-relative maximum height, so short tables need no inner vertical scroll.
No guessed paragraph-to-table conversion, hidden columns, source edits, new
dependencies, or smaller table fonts. Existing summary and table styles are
extended, rather than adding a second renderer.

## Local task graph

1. RED: add behavior tests for Weekly summary recognition, anchors, table
   accessibility, content preservation, and shared-renderer behavior.
2. GREEN: implement deterministic presentation helpers and responsive CSS.
3. Preview: render into a separate workspace directory; copy reader assets there
   and create a preview-only catalog. Never write into tracked reports/data.
4. Verify: unit suite, applicable static checks, browser checks, screenshots.
5. Review: parallel Standards and Spec review; resolve findings and repeat only
   affected checks. Document results and deferred deployment steps.

## Release contract

The stylesheet is embedded in generated HTML, so renderer changes apply to newly
ingested reports. Existing HTML must remain unchanged. For the selected October 4
Weekly, use the existing `ingest_report_content(force=True)` interface without
`original_filename`; its collision-safe naming produces a separate rerun pair.
Update the existing run's artifact pointers/checksums through ingestion and
rebuild the catalog through `ReportCatalog.build_from_scan`. Do not bypass
checksum validation, change research metadata, invent a new run ID, or rewrite
the original files. Do not repeat `force=True` once the rerun exists.

## Verification results — 2026-10-04

- Baseline: 110 tests passed. New behavior tests were observed failing before
  implementation; final suite: 117 passed. Python compileall, JavaScript syntax
  checks, git diff --check, and isolated site-build validation passed.
- This repository has no configured lint/typecheck command; no extra tooling
  was installed. Existing repository virtualenv dependencies were reused.
- In-app browser at 1440px: narrative width 800px, table width 1078px, complete
  five-point summary, and all 24 Weekly chapter links. Summary text remains
  17px desktop / 16px mobile; table font remains 14.72px.
- Direct report and existing sandbox iframe at 375px and 390px: keyboard
  directory, anchors and horizontal table scrolling work. At 375px the
  document width is 375px, table scrollport 349px; at 390px the scrollport is
  364px (previously 324px). The first column stays at the scrollport left edge.
- Synthetic 40-row fixture verifies vertical scrolling and sticky headers:
  direct 375px scrollTop 486px; iframe 390px scrollTop 474px. In both cases,
  header top and first-column left remain one border pixel inside the
  scrollport. The synthetic fixture exists only in the local preview.
- Daily direct 375px and Macro iframe 375/390px have no document overflow.
  Long bilingual Macro risk chips wrap without changing their words or font.
- Standards and Spec reviews passed. Review findings on summary font size and
  print sticky specificity were fixed; final numeric-range and chip-wrap
  adjustments received Standards incremental review.
- Canonical input hashes, research text, table cells and research link targets
  remain unchanged across the three real reports. Tracked reports/data are
  unchanged; original checkout branch, HEAD and pre-existing untracked file
  are unchanged. No commit, push, merge, issue publication or deployment.

Evidence is delivered next to this isolated clone in ../evidence/index.html,
with raw screenshots, browser metrics, canonical hashes, and a complete patch.
Test logs and the reproducible build-preview.py are in the parent workspace.
Preview server: http://127.0.0.1:8765/ (loopback only).

Limits: these are in-app browser viewport checks, not physical iOS/Android or
cross-browser testing. Print rules were reviewed but no visual print/PDF test
was performed. Research generation prompts and paragraph-to-table conversion
remain out of scope; they require a separate source-structure decision.

## Authorized release continuation — 2026-10-06

The user approved deployment after viewing the local screenshots. Integrate only
phase 1 into the existing GitHub Pages pipeline; no hosting, access-permission,
research-generation, or source-structure changes are included.

- Updated the isolated branch to current main
  `9ad51a36cb70bd9badcdd1e98a16f88c5a962d39`; the three intervening commits add
  synchronized reports and do not conflict with this presentation change.
- Preserved all 285 original report files byte-for-byte. The only new report
  pair is `reports/weekly/Weekly_Strategy_2026-10-04_rerun_2045.{md,html}`.
- New Markdown is identical to the original October 4 snapshot, SHA-256
  `bcb47f78c0fd28aa286b5b4c6d1054417683a345e47947afc52947f00d862d12`.
  New HTML SHA-256 is
  `d196d901b65a9a46e86281aea8cb444a7024164d13caf1f7366e5cf4549b2638`.
- The single run record changes only Markdown/HTML paths and HTML checksum.
  The catalog retains both versions, with `latest.weekly` pointing to the rerun.
  The original report URL retains its original interface. The updated interface
  will be available at the new direct URL and ordinary indexed reader URL.
- A new release test checks preservation of original bytes, research text,
  source links and table cells, selection of the new latest Weekly, and repeat
  ingestion as `SKIPPED_EXISTING`. Shared-renderer coverage also includes the
  latest Daily and Macro snapshots from the updated baseline.
- Fresh full suite: 118 tests passed. Independent Standards and Spec reviews
  passed; Spec separately ran all 118 tests and compared all 285 original files.
- Site build, Python compilation, JavaScript syntax checks and whitespace checks
  on source/tests/docs/data passed. The complete snapshot diff reports preserved
  CRLF in the new Markdown and three whitespace-only lines already emitted by
  the original HTML template; these artifact bytes are intentionally retained.
- Fresh browser validation is pending: the earlier in-app browser tool is not
  available in this execution environment, and the existing Safari WebDriver
  refused session creation because Allow Remote Automation is disabled. No
  setting was enabled. October 4 screenshots are historical evidence, not a
  substitute for the requested fresh desktop/mobile/iframe checks.

Release remains gated on fresh 1440px / 375px / 390px direct-and-iframe checks,
Daily/Macro regression, then main integration and successful Pages/live HTTP
verification. No deployment success is claimed by this document. The last
observed successful production baseline is main `9ad51a36` with Pages run
[37469145438](https://github.com/NeoChuang-git/global-macro-research/actions/runs/37469145438).
