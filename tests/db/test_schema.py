import sqlite3
from pathlib import Path
import pytest

SCHEMA = Path("db/schema.sql")
DATABASE = Path("db/test_schema.db")


@pytest.fixture
def db_connection():
    """Pytest fixture to set up and tear down a test database for each test."""
    if DATABASE.exists():
        DATABASE.unlink()
    
    conn = sqlite3.connect(DATABASE)
    with open(SCHEMA, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    
    yield conn  # Provide the connection to the test
    
    conn.close() # Teardown: close connection
    if DATABASE.exists():
        DATABASE.unlink() # Teardown: delete the database file


# ----------------------------------------------------
# Schema file exists
# ----------------------------------------------------

def test_schema_file_exists():
    assert SCHEMA.exists()


# ----------------------------------------------------
# Database created
# ----------------------------------------------------

def test_database_created(db_connection):
    assert DATABASE.exists()


# ----------------------------------------------------
# Check all tables exist
# ----------------------------------------------------
def test_tables_exist(db_connection):
    cursor = db_connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table';
    """)

    tables = {row[0] for row in cursor.fetchall()}

    expected = {
        "companies",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "analysis",
        "documents",
        "prosandcons",
        "sectors",
        "stock_prices",
        "financial_ratios",
        "peer_groups",
    }

    assert expected.issubset(tables)


# ----------------------------------------------------
# Foreign keys enabled
# ----------------------------------------------------

def test_foreign_keys(db_connection):
    cursor = db_connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA foreign_keys;")

    assert cursor.fetchone()[0] == 1


# ----------------------------------------------------
# Companies table columns
# ----------------------------------------------------

def test_companies_columns(db_connection):
    cursor = db_connection.cursor()

    cursor.execute("PRAGMA table_info(companies);")
    
    cols = [row[1] for row in cursor.fetchall()]

    expected = [
        "id",
        "company_logo",
        "company_name",
        "chart_link",
        "about_company",
        "website",
        "nse_profile",
        "bse_profile",
        "face_value",
        "book_value",
        "market_cap",
        "roce_percentage",
        "industry",
        "isin",
        "ticker",
        "created_at",
    ]

    for col in expected:
        assert col in cols


# ----------------------------------------------------
# Profit & Loss columns
# ----------------------------------------------------

def test_profitandloss_columns(db_connection):
    cursor = db_connection.cursor()

    cursor.execute("PRAGMA table_info(profitandloss);")

    cols = [row[1] for row in cursor.fetchall()]

    assert "company_id" in cols
    assert "year" in cols
    assert "sales" in cols
    assert "net_profit" in cols


# ----------------------------------------------------
# Balance Sheet columns
# ----------------------------------------------------

def test_balancesheet_columns(db_connection):
    cursor = db_connection.cursor()

    cursor.execute("PRAGMA table_info(balancesheet);")

    cols = [row[1] for row in cursor.fetchall()]

    assert "company_id" in cols
    assert "year" in cols
    assert "total_assets" in cols
    assert "total_liabilities" in cols


# ----------------------------------------------------
# Cash Flow columns
# ----------------------------------------------------

def test_cashflow_columns(db_connection):
    cursor = db_connection.cursor()

    cursor.execute("PRAGMA table_info(cashflow);")

    cols = [row[1] for row in cursor.fetchall()]

    assert "company_id" in cols
    assert "year" in cols
    assert "net_cash_flow" in cols


# ----------------------------------------------------
# Financial Ratios columns
# ----------------------------------------------------

def test_financial_ratios_columns(db_connection):
    cursor = db_connection.cursor()

    cursor.execute("PRAGMA table_info(financial_ratios);")

    cols = [row[1] for row in cursor.fetchall()]

    assert "earnings_per_share" in cols
    assert "book_value_per_share" in cols