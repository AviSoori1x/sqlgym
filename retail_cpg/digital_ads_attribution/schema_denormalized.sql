-- Denormalized digital ads attribution analytics
-- Trade-off: Pre-calculated attribution metrics and campaign performance vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS campaign_performance (
    campaign_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    platform TEXT NOT NULL,
    impressions INTEGER NOT NULL,
    clicks INTEGER NOT NULL,
    conversions INTEGER NOT NULL,
    spend REAL NOT NULL,
    revenue REAL NOT NULL,
    click_through_rate REAL,
    conversion_rate REAL,
    cost_per_click REAL,
    cost_per_conversion REAL,
    return_on_ad_spend REAL,
    PRIMARY KEY(campaign_id, date)
);

CREATE TABLE IF NOT EXISTS attribution_analysis (
    conversion_id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversion_timestamp TEXT NOT NULL,
    conversion_value REAL NOT NULL,
    first_touch_campaign_id INTEGER,
    last_touch_campaign_id INTEGER,
    touchpoint_count INTEGER NOT NULL,
    journey_duration_hours INTEGER,
    attributed_platforms TEXT, -- JSON array
    linear_attribution_value REAL,
    time_decay_attribution_value REAL,
    position_based_attribution_value REAL
);

CREATE TABLE IF NOT EXISTS user_journey_summary (
    user_id TEXT PRIMARY KEY,
    first_touchpoint_date TEXT,
    last_touchpoint_date TEXT,
    total_touchpoints INTEGER NOT NULL,
    unique_campaigns INTEGER NOT NULL,
    unique_platforms INTEGER NOT NULL,
    total_conversions INTEGER NOT NULL,
    total_conversion_value REAL NOT NULL,
    journey_duration_days INTEGER,
    primary_platform TEXT,
    conversion_path TEXT -- Simplified journey representation
);

CREATE TABLE IF NOT EXISTS cross_platform_attribution (
    date TEXT NOT NULL,
    platform_combination TEXT NOT NULL, -- e.g., "GOOGLE_ADS,FACEBOOK"
    assisted_conversions INTEGER NOT NULL,
    direct_conversions INTEGER NOT NULL,
    total_conversion_value REAL NOT NULL,
    avg_journey_length REAL,
    PRIMARY KEY(date, platform_combination)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_campaign_performance_date ON campaign_performance(date);
CREATE INDEX IF NOT EXISTS idx_campaign_performance_platform ON campaign_performance(platform);
CREATE INDEX IF NOT EXISTS idx_attribution_user ON attribution_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_attribution_timestamp ON attribution_analysis(conversion_timestamp);
CREATE INDEX IF NOT EXISTS idx_journey_summary_platform ON user_journey_summary(primary_platform);
CREATE INDEX IF NOT EXISTS idx_cross_platform_date ON cross_platform_attribution(date);