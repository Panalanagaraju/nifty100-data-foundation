# **Sprint 3 Report**

## **Epics 03 & 04 – Financial Screener & Peer Engine**

**Duration:** Day 15 – Day 21
**Target Story Points:** 49 SP

---

# Sprint Goal

The primary objective of Sprint 3 was to develop an intelligent financial screening system capable of identifying fundamentally strong companies based on predefined investment strategies and custom financial thresholds. In addition, a peer comparison engine was developed to calculate percentile rankings for companies within the same industry group. The sprint also included generating Excel reports, radar chart visualizations, and validating all screening and peer analysis results.

---

# Day 15 – Financial Screener Filter Engine

## Objective

Develop the core financial screener engine capable of dynamically filtering companies using configurable financial thresholds.

---

## Tasks Performed

* Created the `src/screener/engine.py` module.
* Loaded the `financial_ratios` table from the SQLite database.
* Read screening thresholds from `config/screener_config.yaml`.
* Implemented support for fifteen filterable financial metrics:

  * Return on Equity (ROE)
  * Debt-to-Equity Ratio (D/E)
  * Free Cash Flow (FCF)
  * Revenue CAGR (5 Years)
  * PAT CAGR (5 Years)
  * Operating Profit Margin (OPM)
  * Price-to-Earnings Ratio (P/E)
  * Price-to-Book Ratio (P/B)
  * Dividend Yield
  * Interest Coverage Ratio (ICR)
  * Market Capitalization
  * Net Profit
  * EPS CAGR
  * Asset Turnover
  * Sales
* Implemented automatic exclusion of the Debt-to-Equity filter for Financial sector companies.
* Treated debt-free companies as having infinite Interest Coverage Ratio.
* Calculated composite quality scores.
* Returned sorted screening results.

---

## Technologies Used

* Python
* Pandas
* SQLite
* PyYAML

---

## Deliverables

* `engine.py`
* `screener_config.yaml`
* Dynamic filtering engine

---

## Outcome

Successfully developed a configurable screening engine capable of applying multiple financial filters while supporting business-specific exceptions.

---

# Day 16 – Six Preset Investment Screeners

## Objective

Develop predefined financial screeners representing common investment strategies.

---

## Tasks Performed

Implemented the following six investment screeners:

### 1. Quality Compounder

Criteria:

* ROE > 15%
* D/E < 1
* FCF > 0
* Revenue CAGR > 10%

---

### 2. Value Pick

Criteria:

* P/E < 20
* P/B < 3
* D/E < 2
* Dividend Yield > 1%

---

### 3. Growth Accelerator

Criteria:

* PAT CAGR > 20%
* Revenue CAGR > 15%
* D/E < 2

---

### 4. Dividend Champion

Criteria:

* Dividend Yield > 2%
* Dividend Payout < 80%
* Positive Free Cash Flow

---

### 5. Debt-Free Blue Chip

Criteria:

* Debt-to-Equity = 0
* ROE > 12%
* Revenue > ₹5000 Crore

---

### 6. Turnaround Watch

Criteria:

* Revenue CAGR (3 Years) > 10%
* Positive Free Cash Flow
* Declining Debt-to-Equity Ratio

---

## Validation

Each screener was tested using the complete NIFTY100 dataset.

Validation confirmed:

* Minimum 5 companies returned.
* Maximum 50 companies returned.
* Results matched expected investment strategies.

---

## Deliverables

* `presets.py`
* Six investment screeners
* Validation report

---

## Outcome

Successfully developed reusable preset screeners capable of identifying companies satisfying different investment philosophies.

---

# Day 17 – Composite Quality Score & Excel Export

## Objective

Develop a composite quality score for ranking companies and export screening results to Excel.

---

## Tasks Performed

Developed `scoring.py`.

Calculated weighted quality score using:

### Profitability (35%)

* ROE (15%)
* ROCE (10%)
* Net Profit Margin (10%)

---

### Cash Quality (30%)

* FCF CAGR (15%)
* CFO/PAT Ratio (10%)
* Positive FCF Flag (5%)

---

### Growth (20%)

* Revenue CAGR (10%)
* PAT CAGR (10%)

---

### Leverage (15%)

* Debt-to-Equity Score (10%)
* Interest Coverage Score (5%)

---

Applied Winsorization.

* Lower Limit = 10th Percentile
* Upper Limit = 90th Percentile

Normalized every KPI into a 0–100 scale.

Performed sector-relative normalization.

Generated:

```
output/
    screener_output.xlsx
```

Created one worksheet for each screener.

Applied Excel formatting:

* Green = Meets screening condition
* Red = Fails screening condition

Sorted companies by Composite Quality Score.

---

## Technologies Used

* Python
* Pandas
* NumPy
* OpenPyXL

---

## Deliverables

* `scoring.py`
* `screener_output.xlsx`

---

## Outcome

Successfully ranked companies using a standardized quality score and generated professional Excel reports.

---

# Day 18 – Peer Percentile Ranking Engine

## Objective

Develop an industry-based peer comparison engine.

---

## Tasks Performed

Created:

```
src/analytics/peer.py
```

Loaded:

```
peer_groups.xlsx
```

Merged with:

```
financial_ratios
```

Computed percentile rankings for:

* ROE
* ROCE
* Net Profit Margin
* Debt-to-Equity
* Free Cash Flow
* PAT CAGR
* Revenue CAGR
* EPS CAGR
* Interest Coverage Ratio
* Asset Turnover

Implemented inverse ranking for Debt-to-Equity.

Stored results inside SQLite:

```
peer_percentiles
```

Handled companies without peer groups.

Returned:

```
No peer group assigned
```

instead of raising exceptions.

---

## Technologies Used

* Python
* Pandas
* SciPy
* SQLite

---

## Deliverables

* `peer.py`
* `peer_percentiles` table

---

## Outcome

Successfully generated percentile rankings for companies within the same peer groups.

---

# Day 19 – Radar Chart Generation

## Objective

Visualize company performance against peer averages.

---

## Tasks Performed

Created:

```
src/analytics/radar.py
```

Generated radar charts using:

* ROE
* ROCE
* Net Profit Margin
* Debt-to-Equity
* Free Cash Flow Score
* Revenue CAGR
* PAT CAGR
* Composite Score

Displayed:

* Company Performance
* Peer Group Average

Generated PNG images.

Saved inside:

```
reports/radar_charts/
```

Handled companies without peer groups by comparing against NIFTY100 averages.

---

## Technologies Used

* Matplotlib
* Plotly
* Python

---

## Deliverables

* Radar chart PNG files

---

## Outcome

Successfully visualized company strengths and weaknesses relative to industry peers.

---

# Day 20 – Peer Comparison Excel Report

## Objective

Generate a comprehensive peer comparison report.

---

## Tasks Performed

Created:

```
output/
    peer_comparison.xlsx
```

Generated eleven worksheets.

Each worksheet represented one peer group.

Included:

* Company Name
* Twenty Financial KPIs
* Percentile Rankings

Applied formatting:

* Green ≥ 75%
* Yellow 25–75%
* Red ≤ 25%

Highlighted benchmark companies using amber color.

Added peer-group median values.

---

## Technologies Used

* OpenPyXL
* Pandas

---

## Deliverables

* `peer_comparison.xlsx`

---

## Outcome

Successfully generated an interactive peer comparison workbook for all peer groups.

---

# Day 21 – Testing & Sprint Review

## Objective

Validate all developed modules and prepare the sprint for delivery.

---

## Tasks Performed

Executed:

* Fourteen Data Quality Rule Tests
* Financial Screener Validation
* Peer Ranking Validation
* Excel Report Verification
* SQLite Verification

Manual validation included:

### Screener

Verified:

* ROE > 15%
* D/E < 1
* Positive FCF
* Revenue CAGR > 10%

for Quality Compounder results.

Verified Top Five companies manually.

---

### Peer Ranking

Confirmed:

Highest ROE company in IT Services received the highest percentile ranking.

Repeated validation for FMCG peer group.

---

### Reports Verified

* `screener_output.xlsx`
* `peer_comparison.xlsx`
* Radar Charts
* SQLite peer_percentiles table

Conducted Sprint Review and demonstrated the completed modules to the project supervisor/team lead.

---

## Deliverables

* All fourteen unit tests passed.
* Sprint review completed.
* Demo presentation prepared.

---

## Sprint Deliverables

* `config/screener_config.yaml`
* `src/screener/engine.py`
* `src/screener/presets.py`
* `src/screener/scoring.py`
* `src/analytics/peer.py`
* `src/analytics/radar.py`
* `output/screener_output.xlsx`
* `output/peer_comparison.xlsx`
* `reports/radar_charts/`
* `peer_percentiles` SQLite table

---

# Sprint 3 Summary

Sprint 3 successfully delivered a configurable financial screening engine, six preset investment screeners, a composite quality scoring model, peer percentile rankings, radar chart visualizations, and comprehensive Excel reports. All functional and data quality tests passed successfully, meeting the sprint's Definition of Done. The completed modules enable analysts and investors to efficiently screen companies, compare industry peers, and generate professional financial analysis reports, forming a critical component of the overall NIFTY100 Financial Analytics Platform.
