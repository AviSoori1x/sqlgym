PRAGMA foreign_keys=ON;
CREATE TABLE sites (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE sensors (
    id INTEGER PRIMARY KEY,
    site_id INTEGER NOT NULL REFERENCES sites(id),
    name TEXT NOT NULL,
    unit TEXT NOT NULL CHECK(unit IN ('C','F','kW','psi')),
    status TEXT NOT NULL CHECK(status IN ('ACTIVE','INACTIVE','MAINTENANCE'))
);
CREATE INDEX idx_sensors_site ON sensors(site_id);
CREATE TABLE readings (
    id INTEGER PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensors(id),
    reading_time TEXT NOT NULL,
    value REAL NOT NULL,
    quality TEXT NOT NULL CHECK(quality IN ('GOOD','BAD'))
);
CREATE INDEX idx_readings_sensor_time ON readings(sensor_id, reading_time);
