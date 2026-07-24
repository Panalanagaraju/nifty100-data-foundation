from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.utils.excel_export import export_peer_comparison, export_screener_report


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_export_screener_report(temp_output_dir: Path):
    presets = {"My Screener": pd.DataFrame([{"A": 1, "B": 2}])}
    output_file = temp_output_dir / "screener.xlsx"
    result_path = export_screener_report(presets, output_file)
    assert result_path.exists()


def test_export_peer_comparison(temp_output_dir: Path):
    peer_data = pd.DataFrame(
        [{"company_id": 1, "year": 2023, "peer_group": "IT", "metric": "roe", "value": 20, "rank": 0.9}]
    )
    output_file = temp_output_dir / "peer.xlsx"
    result_path = export_peer_comparison(peer_data, output_file)
    assert result_path.exists()