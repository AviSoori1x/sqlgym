PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    risk_rating TEXT NOT NULL CHECK(risk_rating IN ('LOW','MED','HIGH'))
);
CREATE TABLE IF NOT EXISTS branches (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_branch_name_city ON branches(name, city);
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    account_number TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('CHECKING','SAVINGS')),
    opened_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id);
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    txn_date TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING','POSTED','FAILED'))
);
CREATE INDEX IF NOT EXISTS idx_txn_account_date ON transactions(account_id, txn_date);
CREATE INDEX IF NOT EXISTS idx_txn_status ON transactions(status);
