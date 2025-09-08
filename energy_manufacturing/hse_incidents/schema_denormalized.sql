-- Chevron Safety Management Denormalized Analytics
-- Trade-off: Pre-calculated safety metrics and trend analysis vs real-time accuracy
PRAGMA foreign_keys=OFF;

-- Safety metrics summary by department
CREATE TABLE IF NOT EXISTS safety_metrics_summary (
    department TEXT PRIMARY KEY,
    total_incidents INTEGER NOT NULL,
    minor_incidents INTEGER NOT NULL,
    moderate_incidents INTEGER NOT NULL,
    major_incidents INTEGER NOT NULL,
    catastrophic_incidents INTEGER NOT NULL,
    total_injury_days INTEGER NOT NULL,
    ltir REAL NOT NULL,  -- Lost Time Injury Rate
    trir REAL NOT NULL,  -- Total Recordable Injury Rate
    near_miss_count INTEGER NOT NULL,
    safety_score REAL NOT NULL,
    last_incident_date TEXT,
    days_since_last_incident INTEGER NOT NULL
);

-- Monthly safety trends
CREATE TABLE IF NOT EXISTS monthly_safety_trends (
    year_month TEXT PRIMARY KEY,
    total_incidents INTEGER NOT NULL,
    incident_rate REAL NOT NULL,
    severity_index REAL NOT NULL,
    corrective_actions_completed INTEGER NOT NULL,
    corrective_actions_overdue INTEGER NOT NULL,
    training_hours INTEGER NOT NULL,
    safety_investment REAL NOT NULL
);

-- Analytical indexes
CREATE INDEX IF NOT EXISTS idx_safety_summary_score ON safety_metrics_summary(safety_score);
CREATE INDEX IF NOT EXISTS idx_monthly_trends_date ON monthly_safety_trends(year_month);
