-- Denormalized CSAT/NPS analytics mart
-- Trade-off: Pre-calculated metrics for dashboard performance vs real-time accuracy and storage overhead
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS survey_analytics (
    survey_id INTEGER PRIMARY KEY,
    customer_email TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    touchpoint_name TEXT NOT NULL,
    channel TEXT NOT NULL,
    survey_type TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    responded_at TEXT,
    response_time_hours INTEGER,
    score INTEGER,
    score_category TEXT, -- Promoter/Passive/Detractor for NPS, Satisfied/Neutral/Dissatisfied for CSAT
    comment TEXT,
    comment_sentiment TEXT,
    trigger_event TEXT,
    follow_up_action TEXT,
    follow_up_outcome TEXT
);

CREATE TABLE IF NOT EXISTS daily_metrics (
    date TEXT NOT NULL,
    survey_type TEXT NOT NULL,
    total_sent INTEGER NOT NULL,
    total_responses INTEGER NOT NULL,
    response_rate REAL NOT NULL,
    avg_score REAL,
    nps_score INTEGER, -- For NPS type only
    csat_percentage REAL, -- For CSAT type only
    PRIMARY KEY(date, survey_type)
);

CREATE TABLE IF NOT EXISTS segment_scores (
    segment TEXT NOT NULL,
    survey_type TEXT NOT NULL,
    month TEXT NOT NULL,
    total_surveys INTEGER NOT NULL,
    responses INTEGER NOT NULL,
    avg_score REAL,
    score_trend REAL, -- Month-over-month change
    top_positive_driver TEXT,
    top_negative_driver TEXT,
    PRIMARY KEY(segment, survey_type, month)
);

CREATE TABLE IF NOT EXISTS touchpoint_performance (
    touchpoint_name TEXT NOT NULL,
    quarter TEXT NOT NULL,
    total_surveys INTEGER NOT NULL,
    avg_csat REAL,
    avg_nps REAL,
    response_rate REAL,
    follow_up_rate REAL,
    issue_resolution_rate REAL,
    PRIMARY KEY(touchpoint_name, quarter)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_survey_analytics_date ON survey_analytics(sent_at);
CREATE INDEX IF NOT EXISTS idx_survey_analytics_type ON survey_analytics(survey_type);
CREATE INDEX IF NOT EXISTS idx_survey_analytics_segment ON survey_analytics(customer_segment);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);
CREATE INDEX IF NOT EXISTS idx_segment_scores_month ON segment_scores(month);