-- ==========================================================
-- NIFTY100 DATA FOUNDATION
-- Sprint 1 - Day 07
-- exploratory_queries.sql
-- ==========================================================

------------------------------------------------------------
-- Query 1: Total Companies
------------------------------------------------------------
SELECT COUNT(*) AS total_companies
FROM companies;

------------------------------------------------------------
-- Query 2: Total Profit & Loss Records
------------------------------------------------------------
SELECT COUNT(*) AS total_profitandloss
FROM profitandloss;

------------------------------------------------------------
-- Query 3: Total Balance Sheet Records
------------------------------------------------------------
SELECT COUNT(*) AS total_balancesheet
FROM balancesheet;

------------------------------------------------------------
-- Query 4: Total Cash Flow Records
------------------------------------------------------------
SELECT COUNT(*) AS total_cashflow
FROM cashflow;

------------------------------------------------------------
-- Query 5: Total Stock Price Records
------------------------------------------------------------
SELECT COUNT(*) AS total_stock_prices
FROM stock_prices;

------------------------------------------------------------
-- Query 6: Companies by Industry
------------------------------------------------------------
SELECT
    industry,
    COUNT(*) AS companies
FROM companies
GROUP BY industry
ORDER BY companies DESC;

------------------------------------------------------------
-- Query 7: Latest Available Financial Year
------------------------------------------------------------
SELECT
    MAX(year) AS latest_year
FROM profitandloss;

------------------------------------------------------------
-- Query 8: Top 10 Companies by Net Profit
------------------------------------------------------------
SELECT
    c.company_name,
    p.year,
    p.net_profit
FROM companies c
JOIN profitandloss p
ON c.id = p.company_id
ORDER BY p.net_profit DESC
LIMIT 10;

------------------------------------------------------------
-- Query 9: Top 10 Companies by Market Capitalization
------------------------------------------------------------
SELECT
    c.company_name,
    s.market_cap_category
FROM companies c
JOIN sectors s
ON c.id = s.company_id
ORDER BY s.market_cap_category;

------------------------------------------------------------
-- Query 10: Verify Foreign Keys
------------------------------------------------------------
PRAGMA foreign_key_check;