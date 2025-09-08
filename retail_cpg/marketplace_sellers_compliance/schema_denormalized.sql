-- Denormalized marketplace sellers compliance analytics
-- Trade-off: Pre-calculated compliance metrics and seller performance vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS seller_compliance_summary (
    seller_id INTEGER PRIMARY KEY,
    seller_name TEXT NOT NULL,
    business_type TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    performance_rating REAL NOT NULL,
    total_violations INTEGER NOT NULL,
    critical_violations INTEGER NOT NULL,
    open_violations INTEGER NOT NULL,
    last_violation_date TEXT,
    compliance_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    enforcement_actions_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_compliance_metrics (
    date TEXT NOT NULL,
    new_violations INTEGER NOT NULL,
    resolved_violations INTEGER NOT NULL,
    auto_detected_violations INTEGER NOT NULL,
    reported_violations INTEGER NOT NULL,
    avg_resolution_time_days REAL,
    compliance_rate REAL NOT NULL,
    PRIMARY KEY(date)
);

CREATE TABLE IF NOT EXISTS policy_violation_trends (
    policy_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    violation_count INTEGER NOT NULL,
    unique_violators INTEGER NOT NULL,
    total_penalty_amount REAL NOT NULL,
    avg_resolution_days REAL,
    repeat_violator_rate REAL,
    PRIMARY KEY(policy_id, month)
);

CREATE TABLE IF NOT EXISTS seller_performance_metrics (
    seller_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    avg_order_count INTEGER NOT NULL,
    avg_cancellation_rate REAL NOT NULL,
    avg_return_rate REAL NOT NULL,
    avg_late_shipment_rate REAL NOT NULL,
    avg_customer_satisfaction REAL,
    performance_trend TEXT NOT NULL,
    PRIMARY KEY(seller_id, month)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_seller_compliance_risk ON seller_compliance_summary(risk_level);
CREATE INDEX IF NOT EXISTS idx_seller_compliance_rating ON seller_compliance_summary(performance_rating DESC);
CREATE INDEX IF NOT EXISTS idx_daily_compliance_date ON daily_compliance_metrics(date);
CREATE INDEX IF NOT EXISTS idx_violation_trends_month ON policy_violation_trends(month);
CREATE INDEX IF NOT EXISTS idx_seller_performance_month ON seller_performance_metrics(month);