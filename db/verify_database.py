import sqlite3
from pathlib import Path

DATABASE = Path(__file__).parent / "nifty100.db"

conn = sqlite3.connect(DATABASE)

cursor = conn.cursor()

print("\n===== TABLES =====")

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name;
""")

for table in cursor.fetchall():
    print(table[0])

print("\n===== FOREIGN KEYS =====")

cursor.execute("PRAGMA foreign_keys;")

print(cursor.fetchone()[0])

conn.close()