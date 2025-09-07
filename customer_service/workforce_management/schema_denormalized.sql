-- Denormalized workforce management analytics
-- Trade-off: Pre-calculated utilization and performance metrics vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS agent_performance_summary (
    agent_id INTEGER PRIMARY KEY,
    employee_id TEXT NOT NULL,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    skill_level TEXT NOT NULL,
    total_shifts_scheduled INTEGER NOT NULL,
    shifts_completed INTEGER NOT NULL,
    attendance_rate REAL NOT NULL,
    avg_overtime_minutes REAL,
    total_time_off_days INTEGER NOT NULL,
    skill_count INTEGER NOT NULL,
    avg_skill_proficiency REAL,
    last_shift_date TEXT
);

CREATE TABLE IF NOT EXISTS daily_staffing_metrics (
    date TEXT NOT NULL,
    department TEXT NOT NULL,
    scheduled_agents INTEGER NOT NULL,
    actual_agents INTEGER NOT NULL,
    required_agents INTEGER NOT NULL,
    staffing_variance INTEGER NOT NULL,
    total_hours_worked REAL NOT NULL,
    overtime_hours REAL NOT NULL,
    understaffed_hours INTEGER NOT NULL,
    avg_utilization REAL,
    PRIMARY KEY(date, department)
);

CREATE TABLE IF NOT EXISTS shift_coverage_analysis (
    shift_date TEXT NOT NULL,
    shift_type TEXT NOT NULL,
    required_agents INTEGER NOT NULL,
    scheduled_agents INTEGER NOT NULL,
    confirmed_agents INTEGER NOT NULL,
    coverage_percentage REAL NOT NULL,
    skill_match_score REAL,
    avg_agent_experience_days INTEGER,
    PRIMARY KEY(shift_date, shift_type)
);

CREATE TABLE IF NOT EXISTS skill_demand_forecast (
    skill_name TEXT NOT NULL,
    week_start TEXT NOT NULL,
    current_certified_agents INTEGER NOT NULL,
    expiring_certifications INTEGER NOT NULL,
    projected_demand INTEGER NOT NULL,
    gap_analysis INTEGER NOT NULL,
    training_priority_score INTEGER,
    PRIMARY KEY(skill_name, week_start)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_performance_department ON agent_performance_summary(department);
CREATE INDEX IF NOT EXISTS idx_staffing_date ON daily_staffing_metrics(date);
CREATE INDEX IF NOT EXISTS idx_coverage_date ON shift_coverage_analysis(shift_date);
CREATE INDEX IF NOT EXISTS idx_skill_forecast_week ON skill_demand_forecast(week_start);