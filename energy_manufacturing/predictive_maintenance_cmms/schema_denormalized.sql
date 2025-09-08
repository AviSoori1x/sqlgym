-- GE Predix Maintenance Denormalized Analytics
-- Trade-off: Pre-calculated maintenance metrics and asset health vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Asset health summary
CREATE TABLE IF NOT EXISTS asset_health_summary (
    asset_id INTEGER PRIMARY KEY,
    asset_name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    location TEXT NOT NULL,
    health_score REAL NOT NULL,
    total_work_orders INTEGER NOT NULL,
    preventive_maintenance_count INTEGER NOT NULL,
    corrective_maintenance_count INTEGER NOT NULL,
    emergency_repairs INTEGER NOT NULL,
    mtbf_hours REAL NOT NULL,
    mttr_hours REAL NOT NULL,
    availability REAL NOT NULL,
    maintenance_cost REAL NOT NULL,
    replacement_value REAL NOT NULL,
    next_maintenance_due TEXT
);

-- Monthly maintenance metrics
CREATE TABLE IF NOT EXISTS monthly_maintenance_metrics (
    year_month TEXT PRIMARY KEY,
    total_work_orders INTEGER NOT NULL,
    planned_work_orders INTEGER NOT NULL,
    unplanned_work_orders INTEGER NOT NULL,
    avg_completion_time REAL NOT NULL,
    total_maintenance_cost REAL NOT NULL,
    parts_cost REAL NOT NULL,
    labor_cost REAL NOT NULL,
    downtime_hours REAL NOT NULL,
    availability_percentage REAL NOT NULL
);

-- Analytical indexes
CREATE INDEX IF NOT EXISTS idx_asset_health_type ON asset_health_summary(asset_type);
CREATE INDEX IF NOT EXISTS idx_asset_health_score ON asset_health_summary(health_score);
CREATE INDEX IF NOT EXISTS idx_monthly_maintenance_date ON monthly_maintenance_metrics(year_month);
