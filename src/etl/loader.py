from pathlib import Path
import sys
import pandas as pd

# Add project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))


from src.config.settings import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
)
from src.utils import (
    logger,
    clean_columns,
    save_dataframe,
    current_timestamp,
    file_exists,
)

# -----------------------------
# Files with title row
# (matched case-insensitively so "Companies.xlsx" / "COMPANIES.XLSX" also work)
# -----------------------------

HEADER_ONE_FILES = {
    "companies.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "profitandloss.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}

# -----------------------------
# Normalize columns
# -----------------------------


def normalize_columns(df: pd.DataFrame):
    return clean_columns(df)


# -----------------------------
# Read Excel
# -----------------------------


def load_excel(path: Path):

    header = 1 if path.name.lower() in HEADER_ONE_FILES else 0

    logger.info(f"Loading {path.name} (header={header})")

    df = pd.read_excel(
        path,
        header=header,
        engine="openpyxl" if path.suffix.lower() == ".xlsx" else None,
    )

    df = df.dropna(how="all")

    df = normalize_columns(df)

    df = df.drop_duplicates()

    return df


# -----------------------------
# Save CSV
# -----------------------------


def save_csv(df, excel_path):

    csv_name = excel_path.stem.lower() + ".csv"

    out_file = PROCESSED_DATA_DIR / csv_name

    save_dataframe(df, out_file)

    logger.success(f"Saved {csv_name}")

    return out_file


# -----------------------------
# Audit
# -----------------------------


def generate_audit(records):

    audit = pd.DataFrame(
        records,
        columns=["Table", "Rows Loaded", "Rejected", "Time", "Status"],
    )

    save_dataframe(audit, OUTPUT_DIR / "load_audit.csv")

    logger.success("load_audit.csv generated")


# -----------------------------
# Main
# -----------------------------


def main():

    audit = []

    excel_files = list(RAW_DATA_DIR.glob("*.xlsx"))
    excel_files.extend(RAW_DATA_DIR.glob("*.xls"))

    support = RAW_DATA_DIR / "supporting datasets"

    if file_exists(support):
        excel_files.extend(support.glob("*.xlsx"))
        excel_files.extend(support.glob("*.xls"))

    excel_files = sorted(excel_files, key=lambda p: p.name.lower())

    logger.info(f"{len(excel_files)} Excel files found")

    for file in excel_files:

        try:

            df = load_excel(file)

            save_csv(df, file)

            audit.append(
                {
                    "Table": file.stem.lower(),
                    "Rows Loaded": len(df),
                    "Rejected": 0,
                    "Time": current_timestamp(),
                    "Status": "SUCCESS",
                }
            )

        except Exception as e:

            logger.exception(e)

            audit.append(
                {
                    "Table": file.stem.lower(),
                    "Rows Loaded": 0,
                    "Rejected": 0,
                    "Time": current_timestamp(),
                    "Status": f"FAILED: {e}",
                }
            )

    generate_audit(audit)

    logger.success("ETL Completed")


if __name__ == "__main__":
    main()