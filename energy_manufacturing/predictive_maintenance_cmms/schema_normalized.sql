PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS industrial_assets (
    id INTEGER PRIMARY KEY,
    asset_tag TEXT NOT NULL UNIQUE,
    asset_name TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK(asset_type IN ('PUMP', 'MOTOR', 'COMPRESSOR', 'TURBINE', 'CONVEYOR', 'VALVE', 'HEAT_EXCHANGER')),
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    serial_number TEXT NOT NULL UNIQUE,
    installation_date TEXT NOT NULL,
    location TEXT NOT NULL,
    criticality_level TEXT NOT NULL CHECK(criticality_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status TEXT NOT NULL CHECK(status IN ('OPERATING', 'IDLE', 'MAINTENANCE', 'FAILED', 'DECOMMISSIONED'))
);

CREATE TABLE IF NOT EXISTS maintenance_plans (
    id INTEGER PRIMARY KEY,
    plan_id TEXT NOT NULL UNIQUE,
    asset_id INTEGER NOT NULL REFERENCES industrial_assets(id),
    maintenance_type TEXT NOT NULL CHECK(maintenance_type IN ('PREVENTIVE', 'PREDICTIVE', 'CORRECTIVE', 'CONDITION_BASED')),
    frequency_days INTEGER NOT NULL,
    estimated_duration_hours REAL NOT NULL,
    required_skills TEXT, -- JSON array
    required_parts TEXT, -- JSON array  
    procedure_document TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS maintenance_work_orders (
    id INTEGER PRIMARY KEY,
    work_order_number TEXT NOT NULL UNIQUE,
    asset_id INTEGER NOT NULL REFERENCES industrial_assets(id),
    maintenance_plan_id INTEGER REFERENCES maintenance_plans(id),
    work_order_type TEXT NOT NULL CHECK(work_order_type IN ('PLANNED', 'EMERGENCY', 'BREAKDOWN', 'IMPROVEMENT')),
    priority TEXT NOT NULL CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH', 'EMERGENCY')),
    created_date TEXT NOT NULL,
    scheduled_start_date TEXT NOT NULL,
    scheduled_end_date TEXT NOT NULL,
    actual_start_date TEXT,
    actual_end_date TEXT,
    assigned_technician TEXT,
    work_description TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES industrial_assets(id),
    sensor_type TEXT NOT NULL CHECK(sensor_type IN ('VIBRATION', 'TEMPERATURE', 'PRESSURE', 'FLOW', 'CURRENT', 'VOLTAGE')),
    reading_timestamp TEXT NOT NULL,
    reading_value REAL NOT NULL,
    reading_units TEXT NOT NULL,
    alarm_threshold_low REAL,
    alarm_threshold_high REAL,
    alarm_triggered BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS failure_predictions (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES industrial_assets(id),
    prediction_date TEXT NOT NULL,
    predicted_failure_date TEXT NOT NULL,
    confidence_percentage REAL NOT NULL CHECK(confidence_percentage BETWEEN 0 AND 100),
    failure_mode TEXT NOT NULL,
    contributing_factors TEXT, -- JSON array
    recommended_action TEXT NOT NULL,
    model_version TEXT NOT NULL,
    prediction_status TEXT NOT NULL CHECK(prediction_status IN ('ACTIVE', 'RESOLVED', 'FALSE_POSITIVE'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_industrial_assets_type ON industrial_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_industrial_assets_criticality ON industrial_assets(criticality_level);
CREATE INDEX IF NOT EXISTS idx_maintenance_plans_asset ON maintenance_plans(asset_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_work_orders_asset ON maintenance_work_orders(asset_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_work_orders_date ON maintenance_work_orders(scheduled_start_date);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_asset ON sensor_readings(asset_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(reading_timestamp);
CREATE INDEX IF NOT EXISTS idx_failure_predictions_asset ON failure_predictions(asset_id);