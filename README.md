# 📈 NIFTY100 DATA FOUNDATION

## Sprint 1 – Data Foundation & ETL Pipeline

### Project Overview

NIFTY100 Data Foundation is a Python-based ETL (Extract, Transform, Load) project developed to build a clean, validated, and queryable SQLite database for financial analytics. The project ingests financial data from multiple Excel files, performs data normalization and validation using predefined data quality rules, and loads the processed data into a relational SQLite database. This data foundation serves as the base layer for advanced financial analysis, dashboards, APIs, and investment analytics.

---

# Project Objectives

- Build a complete ETL pipeline for NIFTY100 financial data.
- Load data from multiple Excel datasets.
- Normalize and clean the raw financial data.
- Validate data using 16 Data Quality (DQ) rules.
- Store validated data into an SQLite database.
- Generate audit reports and validation reports.
- Prepare the data foundation for analytics, dashboards, and APIs.

---

# Sprint 1 Goals

By the end of Sprint 1, the project delivers:

- Fully populated SQLite database (`nifty100.db`)
- 11 normalized relational tables
- Automated ETL pipeline
- Data validation engine
- Load audit reporting
- Validation failure reporting
- Unit testing framework
- Exploratory SQL notebook

---

# Technology Stack

| Category        | Technology       |
| --------------- | ---------------- |
| Language        | Python 3.13+     |
| Database        | SQLite           |
| Data Processing | Pandas           |
| Excel Reader    | OpenPyXL         |
| Logging         | Loguru           |
| Testing         | PyTest           |
| Notebook        | Jupyter Notebook |
| Version Control | Git              |
| IDE             | VS Code          |

---

# Project Structure

```text
nifty100-data-foundation/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── db/
│   ├── schema.sql
│   ├── database.py
│   └── nifty100.db
│
├── notebooks/
│   ├── exploratory_queries.ipynb
│   └── exploratory_queries.sql
│
├── output/
│   ├── load_audit.csv
│   ├── validation_failures.csv
│   ├── database.log
│   └── logs/
│       └── project.log
│
├── reports/
│
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── etl/
│   │   ├── loader.py
│   │   ├── validator.py
│   │   ├── normaliser.py
│   │   └── audit.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── helper.py
│   │
│   └── main.py
│
├── tests/
│   ├── db/
│   │   ├── test_database.py
│   │   └── test_schema.py
│   │
│   └── etl/
│       ├── test_loader.py
│       ├── test_normaliser.py
│       └── test_validator.py
│
├── Makefile
├── requirements.txt
├── pytest.ini
└── README.md
```

---

# Data Pipeline

```
Raw Excel Files
        │
        ▼
Loader
        │
        ▼
Data Normaliser
        │
        ▼
Processed CSV Files
        │
        ▼
Validator
        │
        ▼
Validation Report
        │
        ▼
SQLite Database
        │
        ▼
Analytics & Dashboard
```

---

# Source Data

The project uses multiple Excel files containing NIFTY100 company information and financial statements.

### Core Datasets

- Companies
- Profit & Loss
- Balance Sheet
- Cash Flow
- Analysis
- Documents
- Pros & Cons

### Supplementary Datasets

- Sectors
- Stock Prices
- Financial Ratios
- Peer Groups

---

# Database Schema

The SQLite database contains the following relational tables:

| Table            |
| ---------------- |
| companies        |
| sectors          |
| peer_groups      |
| analysis         |
| documents        |
| prosandcons      |
| profitandloss    |
| balancesheet     |
| cashflow         |
| financial_ratios |
| stock_prices     |

All tables use primary keys and foreign key relationships to maintain referential integrity.

---

# ETL Workflow

## Step 1 – Extract

- Read Excel files
- Detect header rows
- Load into Pandas DataFrames

## Step 2 – Transform

- Normalize year values
- Normalize ticker symbols
- Normalize company names
- Normalize URLs
- Normalize sector names
- Standardize column names
- Remove empty rows

## Step 3 – Validate

Run all Data Quality rules before loading.

## Step 4 – Load

Insert validated data into SQLite tables.

---

# Data Quality Rules

The validator implements sixteen rules:

| Rule  | Description                     |
| ----- | ------------------------------- |
| DQ-01 | Primary Key uniqueness          |
| DQ-02 | Company-Year uniqueness         |
| DQ-03 | Foreign Key integrity           |
| DQ-04 | Balance Sheet equation          |
| DQ-05 | Operating Margin validation     |
| DQ-06 | Sales must be positive          |
| DQ-07 | Cash Flow consistency           |
| DQ-08 | Net Cash validation             |
| DQ-09 | Tax Rate validation             |
| DQ-10 | Dividend validation             |
| DQ-11 | EPS validation                  |
| DQ-12 | Duplicate row detection         |
| DQ-13 | Missing company detection       |
| DQ-14 | URL validation                  |
| DQ-15 | Company year coverage           |
| DQ-16 | Financial year range validation |

---

# Generated Outputs

After successful execution, the following outputs are generated:

```
output/
│
├── load_audit.csv
├── validation_failures.csv
├── database.log
└── logs/
    └── project.log
```

---

# Database Verification

The project validates:

- Database creation
- Table creation
- Foreign key integrity
- Row counts
- Data loading status

Expected values:

| Table         | Expected Rows |
| ------------- | ------------: |
| Companies     |            92 |
| Profit & Loss |         ~1276 |
| Balance Sheet |         ~1312 |
| Cash Flow     |         ~1187 |
| Stock Prices  |         ~5520 |

---

# Unit Testing

The project includes comprehensive PyTest-based unit tests covering:

- Data Normalisation
- ETL Loader
- Data Validator
- Database
- Schema

Run all tests:

```bash
pytest
```

Run a specific test:

```bash
pytest tests/etl/test_normaliser.py -v
```

---

# Makefile Commands

| Command        | Description                |
| -------------- | -------------------------- |
| make load      | Execute ETL Loader         |
| make validate  | Run Validation Rules       |
| make test      | Execute Unit Tests         |
| make clean     | Clean Generated Files      |
| make report    | Generate Reports           |
| make dashboard | Launch Dashboard           |
| make api       | Run API                    |
| make ratios    | Calculate Financial Ratios |

---

# How to Run

### 1. Clone Repository

```bash
git clone <repository_url>
cd nifty100-data-foundation
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Loader

```bash
python src/etl/loader.py
```

### 6. Validate Data

```bash
python src/etl/validator.py
```

### 7. Build Database

```bash
python db/database.py
```

### 8. Execute Tests

```bash
pytest
```

---

# Future Scope

- Automated financial ratio calculation
- Portfolio analytics
- REST API integration
- Streamlit dashboard
- Power BI dashboard
- Machine Learning models
- Investment recommendation engine
- Scheduled ETL execution
- Cloud deployment

---

# Author

**Panala Nagaraju**

Computer Science Engineer

---

# License

This project is intended for academic and educational purposes.
