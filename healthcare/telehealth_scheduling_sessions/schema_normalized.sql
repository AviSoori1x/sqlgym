PRAGMA foreign_keys=ON;
CREATE TABLE providers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    appt_time TEXT NOT NULL
);
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    appointment_id INTEGER NOT NULL REFERENCES appointments(id),
    start_time TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('COMPLETED','CANCELLED'))
);
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5)
);
CREATE INDEX idx_appt_provider_time ON appointments(provider_id, appt_time);
CREATE INDEX idx_session_appointment ON sessions(appointment_id);
CREATE INDEX idx_feedback_session ON feedback(session_id);
