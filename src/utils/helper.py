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
    df.to_csv(filepath, index=False)


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