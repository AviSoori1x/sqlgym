PRAGMA foreign_keys=ON;
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE encounters (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    encounter_date TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('INPATIENT','OUTPATIENT'))
);
CREATE INDEX idx_encounter_patient_date ON encounters(patient_id, encounter_date);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    encounter_id INTEGER NOT NULL REFERENCES encounters(id),
    order_time TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PLACED','COMPLETED'))
);
CREATE INDEX idx_order_enc_time ON orders(encounter_id, order_time);
CREATE TABLE results (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    result_time TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING','FINAL'))
);
CREATE INDEX idx_result_order_time ON results(order_id, result_time);
