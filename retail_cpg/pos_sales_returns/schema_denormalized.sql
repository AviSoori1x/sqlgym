-- Denormalized daily sales summary.
PRAGMA foreign_keys=OFF;
CREATE TABLE IF NOT EXISTS store_daily_sales (
    store_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    gross_cents INTEGER NOT NULL,
    return_cents INTEGER NOT NULL,
    PRIMARY KEY (store_id, sale_date)
);
CREATE INDEX IF NOT EXISTS idx_sales_date ON store_daily_sales(sale_date, store_id);
