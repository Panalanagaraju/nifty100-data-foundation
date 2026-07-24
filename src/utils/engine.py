from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.config.settings import DATABASE, PROJECT_ROOT
from src.screener.scoring import score_quality
from src.utils.db import get_connection

CONFIG_PATH = PROJECT_ROOT / "config/screener_config.yaml"


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
        SELECT fr.*, c.company_name, s.broad_sector
        FROM financial_ratios fr
        JOIN latest_years ly ON fr.company_id = ly.company_id AND fr.year = ly.max_year
        JOIN companies c ON fr.company_id = c.id
        LEFT JOIN sectors s ON fr.company_id = s.company_id;
        """
        df = pd.read_sql_query(query, conn)
    return df


def load_config() -> dict:
    """Loads the screener configuration from the YAML file."""
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def _apply_filter(df: pd.DataFrame, column: str, min_val: float | None, max_val: float | None) -> pd.DataFrame:
    """Generic function to apply a min/max filter to a DataFrame column."""
    if min_val is not None:
        df = df[df[column] >= min_val]
    if max_val is not None:
        df = df[df[column] <= max_val]
    return df


def apply_filters(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """
    Applies a series of filters to the financial ratios DataFrame.
    Handles special rules for financial companies and ICR.
    """
    filtered_df = df.copy()

    # Map threshold keys to DataFrame columns and filter types (min/max)
    filter_map = {
        "return_on_equity_pct": ("min",),
        "debt_to_equity": ("max",),
        "free_cash_flow_cr": ("min",),
        "revenue_cagr_5yr": ("min",),
        "pat_cagr_5yr": ("min",),
        "net_profit_margin_pct": ("min",),
        "interest_coverage": ("min",),
        "book_value_per_share": ("min",),
        "dividend_payout_ratio_pct": ("max",),
    }

    for key, types in filter_map.items():
        for f_type in types:
            threshold_key = f"{key}_{f_type}"
            if threshold_key in thresholds:
                value = thresholds[threshold_key]

                # Special rule: Skip D/E for Financial companies
                if key == "debt_to_equity" and f_type == "max":
                    # Apply filter only to non-financial companies
                    non_financials = filtered_df[filtered_df["broad_sector"] != "Financial"]
                    financials = filtered_df[filtered_df["broad_sector"] == "Financial"]
                    non_financials_filtered = non_financials[non_financials[key] <= value]
                    filtered_df = pd.concat([non_financials_filtered, financials])
                    continue

                # Special rule: Treat infinite ICR as passing any minimum
                if key == "interest_coverage" and f_type == "min":
                    # Companies with infinite ICR always pass
                    passes = (filtered_df[key] >= value) | (filtered_df[key] == np.inf)
                    filtered_df = filtered_df[passes]
                    continue

                # Standard filter application
                if f_type == "min":
                    filtered_df = filtered_df[filtered_df[key] >= value]
                elif f_type == "max":
                    filtered_df = filtered_df[filtered_df[key] <= value]

    return filtered_df


def run_screener(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """
    Main function to run a screen: apply filters, score, and sort.
    """
    # 1. Apply filters
    filtered_df = apply_filters(df, thresholds)

    if filtered_df.empty:
        return pd.DataFrame()

    # 2. Calculate composite score
    scored_df = score_quality(filtered_df)

    # 3. Sort by score
    sorted_df = scored_df.sort_values("composite_score", ascending=False)

    return sorted_df


def main():
    """Main function to demonstrate running a single screener."""
    print("Running a sample screener: Quality Compounder")
    all_data = _fetch_ratio_frame()
    config = load_config()
    quality_thresholds = config.get("quality_compounder", {})
    result = run_screener(all_data, quality_thresholds)
    print(f"Found {len(result)} companies.")
    print(result[["company_name", "composite_score", "return_on_equity_pct", "debt_to_equity"]].head())


if __name__ == "__main__":
    main()