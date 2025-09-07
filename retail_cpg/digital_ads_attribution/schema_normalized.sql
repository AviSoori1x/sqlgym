PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    platform TEXT NOT NULL CHECK(platform IN ('GOOGLE_ADS', 'FACEBOOK', 'INSTAGRAM', 'TWITTER', 'TIKTOK', 'LINKEDIN', 'AMAZON')),
    campaign_type TEXT NOT NULL CHECK(campaign_type IN ('SEARCH', 'DISPLAY', 'VIDEO', 'SHOPPING', 'SOCIAL', 'RETARGETING')),
    objective TEXT NOT NULL CHECK(objective IN ('AWARENESS', 'TRAFFIC', 'ENGAGEMENT', 'LEADS', 'SALES', 'RETENTION')),
    start_date TEXT NOT NULL,
    end_date TEXT,
    budget REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('DRAFT', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED'))
);

CREATE TABLE IF NOT EXISTS ad_groups (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id),
    name TEXT NOT NULL,
    targeting_criteria TEXT, -- JSON with audience targeting
    bid_strategy TEXT NOT NULL CHECK(bid_strategy IN ('CPC', 'CPM', 'CPA', 'ROAS', 'MAXIMIZE_CLICKS')),
    max_bid REAL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'PAUSED', 'REMOVED'))
);

CREATE TABLE IF NOT EXISTS ads (
    id INTEGER PRIMARY KEY,
    ad_group_id INTEGER NOT NULL REFERENCES ad_groups(id),
    creative_id TEXT NOT NULL,
    ad_type TEXT NOT NULL CHECK(ad_type IN ('TEXT', 'IMAGE', 'VIDEO', 'CAROUSEL', 'COLLECTION', 'DYNAMIC')),
    headline TEXT,
    description TEXT,
    call_to_action TEXT CHECK(call_to_action IN ('LEARN_MORE', 'SHOP_NOW', 'SIGN_UP', 'DOWNLOAD', 'CONTACT_US')),
    landing_page_url TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'PAUSED', 'DISAPPROVED', 'REMOVED'))
);

CREATE TABLE IF NOT EXISTS touchpoints (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL, -- Anonymous or known user identifier
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    platform TEXT NOT NULL CHECK(platform IN ('GOOGLE_ADS', 'FACEBOOK', 'INSTAGRAM', 'TWITTER', 'TIKTOK', 'LINKEDIN', 'AMAZON', 'ORGANIC')),
    campaign_id INTEGER REFERENCES campaigns(id),
    ad_group_id INTEGER REFERENCES ad_groups(id),
    ad_id INTEGER REFERENCES ads(id),
    interaction_type TEXT NOT NULL CHECK(interaction_type IN ('IMPRESSION', 'CLICK', 'VIEW', 'ENGAGEMENT', 'CONVERSION')),
    cost REAL DEFAULT 0,
    revenue REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS conversions (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversion_timestamp TEXT NOT NULL,
    conversion_type TEXT NOT NULL CHECK(conversion_type IN ('PURCHASE', 'SIGNUP', 'LEAD', 'DOWNLOAD', 'SUBSCRIBE', 'ADD_TO_CART')),
    conversion_value REAL NOT NULL,
    order_id TEXT,
    attribution_window_hours INTEGER NOT NULL DEFAULT 168 -- 7 days
);

CREATE TABLE IF NOT EXISTS attribution_models (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    model_type TEXT NOT NULL CHECK(model_type IN ('FIRST_TOUCH', 'LAST_TOUCH', 'LINEAR', 'TIME_DECAY', 'POSITION_BASED', 'DATA_DRIVEN')),
    parameters TEXT, -- JSON configuration
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_campaigns_platform ON campaigns(platform);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_dates ON campaigns(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_ad_groups_campaign ON ad_groups(campaign_id);
CREATE INDEX IF NOT EXISTS idx_ads_ad_group ON ads(ad_group_id);
CREATE INDEX IF NOT EXISTS idx_touchpoints_user ON touchpoints(user_id);
CREATE INDEX IF NOT EXISTS idx_touchpoints_timestamp ON touchpoints(timestamp);
CREATE INDEX IF NOT EXISTS idx_touchpoints_campaign ON touchpoints(campaign_id);
CREATE INDEX IF NOT EXISTS idx_conversions_user ON conversions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversions_timestamp ON conversions(conversion_timestamp);