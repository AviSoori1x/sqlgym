-- Denormalized fund positions summary. Trades off storage duplication for
-- faster analytical scans.
PRAGMA foreign_keys=OFF;
CREATE TABLE IF NOT EXISTS fund_positions (
    fund_id INTEGER NOT NULL,
    fund_name TEXT NOT NULL,
    security_symbol TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    position_date TEXT NOT NULL,
    PRIMARY KEY (fund_id, security_symbol, position_date)
);
