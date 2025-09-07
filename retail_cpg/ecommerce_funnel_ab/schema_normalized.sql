PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    experiment_type TEXT NOT NULL CHECK(experiment_type IN ('A_B', 'MULTIVARIATE', 'SPLIT_URL', 'FUNNEL')),
    status TEXT NOT NULL CHECK(status IN ('DRAFT', 'RUNNING', 'PAUSED', 'COMPLETED', 'CANCELLED')),
    start_date TEXT NOT NULL,
    end_date TEXT,
    traffic_allocation REAL NOT NULL CHECK(traffic_allocation BETWEEN 0 AND 1),
    hypothesis TEXT NOT NULL,
    success_metric TEXT NOT NULL,
    statistical_significance REAL CHECK(statistical_significance BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS variants (
    id INTEGER PRIMARY KEY,
    experiment_id INTEGER NOT NULL REFERENCES experiments(id),
    name TEXT NOT NULL,
    variant_type TEXT NOT NULL CHECK(variant_type IN ('CONTROL', 'TREATMENT')),
    traffic_split REAL NOT NULL CHECK(traffic_split BETWEEN 0 AND 1),
    configuration TEXT, -- JSON with variant-specific settings
    is_winner BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS funnel_steps (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    step_order INTEGER NOT NULL,
    page_url_pattern TEXT NOT NULL,
    step_type TEXT NOT NULL CHECK(step_type IN ('LANDING', 'CATEGORY', 'PRODUCT', 'CART', 'CHECKOUT', 'CONFIRMATION')),
    is_required BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL UNIQUE,
    experiment_id INTEGER REFERENCES experiments(id),
    variant_id INTEGER REFERENCES variants(id),
    start_timestamp TEXT NOT NULL,
    end_timestamp TEXT,
    device_type TEXT NOT NULL CHECK(device_type IN ('DESKTOP', 'MOBILE', 'TABLET')),
    traffic_source TEXT NOT NULL CHECK(traffic_source IN ('ORGANIC', 'PAID', 'DIRECT', 'REFERRAL', 'EMAIL', 'SOCIAL')),
    converted BOOLEAN NOT NULL DEFAULT 0,
    conversion_value REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS funnel_events (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES user_sessions(session_id),
    funnel_step_id INTEGER NOT NULL REFERENCES funnel_steps(id),
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN ('PAGE_VIEW', 'CLICK', 'FORM_SUBMIT', 'ADD_TO_CART', 'PURCHASE')),
    event_data TEXT, -- JSON with event-specific data
    time_on_step INTEGER -- seconds spent on this step
);

CREATE TABLE IF NOT EXISTS conversion_goals (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    goal_type TEXT NOT NULL CHECK(goal_type IN ('REVENUE', 'CONVERSION_RATE', 'ENGAGEMENT', 'RETENTION')),
    target_funnel_step_id INTEGER REFERENCES funnel_steps(id),
    measurement_window_hours INTEGER NOT NULL DEFAULT 24,
    is_primary BOOLEAN NOT NULL DEFAULT 0
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_experiments_dates ON experiments(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_variants_experiment ON variants(experiment_id);
CREATE INDEX IF NOT EXISTS idx_funnel_steps_order ON funnel_steps(step_order);
CREATE INDEX IF NOT EXISTS idx_user_sessions_experiment ON user_sessions(experiment_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_variant ON user_sessions(variant_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_timestamp ON user_sessions(start_timestamp);
CREATE INDEX IF NOT EXISTS idx_funnel_events_session ON funnel_events(session_id);
CREATE INDEX IF NOT EXISTS idx_funnel_events_step ON funnel_events(funnel_step_id);
CREATE INDEX IF NOT EXISTS idx_funnel_events_timestamp ON funnel_events(timestamp);