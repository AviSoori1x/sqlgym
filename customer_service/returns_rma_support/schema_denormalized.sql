-- Denormalized returns and RMA analytics
-- Trade-off: Pre-aggregated return metrics for dashboards vs update complexity
PRAGMA foreign_keys=OFF;

CREATE TABLE IF NOT EXISTS return_analytics (
    rma_id INTEGER PRIMARY KEY,
    customer_email TEXT NOT NULL,
    loyalty_tier TEXT NOT NULL,
    product_sku TEXT NOT NULL,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    order_date TEXT NOT NULL,
    return_request_date TEXT NOT NULL,
    days_since_purchase INTEGER NOT NULL,
    return_reason TEXT NOT NULL,
    current_status TEXT NOT NULL,
    inspection_result TEXT,
    refund_amount REAL,
    original_amount REAL NOT NULL,
    processing_days INTEGER,
    is_warranty_return BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_return_metrics (
    date TEXT NOT NULL,
    total_requests INTEGER NOT NULL,
    approved_count INTEGER NOT NULL,
    rejected_count INTEGER NOT NULL,
    pending_count INTEGER NOT NULL,
    total_refund_amount REAL NOT NULL,
    avg_processing_days REAL,
    return_rate REAL NOT NULL,
    PRIMARY KEY(date)
);

CREATE TABLE IF NOT EXISTS product_return_analysis (
    product_sku TEXT NOT NULL,
    month TEXT NOT NULL,
    units_sold INTEGER NOT NULL,
    units_returned INTEGER NOT NULL,
    return_rate REAL NOT NULL,
    primary_return_reason TEXT,
    avg_days_to_return REAL,
    total_loss REAL NOT NULL,
    quality_score REAL,
    PRIMARY KEY(product_sku, month)
);

CREATE TABLE IF NOT EXISTS customer_return_behavior (
    customer_id INTEGER PRIMARY KEY,
    customer_email TEXT NOT NULL,
    loyalty_tier TEXT NOT NULL,
    total_orders INTEGER NOT NULL,
    total_returns INTEGER NOT NULL,
    return_rate REAL NOT NULL,
    avg_return_value REAL,
    preferred_return_method TEXT,
    fraud_risk_score INTEGER CHECK(fraud_risk_score BETWEEN 0 AND 100),
    last_return_date TEXT
);

-- Indexes for analytical queries
CREATE INDEX IF NOT EXISTS idx_return_analytics_date ON return_analytics(return_request_date);
CREATE INDEX IF NOT EXISTS idx_return_analytics_category ON return_analytics(product_category);
CREATE INDEX IF NOT EXISTS idx_return_analytics_reason ON return_analytics(return_reason);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_return_metrics(date);
CREATE INDEX IF NOT EXISTS idx_product_analysis_rate ON product_return_analysis(return_rate DESC);