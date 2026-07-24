import pandas as pd

from src.screener.engine import apply_filters, load_config, run_screener
from src.screener.presets import run_preset


def test_load_config_returns_preset_thresholds():
    config = load_config()
    assert isinstance(config, dict)
    assert "quality_compounder" in config
    assert config["quality_compounder"]["roe_min"] > 0


def test_apply_filters_skips_financial_de_filter():
    df = pd.DataFrame(
        [
            {"company_name": "HDFCBANK", "broad_sector": "Financial", "return_on_equity_pct": 20, "debt_to_equity": 1.2, "free_cash_flow_cr": 5, "revenue_cagr_5yr": 12, "interest_coverage": 2},
            {"company_name": "TCS", "broad_sector": "IT", "return_on_equity_pct": 20, "debt_to_equity": 0.5, "free_cash_flow_cr": 5, "revenue_cagr_5yr": 12, "interest_coverage": 2},
        ]
    )
    filtered = apply_filters(df, {"debt_equity_max": 1, "roe_min": 15, "fcf_min": 0, "revenue_cagr_5yr_min": 10})
    assert len(filtered) == 2


def test_run_screener_adds_composite_score_and_sorts():
    df = pd.DataFrame(
        [
            {"company_name": "A", "broad_sector": "IT", "return_on_equity_pct": 10, "debt_to_equity": 0.2, "free_cash_flow_cr": 4, "revenue_cagr_5yr": 8, "interest_coverage": 3, "net_profit_margin_pct": 6, "cash_from_operations_cr": 7, "pat_cagr_5yr": 9},
            {"company_name": "B", "broad_sector": "IT", "return_on_equity_pct": 20, "debt_to_equity": 0.5, "free_cash_flow_cr": 6, "revenue_cagr_5yr": 15, "interest_coverage": 8, "net_profit_margin_pct": 10, "cash_from_operations_cr": 10, "pat_cagr_5yr": 12},
        ]
    )
    result = run_screener(df, {"roe_min": 10, "debt_equity_max": 1, "fcf_min": 0, "revenue_cagr_5yr_min": 10})
    assert "composite_score" in result.columns
    assert result.iloc[0]["company_name"] == "B"


def test_run_preset_returns_dataframe():
    result = run_preset("quality_compounder")
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
