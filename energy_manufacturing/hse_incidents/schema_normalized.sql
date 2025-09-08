PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    employee_id TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    department TEXT NOT NULL,
    job_title TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    safety_training_date TEXT,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'TERMINATED'))
);

CREATE TABLE IF NOT EXISTS incident_types (
    id INTEGER PRIMARY KEY,
    type_code TEXT NOT NULL UNIQUE,
    type_name TEXT NOT NULL,
    severity_category TEXT NOT NULL CHECK(severity_category IN ('MINOR', 'MODERATE', 'MAJOR', 'CATASTROPHIC')),
    regulatory_reportable BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS hse_incidents (
    id INTEGER PRIMARY KEY,
    incident_id TEXT NOT NULL UNIQUE,
    incident_date TEXT NOT NULL,
    incident_time TEXT NOT NULL,
    location TEXT NOT NULL,
    incident_type_id INTEGER NOT NULL REFERENCES incident_types(id),
    severity TEXT NOT NULL CHECK(severity IN ('MINOR', 'MODERATE', 'MAJOR', 'CATASTROPHIC')),
    description TEXT NOT NULL,
    immediate_cause TEXT,
    root_cause TEXT,
    injured_employee_id INTEGER REFERENCES employees(id),
    reported_by_employee_id INTEGER NOT NULL REFERENCES employees(id),
    status TEXT NOT NULL CHECK(status IN ('REPORTED', 'INVESTIGATING', 'CLOSED'))
);

CREATE TABLE IF NOT EXISTS investigations (
    id INTEGER PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES hse_incidents(id),
    investigator_id INTEGER NOT NULL REFERENCES employees(id),
    investigation_start_date TEXT NOT NULL,
    investigation_completion_date TEXT,
    findings TEXT,
    contributing_factors TEXT,
    status TEXT NOT NULL CHECK(status IN ('ONGOING', 'COMPLETED', 'PENDING_REVIEW'))
);

CREATE TABLE IF NOT EXISTS corrective_actions (
    id INTEGER PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES hse_incidents(id),
    action_description TEXT NOT NULL,
    responsible_person_id INTEGER NOT NULL REFERENCES employees(id),
    due_date TEXT NOT NULL,
    completion_date TEXT,
    status TEXT NOT NULL CHECK(status IN ('ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_hse_incidents_date ON hse_incidents(incident_date);
CREATE INDEX IF NOT EXISTS idx_hse_incidents_type ON hse_incidents(incident_type_id);
CREATE INDEX IF NOT EXISTS idx_hse_incidents_severity ON hse_incidents(severity);
CREATE INDEX IF NOT EXISTS idx_investigations_incident ON investigations(incident_id);
CREATE INDEX IF NOT EXISTS idx_corrective_actions_incident ON corrective_actions(incident_id);