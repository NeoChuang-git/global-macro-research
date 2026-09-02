#!/usr/bin/env python3

"""Parser, validator, and naming logic for Google Docs Canonical Markdown report blocks."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml


REPORT_BEGIN_MARKER = "<<<REPORT_BEGIN>>>"
REPORT_END_MARKER = "<<<REPORT_END>>>"

VALID_REPORT_TYPES = {
    "GLOBAL_DAILY_BRIEF",
    "MACRO_TAIWAN_EARLY_WARNING",
    "WEEKLY_STRATEGY",
}

REPORT_TYPE_TO_CATEGORY = {
    "GLOBAL_DAILY_BRIEF": "daily",
    "MACRO_TAIWAN_EARLY_WARNING": "early-warning",
    "WEEKLY_STRATEGY": "weekly",
}

CATEGORY_TO_REPORT_TYPE = {
    "daily": "GLOBAL_DAILY_BRIEF",
    "morning": "GLOBAL_DAILY_BRIEF",
    "early-warning": "MACRO_TAIWAN_EARLY_WARNING",
    "weekly": "WEEKLY_STRATEGY",
}

REQUIRED_SECTIONS: Dict[str, List[str]] = {
    "GLOBAL_DAILY_BRIEF": [
        "Executive Intelligence Summary",
        "Daily Signal Board",
        "Themes",
        "Macro Data",
        "Cross-Asset Confirmation",
        "Causal Chain",
        "Transmission",
        "Taiwan Economy",
        "Taiwan Industry",
        "Market Cycle",
        "Action Delta",
        "Scenario Matrix",
        "Risk Lights",
        "Catalysts",
        "Source Audit",
        "Bottom Line",
    ],
    "MACRO_TAIWAN_EARLY_WARNING": [
        "Executive Take",
        "Signal Delta",
        "Why It Matters",
        "Macro / Policy Detail",
        "Cross-Asset Confirmation",
        "Evidence vs Counter-evidence",
        "Taiwan Transmission",
        "Industry / Equity Sensitivity",
        "Market Cycle vs Fundamental Cycle",
        "Classification & Risk Light Delta",
        "Scenario Matrix",
        "Next Confirmation",
        "Source Audit",
        "Bottom Line",
    ],
    "WEEKLY_STRATEGY": [
        "Executive Strategy Summary",
        "Weekly Regime Transition Matrix",
        "Weekly Macro Signal Board",
        "Themes",
        "Signal Persistence",
        "Macro Data",
        "Narrative Validation",
        "Causal Chain",
        "Transmission",
        "Liquidity",
        "Taiwan Economy",
        "Taiwan Industry",
        "Market vs Fundamental Cycle",
        "Strategy Implication Matrix",
        "Taiwan Equity Action Matrix",
        "Top Stock Deep Dives",
        "Price-Impact Scenario Matrix",
        "Rolling Validation",
        "Scenario Matrix",
        "Risk Lights",
        "Thesis",
        "Catalyst Calendar",
        "Source Audit",
        "Bottom Line",
    ],
}

REQUIRED_SECTIONS_V2: Dict[str, List[str]] = {
    "GLOBAL_DAILY_BRIEF": [
        "Executive Summary",
        "Market Signals",
        "Impact",
        "Strategy",
        "Taiwan",
        "Catalysts",
        "Source Audit",
    ],
    "MACRO_TAIWAN_EARLY_WARNING": [
        "Executive Take",
        "Signal Delta",
        "Why It Matters",
        "Macro / Policy Detail",
        "Cross-Asset Confirmation",
        "Taiwan Transmission",
        "Classification & Risk Light Delta",
        "Next Confirmation",
        "Source Audit",
        "Bottom Line",
    ],
    "WEEKLY_STRATEGY": [
        "Executive Strategy Summary",
        "Weekly Regime Transition Matrix",
        "Weekly Macro Signal Board",
        "Themes",
        "Signal Persistence",
        "Macro Data",
        "Transmission",
        "Taiwan",
        "Strategy",
        "Risk Lights",
        "Catalyst Calendar",
        "Source Audit",
        "Bottom Line",
    ],
}


class CanonicalBlockError(RuntimeError):
    """Exception raised when a canonical block is invalid."""


def extract_latest_complete_report_block(text: str) -> Optional[str]:
    """
    Extract the first complete canonical report block starting from the beginning of text.
    Ignores any trailing content or older blocks below.
    """
    if not text or not isinstance(text, str):
        return None

    begin_idx = text.find(REPORT_BEGIN_MARKER)
    if begin_idx == -1:
        return None

    after_begin = begin_idx + len(REPORT_BEGIN_MARKER)
    end_idx = text.find(REPORT_END_MARKER, after_begin)
    if end_idx == -1:
        # Begin exists but no matching end marker found
        return None

    block = text[after_begin:end_idx].strip()
    return block


def parse_frontmatter(block: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse YAML front matter between '---' markers.
    Returns (metadata_dict, markdown_body).
    """
    if not block.startswith("---"):
        raise CanonicalBlockError("missing opening front matter '---'")

    # Find closing ---
    second_delim = block.find("\n---", 3)
    if second_delim == -1:
        raise CanonicalBlockError("missing closing front matter '---'")

    fm_raw = block[3:second_delim].strip()
    body = block[second_delim + 4:].strip()

    try:
        metadata = yaml.safe_load(fm_raw)
    except Exception as exc:
        raise CanonicalBlockError(f"YAML parse failure: {exc}") from exc

    if not isinstance(metadata, dict):
        raise CanonicalBlockError("YAML front matter is not a valid mapping")

    return metadata, body


def validate_metadata(metadata: Dict[str, Any], expected_report_type: Optional[str] = None) -> None:
    """Validate required front matter fields."""
    if metadata.get("research_status") != "COMPLETE":
        raise CanonicalBlockError(
            f"invalid research_status: expected 'COMPLETE', got '{metadata.get('research_status')}'"
        )

    report_type = metadata.get("report_type")
    if not report_type or report_type not in VALID_REPORT_TYPES:
        raise CanonicalBlockError(f"invalid or missing report_type: '{report_type}'")

    if expected_report_type and report_type != expected_report_type:
        raise CanonicalBlockError(
            f"report_type mismatch: expected '{expected_report_type}', got '{report_type}'"
        )

    for req in ("run_id", "generated_at_taipei", "coverage_start_taipei", "coverage_end_taipei", "title"):
        val = metadata.get(req)
        if val is None or not str(val).strip():
            raise CanonicalBlockError(f"missing or empty required field: '{req}'")

    format_version = metadata.get("format_version")
    if format_version not in (1, 2, "1", "2"):
        raise CanonicalBlockError(f"unsupported format_version: '{format_version}', expected 1 or 2")


def validate_required_sections(markdown_body: str, report_type: str, format_version: Any = 1) -> None:
    """
    Verify that required sections exist in the markdown body.
    """
    if str(format_version) == "2" and report_type in REQUIRED_SECTIONS_V2:
        sections = REQUIRED_SECTIONS_V2[report_type]
    else:
        sections = REQUIRED_SECTIONS.get(report_type, [])
    if not sections:
        return

    # Extract all headings (lines starting with #, ##, ###, etc.)
    heading_lines = [
        line.lstrip("#").strip().casefold()
        for line in markdown_body.splitlines()
        if line.strip().startswith("#")
    ]
    headings_blob = "\n".join(heading_lines)

    missing = []
    for section in sections:
        sec_cf = section.casefold()
        # Check if any heading contains the section keyword or phrase
        if sec_cf not in headings_blob and not any(sec_cf in h for h in heading_lines):
            # Also check if it appears in markdown body as bold or section header
            if f"**{section.casefold()}**" not in markdown_body.casefold() and f"### {section.casefold()}" not in markdown_body.casefold():
                missing.append(section)

    if missing:
        raise CanonicalBlockError(f"missing required sections for {report_type}: {', '.join(missing)}")


def parse_and_validate_canonical_block(
    block: str, expected_report_type: Optional[str] = None
) -> Tuple[Dict[str, Any], str]:
    """
    Parse and validate a canonical block.
    Returns (metadata, markdown_body).
    """
    metadata, body = parse_frontmatter(block)
    validate_metadata(metadata, expected_report_type)
    validate_required_sections(body, metadata["report_type"], metadata.get("format_version", 1))
    return metadata, body


def extract_date_and_time(metadata: Dict[str, Any]) -> Tuple[str, str]:
    """Extract YYYY-MM-DD date and HHMM time from generated_at_taipei or coverage_end_taipei."""
    for field in ("generated_at_taipei", "coverage_end_taipei"):
        val = metadata.get(field)
        if val is None:
            continue
        if isinstance(val, datetime):
            return val.strftime("%Y-%m-%d"), val.strftime("%H%M")
        
        val_str = str(val).strip()
        iso_match = re.search(r"(\d{4}-\d{2}-\d{2})(?:[T\s](\d{2}):?(\d{2}))?", val_str)
        if iso_match:
            date_str = iso_match.group(1)
            time_str = (iso_match.group(2) or "00") + (iso_match.group(3) or "00")
            return date_str, time_str

    today = datetime.now().strftime("%Y-%m-%d")
    return today, "0000"


def determine_archive_filename(metadata: Dict[str, Any], existing_filenames: Optional[Set[str]] = None) -> str:
    """
    Determine the canonical filename for markdown snapshot according to specification Section 7:
    - Daily: Global_Daily_Brief_YYYY-MM-DD.md (or _rerun_HHMM.md if date exists)
    - Early Warning: Global_Macro_Early_Warning_YYYY-MM-DD_HHMM_<slug>.md or Global_Macro_Early_Warning_YYYY-MM-DD.md
    - Weekly: Weekly_Strategy_YYYY-MM-DD.md (or _rerun_HHMM.md if date exists)
    """
    report_type = metadata.get("report_type", "GLOBAL_DAILY_BRIEF")
    date_str, time_str = extract_date_and_time(metadata)
    slug = metadata.get("slug") or ""
    slug_clean = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug).strip("_")

    existing = existing_filenames or set()

    if report_type == "GLOBAL_DAILY_BRIEF":
        primary = f"Global_Daily_Brief_{date_str}.md"
        if primary not in existing:
            return primary
        return f"Global_Daily_Brief_{date_str}_rerun_{time_str}.md"

    elif report_type == "MACRO_TAIWAN_EARLY_WARNING":
        if slug_clean:
            return f"Global_Macro_Early_Warning_{date_str}_{time_str}_{slug_clean}.md"
        primary = f"Global_Macro_Early_Warning_{date_str}.md"
        if primary not in existing:
            return primary
        return f"Global_Macro_Early_Warning_{date_str}_{time_str}.md"

    elif report_type == "WEEKLY_STRATEGY":
        primary = f"Weekly_Strategy_{date_str}.md"
        if primary not in existing:
            return primary
        return f"Weekly_Strategy_{date_str}_rerun_{time_str}.md"

    # Default fallback
    return f"Report_{date_str}_{time_str}.md"
