PRAGMA foreign_keys=ON;
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE medications (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE pharmacies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT NOT NULL CHECK(length(state)=2)
);
CREATE TABLE prescriptions (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    medication_id INTEGER NOT NULL REFERENCES medications(id),
    written_date TEXT NOT NULL,
    pharmacy_id INTEGER NOT NULL REFERENCES pharmacies(id)
);
CREATE TABLE fills (
    id INTEGER PRIMARY KEY,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(id),
    fill_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('FILLED','CANCELLED'))
);
CREATE INDEX idx_rx_patient_date ON prescriptions(patient_id, written_date);
CREATE INDEX idx_fill_rx_date ON fills(prescription_id, fill_date);
CREATE INDEX idx_pharmacy_state ON pharmacies(state);
