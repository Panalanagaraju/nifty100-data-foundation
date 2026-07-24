from __future__ import annotations

import pandas as pd
import numpy as np

from src.screener.scoring import normalise_series, score_quality


def test_normalise_series():
    s = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, np.nan])
    # Quantiles: 0.1 -> 21, 0.9 -> 99
    # Clipped: [21, 21, 30, 40, 50, 60, 70, 80, 90, 99, 99, nan]
    # Min: 21, Max: 99
    # Normalised: ((s_clipped - 21) / 78) * 100
    # nan is filled with 50
    normalised = normalise_series(s)
    assert normalised.notna().all()
    assert normalised.iloc[0] == 0.0  # 10 is clipped to 21, so ((21-21)/78)*100 = 0
    assert normalised.iloc[-1] == 50.0  # nan becomes 50
    assert normalised.iloc[9] == 100.0 # 100 is clipped to 99, so ((99-21)/78)*100 = 100


def test_score_quality_adds_composite_score():
    df = pd.DataFrame([
        {"company_id": 1, "return_on_equity_pct": 20, "free_cash_flow_cr": 100, "revenue_cagr_5yr": 15, "debt_to_equity": 0.1},
        {"company_id": 2, "return_on_equity_pct": 10, "free_cash_flow_cr": 50, "revenue_cagr_5yr": 5, "debt_to_equity": 0.8},
    ])
    scored = score_quality(df)
    assert "composite_score" in scored.columns
    assert scored.iloc[0]["composite_score"] > scored.iloc[1]["composite_score"]