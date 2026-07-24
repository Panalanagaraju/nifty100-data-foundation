from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import yaml

# Add project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config.settings import DATABASE, PROJECT_ROOT
from src.utils.db import get_connection


def load_config(path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Loads the screener configuration from the YAML file."""
    config_path = Path(path or PROJECT_ROOT / "config" / "screener_config.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _fetch_ratio_frame() -> pd.DataFrame:
    """Fetches the latest financial ratios for each company."""
    with get_connection(DATABASE) as conn:
        # Query to get the latest year's data for each company
        query = """
        WITH latest_years AS (
            SELECT company_id, MAX(year) as max_year
            FROM financial_ratios
            GROUP BY company_id
        )
        SELECT fr.*, c.company_name, pg.peer_group, pg.broad_sector
        FROM financial_ratios fr
        JOIN latest_years ly ON fr.company_id = ly.company_id AND fr.year = ly.max_year
        JOIN companies c ON fr.company_id = c.id
        LEFT JOIN peer_groups pg ON fr.company_id = pg.company_id;
        """
        df = pd.read_sql_query(query, conn)
    return df


def apply_filters(df: pd.DataFrame, thresholds: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies a series of filters to the financial ratios DataFrame.
    Handles special rules for financial companies and ICR.
    """
    filtered_df = df.copy()

    for key, value in thresholds.items():
        if "_min" in key:
            column = key.replace("_min", "")
            if column not in filtered_df.columns: continue

            # Special rule: Treat infinite ICR as passing any minimum
            if column == "interest_coverage":
                passes = (filtered_df[column] >= value) | (filtered_df[column] == float("inf"))
                filtered_df = filtered_df[passes]
            else:
                filtered_df = filtered_df[filtered_df[column] >= value]

        elif "_max" in key:
            column = key.replace("_max", "")
            if column not in filtered_df.columns: continue

            # Special rule: Skip D/E for Financial companies
            if column == "debt_to_equity":
                # Apply filter only to non-financial companies
                non_financials = filtered_df[filtered_df["broad_sector"] != "Financial Services"]
                financials = filtered_df[filtered_df["broad_sector"] == "Financial Services"]
                non_financials_filtered = non_financials[non_financials[column] <= value]
                filtered_df = pd.concat([non_financials_filtered, financials])
            else:
                filtered_df = filtered_df[filtered_df[column] <= value]

    return filtered_df


def run_screener(df: pd.DataFrame, thresholds: Dict[str, Any]) -> pd.DataFrame:
    from src.screener.scoring import score_quality

    if df.empty:
        return pd.DataFrame()

    # 1. Apply filters
    filtered_df = apply_filters(df, thresholds)

    if filtered_df.empty:
        return pd.DataFrame()

    # 2. Calculate composite score
    scored_df = score_quality(filtered_df)

    # 3. Sort by score
    sorted_df = scored_df.sort_values("composite_score", ascending=False)

    return sorted_df


def main() -> None:
    """Main function to demonstrate running a single screener."""
    print("Running a sample screener: Quality Compounder")
    ratios = _fetch_ratio_frame()
    config = load_config()
    preset = config.get("quality_compounder", {})
    result = run_screener(ratios, preset)
    print(f"Found {len(result)} companies.")
    print(result[["company_name", "composite_score", "return_on_equity_pct", "debt_to_equity"]].head())


if __name__ == "__main__":
    main()
