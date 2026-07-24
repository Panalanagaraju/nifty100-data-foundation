from __future__ import annotations

import pandas as pd

from src.screener.engine import _fetch_ratio_frame, load_config, run_screener


def run_preset(preset_name: str, df: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Runs a single, specified screener preset.
    """
    if df is None:
        df = _fetch_ratio_frame()

    config = load_config()
    if preset_name not in config:
        raise ValueError(f"Preset '{preset_name}' not found in config.")

    thresholds = config[preset_name]
    print(f"--- Running Screener: {preset_name.replace('_', ' ').title()} ---")
    result = run_screener(df, thresholds)
    print(f"Found {len(result)} companies matching the criteria.")
    return result


def run_all_presets() -> dict[str, pd.DataFrame]:
    """
    Runs all available screener presets and returns a dictionary of results.
    """
    df = _fetch_ratio_frame()
    config = load_config()
    all_results = {}

    for preset_name in config:
        result_df = run_preset(preset_name, df.copy())
        all_results[preset_name] = result_df

    return all_results


def main():
    """Main function to run and display results for all presets."""
    results = run_all_presets()
    for name, df in results.items():
        print(f"\n--- Top 5 for {name.replace('_', ' ').title()} ---")
        print(df[["company_name", "composite_score"]].head())


if __name__ == "__main__":
    main()