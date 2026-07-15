import pytest
from src.etl.normaliser import DataNormaliser


# ======================================================
# normalize_year() - 20 Tests
# ======================================================

def test_year_1():
    assert DataNormaliser.normalize_year("2024") == 2024


def test_year_2():
    assert DataNormaliser.normalize_year("2023") == 2023


def test_year_3():
    assert DataNormaliser.normalize_year("FY24") == 2024


def test_year_4():
    assert DataNormaliser.normalize_year("FY23") == 2023


def test_year_5():
    assert DataNormaliser.normalize_year("fy22") == 2022


def test_year_6():
    assert DataNormaliser.normalize_year("2024-25") == 2024


def test_year_7():
    assert DataNormaliser.normalize_year("2022-23") == 2022


def test_year_8():
    assert DataNormaliser.normalize_year("Report 2021") == 2021


def test_year_mar_2023():
    assert DataNormaliser.normalize_year("Mar 2023") == 2023


def test_year_dec_2012():
    assert DataNormaliser.normalize_year("Dec 2012") == 2012


def test_year_mar_13():
    assert DataNormaliser.normalize_year("Mar-13") == 2013

def test_year_ttm():
    assert DataNormaliser.normalize_year("TTM") is None


def test_year_9():
    assert DataNormaliser.normalize_year("Annual Report 2020") == 2020


def test_year_10():
    assert DataNormaliser.normalize_year("FY19") == 2019


def test_year_11():
    assert DataNormaliser.normalize_year("FY18") == 2018


def test_year_12():
    assert DataNormaliser.normalize_year(None) is None


def test_year_13():
    assert DataNormaliser.normalize_year("") is None


def test_year_14():
    assert DataNormaliser.normalize_year("ABC") is None


def test_year_15():
    # Implementation only matches years in the 2000s (regex: (20\d{2})).
    # Pre-2000 years are intentionally rejected.
    assert DataNormaliser.normalize_year("1999") is None


def test_year_16():
    assert DataNormaliser.normalize_year("FY") is None


def test_year_17():
    assert DataNormaliser.normalize_year("2025 Report") == 2025


def test_year_18():
    assert DataNormaliser.normalize_year("FY30") == 2030


def test_year_19():
    assert DataNormaliser.normalize_year("FY00") == 2000


def test_year_20():
    assert DataNormaliser.normalize_year("Financial Year FY21") == 2021


# ======================================================
# normalize_ticker() - 15 Tests
# ======================================================

def test_ticker_1():
    assert DataNormaliser.normalize_ticker("tcs") == "TCS"


def test_ticker_2():
    assert DataNormaliser.normalize_ticker("TCS") == "TCS"


def test_ticker_3():
    assert DataNormaliser.normalize_ticker("tcs.ns") == "TCS"


def test_ticker_4():
    assert DataNormaliser.normalize_ticker("INFY.NS") == "INFY"


def test_ticker_5():
    assert DataNormaliser.normalize_ticker("reliance.bo") == "RELIANCE"


def test_ticker_6():
    assert DataNormaliser.normalize_ticker(" HDFC ") == "HDFC"


def test_ticker_7():
    assert DataNormaliser.normalize_ticker("icici bank") == "ICICIBANK"


def test_ticker_8():
    assert DataNormaliser.normalize_ticker("sbin.ns") == "SBIN"


def test_ticker_9():
    assert DataNormaliser.normalize_ticker("lt.bo") == "LT"


def test_ticker_10():
    # Current implementation returns "" for empty string input
    # (does not convert empty string to None). Update this assertion
    # if that behavior changes.
    assert DataNormaliser.normalize_ticker("") == ""


def test_ticker_11():
    assert DataNormaliser.normalize_ticker(None) is None


def test_ticker_12():
    assert DataNormaliser.normalize_ticker("Asian Paints") == "ASIANPAINTS"


def test_ticker_13():
    assert DataNormaliser.normalize_ticker("Sun Pharma") == "SUNPHARMA"


def test_ticker_14():
    # Only .NS, .BO, and spaces are stripped -- "&" is left untouched,
    # so "M&M" is expected to remain "M&M".
    assert DataNormaliser.normalize_ticker("M&M") == "M&M"


def test_ticker_15():
    assert DataNormaliser.normalize_ticker("tatamotors.ns") == "TATAMOTORS"


# ======================================================
# normalize_company() - Additional coverage (not required
# for Sprint 1, but recommended by review)
# ======================================================

def test_company_1():
    assert DataNormaliser.normalize_company(
        "TATA CONSULTANCY SERVICES LIMITED"
    ) == "Tata Consultancy Services"


def test_company_2():
    assert DataNormaliser.normalize_company("Infosys Ltd.") == "Infosys"


def test_company_3():
    assert DataNormaliser.normalize_company(None) is None


# ======================================================
# normalize_url() - Additional coverage
# ======================================================

def test_url_1():
    assert DataNormaliser.normalize_url("www.tcs.com") == "https://www.tcs.com"


def test_url_2():
    assert DataNormaliser.normalize_url(
        "https://www.tcs.com"
    ) == "https://www.tcs.com"


def test_url_3():
    assert DataNormaliser.normalize_url(None) is None


# ======================================================
# normalize_sector() - Additional coverage
# ======================================================

def test_sector_1():
    assert DataNormaliser.normalize_sector(
        "information technology"
    ) == "Information Technology"


def test_sector_2():
    assert DataNormaliser.normalize_sector(
        "FINANCIAL SERVICES"
    ) == "Financial Services"


def test_sector_3():
    assert DataNormaliser.normalize_sector(None) is None