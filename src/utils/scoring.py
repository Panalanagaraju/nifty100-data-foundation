from __future__ import annotations

import numpy as np
import pandas as pd


def normalise_series(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    """
    Winsorizes a series at the 10th and 90th percentiles, then normalizes to a 0-100 scale.
    Handles NaNs by filling them with the median score (50).
    """
    # Replace inf with nan to handle them in clipping
    s = series.replace([np.inf, -np.inf], np.nan)

    # If all values are NaN, return a series of 50s
    if s.isna().all():
        return pd.Series(50, index=s.index)

    # Calculate quantiles, ignoring NaNs
    low = s.quantile(0.10)
    high = s.quantile(0.90)

    # Clip the series
    clipped = s.clip(lower=low, upper=high)

    # Normalize the clipped series to a 0-100 scale
    min_val, max_val = clipped.min(), clipped.max()

    if max_val == min_val:  # Avoid division by zero if all values are the same
        normalized = pd.Series(50, index=s.index)
    elif higher_is_better:
        normalized = 100 * (clipped - min_val) / (max_val - min_val)
    else:  # For metrics where lower is better (e.g., D/E)
        normalized = 100 * (max_val - clipped) / (max_val - min_val)

    # Fill any remaining NaNs (from original data) with the median score of 50
    normalized = normalized.fillna(50)

    return normalized


def score_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates a composite quality score based on several financial metrics.
    Normalizes scores within each broad_sector.
    """
    scored_df = df.copy()

    # Define metrics and their weights
    metrics_weights = {
        # Profitability (35%)
        "return_on_equity_pct": 0.15,
        "return_on_capital_employed_pct": 0.10, # Assuming this column exists
        "net_profit_margin_pct": 0.10,
        # Cash Quality (30%)
        "free_cash_flow_cagr_5yr": 0.15, # Assuming this column exists
        "cash_from_operations_cr": 0.15, # Proxy for CFO/PAT
        # Growth (20%)
        "revenue_cagr_5yr": 0.10,
        "pat_cagr_5yr": 0.10,
        # Leverage (15%)
        "debt_to_equity": -0.10,  # Negative weight as lower is better
        "interest_coverage": 0.05,
    }

    # Add placeholder columns if they don't exist
    if "return_on_capital_employed_pct" not in scored_df.columns:
        scored_df["return_on_capital_employed_pct"] = scored_df["return_on_equity_pct"]
    if "free_cash_flow_cagr_5yr" not in scored_df.columns:
        scored_df["free_cash_flow_cagr_5yr"] = scored_df["pat_cagr_5yr"]

    # Group by sector and normalize
    all_scores = []
    for sector, group in scored_df.groupby("broad_sector"):
        sector_scores = group.copy()
        sector_scores["composite_score"] = 0

        for metric, weight in metrics_weights.items():
            higher_is_better = weight > 0
            normalized_score = normalise_series(sector_scores[metric], higher_is_better)
            sector_scores["composite_score"] += normalized_score * abs(weight)

        all_scores.append(sector_scores)

    if not all_scores:
        return pd.DataFrame()

    final_df = pd.concat(all_scores)
    return final_df


if __name__ == "__main__":
    # This part would require a sample DataFrame to run.
    # The main execution is handled through engine.py and presets.py.
    print("Scoring module loaded. Run via presets.py or engine.py.")