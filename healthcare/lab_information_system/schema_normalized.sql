PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    patient_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('M', 'F', 'OTHER')),
    medical_record_number TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'DECEASED'))
);

CREATE TABLE IF NOT EXISTS lab_tests (
    id INTEGER PRIMARY KEY,
    test_code TEXT NOT NULL UNIQUE,
    test_name TEXT NOT NULL,
    test_category TEXT NOT NULL CHECK(test_category IN ('CHEMISTRY', 'HEMATOLOGY', 'MICROBIOLOGY', 'IMMUNOLOGY', 'MOLECULAR')),
    specimen_type TEXT NOT NULL CHECK(specimen_type IN ('BLOOD', 'URINE', 'TISSUE', 'SWAB', 'CSF')),
    turnaround_time_hours INTEGER NOT NULL,
    reference_range TEXT,
    critical_low_value REAL,
    critical_high_value REAL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS lab_orders (
    id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    ordering_provider TEXT NOT NULL,
    test_id INTEGER NOT NULL REFERENCES lab_tests(id),
    order_datetime TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('ROUTINE', 'URGENT', 'STAT')),
    clinical_indication TEXT,
    status TEXT NOT NULL CHECK(status IN ('ORDERED', 'COLLECTED', 'RECEIVED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS specimens (
    id INTEGER PRIMARY KEY,
    specimen_id TEXT NOT NULL UNIQUE,
    order_id INTEGER NOT NULL REFERENCES lab_orders(id),
    collection_datetime TEXT NOT NULL,
    collection_method TEXT NOT NULL,
    collected_by TEXT NOT NULL,
    specimen_volume REAL,
    specimen_condition TEXT NOT NULL CHECK(specimen_condition IN ('ACCEPTABLE', 'HEMOLYZED', 'CLOTTED', 'INSUFFICIENT', 'CONTAMINATED')),
    received_datetime TEXT,
    processing_status TEXT NOT NULL CHECK(processing_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'REJECTED'))
);

CREATE TABLE IF NOT EXISTS lab_results (
    id INTEGER PRIMARY KEY,
    specimen_id INTEGER NOT NULL REFERENCES specimens(id),
    test_id INTEGER NOT NULL REFERENCES lab_tests(id),
    result_datetime TEXT NOT NULL,
    result_value TEXT,
    result_units TEXT,
    abnormal_flag TEXT CHECK(abnormal_flag IN ('NORMAL', 'HIGH', 'LOW', 'CRITICAL_HIGH', 'CRITICAL_LOW')),
    technologist_id TEXT NOT NULL,
    reviewed_by_pathologist TEXT,
    result_status TEXT NOT NULL CHECK(result_status IN ('PRELIMINARY', 'FINAL', 'CORRECTED'))
);

CREATE TABLE IF NOT EXISTS quality_controls (
    id INTEGER PRIMARY KEY,
    control_lot_number TEXT NOT NULL,
    test_id INTEGER NOT NULL REFERENCES lab_tests(id),
    run_datetime TEXT NOT NULL,
    expected_value REAL NOT NULL,
    actual_value REAL NOT NULL,
    variance_percentage REAL NOT NULL,
    control_status TEXT NOT NULL CHECK(control_status IN ('PASSED', 'FAILED', 'OUT_OF_RANGE')),
    technologist_id TEXT NOT NULL
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_patients_mrn ON patients(medical_record_number);
CREATE INDEX IF NOT EXISTS idx_lab_tests_category ON lab_tests(test_category);
CREATE INDEX IF NOT EXISTS idx_lab_orders_patient ON lab_orders(patient_id);
CREATE INDEX IF NOT EXISTS idx_lab_orders_datetime ON lab_orders(order_datetime);
CREATE INDEX IF NOT EXISTS idx_specimens_order ON specimens(order_id);
CREATE INDEX IF NOT EXISTS idx_specimens_collection_datetime ON specimens(collection_datetime);
CREATE INDEX IF NOT EXISTS idx_lab_results_specimen ON lab_results(specimen_id);
CREATE INDEX IF NOT EXISTS idx_lab_results_datetime ON lab_results(result_datetime);
CREATE INDEX IF NOT EXISTS idx_quality_controls_test ON quality_controls(test_id);