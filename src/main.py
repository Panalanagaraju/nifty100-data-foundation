from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import pandas as pd

from src.analytics.peer import main as run_peer_analysis
from src.analytics.radar import main as run_radar_charts
from src.screener.presets import run_all_presets
from src.utils.excel_export import export_screener_report, export_peer_comparison


def load():
    print("Loading data...")


def validate():
    print("Running validation...")


def clean():
    print("Cleaning data...")


def report():
    print("Generating report...")


def dashboard():
    print("Launching dashboard...")


def api():
    print("Starting API...")


def ratios():
    print("Calculating financial ratios...")


def sprint3():
    """Runs the full Sprint 3 pipeline."""
    print("--- Starting Sprint 3 Pipeline ---")

    # 1. Run all screener presets
    presets = run_all_presets()

    # 2. Export screener results to Excel
    export_screener_report(presets, "output/screener_output.xlsx")

    # 3. Run peer analysis and save to DB
    run_peer_analysis()

    # 4. Generate and save radar charts
    run_radar_charts()

    print("Sprint 3 pipeline completed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <command>")
        sys.exit()

    command = sys.argv[1]

    commands = {
        "load": load,
        "validate": validate,
        "clean": clean,
        "report": report,
        "dashboard": dashboard,
        "api": api,
        "ratios": ratios,
        "sprint3": sprint3,
    }

    if command in commands:
        commands[command]()
    else:
        print("Unknown command")