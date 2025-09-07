PRAGMA foreign_keys=ON;
CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE care_programs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id),
    program_id INTEGER NOT NULL REFERENCES care_programs(id),
    enroll_date TEXT NOT NULL,
    UNIQUE(member_id, program_id)
);
CREATE TABLE interventions (
    id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    intervention_date TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('CALL','VISIT','EMAIL'))
);
CREATE TABLE outcomes (
    id INTEGER PRIMARY KEY,
    intervention_id INTEGER NOT NULL REFERENCES interventions(id),
    outcome TEXT NOT NULL CHECK(outcome IN ('IMPROVED','NO_CHANGE'))
);
CREATE INDEX idx_enrollment_member_program ON enrollments(member_id, program_id);
CREATE INDEX idx_intervention_enroll_date ON interventions(enrollment_id, intervention_date);
CREATE INDEX idx_outcome_intervention ON outcomes(intervention_id);
