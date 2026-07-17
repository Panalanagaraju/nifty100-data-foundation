import pytest

from src.analytics.cagr import calculate_cagr


def test_normal_cagr():

    value, flag = calculate_cagr(100, 200, 5)

    assert flag == "OK"

    assert round(value, 2) == 14.87


def test_decline_to_loss():

    value, flag = calculate_cagr(100, -50, 5)

    assert value is None

    assert flag == "DECLINE_TO_LOSS"


def test_turnaround():

    value, flag = calculate_cagr(-100, 50, 5)

    assert value is None

    assert flag == "TURNAROUND"


def test_both_negative():

    value, flag = calculate_cagr(-100, -50, 5)

    assert value is None

    assert flag == "BOTH_NEGATIVE"


def test_zero_base():

    value, flag = calculate_cagr(0, 100, 5)

    assert value is None

    assert flag == "ZERO_BASE"


def test_insufficient_years():
    # With the updated logic, 2 years is a valid period for CAGR.
    value, flag = calculate_cagr(100, 200, 2)
    assert flag == "OK"
    assert round(value, 2) == 41.42


def test_zero_years_is_insufficient():
    value, flag = calculate_cagr(100, 200, 0)
    assert value is None
    assert flag == "INSUFFICIENT"


def test_same_values():

    value, flag = calculate_cagr(100, 100, 5)

    assert round(value, 2) == 0.0

    assert flag == "OK"


def test_growth():

    value, flag = calculate_cagr(50, 150, 10)

    assert flag == "OK"


def test_large_growth():

    value, flag = calculate_cagr(100, 1000, 10)

    assert flag == "OK"


def test_small_growth():

    value, flag = calculate_cagr(100, 110, 5)

    assert flag == "OK"