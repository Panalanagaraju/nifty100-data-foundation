Here's a simple Sprint 1 report that you can include in your project documentation or submit to your mentor.

# Sprint 1 Report – Data Foundation (Day 01 – Day 07)

## Project

**NIFTY100 Data Foundation**

## Sprint Duration

**Day 01 – Day 07**

## Epic

**Epic 01 – Data Ingestion & ETL**

## Sprint Goal

The objective of Sprint 1 was to establish a strong data foundation for the NIFTY100 Analytics Platform. The sprint focused on setting up the development environment, building an ETL pipeline, validating the datasets, designing a normalized SQLite database, and loading all processed data into the database. This foundation enables the financial analytics modules to be developed in later sprints.

## Tasks Completed

### Day 01 – Environment Setup

* Created the project folder structure.
* Configured the Python virtual environment.
* Installed all required Python libraries.
* Created the Makefile and project configuration files.

### Day 02 – Data Ingestion & ETL

* Developed `loader.py` to load Excel datasets.
* Implemented data cleaning and column normalization.
* Converted Excel files into processed CSV files.
* Generated `load_audit.csv` to record loading status.

### Day 03 – Data Validation

* Developed `validator.py`.
* Implemented all 16 Data Quality (DQ) validation rules.
* Validated primary keys, foreign keys, duplicate records, year formats, URLs, and missing values.
* Generated `validation_failures.csv` containing validation results.

### Day 04 – SQLite Database Design

* Created `schema.sql` with all required database tables.
* Designed relationships using primary and foreign keys.
* Enabled SQLite foreign key enforcement.
* Developed `database.py` for database creation and schema initialization.

### Day 05 – Database Loading

* Loaded all processed CSV files into SQLite.
* Followed the correct table loading sequence to maintain foreign key integrity.
* Generated `nifty100.db`.
* Verified table creation and database row counts.
* Generated `load_audit.csv` with loading statistics.

### Day 06 – Manual Verification

* Performed manual validation on randomly selected company records.
* Verified data consistency between source Excel files, processed CSV files, and the SQLite database.
* Fixed data loading issues where necessary.

### Day 07 – Testing and Review

* Executed ETL unit tests.
* Created exploratory SQL queries for database validation.
* Reviewed the database structure and loading process.
* Completed Sprint 1 documentation and project review.

## Deliverables

* Project folder structure
* ETL pipeline (`loader.py`)
* Data normalizer (`normaliser.py`)
* Data validator (`validator.py`)
* SQLite schema (`schema.sql`)
* Database management module (`database.py`)
* SQLite database (`nifty100.db`)
* Processed CSV files
* `load_audit.csv`
* `validation_failures.csv`
* ETL unit tests
* Exploratory SQL queries

## Technologies Used

* Python 3
* Pandas
* NumPy
* OpenPyXL
* SQLite
* Loguru
* Pytest
* SQL
* Visual Studio Code

## Outcome

Sprint 1 successfully established the complete ETL and database foundation for the NIFTY100 Analytics Platform. All source datasets were processed, validated, and stored in a structured SQLite database. The completed data foundation is now ready for Sprint 2, where financial ratios, CAGR calculations, cash flow KPIs, and advanced analytics will be implemented.
