-- Denormalized consumer lending and credit card analytics
-- Trade-off: Pre-calculated portfolio metrics and customer risk profiles vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS loan_portfolio_summary (
    loan_id INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL,
    credit_score INTEGER NOT NULL,
    income REAL NOT NULL,
    product_type TEXT NOT NULL,
    principal_amount REAL NOT NULL,
    interest_rate REAL NOT NULL,
    term_months INTEGER NOT NULL,
    loan_status TEXT NOT NULL,
    current_balance REAL NOT NULL,
    delinquency_days INTEGER NOT NULL,
    origination_date TEXT NOT NULL,
    age_of_loan_days INTEGER NOT NULL,
    estimated_ltv REAL -- Loan to Value for auto loans
);

CREATE TABLE IF NOT EXISTS credit_card_portfolio (
    card_id INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL,
    credit_score INTEGER NOT NULL,
    credit_limit REAL NOT NULL,
    current_balance REAL NOT NULL,
    utilization_rate REAL NOT NULL,
    cash_balance REAL NOT NULL,
    cash_utilization_rate REAL,
    card_status TEXT NOT NULL,
    delinquency_days INTEGER NOT NULL,
    last_payment_date TEXT,
    days_since_last_payment INTEGER,
    spending_category_profile TEXT, -- JSON with top spending categories
    rewards_points_balance INTEGER
);

CREATE TABLE IF NOT EXISTS daily_lending_metrics (
    date TEXT NOT NULL,
    product_type TEXT NOT NULL,
    applications_received INTEGER NOT NULL,
    applications_approved INTEGER NOT NULL,
    approval_rate REAL NOT NULL,
    loans_booked INTEGER NOT NULL,
    total_booked_volume REAL NOT NULL,
    avg_interest_rate REAL,
    avg_credit_score REAL,
    delinquency_rate REAL,
    charge_off_volume REAL,
    PRIMARY KEY(date, product_type)
);

CREATE TABLE IF NOT EXISTS customer_risk_profile (
    customer_id INTEGER PRIMARY KEY,
    total_loan_exposure REAL NOT NULL,
    total_credit_card_limit REAL NOT NULL,
    total_credit_card_balance REAL NOT NULL,
    overall_utilization_rate REAL,
    active_loans_count INTEGER NOT NULL,
    active_cards_count INTEGER NOT NULL,
    avg_delinquency_days REAL,
    risk_segment TEXT NOT NULL CHECK(risk_segment IN ('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')),
    last_updated TEXT NOT NULL
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_loan_portfolio_status ON loan_portfolio_summary(loan_status);
CREATE INDEX IF NOT EXISTS idx_loan_portfolio_product ON loan_portfolio_summary(product_type);
CREATE INDEX IF NOT EXISTS idx_cc_portfolio_utilization ON credit_card_portfolio(utilization_rate DESC);
CREATE INDEX IF NOT EXISTS idx_cc_portfolio_delinquency ON credit_card_portfolio(delinquency_days DESC);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_lending_metrics(date);
CREATE INDEX IF NOT EXISTS idx_risk_profile_segment ON customer_risk_profile(risk_segment);
