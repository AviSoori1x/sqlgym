-- Denormalized customer 360 and segmentation analytics
-- Trade-off: Pre-calculated customer metrics and segment performance vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS customer_360_profile (
    customer_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    registration_date TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL,
    days_since_registration INTEGER NOT NULL,
    total_transactions INTEGER NOT NULL,
    total_spent REAL NOT NULL,
    avg_order_value REAL NOT NULL,
    last_transaction_date TEXT,
    days_since_last_purchase INTEGER,
    favorite_channel TEXT,
    preferred_categories TEXT, -- JSON array
    customer_lifetime_value REAL,
    churn_risk_score REAL,
    segment_names TEXT, -- Comma-separated active segments
    engagement_score REAL
);

CREATE TABLE IF NOT EXISTS segment_performance (
    segment_id INTEGER NOT NULL,
    segment_name TEXT NOT NULL,
    month TEXT NOT NULL,
    customer_count INTEGER NOT NULL,
    new_customers INTEGER NOT NULL,
    churned_customers INTEGER NOT NULL,
    total_revenue REAL NOT NULL,
    avg_order_value REAL NOT NULL,
    transaction_frequency REAL,
    engagement_rate REAL,
    retention_rate REAL,
    PRIMARY KEY(segment_id, month)
);

CREATE TABLE IF NOT EXISTS channel_attribution (
    customer_id INTEGER NOT NULL,
    channel TEXT NOT NULL,
    touchpoint_count INTEGER NOT NULL,
    first_touch_date TEXT,
    last_touch_date TEXT,
    attributed_revenue REAL NOT NULL,
    conversion_rate REAL,
    PRIMARY KEY(customer_id, channel)
);

CREATE TABLE IF NOT EXISTS behavioral_cohorts (
    cohort_month TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL,
    cohort_size INTEGER NOT NULL,
    month_1_active INTEGER NOT NULL,
    month_3_active INTEGER NOT NULL,
    month_6_active INTEGER NOT NULL,
    month_12_active INTEGER NOT NULL,
    cumulative_revenue REAL NOT NULL,
    avg_customer_value REAL,
    PRIMARY KEY(cohort_month, acquisition_channel)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_customer_profile_clv ON customer_360_profile(customer_lifetime_value DESC);
CREATE INDEX IF NOT EXISTS idx_customer_profile_churn ON customer_360_profile(churn_risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_segment_performance_month ON segment_performance(month);
CREATE INDEX IF NOT EXISTS idx_channel_attribution_revenue ON channel_attribution(attributed_revenue DESC);
CREATE INDEX IF NOT EXISTS idx_cohorts_month ON behavioral_cohorts(cohort_month);