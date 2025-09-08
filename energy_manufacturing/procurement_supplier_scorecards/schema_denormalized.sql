-- Caterpillar Procurement Denormalized Analytics
-- Trade-off: Pre-calculated supplier performance metrics vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Supplier performance summary
CREATE TABLE IF NOT EXISTS supplier_summary (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT NOT NULL,
    supplier_category TEXT NOT NULL,
    total_orders INTEGER NOT NULL,
    total_spend REAL NOT NULL,
    on_time_delivery_rate REAL NOT NULL,
    quality_score REAL NOT NULL,
    cost_competitiveness REAL NOT NULL,
    innovation_score REAL NOT NULL,
    sustainability_score REAL NOT NULL,
    overall_score REAL NOT NULL,
    risk_rating TEXT NOT NULL,
    contract_value REAL NOT NULL,
    cost_savings REAL NOT NULL,
    last_audit_date TEXT
);

-- Monthly procurement metrics
CREATE TABLE IF NOT EXISTS monthly_procurement_metrics (
    year_month TEXT PRIMARY KEY,
    total_orders INTEGER NOT NULL,
    total_spend REAL NOT NULL,
    avg_order_value REAL NOT NULL,
    on_time_delivery_rate REAL NOT NULL,
    quality_incidents INTEGER NOT NULL,
    cost_savings REAL NOT NULL,
    supplier_count INTEGER NOT NULL,
    new_suppliers INTEGER NOT NULL
);

-- Analytical indexes
CREATE INDEX IF NOT EXISTS idx_supplier_summary_category ON supplier_summary(supplier_category);
CREATE INDEX IF NOT EXISTS idx_supplier_summary_score ON supplier_summary(overall_score);
CREATE INDEX IF NOT EXISTS idx_monthly_procurement_date ON monthly_procurement_metrics(year_month);
