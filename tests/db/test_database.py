import sqlite3
from pathlib import Path
import pytest

from db.database import (
    connect,
    create_schema,
    close,
)
from src.config.settings import DATABASE, SQLITE_PRAGMA


@pytest.fixture(autouse=True)
def cleanup_db():
    if DATABASE.exists():
        DATABASE.unlink()
    yield
    if DATABASE.exists():
        DATABASE.unlink()

# ----------------------------------------------------
# Test Database Connection
# ----------------------------------------------------

def test_connect():
    conn = connect()

    assert isinstance(conn, sqlite3.Connection)

    close(conn)


# ----------------------------------------------------
# Test Foreign Keys Enabled
# ----------------------------------------------------

def test_foreign_keys_enabled():
    conn = connect()

    cursor = conn.cursor()

    for pragma_stmt in SQLITE_PRAGMA:
        if "foreign_keys" in pragma_stmt:
            cursor.execute("PRAGMA foreign_keys;")
            status = cursor.fetchone()[0]
            assert status == 1


    close(conn)


# ----------------------------------------------------
# Test Schema Creation
# ----------------------------------------------------

def test_create_schema():

    conn = connect()

    create_schema(conn)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table';
    """)

    tables = [row[0] for row in cursor.fetchall()]

    expected_tables = [
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
    ]

    for table in expected_tables:
        assert table in tables

    close(conn)


# ----------------------------------------------------
# Test Schema File Exists
# ----------------------------------------------------

def test_schema_exists():

    schema = Path("db/schema.sql")

    assert schema.exists()


# ----------------------------------------------------
# Test Database File Created
# ----------------------------------------------------

def test_database_exists():

    conn = connect()

    create_schema(conn)

    db = DATABASE

    assert db.exists()

    close(conn)