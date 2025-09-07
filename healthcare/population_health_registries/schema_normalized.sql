PRAGMA foreign_keys=ON;
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE registries (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    registry_id INTEGER NOT NULL REFERENCES registries(id),
    enroll_date TEXT NOT NULL,
    UNIQUE(patient_id, registry_id)
);
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    metric_date TEXT NOT NULL,
    metric_value NUMERIC NOT NULL CHECK(metric_value>=0)
);
CREATE TABLE risk_scores (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    score NUMERIC NOT NULL CHECK(score BETWEEN 0 AND 1)
);
CREATE INDEX idx_enroll_patient_registry ON enrollments(patient_id, registry_id);
CREATE INDEX idx_metric_patient_date ON metrics(patient_id, metric_date);
CREATE INDEX idx_risk_patient ON risk_scores(patient_id);
