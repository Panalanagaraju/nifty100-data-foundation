# Sprint 2 Report – Financial Ratio Engine (Day 08 – Day 14)

## Project

**NIFTY100 Data Foundation**

## Sprint Duration

**Day 08 – Day 14**

## Epic

**Epic 02 – Financial Ratio Engine**

## Sprint Goal

The objective of Sprint 2 was to develop a comprehensive Financial Ratio Engine capable of computing key financial performance indicators for all NIFTY100 companies across multiple financial years. The sprint focused on implementing profitability, leverage, efficiency, growth, and cash flow KPIs, handling financial edge cases, populating the `financial_ratios` table in SQLite, and validating the correctness of all calculated metrics through automated testing.

## Tasks Completed

### Day 08 – Profitability Ratios

* Developed `ratios.py` to calculate core profitability metrics.
* Implemented Net Profit Margin (NPM).
* Implemented Operating Profit Margin (OPM).
* Implemented Return on Equity (ROE).
* Implemented Return on Capital Employed (ROCE).
* Implemented Return on Assets (ROA).
* Added handling for zero sales, zero assets, and negative equity.
* Created unit tests for profitability ratio calculations.

### Day 09 – Leverage and Efficiency Ratios

* Implemented Debt-to-Equity Ratio.
* Implemented Interest Coverage Ratio (ICR).
* Added Debt-Free label for companies without borrowings.
* Implemented High Leverage warning flag.
* Calculated Net Debt.
* Implemented Asset Turnover Ratio.
* Added unit tests for leverage and efficiency metrics.

### Day 10 – CAGR Engine

* Developed `cagr.py`.
* Implemented Revenue CAGR.
* Implemented Profit After Tax (PAT) CAGR.
* Implemented EPS CAGR.
* Supported 3-year, 5-year, and 10-year growth calculations.
* Added handling for:

  * Zero base values
  * Turnaround companies
  * Decline to loss
  * Both negative values
  * Insufficient historical data
* Stored CAGR status flags alongside calculated values.
* Developed unit tests for CAGR calculations.

### Day 11 – Cash Flow KPIs

* Developed `cashflow_kpis.py`.
* Calculated Free Cash Flow (FCF).
* Implemented CFO Quality Score.
* Calculated CapEx Intensity.
* Implemented FCF Conversion Ratio.
* Classified capital allocation patterns using cash flow signs.
* Generated `capital_allocation.csv`.

### Day 12 – Populate Financial Ratios Database

* Executed the complete Ratio Engine.
* Calculated KPIs for every company-year record.
* Populated the `financial_ratios` table in SQLite.
* Verified successful insertion of financial metrics.
* Performed manual verification of selected company calculations.

### Day 13 – Edge Case Handling

* Implemented Financial Sector (Bank/NBFC) specific logic.
* Suppressed leverage warnings for financial institutions where appropriate.
* Compared computed ROCE and ROE with available source values.
* Logged all formula anomalies and data inconsistencies.
* Generated `ratio_edge_cases.log`.

### Day 14 – Testing and Sprint Review

* Executed KPI unit tests.
* Verified correctness of calculated financial ratios.
* Reviewed anomaly logs.
* Validated ratio calculations using manual spreadsheet comparisons.
* Demonstrated populated `financial_ratios` table.
* Completed Sprint 2 review and documentation.

## Deliverables

* `src/analytics/ratios.py`
* `src/analytics/cagr.py`
* `src/analytics/cashflow_kpis.py`
* Populated `financial_ratios` table in SQLite
* `capital_allocation.csv`
* `ratio_edge_cases.log`
* KPI unit tests
* Financial analytics documentation

## Technologies Used

* Python 3
* Pandas
* NumPy
* SQLite
* SQL
* Loguru
* Pytest
* Visual Studio Code

## Outcome

Sprint 2 successfully implemented a robust Financial Ratio Engine capable of computing profitability, leverage, efficiency, growth, and cash flow KPIs for all available company-year records. Advanced edge cases such as negative equity, debt-free companies, turnaround scenarios, and CAGR exceptions were handled correctly. The calculated metrics were stored in the SQLite database, validated through automated unit tests, and documented for further analytics. The completed Financial Ratio Engine provides a strong analytical foundation for future dashboard development, company screening, investment analysis, and recommendation systems in subsequent sprints.
