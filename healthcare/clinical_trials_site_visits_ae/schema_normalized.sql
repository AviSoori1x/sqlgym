PRAGMA foreign_keys=ON;
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE trials (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
CREATE TABLE investigators (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE site_visits (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    trial_id INTEGER NOT NULL REFERENCES trials(id),
    investigator_id INTEGER NOT NULL REFERENCES investigators(id),
    visit_date TEXT NOT NULL CHECK(visit_date > '2023-12-31')
);
CREATE TABLE adverse_events (
    id INTEGER PRIMARY KEY,
    visit_id INTEGER NOT NULL REFERENCES site_visits(id),
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('MILD','SEVERE'))
);
CREATE INDEX idx_visit_subject_trial ON site_visits(subject_id, trial_id, visit_date);
CREATE INDEX idx_visit_investigator ON site_visits(investigator_id);
CREATE INDEX idx_ae_visit ON adverse_events(visit_id);
