"""
database.py
Sprint 1 Day 04-05
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config.settings import (
    DATABASE,
    SCHEMA,
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
    LOAD_ORDER,
    SQLITE_PRAGMA,
)
from src.utils import (
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
    dataframe.to_sql(table_name, connection, if_exists="append", index=False)

def load_all_tables(connection):
    audit = []
    processed_files = {p.stem: p for p in PROCESSED_DATA_DIR.glob("*.csv")}

    for table in LOAD_ORDER:
        if table in processed_files:
            df = read_csv(processed_files[table])
            insert_dataframe(connection, df, table)
            logger.success(f"Loaded {len(df)} rows into '{table}' table.")

def verify_counts(connection):
    cur = connection.cursor()
    print_header("TABLE COUNTS")
    for t in ["companies","profitandloss","balancesheet","cashflow","stock_prices"]:
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
    # Clean up old database file if it exists
    if file_exists(DATABASE):
        logger.info(f"Removing old database file: {DATABASE}")
        DATABASE.unlink()

    conn = connect()
    create_schema(conn)
    load_all_tables(conn)
    commit(conn)
    verify_counts(conn)
    verify_foreign_keys(conn)
    show_tables(conn)
    close(conn)
    logger.success("Database build completed.")

if __name__ == "__main__":
    main()
