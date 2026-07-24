from __future__ import annotations

import sys
from pathlib import Path

# Add project root to the Python path to allow direct script execution
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import numpy as np


def normalise_series(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if values.dropna().empty:
        return pd.Series(0, index=series.index)
    lower = values.quantile(0.10)
    upper = values.quantile(0.90)
    clipped = values.clip(lower=lower, upper=upper)
    min_value = clipped.min()
    max_value = clipped.max()
    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return pd.Series(50, index=series.index)
    return ((clipped - min_value) / (max_value - min_value) * 100).fillna(50)


def score_quality(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    for column in ["return_on_equity_pct", "roce_pct", "net_profit_margin_pct", "free_cash_flow_cr", "cash_from_operations_cr", "revenue_cagr_5yr", "pat_cagr_5yr"]:
        if column not in working.columns:
            working[column] = np.nan

    working["debt_to_equity_score"] = normalise_series(working["debt_to_equity"].replace(0, np.nan))
    working["interest_coverage_score"] = normalise_series(working["interest_coverage"].replace(0, np.nan))

    score_map = {
        "profitability_score": "return_on_equity_pct",
        "roce_score": "roce_pct",
        "npm_score": "net_profit_margin_pct",
        "cash_quality_score": "free_cash_flow_cr",
        "cfo_pat_score": "cash_from_operations_cr",
        "growth_score": "revenue_cagr_5yr",
        "pat_growth_score": "pat_cagr_5yr",
        "leverage_score": "debt_to_equity_score",
        "icr_score": "interest_coverage_score",
    }

    for new_name, source in score_map.items():
        working[new_name] = normalise_series(working[source])

    working["composite_score"] = (
        0.35 * working["profitability_score"]
        + 0.30 * working["cash_quality_score"]
        + 0.20 * working["growth_score"]
        + 0.15 * working["leverage_score"]
    )
    return working.reset_index(drop=True)


def main() -> None:
    import sqlite3
    from src.config.settings import DATABASE

    conn = sqlite3.connect(DATABASE)
    ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    conn.close()
    scored = score_quality(ratios)
    print(scored[["company_id", "composite_score"]].head().to_string(index=False))


if __name__ == "__main__":
    main()
