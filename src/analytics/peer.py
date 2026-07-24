from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import numpy as np

from src.config.settings import DATABASE, PROJECT_ROOT


METRICS = [
    "return_on_equity_pct",
    "roce_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover",
]


def ensure_peer_table(db_path: str | None = None) -> Path:
    path = Path(db_path or DATABASE)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS peer_percentiles (company_id INTEGER, peer_group TEXT, metric TEXT, value REAL, rank REAL, year INTEGER)"
    )
    conn.commit()
    conn.close()
    return path


def build_peer_percentiles(ratios: pd.DataFrame) -> pd.DataFrame:
    if ratios.empty:
        return pd.DataFrame(columns=["company_id", "peer_group", "metric", "value", "rank", "year"])

    frame = ratios.copy()
    frame["peer_group"] = frame.get("peer_group", pd.Series(["No peer group assigned"] * len(frame)))
    frame["peer_group"] = frame["peer_group"].fillna("No peer group assigned")
    frame["peer_group"] = frame["peer_group"].astype(str)

    rows = []
    for metric in METRICS:
        if metric not in frame.columns:
            continue
        for _, group in frame.groupby("peer_group"):
            values = pd.to_numeric(group[metric], errors="coerce")
            if values.dropna().empty:
                continue
            if metric == "debt_to_equity":
                ranks = values.rank(method="average", pct=True)
                ranks = 1 - ranks
            else:
                ranks = values.rank(method="average", pct=True)
            for _, row in group.iterrows():
                value = values.loc[row.name]
                rows.append(
                    {
                        "company_id": row.get("company_id"),
                        "peer_group": group.iloc[0].get("peer_group", "No peer group assigned"),
                        "metric": metric,
                        "value": value,
                        "rank": ranks.loc[row.name],
                        "year": row.get("year"),
                    }
                )

    return pd.DataFrame(rows)


def write_peer_percentiles(df: pd.DataFrame, db_path: str | None = None) -> None:
    ensure_peer_table(db_path)
    conn = sqlite3.connect(db_path or DATABASE)
    conn.execute("DELETE FROM peer_percentiles")
    if not df.empty:
        df.to_sql("peer_percentiles", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()


def main() -> None:
    conn = sqlite3.connect(DATABASE)
    ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    companies = pd.read_sql_query("SELECT id, company_name FROM companies", conn)
    peer_groups = pd.read_sql_query("SELECT company_id, peer_group_name FROM peer_groups", conn)
    conn.close()

    ratios = ratios.merge(companies.rename(columns={"id": "company_id"}), on="company_id", how="left")
    ratios = ratios.merge(peer_groups.rename(columns={"peer_group_name": "peer_group"}), on="company_id", how="left")
    result = build_peer_percentiles(ratios)
    write_peer_percentiles(result)
    print(f"peer_percentiles -> {len(result)} rows")


if __name__ == "__main__":
    main()
