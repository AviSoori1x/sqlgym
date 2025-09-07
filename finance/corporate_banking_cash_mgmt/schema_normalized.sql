PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS corporate_clients (
    id INTEGER PRIMARY KEY,
    client_code TEXT NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    industry TEXT NOT NULL,
    annual_revenue REAL NOT NULL,
    employee_count INTEGER NOT NULL,
    relationship_start_date TEXT NOT NULL,
    risk_rating TEXT NOT NULL CHECK(risk_rating IN ('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')),
    kyc_status TEXT NOT NULL CHECK(kyc_status IN ('PENDING', 'APPROVED', 'EXPIRED', 'REJECTED'))
);

CREATE TABLE IF NOT EXISTS account_types (
    id INTEGER PRIMARY KEY,
    type_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK(category IN ('CHECKING', 'SAVINGS', 'MONEY_MARKET', 'CD', 'SWEEP', 'CONCENTRATION')),
    interest_bearing BOOLEAN NOT NULL DEFAULT 0,
    minimum_balance REAL NOT NULL DEFAULT 0,
    fee_structure TEXT, -- JSON with fee details
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    account_number TEXT NOT NULL UNIQUE,
    client_id INTEGER NOT NULL REFERENCES corporate_clients(id),
    account_type_id INTEGER NOT NULL REFERENCES account_types(id),
    currency TEXT NOT NULL DEFAULT 'USD',
    opening_date TEXT NOT NULL,
    current_balance REAL NOT NULL DEFAULT 0,
    available_balance REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'DORMANT', 'FROZEN', 'CLOSED')),
    parent_account_id INTEGER REFERENCES accounts(id) -- For sweep relationships
);

CREATE TABLE IF NOT EXISTS cash_pool_structures (
    id INTEGER PRIMARY KEY,
    pool_name TEXT NOT NULL,
    client_id INTEGER NOT NULL REFERENCES corporate_clients(id),
    master_account_id INTEGER NOT NULL REFERENCES accounts(id),
    pool_type TEXT NOT NULL CHECK(pool_type IN ('ZERO_BALANCE', 'TARGET_BALANCE', 'THRESHOLD_SWEEP')),
    sweep_frequency TEXT NOT NULL CHECK(sweep_frequency IN ('DAILY', 'WEEKLY', 'MONTHLY', 'ON_DEMAND')),
    target_balance REAL DEFAULT 0,
    threshold_amount REAL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS pool_participants (
    id INTEGER PRIMARY KEY,
    pool_id INTEGER NOT NULL REFERENCES cash_pool_structures(id),
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    participation_type TEXT NOT NULL CHECK(participation_type IN ('CONTRIBUTOR', 'BENEFICIARY', 'BOTH')),
    priority_order INTEGER NOT NULL DEFAULT 1,
    min_balance_override REAL,
    max_sweep_amount REAL,
    UNIQUE(pool_id, account_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    transaction_date TEXT NOT NULL,
    value_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('CREDIT', 'DEBIT', 'SWEEP_IN', 'SWEEP_OUT', 'INTEREST', 'FEE')),
    amount REAL NOT NULL,
    description TEXT NOT NULL,
    reference_number TEXT,
    counterparty_account_id INTEGER REFERENCES accounts(id),
    pool_sweep_id INTEGER REFERENCES cash_pool_structures(id)
);

CREATE TABLE IF NOT EXISTS sweep_executions (
    id INTEGER PRIMARY KEY,
    pool_id INTEGER NOT NULL REFERENCES cash_pool_structures(id),
    execution_date TEXT NOT NULL,
    total_amount_swept REAL NOT NULL,
    participant_count INTEGER NOT NULL,
    execution_status TEXT NOT NULL CHECK(execution_status IN ('COMPLETED', 'FAILED', 'PARTIAL')),
    execution_details TEXT -- JSON with sweep breakdown
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_corporate_clients_risk ON corporate_clients(risk_rating);
CREATE INDEX IF NOT EXISTS idx_accounts_client ON accounts(client_id);
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(account_type_id);
CREATE INDEX IF NOT EXISTS idx_pool_structures_client ON cash_pool_structures(client_id);
CREATE INDEX IF NOT EXISTS idx_pool_participants_pool ON pool_participants(pool_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_sweep_executions_pool ON sweep_executions(pool_id);
CREATE INDEX IF NOT EXISTS idx_sweep_executions_date ON sweep_executions(execution_date);