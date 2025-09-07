PRAGMA foreign_keys=ON;
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE bills (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    bill_date TEXT NOT NULL,
    total NUMERIC NOT NULL CHECK(total>=0)
);
CREATE TABLE bill_items (
    id INTEGER PRIMARY KEY,
    bill_id INTEGER NOT NULL REFERENCES bills(id),
    description TEXT NOT NULL,
    amount NUMERIC NOT NULL CHECK(amount>=0)
);
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    bill_id INTEGER NOT NULL REFERENCES bills(id),
    payment_date TEXT NOT NULL,
    amount NUMERIC NOT NULL CHECK(amount>=0)
);
CREATE TABLE denials (
    id INTEGER PRIMARY KEY,
    bill_id INTEGER NOT NULL REFERENCES bills(id),
    denial_date TEXT NOT NULL,
    reason TEXT NOT NULL
);
CREATE INDEX idx_bill_patient_date ON bills(patient_id, bill_date);
CREATE INDEX idx_item_bill ON bill_items(bill_id);
CREATE INDEX idx_denial_bill ON denials(bill_id, denial_date);
