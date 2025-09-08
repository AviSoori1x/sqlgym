-- PG&E Grid Operations Denormalized Analytics
-- Trade-off: Pre-calculated outage metrics and asset reliability vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Asset reliability summary
CREATE TABLE IF NOT EXISTS asset_reliability_summary (
    asset_id INTEGER PRIMARY KEY,
    asset_name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    location TEXT NOT NULL,
    installation_date TEXT NOT NULL,
    total_outages INTEGER NOT NULL,
    total_outage_hours REAL NOT NULL,
    avg_outage_duration REAL NOT NULL,
    mtbf_hours REAL NOT NULL,
    availability_percentage REAL NOT NULL,
    last_maintenance_date TEXT,
    next_maintenance_due TEXT,
    criticality_score REAL NOT NULL,
    replacement_cost REAL NOT NULL
);

-- Daily grid performance metrics
CREATE TABLE IF NOT EXISTS daily_grid_metrics (
    business_date TEXT PRIMARY KEY,
    total_assets INTEGER NOT NULL,
    assets_in_service INTEGER NOT NULL,
    planned_outages INTEGER NOT NULL,
    unplanned_outages INTEGER NOT NULL,
    emergency_outages INTEGER NOT NULL,
    total_customers_affected INTEGER NOT NULL,
    avg_restoration_time REAL NOT NULL,
    system_reliability_index REAL NOT NULL,
    peak_demand_mw REAL NOT NULL
);

-- Analytical indexes
CREATE INDEX IF NOT EXISTS idx_asset_reliability_type ON asset_reliability_summary(asset_type);
CREATE INDEX IF NOT EXISTS idx_asset_reliability_location ON asset_reliability_summary(location);
CREATE INDEX IF NOT EXISTS idx_daily_grid_date ON daily_grid_metrics(business_date);
