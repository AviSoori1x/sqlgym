-- Wallet daily balances mart; trades detail for fast day-level scans.
CREATE TABLE IF NOT EXISTS wallet_daily_balances (
    wallet_id INTEGER NOT NULL,
    balance_date TEXT NOT NULL,
    deposits_sats INTEGER NOT NULL,
    withdrawals_sats INTEGER NOT NULL,
    PRIMARY KEY(wallet_id, balance_date)
);
CREATE INDEX IF NOT EXISTS idx_wdb_wallet_date ON wallet_daily_balances(wallet_id, balance_date);
