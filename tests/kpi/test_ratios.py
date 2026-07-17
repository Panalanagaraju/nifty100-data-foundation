import pytest

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)


# ---------------------------------------------------
# Net Profit Margin
# ---------------------------------------------------

def test_net_profit_margin():
    assert net_profit_margin(100, 1000) == 10.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


# ---------------------------------------------------
# Operating Profit Margin
# ---------------------------------------------------

def test_operating_profit_margin():
    assert operating_profit_margin(250, 1000) == 25.0


def test_operating_profit_margin_zero_sales():
    assert operating_profit_margin(100, 0) is None


# ---------------------------------------------------
# Return on Equity
# ---------------------------------------------------

def test_roe():
    assert return_on_equity(100, 200, 300) == 20.0


def test_roe_negative_equity():
    assert return_on_equity(100, -100, 50) is None


# ---------------------------------------------------
# ROCE
# ---------------------------------------------------

def test_roce():
    assert round(
        return_on_capital_employed(300, 500, 200, 300), 2
    ) == 30.0


# ---------------------------------------------------
# ROA
# ---------------------------------------------------

def test_roa():
    assert return_on_assets(120, 600) == 20.0


def test_roa_zero_assets():
    assert return_on_assets(100, 0) is None


# ---------------------------------------------------
# Debt Equity
# ---------------------------------------------------

def test_debt_equity():
    assert debt_to_equity(100, 200, 300) == 0.5


def test_debt_equity_debt_free():
    assert debt_to_equity(0, 200, 300) == 0


# ---------------------------------------------------
# Interest Coverage
# ---------------------------------------------------

def test_interest_coverage():
    assert interest_coverage_ratio(100, 20, 10) == 5.0


def test_interest_zero():
    assert interest_coverage_ratio(100, 20, 0) == 5.0


# ---------------------------------------------------
# Asset Turnover
# ---------------------------------------------------

def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2.0


def test_asset_turnover_zero():
    assert asset_turnover(1000, 0) is None