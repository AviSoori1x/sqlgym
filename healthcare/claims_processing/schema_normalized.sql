PRAGMA foreign_keys=ON;
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE payer_plans (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE claims (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    claim_date TEXT NOT NULL,
    plan_id INTEGER NOT NULL REFERENCES payer_plans(id),
    status TEXT NOT NULL CHECK(status IN ('OPEN','PAID','DENIED'))
);
CREATE INDEX idx_claim_plan_date ON claims(plan_id, claim_date);
CREATE TABLE claim_lines (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES claims(id),
    code TEXT NOT NULL,
    amount NUMERIC NOT NULL
);
CREATE INDEX idx_lines_claim ON claim_lines(claim_id);
CREATE TABLE adjudications (
    id INTEGER PRIMARY KEY,
    claim_line_id INTEGER NOT NULL REFERENCES claim_lines(id),
    adjudicated_on TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('APPROVED','DENIED'))
);
CREATE INDEX idx_adj_line ON adjudications(claim_line_id);
CREATE TABLE denials (
    id INTEGER PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES claims(id),
    denial_date TEXT NOT NULL,
    reason TEXT NOT NULL
);
CREATE INDEX idx_denial_claim_date ON denials(claim_id, denial_date);
