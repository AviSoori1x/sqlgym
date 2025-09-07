PRAGMA foreign_keys=ON;
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    UNIQUE(customer_id, started_at)
);
CREATE INDEX idx_conv_customer ON conversations(customer_id);
CREATE TABLE intents (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE turns (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    speaker TEXT NOT NULL CHECK(speaker IN ('AGENT','CUSTOMER')),
    intent_id INTEGER REFERENCES intents(id),
    utterance TEXT NOT NULL,
    ts TEXT NOT NULL
);
CREATE INDEX idx_turn_conv_time ON turns(conversation_id, ts);
CREATE INDEX idx_turn_intent ON turns(intent_id);
CREATE TABLE resolutions (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    resolved INTEGER NOT NULL CHECK(resolved IN (0,1)),
    resolution_time TEXT
);
CREATE INDEX idx_res_conv ON resolutions(conversation_id);
