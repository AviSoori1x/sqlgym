-- Boeing Manufacturing Denormalized Analytics
-- Trade-off: Pre-calculated manufacturing metrics and BOM analysis vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Manufacturing performance summary
CREATE TABLE IF NOT EXISTS manufacturing_summary (
    part_id INTEGER PRIMARY KEY,
    part_number TEXT NOT NULL,
    part_name TEXT NOT NULL,
    category TEXT NOT NULL,
    total_work_orders INTEGER NOT NULL,
    completed_work_orders INTEGER NOT NULL,
    avg_completion_time REAL NOT NULL,
    inventory_turnover REAL NOT NULL,
    total_cost REAL NOT NULL,
    quality_score REAL NOT NULL,
    supplier_count INTEGER NOT NULL,
    lead_time_days REAL NOT NULL
);

-- Daily production metrics
CREATE TABLE IF NOT EXISTS daily_production_metrics (
    production_date TEXT PRIMARY KEY,
    total_work_orders INTEGER NOT NULL,
    completed_work_orders INTEGER NOT NULL,
    efficiency_percentage REAL NOT NULL,
    quality_rate REAL NOT NULL,
    total_production_cost REAL NOT NULL,
    inventory_value REAL NOT NULL
);

-- Analytical indexes
CREATE INDEX IF NOT EXISTS idx_manufacturing_summary_category ON manufacturing_summary(category);
CREATE INDEX IF NOT EXISTS idx_manufacturing_summary_score ON manufacturing_summary(quality_score);
CREATE INDEX IF NOT EXISTS idx_daily_production_date ON daily_production_metrics(production_date);
