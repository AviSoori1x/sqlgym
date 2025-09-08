-- Morgan Stanley Wealth Management Denormalized Analytics
-- Trade-off: Pre-calculated client performance metrics and portfolio analytics vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Client portfolio summary with performance metrics
CREATE TABLE IF NOT EXISTS client_portfolio_summary (
    client_id INTEGER PRIMARY KEY,
    client_code TEXT NOT NULL UNIQUE,
    client_name TEXT NOT NULL,
    advisor_id TEXT NOT NULL,
    risk_tolerance TEXT NOT NULL,
    investment_objective TEXT NOT NULL,
    total_portfolio_value REAL NOT NULL,
    total_portfolios INTEGER NOT NULL,
    onboarding_date TEXT NOT NULL,
    net_worth REAL NOT NULL,
    ytd_return REAL NOT NULL,
    ytd_benchmark_return REAL NOT NULL,
    ytd_excess_return REAL NOT NULL,
    total_unrealized_gain_loss REAL NOT NULL,
    asset_allocation_equity_pct REAL NOT NULL,
    asset_allocation_fixed_income_pct REAL NOT NULL,
    asset_allocation_alternative_pct REAL NOT NULL,
    asset_allocation_cash_pct REAL NOT NULL,
    last_updated TEXT NOT NULL
);

-- Portfolio performance analytics
CREATE TABLE IF NOT EXISTS portfolio_performance_analytics (
    portfolio_id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    portfolio_name TEXT NOT NULL,
    portfolio_type TEXT NOT NULL,
    inception_date TEXT NOT NULL,
    current_value REAL NOT NULL,
    benchmark_index TEXT NOT NULL,
    inception_to_date_return REAL NOT NULL,
    inception_to_date_benchmark REAL NOT NULL,
    inception_excess_return REAL NOT NULL,
    one_year_return REAL,
    three_year_return REAL,
    five_year_return REAL,
    sharpe_ratio REAL,
    beta REAL,
    alpha REAL,
    max_drawdown REAL,
    volatility REAL,
    total_trades INTEGER NOT NULL,
    avg_trade_size REAL,
    last_rebalance_date TEXT,
    next_rebalance_date TEXT,
    status TEXT NOT NULL
);

-- Security holdings analysis
CREATE TABLE IF NOT EXISTS security_holdings_analysis (
    security_id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    security_name TEXT NOT NULL,
    asset_class TEXT NOT NULL,
    security_type TEXT NOT NULL,
    sector TEXT,
    total_market_value REAL NOT NULL,
    total_quantity REAL NOT NULL,
    avg_cost_basis REAL NOT NULL,
    current_price REAL NOT NULL,
    total_unrealized_gain_loss REAL NOT NULL,
    unrealized_gain_loss_pct REAL NOT NULL,
    portfolios_holding_count INTEGER NOT NULL,
    largest_position_value REAL NOT NULL,
    smallest_position_value REAL NOT NULL,
    weight_in_total_aum REAL NOT NULL,
    last_trade_date TEXT,
    price_52_week_high REAL,
    price_52_week_low REAL,
    ytd_performance REAL
);

-- Daily AUM and flow metrics
CREATE TABLE IF NOT EXISTS daily_aum_flows (
    business_date TEXT PRIMARY KEY,
    total_aum REAL NOT NULL,
    net_flows REAL NOT NULL,
    market_appreciation REAL NOT NULL,
    new_client_assets REAL NOT NULL,
    client_departures REAL NOT NULL,
    dividend_income REAL NOT NULL,
    interest_income REAL NOT NULL,
    total_fees_generated REAL NOT NULL,
    active_clients INTEGER NOT NULL,
    active_portfolios INTEGER NOT NULL,
    total_trades INTEGER NOT NULL,
    total_trade_volume REAL NOT NULL
);

-- Analytical indexes for performance
CREATE INDEX IF NOT EXISTS idx_client_summary_advisor ON client_portfolio_summary(advisor_id);
CREATE INDEX IF NOT EXISTS idx_client_summary_risk ON client_portfolio_summary(risk_tolerance);
CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_client ON portfolio_performance_analytics(client_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_type ON portfolio_performance_analytics(portfolio_type);
CREATE INDEX IF NOT EXISTS idx_security_analysis_class ON security_holdings_analysis(asset_class);
CREATE INDEX IF NOT EXISTS idx_security_analysis_sector ON security_holdings_analysis(sector);
CREATE INDEX IF NOT EXISTS idx_daily_aum_date ON daily_aum_flows(business_date);
