-- Read-optimized summary of transactions joined with settlements.
PRAGMA foreign_keys=OFF;
CREATE TABLE IF NOT EXISTS merchant_txn_summary (
    merchant_id INTEGER NOT NULL,
    txn_date TEXT NOT NULL,
    gross_cents INTEGER NOT NULL,
    chargeback_cents INTEGER NOT NULL,
    PRIMARY KEY (merchant_id, txn_date)
);
CREATE INDEX IF NOT EXISTS idx_summary_date ON merchant_txn_summary(txn_date, merchant_id);
