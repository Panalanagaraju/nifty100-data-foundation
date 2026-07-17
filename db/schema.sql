PRAGMA foreign_keys = ON;

----------------------------------------------------------
-- 1. Companies
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS companies (

    id INTEGER PRIMARY KEY,

    company_logo TEXT,

    company_name TEXT NOT NULL,

    chart_link TEXT,
    about_company TEXT,
    website TEXT,

    -- Mismatched columns from logs
    nse_profile TEXT,
    bse_profile TEXT,
    face_value REAL,
    book_value REAL,
    market_cap REAL,
    roce_percentage REAL,

    industry TEXT,

    isin TEXT,

    ticker TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

----------------------------------------------------------
-- 2. Profit & Loss
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS profitandloss (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    year INTEGER NOT NULL,

    sales REAL,

    expenses REAL,

    operating_profit REAL,

    opm_percentage REAL,

    other_income REAL,

    interest REAL,

    depreciation REAL,

    profit_before_tax REAL,

    tax REAL,

    net_profit REAL,

    eps REAL,

    dividend REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 3. Balance Sheet
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS balancesheet (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    year INTEGER NOT NULL,

    equity_capital REAL,

    reserves REAL,

    borrowings REAL,

    other_liabilities REAL,

    -- Mismatched column from logs
    cwip REAL,

    total_liabilities REAL,

    fixed_assets REAL,

    investments REAL,

    current_assets REAL,

    other_asset REAL,

    total_assets REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 4. Cash Flow
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS cashflow (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    year INTEGER NOT NULL,

    operating_activity REAL,

    investing_activity REAL,

    financing_activity REAL,

    net_cash_flow REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 5. Analysis
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS analysis (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,
    
    -- Schema was long, but data is wide.
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 6. Documents
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS documents (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,
    
    -- Schema had different columns.
    year INTEGER,
    annual_report TEXT,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 7. Pros & Cons
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS prosandcons (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    pros TEXT,

    cons TEXT,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 8. Sectors
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS sectors (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    broad_sector TEXT,

    sub_sector TEXT,

    index_weight_pct REAL,

    market_cap_category TEXT,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 9. Stock Prices
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS stock_prices (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    date DATE NOT NULL,

    open_price REAL,

    high_price REAL,

    low_price REAL,

    close_price REAL,

    volume INTEGER,

    adjusted_close REAL,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 10. Financial Ratios
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_ratios (

    id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    year INTEGER NOT NULL,

    net_profit_margin_pct REAL,

    operating_profit_margin_pct REAL,

    return_on_equity_pct REAL,

    debt_to_equity REAL,

    interest_coverage REAL,

    asset_turnover REAL,

    free_cash_flow_cr REAL,

    capex_cr REAL,

    earnings_per_share REAL,

    book_value_per_share REAL,

    dividend_payout_ratio_pct REAL,

    total_debt_cr REAL,

    cash_from_operations_cr REAL,

    revenue_cagr_5yr REAL,
    pat_cagr_5yr REAL,
    eps_cagr_5yr REAL,
    composite_quality_score REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- 11. Peer Groups
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS peer_groups (

    id INTEGER PRIMARY KEY,

    peer_group_name TEXT,

    company_id INTEGER NOT NULL,

    is_benchmark INTEGER,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE
);

----------------------------------------------------------
-- Useful Indexes
----------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_profit_company
ON profitandloss(company_id);

CREATE INDEX IF NOT EXISTS idx_bs_company
ON balancesheet(company_id);

CREATE INDEX IF NOT EXISTS idx_cf_company
ON cashflow(company_id);

CREATE INDEX IF NOT EXISTS idx_ratio_company
ON financial_ratios(company_id);

CREATE INDEX IF NOT EXISTS idx_stock_company
ON stock_prices(company_id);

CREATE INDEX IF NOT EXISTS idx_stock_date
ON stock_prices(date);

CREATE INDEX IF NOT EXISTS idx_sector_company
ON sectors(company_id);

CREATE INDEX IF NOT EXISTS idx_peer_company
ON peer_groups(company_id);

CREATE INDEX IF NOT EXISTS idx_document_company
ON documents(company_id);