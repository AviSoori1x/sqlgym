PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS borrowers (
    id INTEGER PRIMARY KEY,
    borrower_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    ssn_hash TEXT NOT NULL UNIQUE,
    current_address TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    employment_status TEXT NOT NULL CHECK(employment_status IN ('EMPLOYED', 'SELF_EMPLOYED', 'RETIRED', 'UNEMPLOYED'))
);

CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY,
    property_address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    property_type TEXT NOT NULL CHECK(property_type IN ('SINGLE_FAMILY', 'CONDO', 'TOWNHOUSE', 'MULTI_FAMILY', 'MANUFACTURED')),
    square_footage INTEGER,
    year_built INTEGER,
    appraised_value REAL NOT NULL,
    appraisal_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mortgage_loans (
    id INTEGER PRIMARY KEY,
    loan_number TEXT NOT NULL UNIQUE,
    borrower_id INTEGER NOT NULL REFERENCES borrowers(id),
    property_id INTEGER NOT NULL REFERENCES properties(id),
    loan_type TEXT NOT NULL CHECK(loan_type IN ('CONVENTIONAL', 'FHA', 'VA', 'USDA', 'JUMBO')),
    loan_purpose TEXT NOT NULL CHECK(loan_purpose IN ('PURCHASE', 'REFINANCE', 'CASH_OUT_REFINANCE')),
    original_amount REAL NOT NULL,
    interest_rate REAL NOT NULL,
    term_months INTEGER NOT NULL,
    origination_date TEXT NOT NULL,
    maturity_date TEXT NOT NULL,
    current_balance REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'PAID_OFF', 'DEFAULT', 'FORECLOSURE', 'REO'))
);

CREATE TABLE IF NOT EXISTS escrow_accounts (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES mortgage_loans(id),
    current_balance REAL NOT NULL DEFAULT 0,
    annual_tax_amount REAL NOT NULL,
    annual_insurance_amount REAL NOT NULL,
    monthly_escrow_payment REAL NOT NULL,
    last_analysis_date TEXT,
    next_analysis_date TEXT,
    shortage_amount REAL DEFAULT 0,
    UNIQUE(loan_id)
);

CREATE TABLE IF NOT EXISTS mortgage_payments (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES mortgage_loans(id),
    payment_date TEXT NOT NULL,
    scheduled_payment_amount REAL NOT NULL,
    actual_payment_amount REAL NOT NULL,
    principal_component REAL NOT NULL,
    interest_component REAL NOT NULL,
    escrow_component REAL NOT NULL,
    late_fees REAL DEFAULT 0,
    payment_method TEXT NOT NULL CHECK(payment_method IN ('AUTO_DEBIT', 'ONLINE', 'MAIL', 'PHONE', 'IN_PERSON')),
    days_late INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS escrow_disbursements (
    id INTEGER PRIMARY KEY,
    escrow_account_id INTEGER NOT NULL REFERENCES escrow_accounts(id),
    disbursement_date TEXT NOT NULL,
    disbursement_type TEXT NOT NULL CHECK(disbursement_type IN ('PROPERTY_TAX', 'HOMEOWNERS_INSURANCE', 'PMI', 'HOA_FEES', 'FLOOD_INSURANCE')),
    amount REAL NOT NULL,
    payee TEXT NOT NULL,
    check_number TEXT,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'ISSUED', 'CLEARED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS delinquency_tracking (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES mortgage_loans(id),
    delinquency_date TEXT NOT NULL,
    days_delinquent INTEGER NOT NULL,
    outstanding_amount REAL NOT NULL,
    stage TEXT NOT NULL CHECK(stage IN ('EARLY', 'LATE', 'DEFAULT', 'FORECLOSURE')),
    action_taken TEXT,
    next_action_date TEXT,
    assigned_collector TEXT
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_borrowers_ssn ON borrowers(ssn_hash);
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(state, city);
CREATE INDEX IF NOT EXISTS idx_mortgage_loans_borrower ON mortgage_loans(borrower_id);
CREATE INDEX IF NOT EXISTS idx_mortgage_loans_status ON mortgage_loans(status);
CREATE INDEX IF NOT EXISTS idx_mortgage_loans_origination ON mortgage_loans(origination_date);
CREATE INDEX IF NOT EXISTS idx_escrow_accounts_loan ON escrow_accounts(loan_id);
CREATE INDEX IF NOT EXISTS idx_mortgage_payments_loan ON mortgage_payments(loan_id);
CREATE INDEX IF NOT EXISTS idx_mortgage_payments_date ON mortgage_payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_escrow_disbursements_account ON escrow_disbursements(escrow_account_id);
CREATE INDEX IF NOT EXISTS idx_delinquency_tracking_loan ON delinquency_tracking(loan_id);
CREATE INDEX IF NOT EXISTS idx_delinquency_tracking_stage ON delinquency_tracking(stage);