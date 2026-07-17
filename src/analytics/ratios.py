"""
ratios.py
---------------------------------------
Financial Ratio Calculation Module (Sprint 2)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to the Python path to allow direct script execution
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config.settings import PROCESSED_DATA_DIR, OUTPUT_DIR
from src.utils import logger, read_csv


def _safe_divide(numerator, denominator):
    if np.isscalar(numerator) and np.isscalar(denominator):
        if denominator in [0, None, np.nan] or denominator == 0:
            return None
        return numerator / denominator

    num = pd.to_numeric(numerator, errors="coerce")
    den = pd.to_numeric(denominator, errors="coerce")
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.divide(num, den)
        return np.where(np.isinf(ratio) | (den == 0) | pd.isna(den), np.nan, ratio)


def net_profit_margin(net_profit, sales):
    ratio = _safe_divide(net_profit, sales)
    if ratio is None:
        return None
    return ratio * 100


def operating_profit_margin(operating_profit, sales):
    ratio = _safe_divide(operating_profit, sales)
    if ratio is None:
        return None
    return ratio * 100


def return_on_equity(net_profit, total_equity, debt=None):
    if np.isscalar(net_profit) and np.isscalar(total_equity):
        if total_equity in [0, None, np.nan] or total_equity <= 0:
            return None
        denominator = total_equity + (debt if debt is not None else 0)
        if denominator in [0, None, np.nan] or denominator <= 0:
            return None
        return (net_profit / denominator) * 100

    net_profit_series = pd.to_numeric(net_profit, errors="coerce")
    equity_series = pd.to_numeric(total_equity, errors="coerce")
    debt_series = pd.to_numeric(debt if debt is not None else 0, errors="coerce")
    denominator = equity_series + debt_series
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.divide(net_profit_series, denominator)
        ratio = np.where(denominator > 0, ratio, np.nan)
    return ratio * 100


def return_on_capital_employed(ebit, capital_employed, current_liabilities=None, total_assets=None):
    if np.isscalar(ebit) and np.isscalar(capital_employed):
        denominator = capital_employed + (current_liabilities if current_liabilities is not None else 0) + (total_assets if total_assets is not None else 0)
        if denominator in [0, None, np.nan] or denominator <= 0:
            return None
        return (ebit / denominator) * 100

    ebit_series = pd.to_numeric(ebit, errors="coerce")
    capital_series = pd.to_numeric(capital_employed, errors="coerce")
    current_liabilities_series = pd.to_numeric(current_liabilities if current_liabilities is not None else 0, errors="coerce")
    total_assets_series = pd.to_numeric(total_assets if total_assets is not None else 0, errors="coerce")
    denominator = capital_series + current_liabilities_series + total_assets_series
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.divide(ebit_series, denominator)
        ratio = np.where(denominator > 0, ratio, np.nan)
    return ratio * 100


def return_on_assets(net_profit, total_assets):
    ratio = _safe_divide(net_profit, total_assets)
    if ratio is None:
        return None
    return ratio * 100


def debt_to_equity(total_debt, total_equity, broad_sector=None):
    if np.isscalar(total_debt) and np.isscalar(total_equity):
        if total_debt in [0, None, np.nan]:
            return 0
        if total_equity in [0, None, np.nan] or total_equity <= 0:
            return None
        return total_debt / total_equity

    debt_series = pd.to_numeric(total_debt, errors="coerce")
    equity_series = pd.to_numeric(total_equity, errors="coerce")
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.divide(debt_series, equity_series)
        ratio = np.where((debt_series == 0) | pd.isna(debt_series), 0, ratio)
        ratio = np.where((equity_series <= 0) | pd.isna(equity_series), np.nan, ratio)
    return ratio


def interest_coverage_ratio(ebit, interest_expense, tax_rate=None):
    if np.isscalar(ebit) and np.isscalar(interest_expense):
        if interest_expense in [0, None, np.nan]:
            return None  # Undefined if there's no interest expense
        return ebit / abs(interest_expense)

    ebit_series = pd.to_numeric(ebit, errors="coerce")
    interest_series = pd.to_numeric(interest_expense, errors="coerce")
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.divide(ebit_series, np.abs(interest_series))
        ratio = np.where(interest_series == 0, np.nan, ratio)
    return ratio


def net_debt(total_debt, cash_and_equivalents):
    return total_debt - cash_and_equivalents


def asset_turnover(sales, total_assets):
    return _safe_divide(sales, total_assets)


def generate_ratio_edge_cases(output_path=None):
    profitandloss_df = read_csv(PROCESSED_DATA_DIR / "profitandloss.csv")
    balancesheet_df = read_csv(PROCESSED_DATA_DIR / "balancesheet.csv")
    merged = profitandloss_df.merge(
        balancesheet_df[["company_id", "year", "total_assets", "borrowings", "equity_capital", "reserves"]],
        on=["company_id", "year"],
        how="left",
    )
    merged["capital_employed"] = pd.to_numeric(merged["total_assets"], errors="coerce")
    merged["computed_roce"] = return_on_capital_employed(pd.to_numeric(merged["operating_profit"], errors="coerce"), merged["capital_employed"])
    merged["source_roce"] = pd.to_numeric(merged["operating_profit"], errors="coerce")
    mask = merged["computed_roce"].notna() & merged["source_roce"].notna() & (abs(pd.to_numeric(merged["computed_roce"], errors="coerce") - pd.to_numeric(merged["source_roce"], errors="coerce")) > 5)
    edge_cases = merged.loc[mask, ["company_id", "year", "computed_roce", "source_roce"]].copy()
    edge_cases["difference"] = abs(edge_cases["computed_roce"] - edge_cases["source_roce"])
    edge_cases["reason"] = "ROCE variance"
    output_path = Path(output_path or OUTPUT_DIR / "ratio_edge_cases.log")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    edge_cases.to_csv(output_path, index=False)
    logger.success(f"Saved ratio edge cases -> {output_path}")
    return output_path


if __name__ == "__main__":
    generate_ratio_edge_cases()