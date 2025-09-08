PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    patient_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('M', 'F', 'OTHER', 'UNKNOWN')),
    address TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    emergency_contact TEXT,
    insurance_id TEXT,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'DECEASED', 'TRANSFERRED'))
);

CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY,
    provider_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    department TEXT NOT NULL,
    npi TEXT NOT NULL UNIQUE,
    license_number TEXT,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'TERMINATED'))
);

CREATE TABLE IF NOT EXISTS encounters (
    id INTEGER PRIMARY KEY,
    encounter_id TEXT NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    encounter_date TEXT NOT NULL,
    encounter_type TEXT NOT NULL CHECK(encounter_type IN ('INPATIENT', 'OUTPATIENT', 'EMERGENCY', 'OBSERVATION', 'SURGERY')),
    admission_date TEXT,
    discharge_date TEXT,
    chief_complaint TEXT,
    diagnosis_codes TEXT, -- JSON array of ICD-10 codes
    status TEXT NOT NULL CHECK(status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW'))
);

CREATE TABLE IF NOT EXISTS order_types (
    id INTEGER PRIMARY KEY,
    order_type_code TEXT NOT NULL UNIQUE,
    order_type_name TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('LABORATORY', 'RADIOLOGY', 'MEDICATION', 'PROCEDURE', 'CONSULT', 'THERAPY')),
    requires_authorization BOOLEAN NOT NULL DEFAULT 0,
    typical_turnaround_hours INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS clinical_orders (
    id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    encounter_id INTEGER NOT NULL REFERENCES encounters(id),
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    order_type_id INTEGER NOT NULL REFERENCES order_types(id),
    order_datetime TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('ROUTINE', 'URGENT', 'STAT', 'ASAP')),
    order_details TEXT, -- JSON with order-specific parameters
    status TEXT NOT NULL CHECK(status IN ('ORDERED', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'DISCONTINUED')),
    scheduled_datetime TEXT,
    completed_datetime TEXT,
    ordering_notes TEXT
);

CREATE TABLE IF NOT EXISTS order_results (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES clinical_orders(id),
    result_datetime TEXT NOT NULL,
    result_type TEXT NOT NULL CHECK(result_type IN ('PRELIMINARY', 'FINAL', 'AMENDED', 'CORRECTED')),
    result_status TEXT NOT NULL CHECK(result_status IN ('NORMAL', 'ABNORMAL', 'CRITICAL', 'PENDING')),
    result_value TEXT,
    result_units TEXT,
    reference_range TEXT,
    interpreting_provider_id INTEGER REFERENCES providers(id),
    result_notes TEXT
);

CREATE TABLE IF NOT EXISTS order_tracking (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES clinical_orders(id),
    status_change_datetime TEXT NOT NULL,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    changed_by_provider_id INTEGER REFERENCES providers(id),
    change_reason TEXT,
    notes TEXT
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id);
CREATE INDEX IF NOT EXISTS idx_patients_status ON patients(status);
CREATE INDEX IF NOT EXISTS idx_providers_specialty ON providers(specialty);
CREATE INDEX IF NOT EXISTS idx_providers_department ON providers(department);
CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters(patient_id);
CREATE INDEX IF NOT EXISTS idx_encounters_provider ON encounters(provider_id);
CREATE INDEX IF NOT EXISTS idx_encounters_date ON encounters(encounter_date);
CREATE INDEX IF NOT EXISTS idx_encounters_type ON encounters(encounter_type);
CREATE INDEX IF NOT EXISTS idx_clinical_orders_encounter ON clinical_orders(encounter_id);
CREATE INDEX IF NOT EXISTS idx_clinical_orders_provider ON clinical_orders(provider_id);
CREATE INDEX IF NOT EXISTS idx_clinical_orders_datetime ON clinical_orders(order_datetime);
CREATE INDEX IF NOT EXISTS idx_clinical_orders_status ON clinical_orders(status);
CREATE INDEX IF NOT EXISTS idx_order_results_order ON order_results(order_id);
CREATE INDEX IF NOT EXISTS idx_order_tracking_order ON order_tracking(order_id);