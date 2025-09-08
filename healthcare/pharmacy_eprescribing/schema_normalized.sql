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
    insurance_id TEXT,
    allergies TEXT, -- JSON array of known allergies
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'DECEASED'))
);

CREATE TABLE IF NOT EXISTS prescribers (
    id INTEGER PRIMARY KEY,
    prescriber_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    npi TEXT NOT NULL UNIQUE,
    dea_number TEXT NOT NULL UNIQUE,
    license_number TEXT NOT NULL,
    practice_address TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED'))
);

CREATE TABLE IF NOT EXISTS pharmacies (
    id INTEGER PRIMARY KEY,
    pharmacy_id TEXT NOT NULL UNIQUE,
    pharmacy_name TEXT NOT NULL,
    chain_name TEXT,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL CHECK(length(state) = 2),
    zip_code TEXT NOT NULL,
    phone TEXT NOT NULL,
    ncpdp_id TEXT NOT NULL UNIQUE,
    pharmacy_type TEXT NOT NULL CHECK(pharmacy_type IN ('RETAIL', 'HOSPITAL', 'MAIL_ORDER', 'SPECIALTY', 'CLINIC'))
);

CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY,
    ndc_code TEXT NOT NULL UNIQUE,
    generic_name TEXT NOT NULL,
    brand_name TEXT,
    strength TEXT NOT NULL,
    dosage_form TEXT NOT NULL CHECK(dosage_form IN ('TABLET', 'CAPSULE', 'LIQUID', 'INJECTION', 'CREAM', 'INHALER')),
    drug_class TEXT NOT NULL,
    controlled_substance_schedule TEXT CHECK(controlled_substance_schedule IN ('CI', 'CII', 'CIII', 'CIV', 'CV')),
    is_generic BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY,
    prescription_id TEXT NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    prescriber_id INTEGER NOT NULL REFERENCES prescribers(id),
    medication_id INTEGER NOT NULL REFERENCES medications(id),
    pharmacy_id INTEGER NOT NULL REFERENCES pharmacies(id),
    written_date TEXT NOT NULL,
    quantity_prescribed INTEGER NOT NULL,
    days_supply INTEGER NOT NULL,
    refills_authorized INTEGER NOT NULL DEFAULT 0,
    directions_for_use TEXT NOT NULL,
    indication TEXT,
    transmission_method TEXT NOT NULL CHECK(transmission_method IN ('ELECTRONIC', 'PHONE', 'FAX', 'WRITTEN')),
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'TRANSMITTED', 'RECEIVED', 'FILLED', 'CANCELLED', 'EXPIRED'))
);

CREATE TABLE IF NOT EXISTS prescription_fills (
    id INTEGER PRIMARY KEY,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(id),
    fill_number INTEGER NOT NULL,
    fill_date TEXT NOT NULL,
    quantity_dispensed INTEGER NOT NULL,
    days_supply_dispensed INTEGER NOT NULL,
    pharmacist_id TEXT NOT NULL,
    fill_status TEXT NOT NULL CHECK(fill_status IN ('PARTIAL', 'COMPLETE', 'CANCELLED')),
    copay_amount REAL,
    insurance_paid_amount REAL,
    patient_paid_amount REAL,
    UNIQUE(prescription_id, fill_number)
);

CREATE TABLE IF NOT EXISTS drug_interactions (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    medication_id_1 INTEGER NOT NULL REFERENCES medications(id),
    medication_id_2 INTEGER NOT NULL REFERENCES medications(id),
    interaction_severity TEXT NOT NULL CHECK(interaction_severity IN ('MINOR', 'MODERATE', 'MAJOR', 'CONTRAINDICATED')),
    interaction_description TEXT NOT NULL,
    detected_date TEXT NOT NULL,
    override_reason TEXT,
    overridden_by_prescriber_id INTEGER REFERENCES prescribers(id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id);
CREATE INDEX IF NOT EXISTS idx_patients_status ON patients(status);
CREATE INDEX IF NOT EXISTS idx_prescribers_npi ON prescribers(npi);
CREATE INDEX IF NOT EXISTS idx_prescribers_specialty ON prescribers(specialty);
CREATE INDEX IF NOT EXISTS idx_pharmacies_state ON pharmacies(state);
CREATE INDEX IF NOT EXISTS idx_pharmacies_type ON pharmacies(pharmacy_type);
CREATE INDEX IF NOT EXISTS idx_medications_ndc ON medications(ndc_code);
CREATE INDEX IF NOT EXISTS idx_medications_class ON medications(drug_class);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_prescriber ON prescriptions(prescriber_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_pharmacy ON prescriptions(pharmacy_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_written_date ON prescriptions(written_date);
CREATE INDEX IF NOT EXISTS idx_prescription_fills_prescription ON prescription_fills(prescription_id);
CREATE INDEX IF NOT EXISTS idx_drug_interactions_patient ON drug_interactions(patient_id);