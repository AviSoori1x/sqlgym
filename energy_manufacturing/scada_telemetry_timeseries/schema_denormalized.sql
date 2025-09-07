PRAGMA foreign_keys=OFF;
CREATE TABLE sensor_readings AS
SELECT r.id AS reading_id, a.name AS asset_name, s.type, r.reading_time, r.value
FROM readings r
JOIN sensors s ON r.sensor_id=s.id
JOIN assets a ON s.asset_id=a.id;
