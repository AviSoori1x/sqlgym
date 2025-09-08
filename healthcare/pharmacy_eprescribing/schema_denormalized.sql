-- Denormalized pharmacy eprescribing analytics
-- Trade-off: Pre-calculated prescription metrics and adherence tracking vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS prescription_analytics (
    prescription_id INTEGER PRIMARY KEY,
    patient_id TEXT NOT NULL,
    patient_name TEXT NOT NULL,
    prescriber_name TEXT NOT NULL,
    prescriber_specialty TEXT NOT NULL,
    generic_name TEXT NOT NULL,
    brand_name TEXT,
    drug_class TEXT NOT NULL,
    written_date TEXT NOT NULL,
    quantity_prescribed INTEGER NOT NULL,
    days_supply INTEGER NOT NULL,
    prescription_status TEXT NOT NULL,
    fill_count INTEGER NOT NULL,
    total_dispensed INTEGER NOT NULL,
    last_fill_date TEXT,
    adherence_rate REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS pharmacy_performance (
    pharmacy_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    prescriptions_filled INTEGER NOT NULL,
    avg_fill_time_hours REAL,
    patient_satisfaction_score REAL,
    error_rate REAL,
    controlled_substance_fills INTEGER NOT NULL,
    PRIMARY KEY(pharmacy_id, month)
);

CREATE TABLE IF NOT EXISTS drug_utilization_summary (
    medication_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    prescription_count INTEGER NOT NULL,
    unique_patients INTEGER NOT NULL,
    total_quantity_dispensed INTEGER NOT NULL,
    avg_days_supply REAL,
    adherence_rate REAL,
    PRIMARY KEY(medication_id, month)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_prescription_analytics_patient ON prescription_analytics(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescription_analytics_prescriber ON prescription_analytics(prescriber_name);
CREATE INDEX IF NOT EXISTS idx_pharmacy_performance_month ON pharmacy_performance(month);
CREATE INDEX IF NOT EXISTS idx_drug_utilization_month ON drug_utilization_summary(month);