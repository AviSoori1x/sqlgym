PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY,
    member_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('M', 'F', 'OTHER', 'UNKNOWN')),
    address TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    enrollment_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'TERMINATED', 'SUSPENDED'))
);

CREATE TABLE IF NOT EXISTS insurance_plans (
    id INTEGER PRIMARY KEY,
    plan_code TEXT NOT NULL UNIQUE,
    plan_name TEXT NOT NULL,
    plan_type TEXT NOT NULL CHECK(plan_type IN ('HMO', 'PPO', 'EPO', 'POS', 'HDHP', 'MEDICARE', 'MEDICAID')),
    coverage_level TEXT NOT NULL CHECK(coverage_level IN ('INDIVIDUAL', 'FAMILY', 'EMPLOYEE_PLUS_ONE', 'EMPLOYEE_PLUS_FAMILY')),
    deductible_amount REAL NOT NULL,
    out_of_pocket_max REAL NOT NULL,
    copay_primary_care REAL,
    copay_specialist REAL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY,
    npi TEXT NOT NULL UNIQUE,
    provider_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    provider_type TEXT NOT NULL CHECK(provider_type IN ('PHYSICIAN', 'HOSPITAL', 'CLINIC', 'LABORATORY', 'PHARMACY', 'DME_SUPPLIER')),
    tax_id TEXT NOT NULL,
    address TEXT NOT NULL,
    network_status TEXT NOT NULL CHECK(network_status IN ('IN_NETWORK', 'OUT_OF_NETWORK', 'CONTRACTED', 'NON_CONTRACTED'))
);

CREATE TABLE IF NOT EXISTS medical_claims (
    id INTEGER PRIMARY KEY,
    claim_number TEXT NOT NULL UNIQUE,
    member_id INTEGER NOT NULL REFERENCES members(id),
    plan_id INTEGER NOT NULL REFERENCES insurance_plans(id),
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    service_date TEXT NOT NULL,
    submission_date TEXT NOT NULL,
    claim_type TEXT NOT NULL CHECK(claim_type IN ('PROFESSIONAL', 'INSTITUTIONAL', 'DENTAL', 'VISION', 'PHARMACY')),
    place_of_service TEXT NOT NULL CHECK(place_of_service IN ('OFFICE', 'HOSPITAL_INPATIENT', 'HOSPITAL_OUTPATIENT', 'EMERGENCY_ROOM', 'HOME', 'NURSING_HOME')),
    diagnosis_codes TEXT NOT NULL, -- JSON array of ICD-10 codes
    total_charged_amount REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('SUBMITTED', 'PENDING', 'APPROVED', 'DENIED', 'PAID', 'APPEALED')),
    processing_priority TEXT NOT NULL CHECK(processing_priority IN ('ROUTINE', 'URGENT', 'EXPEDITED'))
);

CREATE TABLE IF NOT EXISTS claim_line_items (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES medical_claims(id),
    line_number INTEGER NOT NULL,
    procedure_code TEXT NOT NULL, -- CPT/HCPCS code
    modifier_codes TEXT, -- JSON array of modifiers
    service_units INTEGER NOT NULL DEFAULT 1,
    charged_amount REAL NOT NULL,
    allowed_amount REAL,
    paid_amount REAL,
    denied_amount REAL DEFAULT 0,
    copay_amount REAL DEFAULT 0,
    deductible_amount REAL DEFAULT 0,
    coinsurance_amount REAL DEFAULT 0,
    UNIQUE(claim_id, line_number)
);

CREATE TABLE IF NOT EXISTS claim_adjudications (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES medical_claims(id),
    adjudication_date TEXT NOT NULL,
    adjudicator_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK(decision IN ('APPROVED', 'DENIED', 'PARTIAL_APPROVAL', 'PENDED')),
    total_approved_amount REAL NOT NULL,
    total_denied_amount REAL NOT NULL,
    reason_codes TEXT, -- JSON array of reason codes
    processing_time_hours REAL,
    auto_adjudicated BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS claim_denials (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES medical_claims(id),
    line_item_id INTEGER REFERENCES claim_line_items(id),
    denial_date TEXT NOT NULL,
    denial_code TEXT NOT NULL,
    denial_reason TEXT NOT NULL,
    denial_category TEXT NOT NULL CHECK(denial_category IN ('COVERAGE', 'CODING', 'AUTHORIZATION', 'DUPLICATE', 'TIMELY_FILING', 'PROVIDER_ELIGIBILITY')),
    is_appealable BOOLEAN NOT NULL DEFAULT 1,
    appeal_deadline TEXT,
    denial_amount REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS prior_authorizations (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    authorization_number TEXT NOT NULL UNIQUE,
    service_code TEXT NOT NULL,
    requested_date TEXT NOT NULL,
    approval_date TEXT,
    expiration_date TEXT,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'APPROVED', 'DENIED', 'EXPIRED')),
    approved_units INTEGER,
    clinical_criteria TEXT -- JSON with approval criteria
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_members_member_id ON members(member_id);
CREATE INDEX IF NOT EXISTS idx_members_status ON members(status);
CREATE INDEX IF NOT EXISTS idx_insurance_plans_type ON insurance_plans(plan_type);
CREATE INDEX IF NOT EXISTS idx_providers_npi ON providers(npi);
CREATE INDEX IF NOT EXISTS idx_providers_specialty ON providers(specialty);
CREATE INDEX IF NOT EXISTS idx_medical_claims_member ON medical_claims(member_id);
CREATE INDEX IF NOT EXISTS idx_medical_claims_provider ON medical_claims(provider_id);
CREATE INDEX IF NOT EXISTS idx_medical_claims_service_date ON medical_claims(service_date);
CREATE INDEX IF NOT EXISTS idx_medical_claims_status ON medical_claims(status);
CREATE INDEX IF NOT EXISTS idx_claim_line_items_claim ON claim_line_items(claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_adjudications_claim ON claim_adjudications(claim_id);
CREATE INDEX IF NOT EXISTS idx_claim_denials_claim ON claim_denials(claim_id);
CREATE INDEX IF NOT EXISTS idx_prior_authorizations_member ON prior_authorizations(member_id);