-- Denormalized loyalty rewards analytics
-- Trade-off: Pre-calculated member metrics and tier performance vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS member_analytics (
    member_id INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL,
    tier_name TEXT NOT NULL,
    enrollment_date TEXT NOT NULL,
    total_points_earned INTEGER NOT NULL,
    current_points_balance INTEGER NOT NULL,
    lifetime_spend REAL NOT NULL,
    total_redemptions INTEGER NOT NULL,
    total_redeemed_points INTEGER NOT NULL,
    avg_redemption_value REAL,
    last_activity_date TEXT,
    days_since_last_activity INTEGER,
    tier_tenure_days INTEGER,
    engagement_score REAL
);

CREATE TABLE IF NOT EXISTS tier_performance (
    tier_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    member_count INTEGER NOT NULL,
    new_members INTEGER NOT NULL,
    churned_members INTEGER NOT NULL,
    total_points_earned INTEGER NOT NULL,
    total_points_redeemed INTEGER NOT NULL,
    avg_spend_per_member REAL,
    redemption_rate REAL,
    retention_rate REAL,
    PRIMARY KEY(tier_id, month)
);

CREATE TABLE IF NOT EXISTS reward_popularity (
    reward_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    redemption_count INTEGER NOT NULL,
    total_points_redeemed INTEGER NOT NULL,
    unique_redeemers INTEGER NOT NULL,
    avg_days_to_redeem REAL,
    tier_distribution TEXT, -- JSON with tier breakdown
    PRIMARY KEY(reward_id, month)
);

CREATE TABLE IF NOT EXISTS points_economy_summary (
    date TEXT PRIMARY KEY,
    total_points_issued INTEGER NOT NULL,
    total_points_redeemed INTEGER NOT NULL,
    points_liability REAL NOT NULL,
    breakage_rate REAL,
    avg_points_per_transaction REAL,
    active_members_with_balance INTEGER NOT NULL
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_member_analytics_tier ON member_analytics(tier_name);
CREATE INDEX IF NOT EXISTS idx_member_analytics_engagement ON member_analytics(engagement_score DESC);
CREATE INDEX IF NOT EXISTS idx_tier_performance_month ON tier_performance(month);
CREATE INDEX IF NOT EXISTS idx_reward_popularity_month ON reward_popularity(month);
CREATE INDEX IF NOT EXISTS idx_points_economy_date ON points_economy_summary(date);