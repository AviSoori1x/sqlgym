PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS manufacturing_plants (
    id INTEGER PRIMARY KEY,
    plant_code TEXT NOT NULL UNIQUE,
    plant_name TEXT NOT NULL,
    location TEXT NOT NULL,
    plant_type TEXT NOT NULL CHECK(plant_type IN ('AUTOMOTIVE', 'ELECTRONICS', 'FOOD_BEVERAGE', 'PHARMACEUTICAL', 'CHEMICAL', 'TEXTILE')),
    production_capacity REAL NOT NULL,
    operational_start_date TEXT NOT NULL,
    shift_pattern TEXT NOT NULL CHECK(shift_pattern IN ('8_HOUR_3_SHIFT', '12_HOUR_2_SHIFT', 'CONTINUOUS', 'FLEXIBLE')),
    status TEXT NOT NULL CHECK(status IN ('OPERATIONAL', 'MAINTENANCE', 'SHUTDOWN'))
);

CREATE TABLE IF NOT EXISTS production_lines (
    id INTEGER PRIMARY KEY,
    line_code TEXT NOT NULL UNIQUE,
    plant_id INTEGER NOT NULL REFERENCES manufacturing_plants(id),
    line_name TEXT NOT NULL,
    product_family TEXT NOT NULL,
    design_speed_units_per_hour REAL NOT NULL,
    installation_date TEXT NOT NULL,
    last_major_maintenance TEXT,
    automation_level TEXT NOT NULL CHECK(automation_level IN ('MANUAL', 'SEMI_AUTOMATED', 'FULLY_AUTOMATED')),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'IDLE', 'MAINTENANCE', 'DECOMMISSIONED'))
);

CREATE TABLE IF NOT EXISTS shift_schedules (
    id INTEGER PRIMARY KEY,
    plant_id INTEGER NOT NULL REFERENCES manufacturing_plants(id),
    shift_date TEXT NOT NULL,
    shift_number INTEGER NOT NULL CHECK(shift_number BETWEEN 1 AND 3),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    planned_production_minutes INTEGER NOT NULL,
    crew_size INTEGER NOT NULL,
    shift_supervisor TEXT NOT NULL,
    UNIQUE(plant_id, shift_date, shift_number)
);

CREATE TABLE IF NOT EXISTS production_runs (
    id INTEGER PRIMARY KEY,
    run_id TEXT NOT NULL UNIQUE,
    line_id INTEGER NOT NULL REFERENCES production_lines(id),
    shift_schedule_id INTEGER NOT NULL REFERENCES shift_schedules(id),
    product_code TEXT NOT NULL,
    run_start_time TEXT NOT NULL,
    run_end_time TEXT,
    planned_runtime_minutes INTEGER NOT NULL,
    actual_runtime_minutes INTEGER,
    target_units_per_hour REAL NOT NULL,
    actual_units_produced INTEGER,
    good_units_produced INTEGER,
    defective_units INTEGER,
    run_status TEXT NOT NULL CHECK(run_status IN ('RUNNING', 'COMPLETED', 'ABORTED', 'PAUSED'))
);

CREATE TABLE IF NOT EXISTS downtime_events (
    id INTEGER PRIMARY KEY,
    production_run_id INTEGER NOT NULL REFERENCES production_runs(id),
    downtime_start TEXT NOT NULL,
    downtime_end TEXT,
    downtime_minutes INTEGER,
    downtime_category TEXT NOT NULL CHECK(downtime_category IN ('PLANNED_MAINTENANCE', 'UNPLANNED_MAINTENANCE', 'SETUP_CHANGEOVER', 'QUALITY_ISSUE', 'MATERIAL_SHORTAGE', 'OPERATOR_BREAK')),
    root_cause TEXT,
    equipment_involved TEXT,
    resolution_action TEXT,
    resolved_by TEXT
);

CREATE TABLE IF NOT EXISTS quality_checks (
    id INTEGER PRIMARY KEY,
    production_run_id INTEGER NOT NULL REFERENCES production_runs(id),
    check_datetime TEXT NOT NULL,
    check_type TEXT NOT NULL CHECK(check_type IN ('INCOMING_MATERIAL', 'IN_PROCESS', 'FINAL_INSPECTION', 'STATISTICAL_PROCESS_CONTROL')),
    parameter_name TEXT NOT NULL,
    measured_value REAL,
    target_value REAL,
    tolerance_range TEXT,
    pass_fail TEXT NOT NULL CHECK(pass_fail IN ('PASS', 'FAIL', 'WARNING')),
    inspector_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS oee_calculations (
    id INTEGER PRIMARY KEY,
    production_run_id INTEGER NOT NULL REFERENCES production_runs(id),
    calculation_date TEXT NOT NULL,
    availability_percentage REAL NOT NULL CHECK(availability_percentage BETWEEN 0 AND 100),
    performance_percentage REAL NOT NULL CHECK(performance_percentage BETWEEN 0 AND 100),
    quality_percentage REAL NOT NULL CHECK(quality_percentage BETWEEN 0 AND 100),
    oee_percentage REAL NOT NULL CHECK(oee_percentage BETWEEN 0 AND 100),
    calculated_by TEXT NOT NULL,
    UNIQUE(production_run_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_manufacturing_plants_type ON manufacturing_plants(plant_type);
CREATE INDEX IF NOT EXISTS idx_production_lines_plant ON production_lines(plant_id);
CREATE INDEX IF NOT EXISTS idx_shift_schedules_plant_date ON shift_schedules(plant_id, shift_date);
CREATE INDEX IF NOT EXISTS idx_production_runs_line ON production_runs(line_id);
CREATE INDEX IF NOT EXISTS idx_production_runs_start_time ON production_runs(run_start_time);
CREATE INDEX IF NOT EXISTS idx_downtime_events_run ON downtime_events(production_run_id);
CREATE INDEX IF NOT EXISTS idx_downtime_events_category ON downtime_events(downtime_category);
CREATE INDEX IF NOT EXISTS idx_quality_checks_run ON quality_checks(production_run_id);
CREATE INDEX IF NOT EXISTS idx_oee_calculations_run ON oee_calculations(production_run_id);