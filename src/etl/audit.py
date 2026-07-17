"""
audit.py
---------------------------------------
ETL Audit Logger

Responsibilities
----------------
1. Store ETL load statistics
2. Generate load_audit.csv
3. Print audit summary
"""

import pandas as pd

from src.config.settings import OUTPUT_DIR
from src.utils import (
    logger,
    current_timestamp,
    save_dataframe,
    print_header,
)


class AuditLogger:

    def __init__(self):
        self.records = []

    def add_record(self, table, rows_loaded, rejected, status, message=""):
        self.records.append(
            {
                "Table": table,
                "Rows Loaded": rows_loaded,
                "Rejected": rejected,
                "Time": current_timestamp(),
                "Status": status,
                "Message": message,
            }
        )

    def save(self):
        df = pd.DataFrame(self.records)
        out_file = OUTPUT_DIR / "load_audit.csv"
        save_dataframe(df, out_file)
        logger.success(f"Audit saved -> {out_file}")
        return out_file

    def summary(self):
        if len(self.records) == 0:
            print("\nNo audit records.\n")
            return

        df = pd.DataFrame(self.records)
        print_header("LOAD SUMMARY")
        print(df[["Table", "Rows Loaded", "Rejected", "Status"]])
        print("\n" + "-" * 60)
        print("Total Tables :", len(df))
        print("Successful   :", (df["Status"] == "SUCCESS").sum())
        print("Failed       :", (df["Status"] != "SUCCESS").sum())
        print("=" * 60 + "\n")


if __name__ == "__main__":
    audit = AuditLogger()
    audit.add_record("companies", 92, 0, "SUCCESS")
    audit.add_record("profitandloss", 1276, 0, "SUCCESS")
    audit.add_record("balancesheet", 1312, 0, "SUCCESS")
    audit.save()
    audit.summary()