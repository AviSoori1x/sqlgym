PRAGMA foreign_keys=ON;
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE radiologists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE studies (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    study_date TEXT NOT NULL
);
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    study_id INTEGER NOT NULL REFERENCES studies(id),
    modality TEXT NOT NULL CHECK(modality IN ('XRAY','CT','MR'))
);
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY,
    study_id INTEGER NOT NULL REFERENCES studies(id),
    radiologist_id INTEGER NOT NULL REFERENCES radiologists(id),
    assigned_at TEXT NOT NULL CHECK(assigned_at > '2023-12-31')
);
CREATE INDEX idx_study_patient_date ON studies(patient_id, study_date);
CREATE INDEX idx_image_study ON images(study_id);
CREATE INDEX idx_assign_study_radiologist ON assignments(study_id, radiologist_id);
