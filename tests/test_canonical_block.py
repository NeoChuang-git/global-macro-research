#!/usr/bin/env python3

import unittest
from scripts.canonical_block import (
    CanonicalBlockError,
    determine_archive_filename,
    extract_latest_complete_report_block,
    parse_and_validate_canonical_block,
    parse_frontmatter,
    validate_metadata,
    validate_required_sections,
)


SAMPLE_DAILY_BODY = """
# Global Daily Brief

## 1. Executive Intelligence Summary
Overview of today's macro conditions...

## 2. Daily Signal Board
| Sector | Signal |
|---|---|
| Rates | 🔴 Up |

## 3. Top 3 Daily Themes
Theme 1, Theme 2, Theme 3.

## 4. Macro Data & Policy Detail
Data details...

## 5. Cross-Asset Confirmation
Confirmation analysis...

## 6. Causal Chain Audit
Causal link from Fed to Taiwan...

## 7. Global Tech / AI / Semiconductor / Memory / Server Transmission
Transmission into tech...

## 8. Taiwan Economy & Policy
Taiwan macro...

## 9. Taiwan Industry & Equity
Industry detail...

## 10. Market Cycle vs Fundamental Cycle
Cycle divergence...

## 11. Daily Taiwan Equity Action Delta
Actions...

## 12. Scenario Matrix
Scenario A / B / C...

## 13. Risk Lights
- Global 🟠
- Rates 🔴

## 14. Next 24–72h Catalysts
Upcoming catalysts...

## 15. Source Audit
| Claim | Source | URL | Grade |
|---|---|---|---|
| Data | Fed | https://example.com | A |

## 16. Bottom Line
Concluding summary.
"""

SAMPLE_COMPLETE_DAILY_DOC = f"""
<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
report_type: GLOBAL_DAILY_BRIEF
run_id: GDB-20260903-0730
generated_at_taipei: 2026-09-03T07:30:00+08:00
coverage_start_taipei: 2026-09-02T07:30:00+08:00
coverage_end_taipei: 2026-09-03T07:30:00+08:00
title: Global Daily Brief
format_version: 1
risk_light: YELLOW
slug: global_daily_brief
---
{SAMPLE_DAILY_BODY}
<<<REPORT_END>>>

<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
report_type: GLOBAL_DAILY_BRIEF
run_id: GDB-20260902-0730
title: Older Daily Brief
---
Older content here...
<<<REPORT_END>>>
"""


class CanonicalBlockTests(unittest.TestCase):
    def test_extracts_first_complete_report_block(self):
        block = extract_latest_complete_report_block(SAMPLE_COMPLETE_DAILY_DOC)
        self.assertIsNotNone(block)
        self.assertIn("run_id: GDB-20260903-0730", block)
        self.assertNotIn("Older content here", block)

    def test_rejects_missing_report_end(self):
        text = "<<<REPORT_BEGIN>>>\n---\nresearch_status: COMPLETE\n---\nIncomplete"
        block = extract_latest_complete_report_block(text)
        self.assertIsNone(block)

    def test_rejects_missing_report_begin(self):
        text = "Just some text without begin marker\n<<<REPORT_END>>>"
        block = extract_latest_complete_report_block(text)
        self.assertIsNone(block)

    def test_rejects_incomplete_frontmatter(self):
        invalid_block = """---
research_status: COMPLETE
report_type: GLOBAL_DAILY_BRIEF
title: Global Daily Brief
---
# Report
"""
        with self.assertRaisesRegex(CanonicalBlockError, "missing or empty required field"):
            parse_and_validate_canonical_block(invalid_block)

    def test_rejects_non_complete_research_status(self):
        invalid_block = """---
research_status: IN_PROGRESS
report_type: GLOBAL_DAILY_BRIEF
run_id: GDB-1
generated_at_taipei: 2026-09-03T07:30:00+08:00
coverage_start_taipei: 2026-09-02T07:30:00+08:00
coverage_end_taipei: 2026-09-03T07:30:00+08:00
title: Global Daily Brief
format_version: 1
---
# Report
"""
        with self.assertRaisesRegex(CanonicalBlockError, "invalid research_status"):
            parse_and_validate_canonical_block(invalid_block)

    def test_rejects_unknown_format_version(self):
        invalid_block = """---
research_status: COMPLETE
report_type: GLOBAL_DAILY_BRIEF
run_id: GDB-1
generated_at_taipei: 2026-09-03T07:30:00+08:00
coverage_start_taipei: 2026-09-02T07:30:00+08:00
coverage_end_taipei: 2026-09-03T07:30:00+08:00
title: Global Daily Brief
format_version: 99
---
# Report
"""
        with self.assertRaisesRegex(CanonicalBlockError, "unsupported format_version"):
            parse_and_validate_canonical_block(invalid_block)

    def test_validates_required_sections_for_all_report_types(self):
        block = extract_latest_complete_report_block(SAMPLE_COMPLETE_DAILY_DOC)
        metadata, body = parse_and_validate_canonical_block(block)
        self.assertEqual(metadata["run_id"], "GDB-20260903-0730")
        self.assertEqual(metadata["risk_light"], "YELLOW")

        # Missing required sections should raise CanonicalBlockError
        with self.assertRaises(CanonicalBlockError):
            validate_required_sections("# Just a Title", "GLOBAL_DAILY_BRIEF")

    def test_determines_archive_filenames(self):
        meta_daily = {
            "report_type": "GLOBAL_DAILY_BRIEF",
            "generated_at_taipei": "2026-09-03T07:30:00+08:00",
        }
        self.assertEqual(determine_archive_filename(meta_daily), "Global_Daily_Brief_2026-09-03.md")
        self.assertEqual(
            determine_archive_filename(meta_daily, {"Global_Daily_Brief_2026-09-03.md"}),
            "Global_Daily_Brief_2026-09-03_rerun_0730.md",
        )

        meta_ew = {
            "report_type": "MACRO_TAIWAN_EARLY_WARNING",
            "generated_at_taipei": "2026-09-03T14:15:00+08:00",
            "slug": "iran_sanctions_oil_spike",
        }
        self.assertEqual(
            determine_archive_filename(meta_ew),
            "Global_Macro_Early_Warning_2026-09-03_1415_iran_sanctions_oil_spike.md",
        )

        meta_weekly = {
            "report_type": "WEEKLY_STRATEGY",
            "generated_at_taipei": "2026-09-06T18:00:00+08:00",
        }
        self.assertEqual(determine_archive_filename(meta_weekly), "Weekly_Strategy_2026-09-06.md")


if __name__ == "__main__":
    unittest.main()
