-- Denormalized ecommerce funnel and A/B test analytics
-- Trade-off: Pre-calculated funnel metrics and experiment results vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS experiment_results (
    experiment_id INTEGER NOT NULL,
    variant_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    sessions INTEGER NOT NULL,
    conversions INTEGER NOT NULL,
    conversion_rate REAL NOT NULL,
    total_revenue REAL NOT NULL,
    avg_order_value REAL,
    statistical_significance REAL,
    confidence_interval_lower REAL,
    confidence_interval_upper REAL,
    PRIMARY KEY(experiment_id, variant_id, date)
);

CREATE TABLE IF NOT EXISTS funnel_analysis (
    date TEXT NOT NULL,
    experiment_id INTEGER,
    variant_id INTEGER,
    funnel_step_id INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    sessions_entered INTEGER NOT NULL,
    sessions_completed INTEGER NOT NULL,
    completion_rate REAL NOT NULL,
    avg_time_on_step INTEGER,
    drop_off_rate REAL,
    PRIMARY KEY(date, COALESCE(experiment_id, 0), COALESCE(variant_id, 0), funnel_step_id)
);

CREATE TABLE IF NOT EXISTS cohort_funnel_performance (
    cohort_date TEXT NOT NULL,
    traffic_source TEXT NOT NULL,
    device_type TEXT NOT NULL,
    funnel_step_id INTEGER NOT NULL,
    cohort_size INTEGER NOT NULL,
    step_completions INTEGER NOT NULL,
    completion_rate REAL NOT NULL,
    avg_days_to_complete REAL,
    PRIMARY KEY(cohort_date, traffic_source, device_type, funnel_step_id)
);

CREATE TABLE IF NOT EXISTS ab_test_summary (
    experiment_id INTEGER PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    status TEXT NOT NULL,
    total_sessions INTEGER NOT NULL,
    control_conversion_rate REAL,
    treatment_conversion_rate REAL,
    lift_percentage REAL,
    statistical_significance REAL,
    winner_variant_id INTEGER,
    revenue_impact REAL,
    start_date TEXT NOT NULL,
    end_date TEXT
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_experiment_results_date ON experiment_results(date);
CREATE INDEX IF NOT EXISTS idx_experiment_results_experiment ON experiment_results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_funnel_analysis_date ON funnel_analysis(date);
CREATE INDEX IF NOT EXISTS idx_funnel_analysis_step ON funnel_analysis(funnel_step_id);
CREATE INDEX IF NOT EXISTS idx_cohort_performance_date ON cohort_funnel_performance(cohort_date);
CREATE INDEX IF NOT EXISTS idx_ab_summary_status ON ab_test_summary(status);