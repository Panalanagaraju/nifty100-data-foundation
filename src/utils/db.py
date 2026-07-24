from __future__ import annotations

import sqlite3
from pathlib import Path

from src.config.settings import DATABASE


def get_connection(db_path: str | None = None):
    path = Path(db_path or DATABASE)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn
