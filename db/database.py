"""
database.py
Sprint 1 Day 04-05
"""

import sqlite3
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow_kpis import free_cash_flow, cfo_quality_score, capex_intensity, fcf_conversion
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)
from src.config.settings import (
    DATABASE,
    SCHEMA,
    PROCESSED_DATA_DIR,
    LOAD_ORDER,
    SQLITE_PRAGMA,
)
from src.etl.normaliser import DataNormaliser
from src.utils import (
    find_col,
    logger,
    read_csv,
    file_exists,
    print_header,
)


def connect():
    conn = sqlite3.connect(DATABASE)
    for pragma in SQLITE_PRAGMA:
        conn.execute(pragma)
    logger.info(f"Connected to {DATABASE}")
    return conn


def create_schema(connection):
    with open(SCHEMA, "r", encoding="utf-8") as f:
        connection.executescript(f.read())
    logger.success("Schema created")


def insert_dataframe(connection, dataframe, table_name):
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    db_schema = {row[1]: row[2] for row in cursor.fetchall()}

    df_filtered = dataframe[[col for col in dataframe.columns if col in db_schema]].copy()

    for col_name, col_type in db_schema.items():
        if col_name in df_filtered.columns and any(token in col_type.upper() for token in ["INT", "REAL", "FLOAT", "DOUBLE"]):
            df_filtered[col_name] = pd.to_numeric(df_filtered[col_name], errors="coerce")

    df_filtered.to_sql(table_name, connection, if_exists="append", index=False)


def load_all_tables(connection, processed_files, company_map):
    for table in LOAD_ORDER:
        if table in {"companies", "financial_ratios"}:
            continue

        if table in processed_files:
            df = read_csv(processed_files[table])

            if table != "companies":
                company_column = None
                for candidate in ["company", "company_name", "companyid", "company_id", "ticker", "symbol"]:
                    if candidate in df.columns:
                        company_column = candidate
                        break

                if "year" in df.columns:
                    df["year"] = df["year"].apply(lambda value: DataNormaliser.normalize_year(value))
                    df = df.dropna(subset=["year"])

                if {"company_id", "year"}.issubset(df.columns):
                    df = df.sort_values(["company_id", "year"], kind="mergesort")
                    df = df.drop_duplicates(subset=["company_id", "year"], keep="last")

                if company_column is not None:
                    normalized_values = df[company_column].astype(str).str.strip().str.lower()
                    lookup_map = {str(value).strip().lower(): company_id for value, company_id in company_map.items()}
                    mapped_values = normalized_values.map(lookup_map)

                    if mapped_values.isna().all():
                        numeric_values = pd.to_numeric(df[company_column], errors="coerce")
                        if numeric_values.notna().any():
                            mapped_values = numeric_values
                    else:
                        fallback = pd.to_numeric(df[company_column], errors="coerce")
                        mapped_values = mapped_values.fillna(fallback)

                    df["company_id"] = mapped_values

                    unmapped_rows = df[df["company_id"].isna()]
                    if not unmapped_rows.empty:
                        logger.warning(
                            f"Could not map {len(unmapped_rows)} rows for table '{table}'. Unmapped values: {unmapped_rows[company_column].unique().tolist()}"
                        )
                        df = df.dropna(subset=["company_id"])
                    df["company_id"] = df["company_id"].astype(int)

            insert_dataframe(connection, df, table)
            logger.success(f"Loaded {len(df)} rows into '{table}'")
        else:
            logger.warning(f"No processed file found for table '{table}', skipping.")


def populate_financial_ratios(connection):
    logger.info("Calculating and populating financial ratios...")
    
    # Step 1: Read data directly from the database tables for consistency
    profitandloss_df = pd.read_sql("SELECT * FROM profitandloss", connection)
    balancesheet_df = pd.read_sql("SELECT * FROM balancesheet", connection)
    cashflow_df = pd.read_sql("SELECT * FROM cashflow", connection)
    sectors_df = pd.read_sql("SELECT company_id, broad_sector FROM sectors", connection)

    # Step 2: Merge the financial statements into a single DataFrame
    # Start with the P&L data as the base
    ratio_frame = profitandloss_df.copy()

    # Merge with Balance Sheet data
    ratio_frame = pd.merge(
        ratio_frame,
        balancesheet_df[["company_id", "year", "equity_capital", "reserves", "borrowings", "total_assets", "total_liabilities"]],
        on=["company_id", "year"],
        how="left",
    )
    # Merge with Cash Flow data
    ratio_frame = pd.merge(
        ratio_frame,
        cashflow_df[["company_id", "year", "operating_activity", "investing_activity", "financing_activity", "net_cash_flow"]],
        on=["company_id", "year"],
        how="left",
    )
    # Merge with Sectors data
    ratio_frame = pd.merge(
        ratio_frame,
        sectors_df.drop_duplicates(subset=['company_id']),  # Ensure one sector per company
        on="company_id",
        how="left",
    )

    # Step 3: Prepare columns for calculation (convert to numeric, handle errors)
    ratio_frame["year"] = ratio_frame["year"].apply(lambda value: DataNormaliser.normalize_year(value))
    
    # Define columns to convert to numeric
    numeric_cols = [
        "equity_capital", "reserves", "sales", "net_profit", "operating_profit",
        "interest", "borrowings", "total_assets", "operating_activity",
        "investing_activity", "eps"
    ]
    for col in numeric_cols:
        if col in ratio_frame.columns:
            ratio_frame[col] = pd.to_numeric(ratio_frame[col], errors="coerce")

    # Calculate total equity safely
    ratio_frame["total_equity"] = ratio_frame["equity_capital"].fillna(0) + ratio_frame["reserves"].fillna(0)

    # Dividend Payout is not in the schema, so we can't use it.
    # ratio_frame["dividend_payout"] = pd.to_numeric(ratio_frame["dividend_payout"], errors="coerce")

    # Step 4: Calculate Ratios
    ratio_frame["net_profit_margin_pct"] = net_profit_margin(ratio_frame["net_profit"], ratio_frame["sales"])
    ratio_frame["operating_profit_margin_pct"] = operating_profit_margin(ratio_frame["operating_profit"], ratio_frame["sales"])
    ratio_frame["return_on_equity_pct"] = return_on_equity(ratio_frame["net_profit"], ratio_frame["total_equity"])
    ratio_frame["debt_to_equity"] = debt_to_equity(ratio_frame["borrowings"], ratio_frame["total_equity"], broad_sector=ratio_frame["broad_sector"])
    ratio_frame["interest_coverage"] = interest_coverage_ratio(ratio_frame["operating_profit"], ratio_frame["interest"], tax_rate=0.1)
    ratio_frame["asset_turnover"] = asset_turnover(ratio_frame["sales"], ratio_frame["total_assets"])
    ratio_frame["free_cash_flow"] = free_cash_flow(ratio_frame["operating_activity"], ratio_frame["investing_activity"])
    
    # Use np.divide for safe division
    ratio_frame["free_cash_flow_cr"] = np.divide(ratio_frame["free_cash_flow"], ratio_frame["sales"]) * 100
    ratio_frame["capex_cr"] = np.divide(abs(ratio_frame["investing_activity"]), ratio_frame["sales"]) * 100
    ratio_frame["earnings_per_share"] = ratio_frame["eps"]
    ratio_frame["book_value_per_share"] = ratio_frame["total_equity"]
    
    # Dividend Payout is not available, so this ratio cannot be calculated.
    ratio_frame["dividend_payout_ratio_pct"] = None # pd.Series(ratio_frame["dividend_payout"] / ratio_frame["net_profit"] * 100).replace([np.inf, -np.inf], None)
    
    ratio_frame["total_debt_cr"] = np.divide(ratio_frame["borrowings"], ratio_frame["sales"]) * 100
    ratio_frame["cash_from_operations_cr"] = np.divide(ratio_frame["operating_activity"], ratio_frame["sales"]) * 100

    # Replace inf with None for database compatibility
    for col in ["free_cash_flow_cr", "capex_cr", "total_debt_cr", "cash_from_operations_cr"]:
        ratio_frame[col] = ratio_frame[col].replace([np.inf, -np.inf], np.nan)

    # Step 5: Calculate CAGR values
    ratio_frame["revenue_cagr_5yr"] = None
    ratio_frame["pat_cagr_5yr"] = None
    ratio_frame["eps_cagr_5yr"] = None

    for company_id, company_rows in ratio_frame.groupby("company_id"):
        sorted_rows = company_rows.sort_values("year").set_index("year")
        
        for metric in [("sales", "revenue_cagr_5yr"), ("net_profit", "pat_cagr_5yr"), ("eps", "eps_cagr_5yr")]:
            col, cagr_col = metric
            # Use rolling window to find start value 5 years ago
            start_values = sorted_rows[col].rolling(window=5, min_periods=2).apply(lambda x: x.iloc[0], raw=False)
            
            for year, start_val in start_values.items():
                end_val = sorted_rows.loc[year, col]
                span = year - sorted_rows.index[sorted_rows.index < year].max() if any(sorted_rows.index < year) else 1
                span = 5 # A 5-year CAGR

                cagr_val, _ = calculate_cagr(start_val, end_val, span)
                
                # Get original index to update the main dataframe
                original_idx = company_rows[(company_rows['company_id'] == company_id) & (company_rows['year'] == year)].index
                if not original_idx.empty:
                    ratio_frame.loc[original_idx, cagr_col] = cagr_val

    # Step 6: Calculate Composite Score
    ratio_frame["composite_quality_score"] = (
        pd.to_numeric(ratio_frame["net_profit_margin_pct"], errors="coerce").fillna(0)
        + pd.to_numeric(ratio_frame["return_on_equity_pct"], errors="coerce").fillna(0)
        + pd.to_numeric(ratio_frame["interest_coverage"], errors="coerce").fillna(0)
        + pd.to_numeric(ratio_frame["free_cash_flow_cr"], errors="coerce").fillna(0)
    ) / 4

    # Step 7: Prepare final DataFrame for insertion
    output_df = ratio_frame[[
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score",
    ]].copy()

    # Step 8: Final cleanup before inserting to prevent integrity errors
    output_df.dropna(subset=['year', 'company_id'], inplace=True)
    output_df['year'] = output_df['year'].astype(int)

    output_df = output_df.dropna(how="all")
    if not output_df.empty:
        company_ids = pd.read_sql("SELECT id FROM companies", connection)["id"].tolist()
        output_df = output_df[output_df["company_id"].isin(company_ids)]
        output_df = output_df.dropna(subset=["company_id"])
        if not output_df.empty:
            output_df = output_df.sort_values(["company_id", "year"]).drop_duplicates(subset=["company_id", "year"], keep="first")
            output_df.to_sql("financial_ratios", connection, if_exists="append", index=False)
            logger.success(f"Loaded {len(output_df)} rows into 'financial_ratios'")


def verify_counts(connection):
    cur = connection.cursor()
    print_header("TABLE COUNTS")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    tables = [row[0] for row in cur.fetchall()]

    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"{t:20} {cur.fetchone()[0]}")
        except Exception as e:
            print(f"{t}: ERROR ({e})")


def verify_foreign_keys(connection):
    cur = connection.cursor()
    cur.execute("PRAGMA foreign_key_check;")
    rows = cur.fetchall()
    if not rows:
        logger.success("Foreign Key Check PASSED (0 violations)")
    else:
        logger.error(f"{len(rows)} FK violation(s)")
        for r in rows:
            logger.error(r)


def show_tables(connection):
    cur = connection.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    print_header("TABLES")
    for (name,) in cur.fetchall():
        print(name)


def commit(connection):
    connection.commit()


def close(connection):
    connection.close()


def main():
    if file_exists(DATABASE):
        logger.info(f"Removing old database file: {DATABASE}")
        DATABASE.unlink()

    conn = connect()
    processed_files = {p.stem: p for p in PROCESSED_DATA_DIR.glob("*.csv")}

    create_schema(conn)

    logger.info("Loading 'companies' table...")
    companies_df = read_csv(processed_files["companies"])
    companies_df = companies_df.copy()
    company_codes = companies_df["id"].astype(str).str.strip().str.lower()
    company_map = {code: idx for idx, code in enumerate(company_codes, start=1)}

    for _, row in companies_df.iterrows():
        company_name = str(row.get("company_name", "")).strip().lower()
        if company_name:
            company_map[company_name] = int(row.name) + 1

    companies_df["id"] = list(range(1, len(companies_df) + 1))
    insert_dataframe(conn, companies_df, "companies")
    logger.success(f"Loaded {len(companies_df)} rows into 'companies'")

    load_all_tables(conn, processed_files, company_map)
    populate_financial_ratios(conn)

    commit(conn)
    verify_counts(conn)
    verify_foreign_keys(conn)
    show_tables(conn)
    close(conn)
    logger.success("Database build completed.")


if __name__ == "__main__":
    main()
