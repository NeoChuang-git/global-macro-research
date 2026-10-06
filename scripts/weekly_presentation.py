"""Exact, source-preserving tables for the approved October 4 Weekly preview.

These are reviewed presentation mappings, not a prose-to-table parser.
Unrecognized reports, sections, or source text remain untouched.
"""

from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag


@dataclass(frozen=True)
class SectionTable:
    heading: str
    schema: str
    source: str
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    prefix: str = ""
    suffix: str = ""


SECTION_TABLES = (
    SectionTable(
        heading="Regime 轉換矩陣",
        schema="regime-transition-v1",
        source="Soft Landing 28%→31%；Sticky Inflation 34%→32%；Growth Slowdown 17%→20%；Funding/Liquidity Stress 13%→10%；Stagflation 8%→7%。主Regime仍為Soft Landing / Sticky Inflation雙峰；Risk Light維持ORANGE。",
        headers=("情境", "前期機率", "本期機率"),
        rows=(
            ("Soft Landing", "28%", "31%"),
            ("Sticky Inflation", "34%", "32%"),
            ("Growth Slowdown", "17%", "20%"),
            ("Funding/Liquidity Stress", "13%", "10%"),
            ("Stagflation", "8%", "7%"),
        ),
        suffix="主Regime仍為Soft Landing / Sticky Inflation雙峰；Risk Light維持ORANGE。",
    ),
    SectionTable(
        heading="每週總經訊號板",
        schema="macro-signal-board-v1",
        source="Growth：us_growth_momentum →/↘；Inflation：us_inflation_momentum ↗但energy_inflation ↘；Labor：labor_market_cooling形成Trend；Fed：fed_policy_tightening ↗；Rates：rates_shock ↘；Liquidity/Credit暫無系統性stress；Fiscal：treasury_supply_stress ↘；FX funding中性；Trade：global_trade_cycle ↗；Asia/Taiwan：taiwan_leading_cycle ↗。",
        headers=("領域", "訊號與判讀"),
        rows=(
            ("Growth", "us_growth_momentum →/↘"),
            ("Inflation", "us_inflation_momentum ↗但energy_inflation ↘"),
            ("Labor", "labor_market_cooling形成Trend"),
            ("Fed", "fed_policy_tightening ↗"),
            ("Rates", "rates_shock ↘"),
            ("Liquidity/Credit", "暫無系統性stress"),
            ("Fiscal", "treasury_supply_stress ↘"),
            ("FX funding", "中性"),
            ("Trade", "global_trade_cycle ↗"),
            ("Asia/Taiwan", "taiwan_leading_cycle ↗"),
        ),
    ),
    SectionTable(
        heading="訊號持續性評分",
        schema="signal-persistence-v1",
        source="ai_fundamental_cycle 91；memory_cycle 90；energy_inflation 88；taiwan_leading_cycle 86；rates_shock 83；labor_market_cooling 66；fed_policy_tightening 64；semiconductor_relative_weakness 28。",
        headers=("訊號", "持續性評分"),
        rows=(
            ("ai_fundamental_cycle", "91"),
            ("memory_cycle", "90"),
            ("energy_inflation", "88"),
            ("taiwan_leading_cycle", "86"),
            ("rates_shock", "83"),
            ("labor_market_cooling", "66"),
            ("fed_policy_tightening", "64"),
            ("semiconductor_relative_weakness", "28"),
        ),
    ),
    SectionTable(
        heading="總經資料與政策深度分析",
        schema="policy-analysis-v1",
        source="FACT：ISM 54.5、Prices 77.9；非農+2.9萬、失業率4.2%；PCE年增3.4%。MARKET EXPECTATION：10月Fed暫停機率大升、12月仍可能行動。INFERENCE：短端政策壓力改善、長端能源／財政壓力未改善，不等於全面金融條件放鬆。",
        headers=("類別", "內容"),
        rows=(
            ("FACT", "ISM 54.5、Prices 77.9\n非農+2.9萬、失業率4.2%\nPCE年增3.4%。"),
            ("MARKET EXPECTATION", "10月Fed暫停機率大升、12月仍可能行動。"),
            ("INFERENCE", "短端政策壓力改善、長端能源／財政壓力未改善，不等於全面金融條件放鬆。"),
        ),
    ),
    SectionTable(
        heading="情境矩陣與風險燈號",
        schema="risk-scenarios-v1",
        source="Risk Light：ORANGE。GREEN：油價顯著回落、10Y<5%、信用穩定。YELLOW：長端回落但估值仍高。RED：能源再升、10Y創高、信用利差擴張且AI財測下修。",
        headers=("燈號", "觸發條件"),
        rows=(
            ("GREEN", "油價顯著回落、10Y<5%、信用穩定。"),
            ("YELLOW", "長端回落但估值仍高。"),
            ("RED", "能源再升、10Y創高、信用利差擴張且AI財測下修。"),
        ),
        prefix="Risk Light：ORANGE。",
    ),
)


def apply_weekly_tables(soup: BeautifulSoup, metadata: dict) -> None:
    """Replace only complete, plain paragraphs whose approved source matches."""
    if (metadata.get("report_type"), metadata.get("run_id")) != (
        "WEEKLY_STRATEGY", "WKS-20261004-2045"
    ):
        return

    for spec in SECTION_TABLES:
        headings = [h for h in soup.find_all("h2") if h.get_text() == spec.heading]
        if len(headings) != 1:
            continue
        blocks = []
        for sibling in headings[0].next_siblings:
            if isinstance(sibling, Tag):
                if sibling.name in ("h1", "h2"):
                    break
                blocks.append(sibling)
        if len(blocks) != 1:
            continue
        paragraph = blocks[0]
        if paragraph.name != "p" or paragraph.find(True) or paragraph.get_text() != spec.source:
            continue

        table = soup.new_tag("table", attrs={
            "class": "weekly-local-table", "data-weekly-schema": spec.schema,
            "aria-label": spec.heading,
        })
        head = soup.new_tag("thead")
        row = soup.new_tag("tr")
        for label in spec.headers:
            cell = soup.new_tag("th", attrs={"scope": "col"})
            cell.string = label
            row.append(cell)
        head.append(row)
        table.append(head)
        body = soup.new_tag("tbody")
        for values in spec.rows:
            row = soup.new_tag("tr")
            for value in values:
                cell = soup.new_tag("td")
                for index, line in enumerate(value.split("\n")):
                    if index:
                        cell.append(soup.new_tag("br"))
                    cell.append(line)
                row.append(cell)
            body.append(row)
        table.append(body)
        if spec.prefix:
            prefix = soup.new_tag("p")
            prefix.string = spec.prefix
            paragraph.insert_before(prefix)
        paragraph.replace_with(table)
        if spec.suffix:
            suffix = soup.new_tag("p")
            suffix.string = spec.suffix
            table.insert_after(suffix)


def label_weekly_risk_badges(soup: BeautifulSoup) -> None:
    """Keep scenario labels visible after the legacy emoji-only enrichment."""
    table = soup.select_one('table[data-weekly-schema="risk-scenarios-v1"]')
    if table is None:
        return
    for row, label, icon in zip(table.select("tbody tr"),
                                ("GREEN", "YELLOW", "RED"), ("🟢", "🟡", "🔴")):
        cell = row.find("td")
        cell.clear()
        badge = soup.new_tag("span", attrs={"class": f"risk risk-{label.lower()}"})
        decoration = soup.new_tag("span", attrs={"aria-hidden": "true"})
        decoration.string = icon
        badge.append(decoration)
        badge.append(" " + label)
        cell.append(badge)
