-- Denormalized ticket daily counts.
PRAGMA foreign_keys=OFF;
CREATE TABLE IF NOT EXISTS ticket_daily_counts (
    day TEXT NOT NULL,
    status TEXT NOT NULL,
    cnt INTEGER NOT NULL,
    PRIMARY KEY(day, status)
);
CREATE INDEX IF NOT EXISTS idx_tdc_day ON ticket_daily_counts(day);
