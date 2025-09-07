PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS sellers (
    id INTEGER PRIMARY KEY,
    seller_name TEXT NOT NULL,
    business_type TEXT NOT NULL CHECK(business_type IN ('INDIVIDUAL', 'BUSINESS', 'ENTERPRISE')),
    registration_date TEXT NOT NULL,
    country TEXT NOT NULL,
    verification_status TEXT NOT NULL CHECK(verification_status IN ('PENDING', 'VERIFIED', 'REJECTED', 'SUSPENDED')),
    performance_rating REAL CHECK(performance_rating BETWEEN 0 AND 5),
    total_sales REAL NOT NULL DEFAULT 0,
    active_listings INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS compliance_policies (
    id INTEGER PRIMARY KEY,
    policy_name TEXT NOT NULL UNIQUE,
    policy_type TEXT NOT NULL CHECK(policy_type IN ('PRODUCT_QUALITY', 'SHIPPING', 'RETURNS', 'CUSTOMER_SERVICE', 'LEGAL')),
    description TEXT NOT NULL,
    severity_level TEXT NOT NULL CHECK(severity_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    auto_enforcement BOOLEAN NOT NULL DEFAULT 0,
    created_date TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS policy_violations (
    id INTEGER PRIMARY KEY,
    seller_id INTEGER NOT NULL REFERENCES sellers(id),
    policy_id INTEGER NOT NULL REFERENCES compliance_policies(id),
    violation_date TEXT NOT NULL,
    violation_type TEXT NOT NULL CHECK(violation_type IN ('AUTOMATIC', 'REPORTED', 'AUDIT_FOUND')),
    description TEXT NOT NULL,
    evidence TEXT, -- JSON with violation evidence
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'UNDER_REVIEW', 'RESOLVED', 'APPEALED', 'CLOSED')),
    resolution_date TEXT,
    penalty_applied TEXT
);

CREATE TABLE IF NOT EXISTS seller_metrics (
    id INTEGER PRIMARY KEY,
    seller_id INTEGER NOT NULL REFERENCES sellers(id),
    metric_date TEXT NOT NULL,
    orders_count INTEGER NOT NULL DEFAULT 0,
    cancellation_rate REAL NOT NULL DEFAULT 0,
    return_rate REAL NOT NULL DEFAULT 0,
    late_shipment_rate REAL NOT NULL DEFAULT 0,
    customer_satisfaction REAL CHECK(customer_satisfaction BETWEEN 0 AND 5),
    response_time_hours REAL,
    UNIQUE(seller_id, metric_date)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY,
    seller_id INTEGER NOT NULL REFERENCES sellers(id),
    audit_type TEXT NOT NULL CHECK(audit_type IN ('ACCOUNT_REVIEW', 'PRODUCT_AUDIT', 'PERFORMANCE_CHECK', 'COMPLIANCE_SCAN')),
    audit_date TEXT NOT NULL,
    auditor_id TEXT NOT NULL,
    findings TEXT, -- JSON with audit findings
    risk_score INTEGER CHECK(risk_score BETWEEN 0 AND 100),
    follow_up_required BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS enforcement_actions (
    id INTEGER PRIMARY KEY,
    seller_id INTEGER NOT NULL REFERENCES sellers(id),
    action_type TEXT NOT NULL CHECK(action_type IN ('WARNING', 'LISTING_REMOVAL', 'ACCOUNT_SUSPENSION', 'ACCOUNT_TERMINATION', 'FINE')),
    action_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    duration_days INTEGER, -- For suspensions
    monetary_penalty REAL, -- For fines
    appeal_deadline TEXT,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'APPEALED', 'OVERTURNED', 'EXPIRED'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_sellers_verification ON sellers(verification_status);
CREATE INDEX IF NOT EXISTS idx_sellers_rating ON sellers(performance_rating);
CREATE INDEX IF NOT EXISTS idx_policy_violations_seller ON policy_violations(seller_id);
CREATE INDEX IF NOT EXISTS idx_policy_violations_policy ON policy_violations(policy_id);
CREATE INDEX IF NOT EXISTS idx_policy_violations_date ON policy_violations(violation_date);
CREATE INDEX IF NOT EXISTS idx_seller_metrics_seller_date ON seller_metrics(seller_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_audit_logs_seller ON audit_logs(seller_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_actions_seller ON enforcement_actions(seller_id);