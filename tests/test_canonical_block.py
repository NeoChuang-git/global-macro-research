#!/usr/bin/env python3

import unittest
from scripts.canonical_block import (
    CanonicalBlockError,
    REQUIRED_SECTIONS,
    REQUIRED_SECTIONS_V2,
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
    def test_weekly_v2_accepts_equivalent_chinese_section_headings(self):
        body = "\n".join("## " + heading for heading in (
            "執行策略摘要（EXECUTIVE STRATEGY SUMMARY）",
            "Regime 轉換矩陣",
            "每週總經訊號板",
            "三大持續性主題（TOP 3 PERSISTENT THEMES）",
            "訊號持續性評分",
            "總經資料與政策深度分析",
            "全球跨資產傳導",
            "台灣經濟與政策傳導",
            "策略含意矩陣",
            "情境矩陣與風險燈號",
            "下週催化劑行事曆",
            "SOURCE AUDIT",
            "結論（BOTTOM LINE）",
        ))
        validate_required_sections(body, "WEEKLY_STRATEGY", 2)

    def test_weekly_v2_chinese_aliases_do_not_make_sections_optional(self):
        translations = {
            "Weekly Regime Transition Matrix": "Regime 轉換矩陣",
            "Weekly Macro Signal Board": "每週總經訊號板",
            "Signal Persistence": "訊號持續性評分",
            "Macro Data": "總經資料與政策深度分析",
            "Transmission": "全球跨資產傳導",
            "Risk Lights": "情境矩陣與風險燈號",
            "Catalyst Calendar": "下週催化劑行事曆",
        }
        headings = [translations.get(section, section) for section in REQUIRED_SECTIONS_V2["WEEKLY_STRATEGY"]]
        for section, translation in translations.items():
            with self.subTest(section=section):
                body = "\n".join("## " + h for h in headings if h != translation)
                with self.assertRaisesRegex(CanonicalBlockError, section):
                    validate_required_sections(body, "WEEKLY_STRATEGY", 2)

    def test_weekly_chinese_v2_aliases_do_not_change_v1_contract(self):
        body = "\n".join("## " + h for h in REQUIRED_SECTIONS["WEEKLY_STRATEGY"])
        validate_required_sections(body, "WEEKLY_STRATEGY", 1)
        body = body.replace("Weekly Regime Transition Matrix", "Regime 轉換矩陣")
        with self.assertRaisesRegex(CanonicalBlockError, "Weekly Regime Transition Matrix"):
            validate_required_sections(body, "WEEKLY_STRATEGY", 1)

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

    def test_archive_names_reserve_both_artifacts_and_all_rerun_candidates(self):
        cases = (
            ({"report_type": "GLOBAL_DAILY_BRIEF", "generated_at_taipei": "2026-09-29T07:30:00+08:00"}, "Global_Daily_Brief_2026-09-29", "_rerun_0730"),
            ({"report_type": "WEEKLY_STRATEGY", "generated_at_taipei": "2026-09-29T07:30:00+08:00"}, "Weekly_Strategy_2026-09-29", "_rerun_0730"),
            ({"report_type": "MACRO_TAIWAN_EARLY_WARNING", "generated_at_taipei": "2026-09-29T07:30:00+08:00"}, "Global_Macro_Early_Warning_2026-09-29", "_0730"),
        )
        for meta, base, rerun in cases:
            with self.subTest(report_type=meta["report_type"]):
                existing = {base + ".html", base + rerun + ".html", base + rerun + "_2.md"}
                self.assertEqual(determine_archive_filename(meta, existing), base + rerun + "_3.md")
        meta = {"report_type": "MACRO_TAIWAN_EARLY_WARNING", "generated_at_taipei": "2026-09-29T07:30:00+08:00", "slug": "rates"}
        self.assertEqual(determine_archive_filename(meta, {"Global_Macro_Early_Warning_2026-09-29_0730_rates.html"}), "Global_Macro_Early_Warning_2026-09-29_0730_rates_2.md")


class TestEscapedCanonicalBlockSanitization(unittest.TestCase):
    def test_extract_and_parse_escaped_delimiters_and_frontmatter(self):
        escaped_doc = f"""
\\<\\<\\<REPORT\\_BEGIN\\>\\>\\>
\\---
research\\_status: COMPLETE
report\\_type: GLOBAL\\_DAILY\\_BRIEF
run\\_id: GDB-20260929-0730
generated\\_at\\_taipei: 2026-09-29T07:30:00+08:00
coverage\\_start\\_taipei: 2026-09-28T07:30:00+08:00
coverage\\_end\\_taipei: 2026-09-29T07:30:00+08:00
title: Global Daily Brief Escaped Test
format\\_version: 1
risk\\_light: GREEN
\\---
{SAMPLE_DAILY_BODY}
\\<\\<\\<REPORT\\_END\\>\\>\\>
"""
        block = extract_latest_complete_report_block(escaped_doc)
        self.assertIsNotNone(block, "Failed to extract canonical block from escaped delimiters")
        metadata, body = parse_and_validate_canonical_block(block)
        self.assertEqual(metadata["run_id"], "GDB-20260929-0730")
        self.assertEqual(metadata["report_type"], "GLOBAL_DAILY_BRIEF")
        self.assertEqual(metadata["risk_light"], "GREEN")
        self.assertIn("1. Executive Intelligence Summary", body)

    def test_extract_real_early_warning_escaped_document(self):
        import pathlib
        ew_file = pathlib.Path("reports/early-warning/Global_Macro_Early_Warning_2026-09-28_1859_oil-yield-confirmation.md")
        if ew_file.exists():
            content = ew_file.read_text(encoding="utf-8")
            block = extract_latest_complete_report_block(content)
            self.assertIsNotNone(block)
            metadata, body = parse_and_validate_canonical_block(block)
            self.assertEqual(metadata["run_id"], "MTW-20260928-1859-oil-yield-confirmation")
            self.assertEqual(metadata["report_type"], "MACRO_TAIWAN_EARLY_WARNING")
            self.assertEqual(metadata["risk_light"], "ORANGE")



if __name__ == "__main__":
    unittest.main()
