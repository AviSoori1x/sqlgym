PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS intent_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    deflectable BOOLEAN NOT NULL DEFAULT 1,
    priority TEXT NOT NULL CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH'))
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    channel TEXT NOT NULL CHECK(channel IN ('WEB', 'MOBILE', 'SMS', 'VOICE')),
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'RESOLVED', 'ESCALATED', 'ABANDONED')),
    primary_intent_id INTEGER REFERENCES intent_categories(id),
    satisfaction_score INTEGER CHECK(satisfaction_score BETWEEN 1 AND 5)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    sender_type TEXT NOT NULL CHECK(sender_type IN ('CUSTOMER', 'BOT', 'AGENT')),
    content TEXT NOT NULL,
    intent_id INTEGER REFERENCES intent_categories(id),
    confidence_score REAL CHECK(confidence_score BETWEEN 0 AND 1),
    sent_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS escalations (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    reason TEXT NOT NULL CHECK(reason IN ('LOW_CONFIDENCE', 'CUSTOMER_REQUEST', 'COMPLEX_ISSUE', 'SENTIMENT_NEGATIVE')),
    escalated_at TEXT NOT NULL,
    agent_id INTEGER,
    resolved_at TEXT,
    UNIQUE(conversation_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_started ON conversations(started_at);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, sent_at);
CREATE INDEX IF NOT EXISTS idx_messages_intent ON messages(intent_id);
CREATE INDEX IF NOT EXISTS idx_escalations_reason ON escalations(reason);
