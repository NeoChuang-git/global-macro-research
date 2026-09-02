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
        "Cross-Asset Confirmation",
        "Evidence vs Counter-evidence",
        "Taiwan Transmission",
        "Industry / Equity Sensitivity",
        "Classification & Risk Light",
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

    # If markdown body has a specific full descriptive H1 title (e.g. "# Category | Full Subtitle"), use it
    h1_match = re.search(r"^\s*#\s+(.+)$", body, flags=re.MULTILINE)
    if h1_match:
        h1_text = h1_match.group(1).strip()
        if "｜" in h1_text or "|" in h1_text or len(h1_text) > len(str(metadata.get("title", ""))):
            metadata["title"] = h1_text

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


SECTION_KEYWORD_ALIASES: Dict[str, List[str]] = {
    "executive summary": ["executive summary", "執行摘要", "executive intelligence summary", "executive take", "executive strategy summary"],
    "market signals": ["market signals", "市場訊號", "signal board", "today top 3 market signals", "今日三大市場訊號", "signal delta"],
    "impact": ["impact", "市場影響力", "top 3 market impact events", "市場影響力前三大事件", "events", "事件"],
    "strategy": ["strategy", "策略", "us tech strategy", "美國科技股策略", "taiwan equity action matrix", "strategy implication matrix"],
    "taiwan": ["taiwan", "台灣", "taiwan economy", "taiwan industry", "taiwan impact", "台灣 ai", "台灣傳導", "taiwan transmission", "taiwan relevance"],
    "catalysts": ["catalysts", "催化劑", "next catalysts", "下一階段催化劑", "catalyst calendar"],
    "source audit": ["source audit", "資料來源", "資料來源審計", "來源審計", "source"],
}


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
    body_cf = markdown_body.casefold()

    missing = []
    for section in sections:
        sec_cf = section.casefold()
        aliases = SECTION_KEYWORD_ALIASES.get(sec_cf, [sec_cf])
        found = False
        for alias in aliases:
            a_cf = alias.casefold()
            if a_cf in headings_blob or any(a_cf in h for h in heading_lines) or f"**{a_cf}**" in body_cf or f"### {a_cf}" in body_cf or f"## {a_cf}" in body_cf:
                found = True
                break

        if not found:
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
