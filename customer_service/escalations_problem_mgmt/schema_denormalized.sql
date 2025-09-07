-- Denormalized escalation and problem management analytics
-- Trade-off: Pre-aggregated metrics for management dashboards vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS issue_analytics (
    issue_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    customer_tier TEXT NOT NULL,
    account_value INTEGER NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    resolution_hours INTEGER,
    total_escalations INTEGER NOT NULL,
    escalation_chain TEXT, -- JSON array of agent names
    final_resolver_name TEXT,
    final_resolver_level TEXT,
    has_problem_record BOOLEAN NOT NULL,
    affected_customers INTEGER
);

CREATE TABLE IF NOT EXISTS daily_escalation_metrics (
    date TEXT NOT NULL,
    department TEXT NOT NULL,
    total_issues INTEGER NOT NULL,
    escalated_issues INTEGER NOT NULL,
    escalation_rate REAL NOT NULL,
    avg_escalations_per_issue REAL,
    critical_issues INTEGER NOT NULL,
    sla_breaches INTEGER NOT NULL,
    PRIMARY KEY(date, department)
);

CREATE TABLE IF NOT EXISTS agent_performance (
    agent_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    skill_level TEXT NOT NULL,
    issues_handled INTEGER NOT NULL,
    issues_resolved INTEGER NOT NULL,
    issues_escalated_up INTEGER NOT NULL,
    issues_received_from_escalation INTEGER NOT NULL,
    resolution_rate REAL,
    avg_resolution_hours REAL,
    customer_tier_distribution TEXT, -- JSON object
    PRIMARY KEY(agent_id, month)
);

CREATE TABLE IF NOT EXISTS problem_impact_summary (
    problem_id INTEGER PRIMARY KEY,
    problem_statement TEXT NOT NULL,
    category TEXT NOT NULL,
    root_cause TEXT,
    total_affected_customers INTEGER NOT NULL,
    total_related_issues INTEGER NOT NULL,
    avg_resolution_hours REAL,
    revenue_at_risk INTEGER,
    created_at TEXT NOT NULL,
    time_to_root_cause_hours INTEGER,
    time_to_resolution_hours INTEGER
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_issue_analytics_date ON issue_analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_issue_analytics_tier ON issue_analytics(customer_tier);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_escalation_metrics(date);
CREATE INDEX IF NOT EXISTS idx_agent_performance_month ON agent_performance(month);
CREATE INDEX IF NOT EXISTS idx_problem_impact_customers ON problem_impact_summary(total_affected_customers DESC);