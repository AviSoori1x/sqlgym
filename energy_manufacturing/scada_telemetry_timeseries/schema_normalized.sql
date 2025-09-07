PRAGMA foreign_keys=ON;
CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE sensors (
    id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    type TEXT NOT NULL CHECK(type IN ('TEMP','PRESSURE','FLOW'))
);
CREATE INDEX idx_sensor_asset ON sensors(asset_id);
CREATE TABLE readings (
    id INTEGER PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensors(id),
    reading_time TEXT NOT NULL,
    value NUMERIC NOT NULL
);
CREATE INDEX idx_reading_sensor_time ON readings(sensor_id, reading_time);
CREATE TABLE shift_calendar (
    id INTEGER PRIMARY KEY,
    day TEXT NOT NULL,
    shift TEXT NOT NULL
);
