-- Denormalized daily balance summary.
PRAGMA foreign_keys=OFF;
CREATE TABLE IF NOT EXISTS account_daily_balances (
    account_id INTEGER NOT NULL,
    balance_date TEXT NOT NULL,
    balance_cents INTEGER NOT NULL,
    PRIMARY KEY(account_id, balance_date)
);
CREATE INDEX IF NOT EXISTS idx_balances_date ON account_daily_balances(balance_date, account_id);
