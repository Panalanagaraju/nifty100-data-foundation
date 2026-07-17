"""
cagr.py
---------------------------------------
Compound Annual Growth Rate (CAGR) Calculation Module (Sprint 2)

This module provides functions to calculate CAGR and handle various
edge cases as per the financial context, such as negative or zero
starting values.
"""
import sys
from pathlib import Path
import numpy as np

# Add project root to the Python path to allow direct script execution
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


def calculate_cagr(beginning_value, ending_value, num_years):
    if num_years is None or num_years <= 0:
        return None, "INSUFFICIENT"

    if beginning_value is None or ending_value is None:
        return None, "INSUFFICIENT"

    if beginning_value == 0:
        return None, "ZERO_BASE"

    if beginning_value < 0 and ending_value > 0:
        return None, "TURNAROUND"

    if beginning_value > 0 and ending_value < 0:
        return None, "DECLINE_TO_LOSS"

    if beginning_value < 0 and ending_value < 0:
        return None, "BOTH_NEGATIVE"

    cagr = ((ending_value / beginning_value) ** (1 / num_years)) - 1
    return cagr * 100, "OK"


def revenue_cagr(beginning_revenue, ending_revenue, num_years):
    """
    Wrapper for calculating Revenue CAGR.
    """
    return calculate_cagr(beginning_revenue, ending_revenue, num_years)


def pat_cagr(beginning_pat, ending_pat, num_years):
    """
    Wrapper for calculating Profit After Tax (PAT) CAGR.
    """
    return calculate_cagr(beginning_pat, ending_pat, num_years)


def eps_cagr(beginning_eps, ending_eps, num_years):
    """
    Wrapper for calculating Earnings Per Share (EPS) CAGR.
    """
    return calculate_cagr(beginning_eps, ending_eps, num_years)


if __name__ == "__main__":
    print("--- Running CAGR Calculation Examples ---")

    # Example 1: Normal Growth
    cagr, status = calculate_cagr(100, 200, 5)
    print(f"Normal Growth (100 -> 200 over 5 years):")
    if status == "OK":
        print(f"  CAGR: {cagr:.2f}%, Status: {status}")
    else:
        print(f"  Calculation failed. Status: {status}")

    # Example 2: Decline to Loss
    cagr, status = calculate_cagr(100, -50, 5)
    print(f"Decline to Loss (100 -> -50 over 5 years):")
    print(f"  CAGR: {cagr}, Status: {status}")

    # Example 3: Insufficient Years
    cagr, status = calculate_cagr(100, 200, 2)
    print(f"Insufficient Years (100 -> 200 over 2 years):")
    print(f"  CAGR: {cagr}, Status: {status}")