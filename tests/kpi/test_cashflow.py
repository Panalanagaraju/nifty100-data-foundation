import pytest

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion,
)


# ---------------------------------------------------
# Free Cash Flow
# ---------------------------------------------------

def test_fcf():

    assert free_cash_flow(100, -30) == 70


def test_fcf_negative():

    assert free_cash_flow(20, -80) == -60


# ---------------------------------------------------
# CFO Quality
# ---------------------------------------------------

def test_quality_high():

    score, label = cfo_quality_score(120, 100)

    assert label == "High Quality"


def test_quality_moderate():

    score, label = cfo_quality_score(70, 100)

    assert label == "Moderate"


def test_quality_risk():

    score, label = cfo_quality_score(30, 100)

    assert label == "Accrual Risk"


def test_quality_zero_pat():

    score, label = cfo_quality_score(50, 0)

    assert score is None


# ---------------------------------------------------
# Capex Intensity
# ---------------------------------------------------

def test_capex_low():

    value, label = capex_intensity(-20, 1000)

    assert label == "Asset Light"


def test_capex_medium():

    value, label = capex_intensity(-50, 1000)

    assert label == "Moderate"


def test_capex_high():

    value, label = capex_intensity(-120, 1000)

    assert label == "Capital Intensive"


# ---------------------------------------------------
# FCF Conversion
# ---------------------------------------------------

def test_conversion():

    assert fcf_conversion(100, 200) == 50.0


def test_conversion_zero():

    assert fcf_conversion(100, 0) is None