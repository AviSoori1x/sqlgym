-- Denormalized corporate banking cash management analytics
-- Trade-off: Pre-calculated liquidity metrics and pool performance vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS client_cash_position (
    client_id INTEGER PRIMARY KEY,
    client_code TEXT NOT NULL,
    company_name TEXT NOT NULL,
    risk_rating TEXT NOT NULL,
    total_accounts INTEGER NOT NULL,
    total_balance REAL NOT NULL,
    available_balance REAL NOT NULL,
    sweep_pool_count INTEGER NOT NULL,
    avg_daily_balance REAL,
    interest_earned_mtd REAL,
    fees_paid_mtd REAL,
    last_sweep_date TEXT,
    liquidity_score REAL,
    concentration_risk_score REAL
);

CREATE TABLE IF NOT EXISTS daily_liquidity_metrics (
    date TEXT NOT NULL,
    client_id INTEGER NOT NULL,
    total_cash_position REAL NOT NULL,
    intraday_peak REAL NOT NULL,
    intraday_trough REAL NOT NULL,
    volatility_score REAL,
    sweep_volume REAL NOT NULL,
    interest_earned REAL NOT NULL,
    overdraft_amount REAL DEFAULT 0,
    PRIMARY KEY(date, client_id)
);

CREATE TABLE IF NOT EXISTS pool_performance_summary (
    pool_id INTEGER PRIMARY KEY,
    pool_name TEXT NOT NULL,
    client_code TEXT NOT NULL,
    pool_type TEXT NOT NULL,
    participant_accounts INTEGER NOT NULL,
    avg_daily_balance REAL NOT NULL,
    total_sweep_volume_mtd REAL NOT NULL,
    sweep_frequency_actual REAL, -- actual vs configured
    efficiency_score REAL,
    cost_savings_mtd REAL,
    last_execution_date TEXT
);

CREATE TABLE IF NOT EXISTS account_utilization_analysis (
    account_id INTEGER PRIMARY KEY,
    account_number TEXT NOT NULL,
    client_code TEXT NOT NULL,
    account_category TEXT NOT NULL,
    current_balance REAL NOT NULL,
    avg_balance_30d REAL NOT NULL,
    min_balance_30d REAL NOT NULL,
    max_balance_30d REAL NOT NULL,
    transaction_count_30d INTEGER NOT NULL,
    dormancy_days INTEGER NOT NULL,
    utilization_category TEXT NOT NULL CHECK(utilization_category IN ('HIGH', 'MEDIUM', 'LOW', 'DORMANT'))
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_client_position_risk ON client_cash_position(risk_rating);
CREATE INDEX IF NOT EXISTS idx_client_position_balance ON client_cash_position(total_balance DESC);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_liquidity_metrics(date);
CREATE INDEX IF NOT EXISTS idx_pool_performance_efficiency ON pool_performance_summary(efficiency_score DESC);
CREATE INDEX IF NOT EXISTS idx_account_utilization_category ON account_utilization_analysis(utilization_category);