-- Denormalized mortgage servicing analytics
-- Trade-off: Pre-calculated loan performance metrics and portfolio analysis vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS loan_servicing_summary (
    loan_id INTEGER PRIMARY KEY,
    loan_number TEXT NOT NULL,
    borrower_name TEXT NOT NULL,
    property_address TEXT NOT NULL,
    loan_type TEXT NOT NULL,
    original_amount REAL NOT NULL,
    current_balance REAL NOT NULL,
    interest_rate REAL NOT NULL,
    loan_status TEXT NOT NULL,
    origination_date TEXT NOT NULL,
    loan_age_months INTEGER NOT NULL,
    remaining_term_months INTEGER NOT NULL,
    current_ltv REAL, -- Loan to Value ratio
    payment_status TEXT NOT NULL,
    days_delinquent INTEGER NOT NULL,
    escrow_balance REAL,
    last_payment_date TEXT,
    next_payment_due_date TEXT
);

CREATE TABLE IF NOT EXISTS portfolio_performance_daily (
    date TEXT NOT NULL,
    loan_type TEXT NOT NULL,
    total_loans INTEGER NOT NULL,
    total_upb REAL NOT NULL, -- Unpaid Principal Balance
    delinquent_30_plus INTEGER NOT NULL,
    delinquent_60_plus INTEGER NOT NULL,
    delinquent_90_plus INTEGER NOT NULL,
    foreclosure_count INTEGER NOT NULL,
    total_payments_received REAL NOT NULL,
    escrow_collections REAL NOT NULL,
    late_fees_collected REAL NOT NULL,
    PRIMARY KEY(date, loan_type)
);

CREATE TABLE IF NOT EXISTS escrow_analysis_summary (
    escrow_account_id INTEGER PRIMARY KEY,
    loan_number TEXT NOT NULL,
    borrower_name TEXT NOT NULL,
    current_escrow_balance REAL NOT NULL,
    annual_disbursement_estimate REAL NOT NULL,
    monthly_collection_amount REAL NOT NULL,
    projected_shortage REAL,
    projected_surplus REAL,
    last_analysis_date TEXT,
    cushion_amount REAL,
    analysis_status TEXT NOT NULL CHECK(analysis_status IN ('CURRENT', 'SHORTAGE', 'SURPLUS', 'OVERDUE'))
);

CREATE TABLE IF NOT EXISTS delinquency_roll_rates (
    analysis_month TEXT NOT NULL,
    loan_type TEXT NOT NULL,
    current_30_count INTEGER NOT NULL,
    roll_to_60_count INTEGER NOT NULL,
    roll_to_90_count INTEGER NOT NULL,
    roll_to_foreclosure_count INTEGER NOT NULL,
    cure_to_current_count INTEGER NOT NULL,
    roll_rate_30_to_60 REAL,
    roll_rate_60_to_90 REAL,
    cure_rate REAL,
    PRIMARY KEY(analysis_month, loan_type)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_servicing_summary_status ON loan_servicing_summary(payment_status);
CREATE INDEX IF NOT EXISTS idx_servicing_summary_delinquent ON loan_servicing_summary(days_delinquent DESC);
CREATE INDEX IF NOT EXISTS idx_servicing_summary_ltv ON loan_servicing_summary(current_ltv DESC);
CREATE INDEX IF NOT EXISTS idx_portfolio_daily_date ON portfolio_performance_daily(date);
CREATE INDEX IF NOT EXISTS idx_escrow_analysis_status ON escrow_analysis_summary(analysis_status);
CREATE INDEX IF NOT EXISTS idx_delinquency_roll_month ON delinquency_roll_rates(analysis_month);