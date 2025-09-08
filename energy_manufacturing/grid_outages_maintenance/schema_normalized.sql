PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS grid_assets (
    id INTEGER PRIMARY KEY,
    asset_id TEXT NOT NULL UNIQUE,
    asset_name TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK(asset_type IN ('TRANSFORMER', 'TRANSMISSION_LINE', 'SUBSTATION', 'GENERATOR', 'SWITCH', 'BREAKER')),
    voltage_level TEXT NOT NULL,
    location TEXT NOT NULL,
    installation_date TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    capacity_rating REAL,
    status TEXT NOT NULL CHECK(status IN ('IN_SERVICE', 'OUT_OF_SERVICE', 'MAINTENANCE', 'DECOMMISSIONED'))
);

CREATE TABLE IF NOT EXISTS outage_events (
    id INTEGER PRIMARY KEY,
    outage_id TEXT NOT NULL UNIQUE,
    affected_asset_id INTEGER NOT NULL REFERENCES grid_assets(id),
    outage_start_time TEXT NOT NULL,
    outage_end_time TEXT,
    outage_type TEXT NOT NULL CHECK(outage_type IN ('PLANNED', 'UNPLANNED', 'EMERGENCY')),
    cause_category TEXT NOT NULL CHECK(cause_category IN ('EQUIPMENT_FAILURE', 'WEATHER', 'HUMAN_ERROR', 'CYBER_ATTACK', 'MAINTENANCE')),
    customers_affected INTEGER,
    estimated_restoration_time TEXT,
    priority_level TEXT NOT NULL CHECK(priority_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE TABLE IF NOT EXISTS maintenance_schedules (
    id INTEGER PRIMARY KEY,
    schedule_id TEXT NOT NULL UNIQUE,
    asset_id INTEGER NOT NULL REFERENCES grid_assets(id),
    maintenance_type TEXT NOT NULL CHECK(maintenance_type IN ('PREVENTIVE', 'CORRECTIVE', 'PREDICTIVE', 'EMERGENCY')),
    scheduled_date TEXT NOT NULL,
    estimated_duration_hours REAL NOT NULL,
    crew_requirements TEXT,
    special_equipment_needed TEXT,
    status TEXT NOT NULL CHECK(status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS crew_assignments (
    id INTEGER PRIMARY KEY,
    maintenance_schedule_id INTEGER NOT NULL REFERENCES maintenance_schedules(id),
    crew_leader TEXT NOT NULL,
    crew_members TEXT, -- JSON array
    assignment_date TEXT NOT NULL,
    estimated_completion_time TEXT,
    actual_completion_time TEXT,
    work_performed TEXT,
    status TEXT NOT NULL CHECK(status IN ('ASSIGNED', 'DISPATCHED', 'ON_SITE', 'COMPLETED'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_grid_assets_type ON grid_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_grid_assets_status ON grid_assets(status);
CREATE INDEX IF NOT EXISTS idx_outage_events_asset ON outage_events(affected_asset_id);
CREATE INDEX IF NOT EXISTS idx_outage_events_start_time ON outage_events(outage_start_time);
CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_asset ON maintenance_schedules(asset_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_date ON maintenance_schedules(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_crew_assignments_schedule ON crew_assignments(maintenance_schedule_id);