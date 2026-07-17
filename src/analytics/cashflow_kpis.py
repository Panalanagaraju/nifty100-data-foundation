"""
cashflow_kpis.py
---------------------------------------
Cash Flow KPIs and Analytics Module (Sprint 2)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to the Python path to allow direct script execution
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config.settings import OUTPUT_DIR, PROCESSED_DATA_DIR
from src.utils import logger, read_csv


def free_cash_flow(cfo, capex):
    if np.isscalar(cfo) and np.isscalar(capex):
        return cfo + capex if capex < 0 else cfo - capex

    cfo_series = pd.to_numeric(cfo, errors="coerce")
    capex_series = pd.to_numeric(capex, errors="coerce")
    return np.where(capex_series < 0, cfo_series + capex_series, cfo_series - capex_series)


def cfo_quality_score(cfo, net_profit):
    if net_profit in [0, None, np.nan]:
        return None, "Accrual Risk"
    ratio = cfo / net_profit
    if ratio >= 0.8:
        label = "High Quality"
    elif ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"
    return ratio, label


def capex_intensity(capex, revenue):
    if np.isscalar(capex) and np.isscalar(revenue):
        if revenue in [0, None, np.nan]:
            return None, "Moderate"
        ratio = abs(capex) / revenue * 100
        if ratio < 5:
            label = "Asset Light"
        elif ratio < 10:
            label = "Moderate"
        else:
            label = "Capital Intensive"
        return ratio, label

    capex_series = pd.to_numeric(capex, errors="coerce")
    revenue_series = pd.to_numeric(revenue, errors="coerce")
    ratio = np.divide(np.abs(capex_series), revenue_series) * 100
    labels = np.where(ratio < 5, "Asset Light", np.where(ratio < 10, "Moderate", "Capital Intensive"))
    return ratio, labels


def fcf_conversion(fcf, net_profit):
    if net_profit in [0, None, np.nan]:
        return None
    return fcf / net_profit * 100


def capital_allocation_pattern(cfo, cfi, cff):
    get_sign = lambda x: "+" if x >= 0 else "-"
    cfo_s, cfi_s, cff_s = get_sign(cfo), get_sign(cfi), get_sign(cff)
    pattern = (cfo_s, cfi_s, cff_s)
    pattern_map = {
        ("+", "-", "-"): "Reinvestor",
        ("+", "-", "+"): "Mixed",
        ("+", "+", "-"): "Liquidating Assets",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("-", "+", "-"): "Shrinking",
    }
    label = pattern_map.get(pattern, "Mixed")
    return cfo_s, cfi_s, cff_s, label


def generate_capital_allocation(output_path=None):
    cashflow_df = read_csv(PROCESSED_DATA_DIR / "cashflow.csv")
    output_path = Path(output_path or OUTPUT_DIR / "capital_allocation.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    allocation = []
    for _, row in cashflow_df.iterrows():
        cfo_s, cfi_s, cff_s, label = capital_allocation_pattern(row.get("operating_activity", 0), row.get("investing_activity", 0), row.get("financing_activity", 0))
        allocation.append({
            "company_id": row.get("company_id"),
            "year": row.get("year"),
            "cfo_sign": cfo_s,
            "cfi_sign": cfi_s,
            "cff_sign": cff_s,
            "pattern_label": label,
        })

    df = pd.DataFrame(allocation)
    df.to_csv(output_path, index=False)
    logger.success(f"Saved capital allocation -> {output_path}")
    return output_path


if __name__ == "__main__":
    generate_capital_allocation()