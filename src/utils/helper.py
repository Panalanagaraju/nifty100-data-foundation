"""
helper.py
---------------------------------------
Common helper functions.
"""

from pathlib import Path
from datetime import datetime
import pandas as pd


# --------------------------------------------------
# Create Directory
# --------------------------------------------------

def ensure_directory(path):
    """
    Create directory if it does not exist.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Current Timestamp
# --------------------------------------------------

def current_timestamp():
    """
    Returns current timestamp.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --------------------------------------------------
# Save CSV
# --------------------------------------------------

def save_dataframe(df, filepath):
    """
    Save dataframe as CSV.
    """
    output_path = Path(filepath)
    ensure_directory(output_path.parent)
    df.to_csv(output_path, index=False)


# --------------------------------------------------
# Read CSV
# --------------------------------------------------

def read_csv(filepath):
    """
    Read CSV safely.
    """
    return pd.read_csv(filepath)


# --------------------------------------------------
# Normalize Column Names
# --------------------------------------------------

def clean_columns(df):
    """
    Standardize DataFrame column names.
    """
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
        .str.replace("%", "pct", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    return df


# --------------------------------------------------
# Column resolution helper
# --------------------------------------------------

def find_col(df, field):
    """Return the actual column name in df matching a logical field name or None."""
    if df is None:
        return None

    normalized_field = str(field).strip().lower()
    aliases = {
        "company": ["company", "company_name", "companyname", "ticker", "symbol", "name"],
        "company_id": ["company_id", "companyid", "ticker", "symbol", "id"],
        "company_name": ["company_name", "companyname", "name"],
        "website": ["website", "url"],
        "year": ["year", "fiscal_year", "fy"],
        "total_assets": ["total_assets", "totalasset", "assets"],
        "total_liabilities": ["total_liabilities", "totalliabilities", "liabilities"],
        "total_equity": ["total_equity", "shareholders_equity", "equity"],
        "sales": ["sales", "revenue", "total_revenue", "net_sales"],
        "operating_profit": ["operating_profit", "ebit", "op_profit"],
        "operating_margin": ["operating_margin", "opm"],
        "net_profit": ["net_profit", "profit_after_tax", "pat"],
        "tax": ["tax", "tax_expense"],
        "profit_before_tax": ["profit_before_tax", "pbt"],
        "eps": ["eps", "earnings_per_share"],
        "shares_outstanding": ["shares_outstanding", "no_of_shares"],
        "dividend": ["dividend", "dividend_paid"],
        "operating_cf": ["operating_cash_flow", "cash_from_operating", "operating_activity"],
        "investing_cf": ["investing_cash_flow", "cash_from_investing", "investing_activity"],
        "financing_cf": ["financing_cash_flow", "cash_from_financing", "financing_activity"],
        "net_cash_flow": ["net_cash_flow", "net_cash_flow_generated"],
        "opening_cash": ["opening_cash", "opening_cash_balance"],
        "closing_cash": ["closing_cash", "closing_cash_balance"],
    }

    for alias in aliases.get(normalized_field, [normalized_field]):
        key = str(alias).strip().lower()
        for col in df.columns:
            if str(col).strip().lower() == key:
                return col

    return None


# --------------------------------------------------
# Print Section Header
# --------------------------------------------------

def print_header(title):
    """
    Pretty console header.
    """
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


# --------------------------------------------------
# File Exists
# --------------------------------------------------

def file_exists(path):
    """
    Check file existence.
    """
    return Path(path).exists()