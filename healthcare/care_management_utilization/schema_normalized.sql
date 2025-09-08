PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY,
    member_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('M', 'F', 'OTHER')),
    risk_level TEXT NOT NULL CHECK(risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    chronic_conditions TEXT, -- JSON array
    enrollment_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'DISENROLLED'))
);

CREATE TABLE IF NOT EXISTS care_managers (
    id INTEGER PRIMARY KEY,
    manager_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    credentials TEXT NOT NULL,
    specialization TEXT NOT NULL,
    caseload_capacity INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'ON_LEAVE'))
);

CREATE TABLE IF NOT EXISTS care_plans (
    id INTEGER PRIMARY KEY,
    plan_id TEXT NOT NULL UNIQUE,
    member_id INTEGER NOT NULL REFERENCES members(id),
    care_manager_id INTEGER NOT NULL REFERENCES care_managers(id),
    plan_start_date TEXT NOT NULL,
    plan_end_date TEXT,
    plan_type TEXT NOT NULL CHECK(plan_type IN ('CHRONIC_CARE', 'TRANSITIONAL', 'BEHAVIORAL_HEALTH', 'COMPLEX_CASE')),
    goals TEXT, -- JSON array of care goals
    interventions TEXT, -- JSON array of planned interventions
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'COMPLETED', 'SUSPENDED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS utilization_reviews (
    id INTEGER PRIMARY KEY,
    review_id TEXT NOT NULL UNIQUE,
    member_id INTEGER NOT NULL REFERENCES members(id),
    service_type TEXT NOT NULL CHECK(service_type IN ('INPATIENT', 'OUTPATIENT', 'EMERGENCY', 'SPECIALIST', 'DME', 'PHARMACY')),
    requested_service TEXT NOT NULL,
    review_date TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK(decision IN ('APPROVED', 'DENIED', 'MODIFIED', 'PENDING')),
    clinical_criteria TEXT,
    decision_rationale TEXT
);

CREATE TABLE IF NOT EXISTS authorizations (
    id INTEGER PRIMARY KEY,
    authorization_id TEXT NOT NULL UNIQUE,
    member_id INTEGER NOT NULL REFERENCES members(id),
    service_code TEXT NOT NULL,
    authorized_units INTEGER NOT NULL,
    authorization_date TEXT NOT NULL,
    effective_start_date TEXT NOT NULL,
    expiration_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'EXPIRED', 'CANCELLED', 'EXHAUSTED'))
);

CREATE TABLE IF NOT EXISTS case_notes (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    care_manager_id INTEGER NOT NULL REFERENCES care_managers(id),
    note_datetime TEXT NOT NULL,
    note_type TEXT NOT NULL CHECK(note_type IN ('ASSESSMENT', 'INTERVENTION', 'COORDINATION', 'FOLLOW_UP', 'DISCHARGE')),
    note_content TEXT NOT NULL,
    action_items TEXT, -- JSON array
    next_contact_date TEXT
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_members_risk_level ON members(risk_level);
CREATE INDEX IF NOT EXISTS idx_care_plans_member ON care_plans(member_id);
CREATE INDEX IF NOT EXISTS idx_care_plans_manager ON care_plans(care_manager_id);
CREATE INDEX IF NOT EXISTS idx_utilization_reviews_member ON utilization_reviews(member_id);
CREATE INDEX IF NOT EXISTS idx_authorizations_member ON authorizations(member_id);
CREATE INDEX IF NOT EXISTS idx_case_notes_member ON case_notes(member_id);