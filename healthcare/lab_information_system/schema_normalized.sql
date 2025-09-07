PRAGMA foreign_keys=ON;
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE lab_tests (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE lab_orders (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    test_id INTEGER NOT NULL REFERENCES lab_tests(id) CHECK(test_id>0),
    ordered_at TEXT NOT NULL
);
CREATE TABLE specimens (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES lab_orders(id),
    collected_at TEXT NOT NULL
);
CREATE TABLE lab_results (
    id INTEGER PRIMARY KEY,
    specimen_id INTEGER NOT NULL REFERENCES specimens(id),
    result_value TEXT NOT NULL CHECK(result_value<>''),
    result_date TEXT NOT NULL
);
CREATE INDEX idx_orders_patient_date ON lab_orders(patient_id, ordered_at);
CREATE INDEX idx_specimen_order ON specimens(order_id);
CREATE INDEX idx_result_specimen ON lab_results(specimen_id, result_date);
