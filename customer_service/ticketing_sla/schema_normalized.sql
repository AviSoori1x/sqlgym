PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS service_levels (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    response_hours INTEGER NOT NULL CHECK(response_hours>0)
);
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    agent_id INTEGER REFERENCES agents(id),
    sl_id INTEGER NOT NULL REFERENCES service_levels(id),
    status TEXT NOT NULL CHECK(status IN ('OPEN','PENDING','CLOSED')),
    priority TEXT NOT NULL CHECK(priority IN ('LOW','MED','HIGH')),
    opened_at TEXT NOT NULL,
    closed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_opened ON tickets(opened_at);
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id),
    agent_id INTEGER NOT NULL REFERENCES agents(id),
    note TEXT NOT NULL,
    interacted_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_interactions_ticket_time ON interactions(ticket_id, interacted_at);
