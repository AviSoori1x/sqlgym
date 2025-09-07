PRAGMA foreign_keys=OFF;
CREATE TABLE IF NOT EXISTS sensor_daily_avg (
    day TEXT NOT NULL,
    sensor_id INTEGER NOT NULL,
    avg_value REAL NOT NULL,
    PRIMARY KEY(day, sensor_id)
);
CREATE INDEX idx_sda_day ON sensor_daily_avg(day);
