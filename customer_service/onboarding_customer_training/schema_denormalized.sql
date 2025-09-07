-- Denormalized onboarding and training analytics
-- Trade-off: Pre-calculated completion metrics and cohort analysis vs storage and update complexity
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS customer_training_summary (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    company_size TEXT NOT NULL,
    onboarding_tier TEXT NOT NULL,
    total_programs_enrolled INTEGER NOT NULL,
    programs_completed INTEGER NOT NULL,
    programs_in_progress INTEGER NOT NULL,
    overall_completion_rate REAL,
    total_training_hours REAL,
    last_activity_date TEXT,
    onboarding_status TEXT,
    days_to_first_completion INTEGER,
    certification_count INTEGER
);

CREATE TABLE IF NOT EXISTS program_effectiveness (
    program_id INTEGER NOT NULL,
    program_name TEXT NOT NULL,
    program_type TEXT NOT NULL,
    month TEXT NOT NULL,
    total_enrollments INTEGER NOT NULL,
    completions INTEGER NOT NULL,
    completion_rate REAL,
    avg_time_to_complete_days REAL,
    avg_score REAL,
    dropout_rate REAL,
    satisfaction_rating REAL,
    PRIMARY KEY(program_id, month)
);

CREATE TABLE IF NOT EXISTS cohort_analysis (
    cohort_month TEXT NOT NULL,
    onboarding_tier TEXT NOT NULL,
    cohort_size INTEGER NOT NULL,
    day_1_active INTEGER NOT NULL,
    day_7_active INTEGER NOT NULL,
    day_30_active INTEGER NOT NULL,
    day_90_active INTEGER NOT NULL,
    onboarding_completed INTEGER NOT NULL,
    avg_programs_completed REAL,
    time_to_value_days REAL,
    PRIMARY KEY(cohort_month, onboarding_tier)
);

CREATE TABLE IF NOT EXISTS learning_path_analytics (
    customer_id INTEGER NOT NULL,
    learning_path TEXT NOT NULL, -- JSON array of program sequence
    path_length INTEGER NOT NULL,
    current_position INTEGER NOT NULL,
    estimated_completion_date TEXT,
    blockers TEXT, -- JSON array of incomplete prerequisites
    recommended_next TEXT, -- JSON array of suggested programs
    PRIMARY KEY(customer_id)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_training_summary_tier ON customer_training_summary(onboarding_tier);
CREATE INDEX IF NOT EXISTS idx_training_summary_status ON customer_training_summary(onboarding_status);
CREATE INDEX IF NOT EXISTS idx_program_effectiveness_type ON program_effectiveness(program_type);
CREATE INDEX IF NOT EXISTS idx_cohort_month ON cohort_analysis(cohort_month);
CREATE INDEX IF NOT EXISTS idx_learning_path_position ON learning_path_analytics(current_position);