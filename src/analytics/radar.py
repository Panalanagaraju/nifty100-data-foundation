from __future__ import annotations

from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config.settings import DATABASE, REPORTS_DIR


METRICS = ["return_on_equity_pct", "roce_pct", "net_profit_margin_pct", "debt_to_equity", "free_cash_flow_cr", "pat_cagr_5yr", "revenue_cagr_5yr", "composite_score"]


def build_radar_chart(company_row: pd.Series, peer_rows: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    labels = ["ROE", "ROCE", "NPM", "D/E", "FCF", "PAT CAGR", "Revenue CAGR", "Composite Score"]
    values = [company_row.get(metric, 0) for metric in ["return_on_equity_pct", "roce_pct", "net_profit_margin_pct", "debt_to_equity", "free_cash_flow_cr", "pat_cagr_5yr", "revenue_cagr_5yr", "composite_score"]]
    peer_values = [peer_rows[metric].mean() if not peer_rows.empty else 0 for metric in ["return_on_equity_pct", "roce_pct", "net_profit_margin_pct", "debt_to_equity", "free_cash_flow_cr", "pat_cagr_5yr", "revenue_cagr_5yr", "composite_score"]]

    angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
    angles += angles[:1]
    values += values[:1]
    peer_values += peer_values[:1]

    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(3.14159 / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.plot(angles, values, 'o-', linewidth=1, label='Company')
    ax.plot(angles, peer_values, 'o-', linewidth=1, label='Peer Average')
    ax.set_ylim(0, max(max(values), max(peer_values), 1))
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def main() -> None:
    conn = sqlite3.connect(DATABASE)
    ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    companies = pd.read_sql_query("SELECT id, company_name FROM companies", conn)
    peer_groups = pd.read_sql_query("SELECT company_id, peer_group_name FROM peer_groups", conn)
    conn.close()

    ratios = ratios.merge(companies.rename(columns={"id": "company_id"}), on="company_id", how="left")
    ratios = ratios.merge(peer_groups.rename(columns={"peer_group_name": "peer_group"}), on="company_id", how="left")

    output_dir = REPORTS_DIR / "radar_charts"
    output_dir.mkdir(parents=True, exist_ok=True)

    for _, row in ratios.head(10).iterrows():
        peer_group = row.get("peer_group") or "No peer group assigned"
        peer_rows = ratios[ratios["peer_group"] == peer_group] if peer_group != "No peer group assigned" else ratios.iloc[0:0]
        output_path = output_dir / f"{row['company_name']}_radar.png"
        build_radar_chart(row, peer_rows, output_path)

    print(f"Generated radar charts in {output_dir}")


if __name__ == "__main__":
    main()
