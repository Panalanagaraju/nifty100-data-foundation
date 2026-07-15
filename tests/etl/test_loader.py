import pandas as pd
from pathlib import Path

from src.etl.loader import (
    normalize_columns,
    load_excel,
)

# -------------------------------------------------
# normalize_columns()
# -------------------------------------------------

def test_normalize_columns_spaces():
    df = pd.DataFrame(columns=["Company Name", "BSE Code"])
    df = normalize_columns(df)

    assert list(df.columns) == [
        "company_name",
        "bse_code",
    ]


def test_normalize_columns_percent():
    df = pd.DataFrame(columns=["OPM %"])

    df = normalize_columns(df)

    assert "opm_pct" in df.columns


def test_normalize_columns_slash():
    df = pd.DataFrame(columns=["Sales/Income"])

    df = normalize_columns(df)

    assert "sales_income" in df.columns


def test_normalize_columns_brackets():
    df = pd.DataFrame(columns=["Revenue (Cr)"])

    df = normalize_columns(df)

    assert "revenue_cr" in df.columns


def test_normalize_columns_lowercase():
    df = pd.DataFrame(columns=["COMPANY"])

    df = normalize_columns(df)

    assert "company" in df.columns


# -------------------------------------------------
# load_excel()
# -------------------------------------------------

def test_load_excel_returns_dataframe(tmp_path):

    df = pd.DataFrame({
        "Company Name": ["ABC"],
        "Ticker": ["ABC"],
    })

    excel = tmp_path / "sample.xlsx"

    df.to_excel(excel, index=False)

    result = load_excel(excel)

    assert isinstance(result, pd.DataFrame)


def test_load_excel_not_empty(tmp_path):

    df = pd.DataFrame({
        "Company Name": ["ABC"],
    })

    excel = tmp_path / "sample.xlsx"

    df.to_excel(excel, index=False)

    result = load_excel(excel)

    assert len(result) == 1


def test_load_excel_columns_normalized(tmp_path):

    df = pd.DataFrame({
        "Company Name": ["ABC"],
        "Ticker Symbol": ["ABC"],
    })

    excel = tmp_path / "sample.xlsx"

    df.to_excel(excel, index=False)

    result = load_excel(excel)

    assert "company_name" in result.columns

    assert "ticker_symbol" in result.columns


def test_load_excel_drop_empty_rows(tmp_path):

    df = pd.DataFrame({
        "Company Name": ["ABC", None],
        "Ticker": ["ABC", None],
    })

    excel = tmp_path / "sample.xlsx"

    df.to_excel(excel, index=False)

    result = load_excel(excel)

    assert len(result) == 1


def test_dataframe_type(tmp_path):

    df = pd.DataFrame({
        "A": [1],
    })

    excel = tmp_path / "sample.xlsx"

    df.to_excel(excel, index=False)

    result = load_excel(excel)

    assert type(result) == pd.DataFrame