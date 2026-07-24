"""
validator.py
------------
Day 03 — Data Quality Validation for the nifty100-data-foundation project.

Reads the cleaned CSVs produced by loader.py (data/processed/*.csv),
runs DQ-01 through DQ-16, and writes every failing row/record to:

    output/validation_failures.csv

with columns: Rule, Severity, Table, Company, Year, Description

--------------------------------------------------------------------------
IMPORTANT — COLUMN NAME ASSUMPTIONS
--------------------------------------------------------------------------
I don't have access to your actual processed CSV headers, so every logical
field (e.g. "company", "sales", "operating_profit") is resolved through the
`CANDIDATES` table below, which tries several likely spellings/cases and
picks whichever one actually exists in the file. If a check silently finds
0 rows for a table, print the file's real columns (the script does this
automatically in DEBUG-ish form via `logger.debug`) and add the real name
to the relevant CANDIDATES list.
--------------------------------------------------------------------------
"""

import re
import sys
from pathlib import Path

# Add project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))


import pandas as pd

from src.config.settings import (
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
)
from src.utils import (
    logger,
    read_csv,
    save_dataframe,
)

OUTPUT_FILE = OUTPUT_DIR / "validation_failures.csv"

MIN_YEAR = 2015
MAX_YEAR = 2026

BALANCE_SHEET_TOLERANCE = 1.0        # absolute tolerance (in ₹ crore/lakh, same unit as data) for Assets = Liab + Equity
CASH_FLOW_TOLERANCE = 1.0            # absolute tolerance for net cash flow reconciliation
MARGIN_TOLERANCE = 0.02              # 2% tolerance for operating margin recomputation
EPS_TOLERANCE = 0.5                  # absolute tolerance for EPS recomputation

FAILURES = []  # list of dicts, becomes validation_failures.csv


# --------------------------------------------------------------------------
# Column-name resolution helpers
# --------------------------------------------------------------------------

CANDIDATES = {
    "company":            ["company", "Company", "company_name", "Company Name", "ticker", "Ticker", "symbol", "Symbol", "name"],
    "company_id":         ["company_id", "Company ID", "ticker", "Ticker", "symbol", "Symbol", "id"],
    "company_name":       ["company_name", "Company Name", "name", "Name"],
    "website":            ["website", "Website", "url", "URL"],
    "sector":              ["sector", "Sector"],
    "year":               ["year", "Year", "fiscal_year", "Fiscal Year", "FY"],

    "total_assets":       ["total_assets", "Total Assets", "other_asset"],
    "total_liabilities":  ["total_liabilities", "Total Liabilities"],
    "total_equity":       ["total_equity", "Total Equity", "shareholders_equity", "Shareholders Equity"],

    "sales":              ["sales", "Sales", "revenue", "Revenue", "total_revenue", "Total Revenue", "net_sales", "Net Sales"],
    "operating_profit":   ["operating_profit", "Operating Profit", "ebit", "EBIT"],
    "operating_margin":   ["operating_margin", "Operating Margin", "opm", "OPM", "opm_%", "OPM %", "opm_percentage"],
    "net_profit":         ["net_profit", "Net Profit", "profit_after_tax", "Profit After Tax", "PAT"],
    "tax":                ["tax", "Tax", "tax_expense", "Tax Expense"],
    "profit_before_tax":  ["profit_before_tax", "Profit Before Tax", "PBT"],
    "tax_rate":           ["tax_rate", "Tax Rate", "tax_%", "Tax %"],
    "eps":                ["eps", "EPS", "earnings_per_share", "Earnings Per Share"],
    "shares_outstanding": ["shares_outstanding", "Shares Outstanding", "no_of_shares", "No. of Shares"],
    "dividend":           ["dividend", "Dividend", "dividend_paid", "Dividend Paid", "dividend_amount"],

    "operating_cf":       ["operating_cash_flow", "Operating Cash Flow", "cash_from_operating", "Cash from Operating Activity"],
    "investing_cf":       ["investing_cash_flow", "Investing Cash Flow", "cash_from_investing", "Cash from Investing Activity"],
    "financing_cf":       ["financing_cash_flow", "Financing Cash Flow", "cash_from_financing", "Cash from Financing Activity"],
    "net_cash_flow":      ["net_cash_flow", "Net Cash Flow", "net_cash_flow_generated"],
    "opening_cash":       ["opening_cash", "Opening Cash", "opening_cash_balance", "Opening Cash Balance"],
    "closing_cash":       ["closing_cash", "Closing Cash", "closing_cash_balance", "Closing Cash Balance"],
}


def find_col(df: pd.DataFrame, field: str) -> str | None:
    """Return the actual column name in df matching a logical field name, or None."""
    candidates = CANDIDATES.get(field, [field])
    lower_map = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        key = cand.lower().strip()
        if key in lower_map:
            return lower_map[key]
    return None


def add_failure(rule: str, severity: str, table: str, company="", year="", description=""):
    failure = {
        "Rule": rule,
        "Severity": severity,
        "Table": table,
        "Company": company,
        "Year": year,
        "Description": description,
    }
    FAILURES.append(failure)
    return failure


# --------------------------------------------------------------------------
# File loading
# --------------------------------------------------------------------------

def load_processed_csvs() -> dict[str, pd.DataFrame]:
    """Load every CSV in data/processed into a dict keyed by a friendly table name."""
    if not PROCESSED_DATA_DIR.exists() or not list(PROCESSED_DATA_DIR.glob("*.csv")):
        logger.error("Processed CSV files not found.")
        logger.error("Run loader.py before validator.py.")
        sys.exit(1)

    tables: dict[str, pd.DataFrame] = {}
    for csv_path in sorted(PROCESSED_DATA_DIR.glob("*.csv")):
        # loader.py names files like "balancesheet_Balance Sheet.csv" -> use the part
        # before the first underscore as the friendly table key.
        key = csv_path.stem.split("_")[0].lower()
        try:
            df = read_csv(csv_path)
        except Exception as exc:
            logger.warning(f"Could not read {csv_path.name}: {exc}")
            continue
        tables[key] = df
        logger.info(f"Loaded {csv_path.name} -> table '{key}' ({len(df)} rows, {len(df.columns)} cols)")
        logger.debug(f"{key} columns: {list(df.columns)}")

    return tables


# --------------------------------------------------------------------------
# DQ-01  Primary Key uniqueness (companies table)
# --------------------------------------------------------------------------

def check_primary_key(companies: pd.DataFrame | None, reset: bool = True):
    if reset:
        FAILURES.clear()
    if companies is None:
        return []
    id_col = find_col(companies, "company_id")
    if not id_col:
        logger.warning("DQ-01: could not find a company identifier column in companies table.")
        return []

    failures = []
    dupes = companies[companies[id_col].duplicated(keep=False)]
    for _, row in dupes.iterrows():
        failures.append(add_failure(
            "DQ-01", "HIGH", "companies", row.get(id_col, ""), "",
            f"Duplicate primary key value '{row[id_col]}' in companies table."
        ))
    return failures


# --------------------------------------------------------------------------
# DQ-02  (company, year) composite key uniqueness across time-series tables
# --------------------------------------------------------------------------

def check_company_year_key(name: str, df: pd.DataFrame, reset: bool = True):
    if reset:
        FAILURES.clear()
    company_col = find_col(df, "company")
    year_col = find_col(df, "year")
    if not company_col or not year_col:
        logger.warning(f"DQ-02: skipping '{name}' (missing company/year column).")
        return []

    failures = []
    dupes = df[df.duplicated(subset=[company_col, year_col], keep=False)]
    for _, row in dupes.iterrows():
        failures.append(add_failure(
            "DQ-02", "HIGH", name, row.get(company_col, ""), row.get(year_col, ""),
            f"Duplicate (company, year) combination in '{name}'."
        ))
    return failures


# --------------------------------------------------------------------------
# DQ-03  Foreign key — company must exist in companies table
# --------------------------------------------------------------------------

def check_foreign_key(name: str, df: pd.DataFrame, valid_companies: set, reset: bool = True):
    if reset:
        FAILURES.clear()
    company_col = find_col(df, "company")
    if not company_col or not valid_companies:
        logger.warning(f"DQ-03: skipping '{name}' (missing company column or no companies list).")
        return []

    failures = []
    unknown = df[~df[company_col].isin(valid_companies)]
    for _, row in unknown.iterrows():
        failures.append(add_failure(
            "DQ-03", "HIGH", name, row.get(company_col, ""), row.get(find_col(df, "year"), ""),
            f"Company '{row[company_col]}' in '{name}' not found in companies table."
        ))
    return failures


# --------------------------------------------------------------------------
# DQ-04  Balance Sheet equation: Assets = Liabilities + Equity
# --------------------------------------------------------------------------

def check_balance_sheet_equation(df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    assets_col = find_col(df, "total_assets")
    liab_col = find_col(df, "total_liabilities")
    equity_col = find_col(df, "total_equity")

    if not all([assets_col, liab_col, equity_col]):
        logger.warning("DQ-04: skipping (missing assets/liabilities/equity columns in balance sheet).")
        return

    df_check = df[[company_col, year_col, assets_col, liab_col, equity_col]].copy()
    df_check[assets_col] = pd.to_numeric(df_check[assets_col], errors='coerce')
    df_check[liab_col] = pd.to_numeric(df_check[liab_col], errors='coerce')
    df_check[equity_col] = pd.to_numeric(df_check[equity_col], errors='coerce')
    df_check.dropna(subset=[assets_col, liab_col, equity_col], inplace=True)

    for _, row in df_check.iterrows():
        assets, liab, equity = row[assets_col], row[liab_col], row[equity_col]
        diff = abs(assets - (liab + equity))
        if diff > BALANCE_SHEET_TOLERANCE:
            add_failure(
                "DQ-04", "HIGH", "balancesheet", row[company_col], row[year_col],
                f"Assets ({assets}) != Liabilities + Equity ({liab + equity}); diff={diff:.2f}."
            )


# --------------------------------------------------------------------------
# DQ-05  Operating margin sanity check
# --------------------------------------------------------------------------

def check_operating_margin(df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    sales_col = find_col(df, "sales")
    op_profit_col = find_col(df, "operating_profit")
    op_margin_col = find_col(df, "operating_margin")

    if not sales_col or not op_profit_col:
        logger.warning("DQ-05: skipping (missing sales/operating_profit columns).")
        return

    cols_to_check = [company_col, year_col, sales_col, op_profit_col]
    if op_margin_col:
        cols_to_check.append(op_margin_col)

    # Filter out None values from cols_to_check that result from find_col failing
    valid_cols_to_check = [col for col in cols_to_check if col is not None]

    df_check = df[valid_cols_to_check].copy()
    df_check[sales_col] = pd.to_numeric(df_check[sales_col], errors='coerce')
    df_check[op_profit_col] = pd.to_numeric(df_check[op_profit_col], errors='coerce')
    df_check.dropna(subset=[sales_col, op_profit_col], inplace=True)

    for _, row in df_check.iterrows():
        sales, op_profit = row[sales_col], row[op_profit_col]
        if sales == 0:
            continue
        computed_margin = op_profit / sales

        if not (-1.0 <= computed_margin <= 1.0):
            add_failure(
                "DQ-05", "MEDIUM", "profitandloss", row[company_col], row[year_col],
                f"Operating margin {computed_margin:.2%} is outside plausible [-100%, 100%] range."
            )

        if op_margin_col and pd.notna(row.get(op_margin_col)):
            reported_margin_val = pd.to_numeric(row[op_margin_col], errors='coerce')
            if pd.notna(reported_margin_val):
                reported_margin = reported_margin_val
                if abs(reported_margin) > 1:  # Normalize if it's a percentage like 15.5
                    reported_margin /= 100.0

                if abs(reported_margin - computed_margin) > MARGIN_TOLERANCE:
                    add_failure(
                        "DQ-05", "LOW", "profitandloss", row[company_col], row[year_col],
                        f"Reported operating margin ({reported_margin:.2%}) does not match "
                        f"computed operating_profit/sales ({computed_margin:.2%})."
                    )


# --------------------------------------------------------------------------
# DQ-06  Sales > 0
# --------------------------------------------------------------------------

def check_sales_positive(df: pd.DataFrame, reset: bool = True):
    if reset:
        FAILURES.clear()
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    sales_col = find_col(df, "sales")
    if not sales_col:
        logger.warning("DQ-06: skipping (missing sales column).")
        return []

    failures = []
    df_check = df[[company_col, year_col, sales_col]].copy()
    df_check['sales_numeric'] = pd.to_numeric(df_check[sales_col], errors='coerce')

    # Check for non-numeric sales
    for _, row in df_check[df_check['sales_numeric'].isna()].iterrows():
        failures.append(add_failure("DQ-06", "HIGH", "profitandloss", row[company_col], row[year_col], "Sales value missing or non-numeric."))

    # Check for non-positive sales
    for _, row in df_check.dropna(subset=['sales_numeric']).iterrows():
        sales = row['sales_numeric']
        if sales <= 0:
            failures.append(add_failure("DQ-06", "HIGH", "profitandloss", row[company_col], row[year_col],
                f"Sales value {sales} is not greater than 0."
            ))
    return failures


# --------------------------------------------------------------------------
# DQ-07  Cash flow consistency: operating + investing + financing = net
# --------------------------------------------------------------------------

def check_cash_flow_consistency(df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    op_col = find_col(df, "operating_cf")
    inv_col = find_col(df, "investing_cf")
    fin_col = find_col(df, "financing_cf")
    net_col = find_col(df, "net_cash_flow")

    if not all([op_col, inv_col, fin_col, net_col]):
        logger.warning("DQ-07: skipping (missing one of operating/investing/financing/net cash flow columns).")
        return

    df_check = df[[company_col, year_col, op_col, inv_col, fin_col, net_col]].copy()
    numeric_cols = [op_col, inv_col, fin_col, net_col]
    for col in numeric_cols:
        df_check[col] = pd.to_numeric(df_check[col], errors='coerce')
    df_check.dropna(subset=numeric_cols, inplace=True)

    for _, row in df_check.iterrows():
        total = row[op_col] + row[inv_col] + row[fin_col]
        net = row[net_col]
        diff = abs(total - net)
        if diff > CASH_FLOW_TOLERANCE:
            add_failure(
                "DQ-07", "HIGH", "cashflow", row[company_col], row[year_col],
                f"Operating+Investing+Financing ({total}) != reported Net Cash Flow ({net}); diff={diff:.2f}."
            )


# --------------------------------------------------------------------------
# DQ-08  Net Cash reconciliation: closing = opening + net cash flow
# --------------------------------------------------------------------------

def check_net_cash(df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    open_col = find_col(df, "opening_cash")
    close_col = find_col(df, "closing_cash")
    net_col = find_col(df, "net_cash_flow")

    if not all([open_col, close_col, net_col]):
        logger.warning("DQ-08: skipping (missing opening/closing/net cash columns).")
        return

    df_check = df[[company_col, year_col, open_col, close_col, net_col]].copy()
    numeric_cols = [open_col, close_col, net_col]
    for col in numeric_cols:
        df_check[col] = pd.to_numeric(df_check[col], errors='coerce')
    df_check.dropna(subset=numeric_cols, inplace=True)

    for _, row in df_check.iterrows():
        opening, closing, net = row[open_col], row[close_col], row[net_col]
        diff = abs((opening + net) - closing)
        if diff > CASH_FLOW_TOLERANCE:
            add_failure(
                "DQ-08", "MEDIUM", "cashflow", row[company_col], row[year_col],
                f"Opening cash ({opening}) + Net cash flow ({net}) != Closing cash ({closing}); diff={diff:.2f}."
            )


# --------------------------------------------------------------------------
# DQ-09  Tax rate should be within [0, 100]%
# --------------------------------------------------------------------------

def check_tax_rate(df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    tax_col = find_col(df, "tax")
    pbt_col = find_col(df, "profit_before_tax")
    tax_rate_col = find_col(df, "tax_rate")

    # Vectorized approach is complex here due to conditional logic. Row-by-row is clearer.
    for _, row in df.iterrows():
        rate = None
        if tax_rate_col and pd.notna(row.get(tax_rate_col)):
            rate_val = pd.to_numeric(row[tax_rate_col], errors='coerce')
            if pd.notna(rate_val):
                rate = rate_val
                if abs(rate) <= 1:
                    rate = rate * 100

        elif tax_col and pbt_col:
            pbt = pd.to_numeric(row.get(pbt_col), errors='coerce')
            tax = pd.to_numeric(row.get(tax_col), errors='coerce')
            if pd.notna(pbt) and pd.notna(tax):
                if pbt != 0:
                    rate = (tax / pbt) * 100

        if rate is None:
            continue

        if rate < 0 or rate > 100:
            add_failure(
                "DQ-09", "MEDIUM", "profitandloss", row.get(company_col, ""), row.get(year_col, ""),
                f"Tax rate {rate:.2f}% is outside plausible [0, 100]% range."
            )


# --------------------------------------------------------------------------
# DQ-10  Dividend should not exceed net profit and should not be negative
# --------------------------------------------------------------------------

def check_dividend(df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    div_col = find_col(df, "dividend")
    profit_col = find_col(df, "net_profit")

    if not div_col:
        logger.warning("DQ-10: skipping (missing dividend column).")
        return

    cols_to_check = [company_col, year_col, div_col]
    if profit_col:
        cols_to_check.append(profit_col)
    df_check = df[cols_to_check].copy()
    df_check[div_col] = pd.to_numeric(df_check[div_col], errors='coerce')
    if profit_col:
        df_check[profit_col] = pd.to_numeric(df_check[profit_col], errors='coerce')
    df_check.dropna(subset=[div_col], inplace=True)

    for _, row in df_check.iterrows():
        div = row[div_col]
        if div < 0:
            add_failure(
                "DQ-10", "MEDIUM", "profitandloss", row[company_col], row[year_col],
                f"Dividend value {div} is negative."
            )
        if profit_col and pd.notna(row[profit_col]):
            profit = row[profit_col]
            if profit > 0 and div > profit:
                add_failure("DQ-10", "LOW", "profitandloss", row[company_col], row[year_col],
                            f"Dividend ({div}) exceeds net profit ({profit}).")


# --------------------------------------------------------------------------
# DQ-11  EPS = Net Profit / Shares Outstanding
# --------------------------------------------------------------------------

def check_eps(df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    eps_col = find_col(df, "eps")
    profit_col = find_col(df, "net_profit")
    shares_col = find_col(df, "shares_outstanding")

    if not eps_col:
        logger.warning("DQ-11: skipping (missing EPS column).")
        return

    df_check = df.copy()
    df_check['eps_numeric'] = pd.to_numeric(df_check[eps_col], errors='coerce')

    # Check for non-numeric EPS
    for _, row in df_check[df_check['eps_numeric'].isna()].iterrows():
        add_failure("DQ-11", "MEDIUM", "profitandloss", row.get(company_col, ""), row.get(year_col, ""), "EPS value missing or non-numeric.")

    df_check.dropna(subset=['eps_numeric'], inplace=True)

    if profit_col and shares_col:
        df_check[profit_col] = pd.to_numeric(df_check[profit_col], errors='coerce')
        df_check[shares_col] = pd.to_numeric(df_check[shares_col], errors='coerce')
        df_check.dropna(subset=[profit_col, shares_col], inplace=True)

        for _, row in df_check.iterrows():
            eps, profit, shares = row['eps_numeric'], row[profit_col], row[shares_col]
            if shares != 0:
                computed_eps = profit / shares
                if abs(computed_eps - eps) > EPS_TOLERANCE:
                    add_failure(
                        "DQ-11", "LOW", "profitandloss", row[company_col], row[year_col],
                        f"Reported EPS ({eps}) does not match computed Net Profit/Shares ({computed_eps:.2f})."
                    )


# --------------------------------------------------------------------------
# DQ-12  Duplicate rows (exact full-row duplicates) in any table
# --------------------------------------------------------------------------

def check_duplicate_rows(name: str, df: pd.DataFrame):
    dupes = df[df.duplicated(keep=False)]
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    for idx, row in dupes.iterrows():
        add_failure(
            "DQ-12", "LOW", name,
            row.get(company_col, "") if company_col else "",
            row.get(year_col, "") if year_col else "",
            f"Exact duplicate row at index {idx} in '{name}'."
        )


# --------------------------------------------------------------------------
# DQ-13  Missing company value
# --------------------------------------------------------------------------

def check_missing_company(name: str, df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    if not company_col:
        return
    missing = df[df[company_col].isna() | (df[company_col].astype(str).str.strip() == "")]
    year_col = find_col(df, "year")
    for idx, row in missing.iterrows():
        add_failure(
            "DQ-13", "HIGH", name, "", row.get(year_col, "") if year_col else "",
            f"Missing company value at row index {idx} in '{name}'."
        )


# --------------------------------------------------------------------------
# DQ-14  URL validity (companies.website)
# --------------------------------------------------------------------------

URL_PATTERN = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)


def check_url_validity(companies: pd.DataFrame | None):
    if companies is None:
        return
    website_col = find_col(companies, "website")
    company_col = find_col(companies, "company")
    company_col = find_col(companies, "company") or find_col(df, "company_id")
    if not website_col:
        logger.warning("DQ-14: skipping (missing website column in companies table).")
        return

    for _, row in companies.iterrows():
        url = row.get(website_col)
        if pd.isna(url) or str(url).strip() == "":
            add_failure(
                "DQ-14", "LOW", "companies", row.get(company_col, ""), "",
                "Website URL is missing."
            )
            continue
        if not URL_PATTERN.match(str(url).strip()):
            add_failure(
                "DQ-14", "LOW", "companies", row.get(company_col, ""), "",
                f"Website URL '{url}' does not look valid."
            )


# --------------------------------------------------------------------------
# DQ-15  Coverage: every company should have a record for every expected year
# --------------------------------------------------------------------------

def check_coverage(name: str, df: pd.DataFrame, valid_companies: set):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    if not company_col or not year_col or not valid_companies:
        logger.warning(f"DQ-15: skipping '{name}' (missing company/year column or no companies list).")
        return

    years_present = sorted(df[year_col].dropna().unique().tolist())
    if not years_present:
        return

    for company in valid_companies:
        company_years = set(df.loc[df[company_col] == company, year_col].dropna().tolist())
        missing_years = [y for y in years_present if y not in company_years]
        for y in missing_years:
            add_failure(
                "DQ-15", "MEDIUM", name, company, y,
                f"No record found for company '{company}' in year {y} (coverage gap) in '{name}'."
            )


# --------------------------------------------------------------------------
# DQ-16  Year range sanity check
# --------------------------------------------------------------------------

def check_year_range(name: str, df: pd.DataFrame):
    company_col = find_col(df, "company")
    company_col = find_col(df, "company") or find_col(df, "company_id")
    year_col = find_col(df, "year")
    if not year_col:
        return

    df_check = df.copy()
    # The normalizer should have already converted years to numeric types.
    # This check now catches failures from the normalization step.
    df_check['year_numeric'] = pd.to_numeric(df_check[year_col], errors='coerce')

    # Report rows where year could not be converted to a number
    bad_years = df_check[df_check['year_numeric'].isna()]
    for _, row in bad_years.iterrows():
        add_failure("DQ-16", "MEDIUM", name, row.get(company_col, "") if company_col else "", row.get(year_col, ""), "Year value missing or non-numeric.")

    # Report rows where the numeric year is out of range
    valid_years = df_check.dropna(subset=['year_numeric'])
    for _, row in valid_years.iterrows():
        year = int(row['year_numeric'])
        if year < MIN_YEAR or year > MAX_YEAR:
            add_failure("DQ-16", "MEDIUM", name, row.get(company_col, "") if company_col else "", year,
                f"Year {year} is outside expected range [{MIN_YEAR}, {MAX_YEAR}]."
            )


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

TIME_SERIES_TABLES = ["balancesheet", "cashflow", "profitandloss", "financial_ratios", "market_cap"]


def run_validation(tables: dict[str, pd.DataFrame]):
    companies = tables.get("companies")
    valid_companies: set = set()
    if companies is not None:
        company_col = find_col(companies, "company")
        company_col = find_col(companies, "company") or find_col(companies, "company_id")
        if company_col:
            valid_companies = set(companies[company_col].dropna().unique().tolist())

    # DQ-01 : primary key uniqueness on companies
    check_primary_key(companies)

    # DQ-14 : URL validity on companies
    check_url_validity(companies)

    # Per-table checks
    for name, df in tables.items():
        # DQ-12 : duplicate rows, every table
        check_duplicate_rows(name, df)
        # DQ-13 : missing company, every table that has a company column
        check_missing_company(name, df)

        if name in TIME_SERIES_TABLES:
            # DQ-02 : composite key
            check_company_year_key(name, df)
            # DQ-03 : foreign key back to companies
            check_foreign_key(name, df, valid_companies)
            # DQ-16 : year range
            check_year_range(name, df)
            # DQ-15 : coverage
            check_coverage(name, df, valid_companies)

    # Table-specific business rule checks
    if "balancesheet" in tables:
        check_balance_sheet_equation(tables["balancesheet"])
    if "profitandloss" in tables:
        check_operating_margin(tables["profitandloss"])
        check_sales_positive(tables["profitandloss"])
        check_tax_rate(tables["profitandloss"])
        check_dividend(tables["profitandloss"])
        check_eps(tables["profitandloss"])
    if "cashflow" in tables:
        check_cash_flow_consistency(tables["cashflow"])
        check_net_cash(tables["cashflow"])


def save_failures():
    columns = ["Rule", "Severity", "Table", "Company", "Year", "Description"]
    df = pd.DataFrame(FAILURES, columns=columns)
    df.to_csv(OUTPUT_FILE, index=False)
    logger.success(f"Saved -> {OUTPUT_FILE} ({len(df)} failure(s) recorded)")


def main():
    logger.info("Starting validation run...")
    tables = load_processed_csvs()
    run_validation(tables)
    save_failures()
    logger.info("Validation complete.")


if __name__ == "__main__":
    main()