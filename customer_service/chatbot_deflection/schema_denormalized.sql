-- Denormalized chatbot deflection analytics mart
-- Trade-off: Pre-aggregated metrics for fast dashboard queries vs storage overhead and ETL complexity
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS conversation_analytics (
    conversation_id INTEGER PRIMARY KEY,
    customer_email TEXT NOT NULL,
    channel TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_seconds INTEGER,
    status TEXT NOT NULL,
    primary_intent TEXT,
    message_count INTEGER NOT NULL,
    bot_message_count INTEGER NOT NULL,
    customer_message_count INTEGER NOT NULL,
    avg_confidence_score REAL,
    was_escalated BOOLEAN NOT NULL,
    escalation_reason TEXT,
    satisfaction_score INTEGER,
    resolution_type TEXT
);

CREATE TABLE IF NOT EXISTS daily_deflection_metrics (
    date TEXT NOT NULL,
    channel TEXT NOT NULL,
    total_conversations INTEGER NOT NULL,
    deflected_count INTEGER NOT NULL,
    escalated_count INTEGER NOT NULL,
    abandoned_count INTEGER NOT NULL,
    avg_satisfaction REAL,
    avg_duration_seconds INTEGER,
    deflection_rate REAL NOT NULL,
    PRIMARY KEY(date, channel)
);

CREATE TABLE IF NOT EXISTS intent_performance (
    intent_name TEXT NOT NULL,
    month TEXT NOT NULL,
    total_occurrences INTEGER NOT NULL,
    successful_deflections INTEGER NOT NULL,
    escalations INTEGER NOT NULL,
    avg_confidence REAL,
    deflection_success_rate REAL,
    PRIMARY KEY(intent_name, month)
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_conv_analytics_status ON conversation_analytics(status);
CREATE INDEX IF NOT EXISTS idx_conv_analytics_date ON conversation_analytics(started_at);
CREATE INDEX IF NOT EXISTS idx_conv_analytics_intent ON conversation_analytics(primary_intent);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_deflection_metrics(date);
CREATE INDEX IF NOT EXISTS idx_intent_perf_month ON intent_performance(month);
