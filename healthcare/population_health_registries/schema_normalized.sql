PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    patient_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('M', 'F', 'OTHER')),
    race_ethnicity TEXT,
    address TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'DECEASED'))
);

CREATE TABLE IF NOT EXISTS disease_registries (
    id INTEGER PRIMARY KEY,
    registry_code TEXT NOT NULL UNIQUE,
    registry_name TEXT NOT NULL,
    disease_category TEXT NOT NULL CHECK(disease_category IN ('DIABETES', 'HYPERTENSION', 'CANCER', 'HEART_DISEASE', 'COPD', 'MENTAL_HEALTH')),
    inclusion_criteria TEXT, -- JSON with enrollment criteria
    quality_measures TEXT, -- JSON with tracked measures
    reporting_frequency TEXT NOT NULL CHECK(reporting_frequency IN ('MONTHLY', 'QUARTERLY', 'ANNUALLY')),
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS registry_enrollments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    registry_id INTEGER NOT NULL REFERENCES disease_registries(id),
    enrollment_date TEXT NOT NULL,
    enrollment_source TEXT NOT NULL CHECK(enrollment_source IN ('PROVIDER_REFERRAL', 'CLAIMS_DATA', 'LAB_RESULTS', 'PATIENT_SELF_REPORT')),
    risk_stratification TEXT NOT NULL CHECK(risk_stratification IN ('LOW', 'MEDIUM', 'HIGH')),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'GRADUATED', 'DECEASED')),
    UNIQUE(patient_id, registry_id)
);

CREATE TABLE IF NOT EXISTS health_measures (
    id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES registry_enrollments(id),
    measure_date TEXT NOT NULL,
    measure_type TEXT NOT NULL CHECK(measure_type IN ('CLINICAL', 'BEHAVIORAL', 'OUTCOME', 'PROCESS')),
    measure_name TEXT NOT NULL,
    measure_value REAL,
    measure_units TEXT,
    target_value REAL,
    is_goal_met BOOLEAN NOT NULL DEFAULT 0,
    data_source TEXT NOT NULL CHECK(data_source IN ('EHR', 'CLAIMS', 'PATIENT_REPORTED', 'DEVICE'))
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    registry_id INTEGER NOT NULL REFERENCES disease_registries(id),
    assessment_date TEXT NOT NULL,
    risk_score REAL NOT NULL CHECK(risk_score BETWEEN 0 AND 100),
    risk_factors TEXT, -- JSON array of identified risk factors
    recommended_interventions TEXT, -- JSON array
    next_assessment_date TEXT,
    assessed_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    registry_id INTEGER NOT NULL REFERENCES disease_registries(id),
    intervention_date TEXT NOT NULL,
    intervention_type TEXT NOT NULL CHECK(intervention_type IN ('EDUCATION', 'CARE_COORDINATION', 'MEDICATION_REVIEW', 'LIFESTYLE_COUNSELING', 'REFERRAL')),
    intervention_description TEXT NOT NULL,
    delivered_by TEXT NOT NULL,
    outcome_measured TEXT,
    effectiveness_score INTEGER CHECK(effectiveness_score BETWEEN 1 AND 5)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_patients_zip ON patients(zip_code);
CREATE INDEX IF NOT EXISTS idx_registry_enrollments_patient ON registry_enrollments(patient_id);
CREATE INDEX IF NOT EXISTS idx_registry_enrollments_registry ON registry_enrollments(registry_id);
CREATE INDEX IF NOT EXISTS idx_health_measures_enrollment ON health_measures(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_health_measures_date ON health_measures(measure_date);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_patient ON risk_assessments(patient_id);
CREATE INDEX IF NOT EXISTS idx_interventions_patient ON interventions(patient_id);