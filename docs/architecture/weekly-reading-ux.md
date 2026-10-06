# Weekly reading interface — original-style correction

## Current scope — 2026-10-06

The user rejected the broader candidate's overall rendering and requested the
original production visual style. This scope supersedes the historical phase 1
specification and its deployment approval. PR #18 stays draft. Do not merge or
publish until the user reviews and approves this corrected candidate.

Use production main `9ad51a36cb70bd9badcdd1e98a16f88c5a962d39` as the visual
baseline. Preserve its palette, typography, container widths, spacing, summary
list, and cards. Remove the visible chapter directory and the previous candidate's
narrow narrative, summary-card expansion, fixed first columns, scrolling hints,
and bounded vertical table scrollports. Stable heading IDs may remain; no new
visible navigation or interactions are added.

The five approved October 4 paragraphs become compact tables:

1. 訊號持續性評分: 訊號 / 持續性評分; preserve the eight signal names, order,
   and scores (91, 90, 88, 86, 83, 66, 64, 28). Do not invent a /100 scale.
2. 總經資料與政策深度分析: 類別 / 內容; FACT, MARKET EXPECTATION, INFERENCE.
   FACT has three lines replacing its two semicolon separators. Preserve every
   number and qualifier, including 12月仍可能行動 and 不等於全面金融條件放鬆.
3. 情境矩陣與風險燈號: retain the existing current ORANGE badge in a paragraph
   before the table. The three scenario rows have visible GREEN / YELLOW / RED
   labels with the existing colored badges and complete trigger conditions.
   RED retains 信用利差擴張且AI財測下修. Do not invent an ORANGE scenario row or
   imply the three scenarios are current states.
4. Regime 轉換矩陣: 情境 / 前期機率 / 本期機率. Preserve all five pairs:
   Soft Landing 28%→31%, Sticky Inflation 34%→32%, Growth Slowdown 17%→20%,
   Funding/Liquidity Stress 13%→10%, Stagflation 8%→7%. Keep the complete
   dual-peak and ORANGE conclusion in a paragraph after the table.
5. 每週總經訊號板: 領域 / 訊號與判讀. Keep ten rows in original order,
   including Growth's mixed directions, Inflation's 但 clause, Labor's 形成Trend,
   Liquidity/Credit's 暫無系統性stress and FX funding's 中性. Do not infer missing
   signal IDs, directions or values. Keep the original direction styling.

The last two conversions were requested after candidate `4a3dd361`. The supplied
screenshot was materialized to the local executor and visually inspected; its
two paragraphs match canonical source. This extension changes no other chapter,
CSS, renderer behavior, layout or previously approved table.

Small readability corrections are limited to existing Previous/neutral text
contrast and intact percentage ranges. Only the approved compact tables override
the original 680px minimum table width and allow long labels to wrap. Original
wide matrices retain their original horizontal scrolling and styling.

## Implementation and preservation contract

`scripts/weekly_presentation.py` holds five explicit source-to-row mappings.
They apply only to `WEEKLY_STRATEGY`, `WKS-20261004-2045`, a unique exact chapter
heading, and a single plain paragraph matching the entire approved source.
Additional paragraphs, links, markup, missing fields, changed numbers or
qualifiers leave that section unchanged. There is no generic semicolon parser
and no research-generation prompt change. Scenario labels are restored after
legacy semantic enrichment, which otherwise renders standalone risk words as
emoji only; current ORANGE processing remains unchanged.

Canonical Markdown remains byte-for-byte identical. All 285 production report
artifacts remain immutable. The unmerged candidate at `0ffe2c18` is preserved
in Git history and `codex/weekly-reading-ux-before-style-correction`; local
patches and archived previews remain in the evidence directory.

The previous original-style candidate `4a3dd361` and its `_rerun_2045` pair
remain unchanged. For this two-section extension, use the existing
`ingest_report_content(force=True)` API without `original_filename` once. Its
collision-safe archive naming creates `_rerun_2045_2.{md,html}`. Preserve the
source document ID and canonical bytes. Ingestion updates the same run's artifact
pointers/checksums; rebuild the catalog through `ReportCatalog.build_from_scan`
with existing Drive sync state. Both earlier report URLs remain available.
Do not repeat force ingestion or overwrite a previous candidate. Do not bypass
checksum checks, change research metadata, or invent a run ID.

## Acceptance and verification

- Seven tables total: the previous five plus these two new tables. Preserve all
  24 chapters, research links, numbers, conditions and original table cells.
- Reconstruct the original paragraphs from actual visible table cells and
  compare exact wording/punctuation; hidden copies are not preservation proof.
- Negative cases must leave unmatched paragraphs unchanged. Daily and Macro
  research, tables, and summary layouts retain baseline behavior.
- For this extension, CSS and all five prior tables must match `4a3dd361`
  exactly. No directory markup/CSS or layout change is introduced.
- Full unit suite, deterministic render, original-file hashes, run/catalog
  changes, and isolated site build must pass. Run Standards and Spec reviews.
- Fresh visual acceptance is pending at desktop 1440px and mobile 375/390px,
  direct and iframe: confirm original style, visible risk labels, no directory,
  readable new tables, complete original wide tables and no text truncation.
  No supported browser/CUA is available here. Do not install tools or change
  browser/security settings; HTTP/DOM checks do not count as screenshots.

## Regime ORANGE badge correction — 2026-10-07

The user identified plain ORANGE in the Regime conclusion. Wrap only that
approved conclusion's ORANGE in the existing `risk risk-orange` badge, retaining
its exact visible text and the whole original sentence. No CSS or other DOM
change is allowed. The scoped badge also works when the separate scenario
paragraph is not converted. Full suite: 128 tests pass after observed RED.
Unwrapping the new span reproduces the previous candidate DOM exactly.

Revise the current unpublished `_rerun_2045_2` artifact with its explicit filename;
its previous bytes remain in commit `bc4aa289`. Canonical Markdown, the 285
production artifacts and the older candidate pair remain unchanged. Update only
the current HTML hash in manifest/catalog. The same preview URL remains valid.
No merge/deployment before user confirmation.

## Regime and signal-board extension verification — 2026-10-06

- New requirements failed on `4a3dd361` (four RED failures); all 17 scoped
  tests pass after implementation, including 11 new changed-source cases.
  Full suite: 127 tests passed. Independent Standards and Spec reviews pass.
- Regime's actual visible cells reconstruct the five original probability
  transitions, with its full conclusion after the table. Macro's actual visible
  cells reconstruct all ten original clauses including every qualifier.
- The prior five table DOMs, CSS and shared renderer match `4a3dd361` exactly.
  All 287 previous report files, including its candidate pair, remain unchanged.
- New candidate: `reports/weekly/Weekly_Strategy_2026-10-04_rerun_2045_2.html`.
  HTML SHA-256: `ab53d43b5d839c4c4531e1a24baaa79192bc94a822a0059cf66552a9ac00de66`.
  Canonical Markdown SHA-256 remains
  `bcb47f78c0fd28aa286b5b4c6d1054417683a345e47947afc52947f00d862d12`.
- The same run's artifact pointers and HTML hash change; the catalog preserves
  all three report URLs and selects `_2` as latest. Deterministic rendering,
  site build, Python compilation and source/test/doc/data whitespace checks pass.
- User-provided reference screenshot was downloaded with Library metadata and
  inspected locally. It is source evidence, not a screenshot of the new UI.
  Fresh output browser validation and user confirmation remain pending.
- No research prompt changes, extra chapter transformations, tool installation,
  browser/security changes, merge or deployment are included.

## Previous five-table candidate verification — 2026-10-06 (4a3dd361)

- The 12 scoped tests were observed failing on the restored baseline, then
  passed with the three approved mappings. Full suite: 122 tests passed.
- Independent Standards and Spec reviews passed. Spec also exercised 18
  malformed/format-changed source cases; all preserved the original DOM.
- All 285 production artifact bytes match `9ad51a36`; candidate Markdown is
  identical to canonical SHA-256 `bcb47f78c0fd28aa286b5b4c6d1054417683a345e47947afc52947f00d862d12`.
- Corrected HTML SHA-256:
  `70918b6913db9e2bc73a44ed0ad7dd2ef06745790759a012617a21ac9dd28cdd`.
  Its visible cells reconstruct the original paragraphs; the report retains
  24 chapters and five tables. Current ORANGE is unchanged.
- Compared with the prior unpublished candidate, run manifest and catalog
  change only the candidate HTML hash. Site build, Python compilation and
  `git diff --check` pass.
- The loopback Pages preview uses port 8768; isolated freshly rendered Daily
  and Macro regression fixtures use 8769. Older preview archives are retained.
- No fresh screenshots or visual acceptance are claimed. User confirmation
  of this corrected candidate remains required before merge/deployment.

## Historical evidence — superseded candidate only

Everything below records the former candidate and its earlier authorization.
It is retained for traceability, not current acceptance or deployment approval.
Its screenshots and pass counts do not validate the corrected candidate.

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
