PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    patient_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    insurance_primary TEXT,
    insurance_secondary TEXT,
    financial_class TEXT NOT NULL CHECK(financial_class IN ('COMMERCIAL', 'MEDICARE', 'MEDICAID', 'SELF_PAY', 'CHARITY'))
);

CREATE TABLE IF NOT EXISTS payers (
    id INTEGER PRIMARY KEY,
    payer_code TEXT NOT NULL UNIQUE,
    payer_name TEXT NOT NULL,
    payer_type TEXT NOT NULL CHECK(payer_type IN ('COMMERCIAL', 'GOVERNMENT', 'SELF_PAY')),
    contract_rate REAL,
    payment_terms_days INTEGER NOT NULL DEFAULT 30
);

CREATE TABLE IF NOT EXISTS charges (
    id INTEGER PRIMARY KEY,
    charge_id TEXT NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    service_date TEXT NOT NULL,
    procedure_code TEXT NOT NULL,
    diagnosis_codes TEXT, -- JSON array
    charge_amount REAL NOT NULL,
    units INTEGER NOT NULL DEFAULT 1,
    department TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'BILLED', 'PAID', 'DENIED', 'WRITTEN_OFF'))
);

CREATE TABLE IF NOT EXISTS billing_transactions (
    id INTEGER PRIMARY KEY,
    charge_id INTEGER NOT NULL REFERENCES charges(id),
    payer_id INTEGER NOT NULL REFERENCES payers(id),
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('CHARGE', 'PAYMENT', 'ADJUSTMENT', 'REFUND')),
    amount REAL NOT NULL,
    payment_method TEXT CHECK(payment_method IN ('CHECK', 'EFT', 'CREDIT_CARD', 'CASH')),
    reference_number TEXT
);

CREATE TABLE IF NOT EXISTS denials (
    id INTEGER PRIMARY KEY,
    charge_id INTEGER NOT NULL REFERENCES charges(id),
    payer_id INTEGER NOT NULL REFERENCES payers(id),
    denial_date TEXT NOT NULL,
    denial_reason_code TEXT NOT NULL,
    denial_reason TEXT NOT NULL,
    denied_amount REAL NOT NULL,
    denial_category TEXT NOT NULL CHECK(denial_category IN ('AUTHORIZATION', 'ELIGIBILITY', 'CODING', 'MEDICAL_NECESSITY', 'TIMELY_FILING')),
    is_appealable BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS appeals (
    id INTEGER PRIMARY KEY,
    denial_id INTEGER NOT NULL REFERENCES denials(id),
    appeal_level INTEGER NOT NULL CHECK(appeal_level BETWEEN 1 AND 3),
    appeal_date TEXT NOT NULL,
    appeal_amount REAL NOT NULL,
    appeal_reason TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'APPROVED', 'DENIED', 'WITHDRAWN')),
    decision_date TEXT,
    recovered_amount REAL DEFAULT 0
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id);
CREATE INDEX IF NOT EXISTS idx_charges_patient ON charges(patient_id);
CREATE INDEX IF NOT EXISTS idx_charges_service_date ON charges(service_date);
CREATE INDEX IF NOT EXISTS idx_charges_status ON charges(status);
CREATE INDEX IF NOT EXISTS idx_billing_transactions_charge ON billing_transactions(charge_id);
CREATE INDEX IF NOT EXISTS idx_denials_charge ON denials(charge_id);
CREATE INDEX IF NOT EXISTS idx_denials_date ON denials(denial_date);
CREATE INDEX IF NOT EXISTS idx_appeals_denial ON appeals(denial_id);