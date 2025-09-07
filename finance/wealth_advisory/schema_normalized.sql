PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    client_code TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    net_worth REAL NOT NULL,
    risk_tolerance TEXT NOT NULL CHECK(risk_tolerance IN ('CONSERVATIVE', 'MODERATE', 'AGGRESSIVE', 'VERY_AGGRESSIVE')),
    investment_objective TEXT NOT NULL CHECK(investment_objective IN ('CAPITAL_PRESERVATION', 'INCOME', 'GROWTH', 'AGGRESSIVE_GROWTH')),
    advisor_id TEXT NOT NULL,
    onboarding_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    portfolio_name TEXT NOT NULL,
    portfolio_type TEXT NOT NULL CHECK(portfolio_type IN ('TAXABLE', 'IRA', 'ROTH_IRA', '401K', 'TRUST', 'FOUNDATION')),
    inception_date TEXT NOT NULL,
    benchmark_index TEXT NOT NULL,
    target_allocation TEXT, -- JSON with asset allocation targets
    current_value REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'CLOSED', 'RESTRICTED'))
);

CREATE TABLE IF NOT EXISTS securities (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    security_name TEXT NOT NULL,
    asset_class TEXT NOT NULL CHECK(asset_class IN ('EQUITY', 'FIXED_INCOME', 'ALTERNATIVE', 'CASH', 'COMMODITY')),
    security_type TEXT NOT NULL CHECK(security_type IN ('STOCK', 'BOND', 'ETF', 'MUTUAL_FUND', 'OPTION', 'FUTURE', 'PRIVATE_EQUITY')),
    sector TEXT,
    currency TEXT NOT NULL DEFAULT 'USD',
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    security_id INTEGER NOT NULL REFERENCES securities(id),
    quantity REAL NOT NULL,
    average_cost REAL NOT NULL,
    current_price REAL NOT NULL,
    market_value REAL NOT NULL,
    unrealized_gain_loss REAL NOT NULL,
    position_date TEXT NOT NULL,
    UNIQUE(portfolio_id, security_id, position_date)
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    security_id INTEGER NOT NULL REFERENCES securities(id),
    trade_date TEXT NOT NULL,
    settlement_date TEXT NOT NULL,
    trade_type TEXT NOT NULL CHECK(trade_type IN ('BUY', 'SELL', 'DIVIDEND', 'INTEREST', 'FEE')),
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    gross_amount REAL NOT NULL,
    commission REAL DEFAULT 0,
    net_amount REAL NOT NULL,
    trade_reason TEXT
);

CREATE TABLE IF NOT EXISTS performance_attribution (
    id INTEGER PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    attribution_date TEXT NOT NULL,
    period_type TEXT NOT NULL CHECK(period_type IN ('DAILY', 'MONTHLY', 'QUARTERLY', 'ANNUAL')),
    total_return REAL NOT NULL,
    benchmark_return REAL NOT NULL,
    excess_return REAL NOT NULL,
    asset_allocation_effect REAL,
    security_selection_effect REAL,
    interaction_effect REAL,
    UNIQUE(portfolio_id, attribution_date, period_type)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_clients_advisor ON clients(advisor_id);
CREATE INDEX IF NOT EXISTS idx_clients_risk_tolerance ON clients(risk_tolerance);
CREATE INDEX IF NOT EXISTS idx_portfolios_client ON portfolios(client_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_type ON portfolios(portfolio_type);
CREATE INDEX IF NOT EXISTS idx_securities_asset_class ON securities(asset_class);
CREATE INDEX IF NOT EXISTS idx_positions_portfolio ON positions(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_positions_date ON positions(position_date);
CREATE INDEX IF NOT EXISTS idx_trades_portfolio ON trades(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(trade_date);
CREATE INDEX IF NOT EXISTS idx_performance_portfolio ON performance_attribution(portfolio_id);