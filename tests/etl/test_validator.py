import pandas as pd
import pytest

from src.etl import validator


@pytest.fixture(autouse=True)
def clear_failures():
    """Fixture to clear the global FAILURES list before each test."""
    validator.FAILURES = []
    yield
    validator.FAILURES = []


# ======================================================
# DQ-01 Primary Key
# ======================================================

def test_dq01_primary_key_unique():
    df = pd.DataFrame({
        "company_id": [1, 2, 3]
    })
    validator.check_primary_key(df)
    assert validator.FAILURES == []
    failures = validator.check_primary_key(df)
    assert failures == []


def test_dq01_primary_key_duplicate():
    df = pd.DataFrame({
        "company_id": [1, 1, 2]
    })
    validator.check_primary_key(df)
    assert len(validator.FAILURES) == 2
    assert validator.FAILURES[0]['Rule'] == 'DQ-01'
    failures = validator.check_primary_key(df)
    assert len(failures) == 2
    assert failures[0]['Rule'] == 'DQ-01'


# ======================================================
# DQ-02 Company + Year
# ======================================================

def test_dq02_company_year_unique():
    df = pd.DataFrame({
        "company": ["A", "A"],
        "year": [2023, 2024]
    })
    validator.check_company_year_key("test_table", df)
    assert validator.FAILURES == []
    failures = validator.check_company_year_key("test_table", df)
    assert failures == []


def test_dq02_company_year_duplicate():
    df = pd.DataFrame({
        "company": ["A", "A"],
        "year": [2024, 2024]
    })
    validator.check_company_year_key("test_table", df)
    assert len(validator.FAILURES) == 2
    assert validator.FAILURES[0]['Rule'] == 'DQ-02'
    failures = validator.check_company_year_key("test_table", df)
    assert len(failures) == 2
    assert failures[0]['Rule'] == 'DQ-02'


# ======================================================
# DQ-03 Foreign Key
# ======================================================

def test_dq03_foreign_key_valid():
    valid_companies = {"A", "B"}
    child = pd.DataFrame({
        "company": ["A", "B"],
        "year": [2023, 2023]
    })
    validator.check_foreign_key("child_table", child, valid_companies)
    assert validator.FAILURES == []
    failures = validator.check_foreign_key("child_table", child, valid_companies)
    assert failures == []


def test_dq03_foreign_key_invalid():
    valid_companies = {"A"}
    child = pd.DataFrame({
        "company": ["A", "C"],
        "year": [2023, 2023]
    })
    validator.check_foreign_key("child_table", child, valid_companies)
    assert len(validator.FAILURES) == 1
    assert validator.FAILURES[0]['Rule'] == 'DQ-03'
    assert validator.FAILURES[0]['Company'] == 'C'
    failures = validator.check_foreign_key("child_table", child, valid_companies)
    assert len(failures) == 1
    assert failures[0]['Rule'] == 'DQ-03'
    assert failures[0]['Company'] == 'C'


# ======================================================
# DQ-06 Positive Sales
# ======================================================

def test_dq06_sales_positive():
    df = pd.DataFrame({
        "company": ["A", "B"],
        "year": [2023, 2023],
        "sales": [100, 200]
    })
    validator.check_sales_positive(df)
    assert validator.FAILURES == []
    failures = validator.check_sales_positive(df)
    assert failures == []


def test_dq06_sales_negative():
    df = pd.DataFrame({
        "company": ["A", "B"],
        "year": [2023, 2023],
        "sales": [100, -10]
    })
    validator.check_sales_positive(df)
    assert len(validator.FAILURES) == 1
    assert validator.FAILURES[0]['Rule'] == 'DQ-06'
    assert "not greater than 0" in validator.FAILURES[0]['Description']
    failures = validator.check_sales_positive(df)
    assert len(failures) == 1
    assert failures[0]['Rule'] == 'DQ-06'
    assert "not greater than 0" in failures[0]['Description']


# ======================================================
# DQ-12 Duplicate Rows
# ======================================================

def test_dq12_duplicate_rows():
    df = pd.DataFrame({
        "a": [1, 1],
        "b": [2, 2]
    })
    validator.check_duplicate_rows("test_table", df)
    assert len(validator.FAILURES) == 2
    assert validator.FAILURES[0]['Rule'] == 'DQ-12'
    failures = validator.check_duplicate_rows("test_table", df)
    assert len(failures) == 2
    assert failures[0]['Rule'] == 'DQ-12'


def test_dq12_no_duplicate_rows():
    df = pd.DataFrame({
        "a": [1, 2],
        "b": [2, 3]
    })
    validator.check_duplicate_rows("test_table", df)
    assert validator.FAILURES == []
    failures = validator.check_duplicate_rows("test_table", df)
    assert failures == []


# ======================================================
# DQ-14 URL Validation
# ======================================================

def test_dq14_url_valid():
    df = pd.DataFrame({
        "company": ["ABC", "XYZ"],
        "website": [
            "https://abc.com",
            "http://xyz.com"
        ]
    })
    validator.check_url_validity(df)
    assert validator.FAILURES == []
    failures = validator.check_url_validity(df)
    assert failures == []


def test_dq14_url_invalid():
    df = pd.DataFrame({
        "company": ["ABC"],
        "website": [
            "abc.com"
        ]
    })
    validator.check_url_validity(df)
    assert len(validator.FAILURES) == 1
    assert validator.FAILURES[0]['Rule'] == 'DQ-14'
    failures = validator.check_url_validity(df)
    assert len(failures) == 1
    assert failures[0]['Rule'] == 'DQ-14'


# ======================================================
# DQ-16 Year Range
# ======================================================

def test_dq16_year_range_valid():
    df = pd.DataFrame({
        "company": ["A", "B", "C"],
        "year": [2019, 2020, 2024]
    })
    validator.check_year_range("test_table", df)
    assert validator.FAILURES == []
    failures = validator.check_year_range("test_table", df)
    assert failures == []


def test_dq16_year_range_invalid():
    df = pd.DataFrame({
        "company": ["A", "B"],
        "year": [1998, 2035]
    })
    validator.check_year_range("test_table", df)
    assert len(validator.FAILURES) == 2
    assert validator.FAILURES[0]['Rule'] == 'DQ-16'
    assert validator.FAILURES[1]['Rule'] == 'DQ-16'
    failures = validator.check_year_range("test_table", df)
    assert len(failures) == 2
    assert failures[0]['Rule'] == 'DQ-16'
    assert failures[1]['Rule'] == 'DQ-16'