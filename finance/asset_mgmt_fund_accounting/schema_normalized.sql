PRAGMA foreign_keys=ON;
CREATE TABLE funds (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    domicile TEXT NOT NULL CHECK(domicile IN ('US','EU','APAC')),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE','INACTIVE'))
);
CREATE TABLE investors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tier TEXT NOT NULL CHECK(tier IN ('RETAIL','INSTITUTIONAL')),
    risk_profile TEXT NOT NULL CHECK(risk_profile IN ('LOW','MED','HIGH'))
);
CREATE TABLE securities (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('EQUITY','BOND','CASH')),
    currency TEXT NOT NULL CHECK(currency IN ('USD','EUR','JPY'))
);
CREATE TABLE holdings (
    id INTEGER PRIMARY KEY,
    fund_id INTEGER NOT NULL REFERENCES funds(id),
    security_id INTEGER NOT NULL REFERENCES securities(id),
    quantity INTEGER NOT NULL CHECK(quantity>0),
    position_date TEXT NOT NULL
);
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    fund_id INTEGER NOT NULL REFERENCES funds(id),
    investor_id INTEGER NOT NULL REFERENCES investors(id),
    subscribed_at TEXT NOT NULL
);
-- Indexes created post-load for performance
-- CREATE INDEX idx_funds_status ON funds(status);
-- CREATE INDEX idx_investors_tier ON investors(tier);
-- CREATE INDEX idx_securities_type ON securities(type);
-- CREATE INDEX idx_holdings_fund_date ON holdings(fund_id, position_date);
-- CREATE INDEX idx_subs_fund_inv ON subscriptions(fund_id, investor_id);
