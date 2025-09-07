PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    segment TEXT NOT NULL CHECK(segment IN ('ENTERPRISE', 'SMB', 'CONSUMER')),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS touchpoints (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    channel TEXT NOT NULL CHECK(channel IN ('EMAIL', 'SMS', 'IN_APP', 'PHONE', 'WEB'))
);

CREATE TABLE IF NOT EXISTS surveys (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    touchpoint_id INTEGER NOT NULL REFERENCES touchpoints(id),
    survey_type TEXT NOT NULL CHECK(survey_type IN ('CSAT', 'NPS', 'CES')),
    sent_at TEXT NOT NULL,
    responded_at TEXT,
    score INTEGER CHECK(score BETWEEN 1 AND 10),
    comment TEXT,
    status TEXT NOT NULL CHECK(status IN ('SENT', 'OPENED', 'COMPLETED', 'EXPIRED'))
);

CREATE TABLE IF NOT EXISTS survey_triggers (
    id INTEGER PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(id),
    trigger_event TEXT NOT NULL CHECK(trigger_event IN ('PURCHASE', 'SUPPORT_CLOSE', 'ONBOARDING', 'RENEWAL', 'CANCELLATION')),
    event_timestamp TEXT NOT NULL,
    context_data TEXT
);

CREATE TABLE IF NOT EXISTS follow_ups (
    id INTEGER PRIMARY KEY,
    survey_id INTEGER NOT NULL REFERENCES surveys(id),
    action_type TEXT NOT NULL CHECK(action_type IN ('CALLBACK', 'EMAIL', 'DISCOUNT', 'ESCALATION', 'NONE')),
    assigned_to TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    outcome TEXT,
    UNIQUE(survey_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_surveys_customer ON surveys(customer_id);
CREATE INDEX IF NOT EXISTS idx_surveys_type ON surveys(survey_type);
CREATE INDEX IF NOT EXISTS idx_surveys_sent ON surveys(sent_at);
CREATE INDEX IF NOT EXISTS idx_surveys_status ON surveys(status);
CREATE INDEX IF NOT EXISTS idx_surveys_score ON surveys(score);
CREATE INDEX IF NOT EXISTS idx_triggers_event ON survey_triggers(trigger_event);