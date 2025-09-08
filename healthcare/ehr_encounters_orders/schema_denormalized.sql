-- Denormalized EHR encounters and orders analytics
-- Trade-off: Pre-calculated workflow metrics and provider performance vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS encounter_summary (
    encounter_id INTEGER PRIMARY KEY,
    patient_name TEXT NOT NULL,
    provider_name TEXT NOT NULL,
    provider_specialty TEXT NOT NULL,
    encounter_date TEXT NOT NULL,
    encounter_type TEXT NOT NULL,
    chief_complaint TEXT,
    total_orders INTEGER NOT NULL,
    completed_orders INTEGER NOT NULL,
    pending_orders INTEGER NOT NULL,
    cancelled_orders INTEGER NOT NULL,
    avg_order_turnaround_hours REAL,
    length_of_stay_hours REAL,
    encounter_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_productivity (
    provider_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    encounters_count INTEGER NOT NULL,
    total_orders INTEGER NOT NULL,
    completed_orders INTEGER NOT NULL,
    avg_turnaround_time_hours REAL,
    stat_orders_count INTEGER NOT NULL,
    stat_completion_rate REAL,
    patient_satisfaction_score REAL,
    PRIMARY KEY(provider_id, date)
);

CREATE TABLE IF NOT EXISTS order_workflow_metrics (
    order_type_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    orders_placed INTEGER NOT NULL,
    orders_completed INTEGER NOT NULL,
    avg_completion_time_hours REAL,
    stat_orders INTEGER NOT NULL,
    delayed_orders INTEGER NOT NULL,
    cancellation_rate REAL,
    PRIMARY KEY(order_type_id, date)
);

CREATE TABLE IF NOT EXISTS department_utilization (
    department TEXT NOT NULL,
    date TEXT NOT NULL,
    total_encounters INTEGER NOT NULL,
    total_orders INTEGER NOT NULL,
    provider_count INTEGER NOT NULL,
    avg_encounters_per_provider REAL,
    peak_hour_utilization REAL,
    capacity_utilization_rate REAL,
    PRIMARY KEY(department, date)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_encounter_summary_provider ON encounter_summary(provider_name);
CREATE INDEX IF NOT EXISTS idx_encounter_summary_date ON encounter_summary(encounter_date);
CREATE INDEX IF NOT EXISTS idx_provider_productivity_date ON provider_productivity(date);
CREATE INDEX IF NOT EXISTS idx_order_workflow_date ON order_workflow_metrics(date);
CREATE INDEX IF NOT EXISTS idx_department_utilization_date ON department_utilization(date);