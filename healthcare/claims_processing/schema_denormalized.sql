-- Denormalized claims processing analytics
-- Trade-off: Pre-calculated claim metrics and denial analysis vs real-time accuracy
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS claims_analytics (
    claim_id INTEGER PRIMARY KEY,
    claim_number TEXT NOT NULL,
    member_id TEXT NOT NULL,
    member_name TEXT NOT NULL,
    plan_code TEXT NOT NULL,
    plan_type TEXT NOT NULL,
    provider_npi TEXT NOT NULL,
    provider_name TEXT NOT NULL,
    provider_specialty TEXT NOT NULL,
    service_date TEXT NOT NULL,
    submission_date TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    place_of_service TEXT NOT NULL,
    total_charged_amount REAL NOT NULL,
    total_allowed_amount REAL NOT NULL,
    total_paid_amount REAL NOT NULL,
    member_responsibility REAL NOT NULL,
    processing_days INTEGER NOT NULL,
    claim_status TEXT NOT NULL,
    denial_count INTEGER NOT NULL,
    appeal_count INTEGER NOT NULL,
    auto_adjudicated BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_claims_metrics (
    date TEXT NOT NULL,
    plan_type TEXT NOT NULL,
    claims_received INTEGER NOT NULL,
    claims_processed INTEGER NOT NULL,
    claims_approved INTEGER NOT NULL,
    claims_denied INTEGER NOT NULL,
    total_charged_amount REAL NOT NULL,
    total_paid_amount REAL NOT NULL,
    avg_processing_time_hours REAL,
    auto_adjudication_rate REAL,
    denial_rate REAL,
    PRIMARY KEY(date, plan_type)
);

CREATE TABLE IF NOT EXISTS provider_performance (
    provider_id INTEGER NOT NULL,
    provider_npi TEXT NOT NULL,
    provider_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    month TEXT NOT NULL,
    claims_submitted INTEGER NOT NULL,
    claims_approved INTEGER NOT NULL,
    claims_denied INTEGER NOT NULL,
    total_charged REAL NOT NULL,
    total_paid REAL NOT NULL,
    avg_approval_time_days REAL,
    denial_rate REAL,
    clean_claim_rate REAL,
    PRIMARY KEY(provider_id, month)
);

CREATE TABLE IF NOT EXISTS denial_analysis (
    denial_code TEXT NOT NULL,
    denial_category TEXT NOT NULL,
    month TEXT NOT NULL,
    denial_count INTEGER NOT NULL,
    total_denied_amount REAL NOT NULL,
    appeals_filed INTEGER NOT NULL,
    appeals_overturned INTEGER NOT NULL,
    avg_time_to_appeal_days REAL,
    top_procedure_codes TEXT, -- JSON array
    PRIMARY KEY(denial_code, month)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_claims_analytics_member ON claims_analytics(member_id);
CREATE INDEX IF NOT EXISTS idx_claims_analytics_provider ON claims_analytics(provider_npi);
CREATE INDEX IF NOT EXISTS idx_claims_analytics_service_date ON claims_analytics(service_date);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_claims_metrics(date);
CREATE INDEX IF NOT EXISTS idx_provider_performance_month ON provider_performance(month);
CREATE INDEX IF NOT EXISTS idx_provider_performance_denial_rate ON provider_performance(denial_rate DESC);
CREATE INDEX IF NOT EXISTS idx_denial_analysis_category ON denial_analysis(denial_category);