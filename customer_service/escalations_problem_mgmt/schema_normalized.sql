PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tier TEXT NOT NULL CHECK(tier IN ('BRONZE', 'SILVER', 'GOLD', 'PLATINUM')),
    account_value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    skill_level TEXT NOT NULL CHECK(skill_level IN ('L1', 'L2', 'L3', 'MANAGER', 'DIRECTOR')),
    department TEXT NOT NULL CHECK(department IN ('SUPPORT', 'TECHNICAL', 'BILLING', 'SALES'))
);

CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    created_by_agent_id INTEGER NOT NULL REFERENCES agents(id),
    category TEXT NOT NULL CHECK(category IN ('BUG', 'BILLING', 'ACCESS', 'PERFORMANCE', 'FEATURE_REQUEST', 'COMPLIANCE')),
    severity TEXT NOT NULL CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'IN_PROGRESS', 'ESCALATED', 'RESOLVED', 'CLOSED')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT,
    description TEXT NOT NULL,
    impact_score INTEGER CHECK(impact_score BETWEEN 1 AND 100)
);

CREATE TABLE IF NOT EXISTS escalations (
    id INTEGER PRIMARY KEY,
    issue_id INTEGER NOT NULL REFERENCES issues(id),
    from_agent_id INTEGER NOT NULL REFERENCES agents(id),
    to_agent_id INTEGER NOT NULL REFERENCES agents(id),
    escalation_reason TEXT NOT NULL CHECK(escalation_reason IN ('EXPERTISE_REQUIRED', 'CUSTOMER_REQUEST', 'SLA_BREACH', 'HIGH_VALUE_CUSTOMER', 'LEGAL_RISK')),
    escalated_at TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS problem_records (
    id INTEGER PRIMARY KEY,
    root_issue_id INTEGER NOT NULL REFERENCES issues(id),
    problem_statement TEXT NOT NULL,
    root_cause TEXT,
    permanent_fix TEXT,
    affected_customers INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    closed_at TEXT,
    status TEXT NOT NULL CHECK(status IN ('INVESTIGATING', 'ROOT_CAUSE_FOUND', 'FIX_IN_PROGRESS', 'RESOLVED')),
    UNIQUE(root_issue_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_issues_customer ON issues(customer_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity);
CREATE INDEX IF NOT EXISTS idx_issues_created ON issues(created_at);
CREATE INDEX IF NOT EXISTS idx_escalations_issue ON escalations(issue_id);
CREATE INDEX IF NOT EXISTS idx_escalations_date ON escalations(escalated_at);
CREATE INDEX IF NOT EXISTS idx_problem_records_status ON problem_records(status);