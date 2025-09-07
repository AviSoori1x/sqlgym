PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT,
    gender TEXT CHECK(gender IN ('M', 'F', 'OTHER', 'PREFER_NOT_SAY')),
    registration_date TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL CHECK(acquisition_channel IN ('ORGANIC', 'PAID_SEARCH', 'SOCIAL', 'EMAIL', 'REFERRAL', 'DIRECT')),
    preferred_store_id INTEGER,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'INACTIVE', 'CHURNED', 'SUSPENDED'))
);

CREATE TABLE IF NOT EXISTS customer_segments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    segment_type TEXT NOT NULL CHECK(segment_type IN ('DEMOGRAPHIC', 'BEHAVIORAL', 'VALUE', 'LIFECYCLE')),
    criteria_json TEXT NOT NULL, -- JSON defining segment rules
    priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 10)
);

CREATE TABLE IF NOT EXISTS customer_segment_assignments (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    segment_id INTEGER NOT NULL REFERENCES customer_segments(id),
    assigned_date TEXT NOT NULL,
    confidence_score REAL CHECK(confidence_score BETWEEN 0 AND 1),
    expires_date TEXT,
    UNIQUE(customer_id, segment_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    transaction_date TEXT NOT NULL,
    channel TEXT NOT NULL CHECK(channel IN ('STORE', 'ONLINE', 'MOBILE_APP', 'PHONE', 'CATALOG')),
    store_id INTEGER,
    total_amount REAL NOT NULL,
    discount_amount REAL DEFAULT 0,
    payment_method TEXT NOT NULL CHECK(payment_method IN ('CASH', 'CREDIT', 'DEBIT', 'DIGITAL_WALLET', 'GIFT_CARD'))
);

CREATE TABLE IF NOT EXISTS customer_interactions (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    interaction_date TEXT NOT NULL,
    interaction_type TEXT NOT NULL CHECK(interaction_type IN ('PURCHASE', 'BROWSE', 'SUPPORT', 'REVIEW', 'SOCIAL_SHARE', 'EMAIL_OPEN', 'EMAIL_CLICK')),
    channel TEXT NOT NULL CHECK(channel IN ('WEB', 'MOBILE', 'STORE', 'EMAIL', 'SOCIAL', 'CALL_CENTER')),
    interaction_value TEXT, -- JSON with type-specific data
    session_id TEXT
);

CREATE TABLE IF NOT EXISTS customer_preferences (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    preference_type TEXT NOT NULL CHECK(preference_type IN ('CATEGORY', 'BRAND', 'COMMUNICATION', 'DELIVERY')),
    preference_value TEXT NOT NULL,
    confidence_score REAL CHECK(confidence_score BETWEEN 0 AND 1),
    updated_date TEXT NOT NULL,
    UNIQUE(customer_id, preference_type, preference_value)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_registration ON customers(registration_date);
CREATE INDEX IF NOT EXISTS idx_segment_assignments_customer ON customer_segment_assignments(customer_id);
CREATE INDEX IF NOT EXISTS idx_segment_assignments_segment ON customer_segment_assignments(segment_id);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_interactions_customer_date ON customer_interactions(customer_id, interaction_date);
CREATE INDEX IF NOT EXISTS idx_preferences_customer ON customer_preferences(customer_id);