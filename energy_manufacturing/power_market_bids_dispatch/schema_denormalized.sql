-- Constellation Energy Trading Denormalized Analytics
-- Trade-off: Pre-calculated market metrics and trading performance vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Trading performance summary
CREATE TABLE IF NOT EXISTS trading_summary (
    market_date TEXT PRIMARY KEY,
    total_bids INTEGER NOT NULL,
    accepted_bids INTEGER NOT NULL,
    bid_acceptance_rate REAL NOT NULL,
    total_mwh REAL NOT NULL,
    avg_price REAL NOT NULL,
    revenue REAL NOT NULL,
    profit_margin REAL NOT NULL,
    market_share REAL NOT NULL,
    congestion_cost REAL NOT NULL
);

-- Unit performance analytics
CREATE TABLE IF NOT EXISTS unit_performance_analytics (
    unit_id INTEGER PRIMARY KEY,
    unit_name TEXT NOT NULL,
    unit_type TEXT NOT NULL,
    capacity_mw REAL NOT NULL,
    total_bids INTEGER NOT NULL,
    successful_bids INTEGER NOT NULL,
    avg_clearing_price REAL NOT NULL,
    capacity_factor REAL NOT NULL,
    revenue_per_mwh REAL NOT NULL,
    operating_cost_per_mwh REAL NOT NULL,
    profit_margin REAL NOT NULL
);

-- Analytical indexes
CREATE INDEX IF NOT EXISTS idx_trading_summary_date ON trading_summary(market_date);
CREATE INDEX IF NOT EXISTS idx_unit_performance_type ON unit_performance_analytics(unit_type);
CREATE INDEX IF NOT EXISTS idx_unit_performance_margin ON unit_performance_analytics(profit_margin);
