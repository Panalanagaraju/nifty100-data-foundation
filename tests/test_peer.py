from __future__ import annotations

import pandas as pd
import pytest

from src.analytics.peer import build_peer_percentiles


@pytest.fixture
def sample_ratios_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"company_id": 1, "year": 2023, "peer_group": "IT", "return_on_equity_pct": 20, "debt_to_equity": 0.1},
            {"company_id": 2, "year": 2023, "peer_group": "IT", "return_on_equity_pct": 10, "debt_to_equity": 0.5},
            {"company_id": 3, "year": 2023, "peer_group": "Banks", "return_on_equity_pct": 15, "debt_to_equity": 8.0},
            {"company_id": 4, "year": 2023, "peer_group": "IT", "return_on_equity_pct": 30, "debt_to_equity": 0.2},
        ]
    )


def test_build_peer_percentiles(sample_ratios_df: pd.DataFrame):
    result = build_peer_percentiles(sample_ratios_df)
    assert not result.empty
    assert len(result) == 8  # 4 companies * 2 metrics

    it_roe = result[(result["peer_group"] == "IT") & (result["metric"] == "return_on_equity_pct")]
    assert it_roe[it_roe["company_id"] == 4]["rank"].iloc[0] == 1.0  # 30 is highest ROE

    it_de = result[(result["peer_group"] == "IT") & (result["metric"] == "debt_to_equity")]
    assert it_de[it_de["company_id"] == 1]["rank"].iloc[0] == 1.0  # 0.1 is lowest D/E, so rank is 1.0