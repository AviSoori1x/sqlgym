PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    address TEXT NOT NULL,
    credit_score INTEGER NOT NULL CHECK(credit_score BETWEEN 300 AND 850),
    income REAL NOT NULL,
    employment_status TEXT NOT NULL CHECK(employment_status IN ('EMPLOYED', 'SELF_EMPLOYED', 'UNEMPLOYED', 'RETIRED', 'STUDENT'))
);

CREATE TABLE IF NOT EXISTS loan_products (
    id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_type TEXT NOT NULL CHECK(product_type IN ('PERSONAL_LOAN', 'AUTO_LOAN', 'CREDIT_CARD', 'STUDENT_LOAN')),
    min_credit_score INTEGER NOT NULL,
    max_loan_amount REAL NOT NULL,
    interest_rate_range TEXT NOT NULL, -- JSON array [min, max]
    term_months_range TEXT NOT NULL, -- JSON array [min, max]
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS loan_applications (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    product_id INTEGER NOT NULL REFERENCES loan_products(id),
    application_date TEXT NOT NULL,
    requested_amount REAL NOT NULL,
    requested_term_months INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED', 'WITHDRAWN', 'BOOKED')),
    approved_amount REAL,
    interest_rate REAL,
    decision_date TEXT,
    underwriter_id TEXT
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES loan_applications(id),
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    loan_product_id INTEGER NOT NULL REFERENCES loan_products(id),
    principal_amount REAL NOT NULL,
    interest_rate REAL NOT NULL,
    term_months INTEGER NOT NULL,
    origination_date TEXT NOT NULL,
    maturity_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'PAID_OFF', 'DEFAULT', 'CHARGED_OFF')),
    current_balance REAL NOT NULL,
    delinquency_days INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS loan_payments (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES loans(id),
    payment_date TEXT NOT NULL,
    payment_amount REAL NOT NULL,
    principal_component REAL NOT NULL,
    interest_component REAL NOT NULL,
    late_fees REAL DEFAULT 0,
    payment_method TEXT NOT NULL CHECK(payment_method IN ('AUTO_DEBIT', 'BANK_TRANSFER', 'CHECK', 'ONLINE_PORTAL'))
);

CREATE TABLE IF NOT EXISTS credit_cards (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL REFERENCES loans(id), -- A credit card is a type of revolving loan
    card_number TEXT NOT NULL UNIQUE,
    credit_limit REAL NOT NULL,
    cash_limit REAL NOT NULL,
    card_type TEXT NOT NULL CHECK(card_type IN ('REWARDS', 'CASHBACK', 'LOW_APR', 'TRAVEL', 'SECURED')),
    issue_date TEXT NOT NULL,
    expiration_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'LOST_STOLEN', 'CLOSED'))
);

CREATE TABLE IF NOT EXISTS card_transactions (
    id INTEGER PRIMARY KEY,
    card_id INTEGER NOT NULL REFERENCES credit_cards(id),
    transaction_date TEXT NOT NULL,
    merchant_name TEXT NOT NULL,
    merchant_category TEXT NOT NULL,
    transaction_amount REAL NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('PURCHASE', 'CASH_ADVANCE', 'BALANCE_TRANSFER', 'FEE', 'PAYMENT', 'RETURN'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_customers_credit_score ON customers(credit_score);
CREATE INDEX IF NOT EXISTS idx_loan_products_type ON loan_products(product_type);
CREATE INDEX IF NOT EXISTS idx_loan_applications_customer ON loan_applications(customer_id);
CREATE INDEX IF NOT EXISTS idx_loan_applications_status ON loan_applications(status);
CREATE INDEX IF NOT EXISTS idx_loans_customer ON loans(customer_id);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
CREATE INDEX IF NOT EXISTS idx_loan_payments_loan ON loan_payments(loan_id);
CREATE INDEX IF NOT EXISTS idx_credit_cards_loan ON credit_cards(loan_id);
CREATE INDEX IF NOT EXISTS idx_card_transactions_card ON card_transactions(card_id);
CREATE INDEX IF NOT EXISTS idx_card_transactions_date ON card_transactions(transaction_date);
