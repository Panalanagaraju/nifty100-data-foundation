"""
settings.py
-----------------------------------------
Central configuration for the project.
"""

from pathlib import Path

# ======================================================
# Project Paths
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data folders
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Database
DB_DIR = PROJECT_ROOT / "db"
DATABASE = DB_DIR / "nifty100.db"
SCHEMA = DB_DIR / "schema.sql"

# Output
OUTPUT_DIR = PROJECT_ROOT / "output"

# Tests
TESTS_DIR = PROJECT_ROOT / "tests"

# Notebooks
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Reports
REPORTS_DIR = PROJECT_ROOT / "reports"

# Logs
LOGS_DIR = OUTPUT_DIR / "logs"

# ======================================================
# Create Directories
# ======================================================

DIRECTORIES = [
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    DB_DIR,
    OUTPUT_DIR,
    LOGS_DIR,
    REPORTS_DIR,
    NOTEBOOKS_DIR,
    TESTS_DIR,
]

def create_project_directories():
    for directory in DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)
create_project_directories()

# ======================================================
# SQLite Settings
# ======================================================

SQLITE_PRAGMA = [
    "PRAGMA foreign_keys = ON;",
]

# ======================================================
# Expected Tables
# ======================================================

TABLES = [
    "companies",
    "sectors",
    "peer_groups",
    "analysis",
    "documents",
    "prosandcons",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "financial_ratios",
    "stock_prices",
]

# ======================================================
# Expected Row Counts
# ======================================================

EXPECTED_COUNTS = {
    "companies": 92,
    "profitandloss": 1276,
    "balancesheet": 1312,
    "cashflow": 1187,
    "stock_prices": 5520,
}

# ======================================================
# Data Quality Rules
# ======================================================

DQ_RULES = [
    "DQ-01",
    "DQ-02",
    "DQ-03",
    "DQ-04",
    "DQ-05",
    "DQ-06",
    "DQ-07",
    "DQ-08",
    "DQ-09",
    "DQ-10",
    "DQ-11",
    "DQ-12",
    "DQ-13",
    "DQ-14",
    "DQ-15",
    "DQ-16",
]

# ======================================================
# Loader Order
# ======================================================

LOAD_ORDER = [
    "companies",
    "sectors",
    "peer_groups",
    "analysis",
    "documents",
    "prosandcons",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "financial_ratios",
    "stock_prices",
]