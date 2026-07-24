from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.screener.engine import load_config, run_screener, _fetch_ratio_frame


def run_preset(name: str) -> pd.DataFrame:
    config = load_config()
    thresholds = config.get(name, {})
    ratios = _fetch_ratio_frame()
    return run_screener(ratios, thresholds)


def run_all_presets() -> Dict[str, pd.DataFrame]:
    config = load_config()
    ratios = _fetch_ratio_frame()
    results = {}
    for preset_name in config:
        results[preset_name] = run_screener(ratios, config[preset_name])
    return results


def main() -> None:
    for preset_name in ["quality_compounder", "value_pick", "growth_accelerator", "dividend_champion", "debt_free_bluechip", "turnaround_watch"]:
        result_df = run_preset(preset_name)
        print(f"Preset '{preset_name}': Found {len(result_df)} companies.")


if __name__ == "__main__":
    main()
