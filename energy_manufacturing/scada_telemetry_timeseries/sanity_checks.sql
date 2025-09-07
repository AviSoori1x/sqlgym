-- 1. sensors reference valid sites
SELECT COUNT(*) FROM sensors s LEFT JOIN sites si ON s.site_id=si.id WHERE si.id IS NULL;
-- 2. readings reference valid sensors
SELECT COUNT(*) FROM readings r LEFT JOIN sensors s ON r.sensor_id=s.id WHERE s.id IS NULL;
-- 3. sensor unit enum
SELECT COUNT(*) FROM sensors WHERE unit NOT IN ('C','F','kW','psi');
-- 4. sensor status enum
SELECT COUNT(*) FROM sensors WHERE status NOT IN ('ACTIVE','INACTIVE','MAINTENANCE');
-- 5. reading quality enum
SELECT COUNT(*) FROM readings WHERE quality NOT IN ('GOOD','BAD');
-- 6. pressure readings within spec
SELECT COUNT(*) FROM readings r JOIN sensors s ON r.sensor_id=s.id
WHERE s.unit='psi' AND r.value > json_extract((SELECT value FROM evidence_kv WHERE key='sensor_specs'), '$.pressure_max');
-- 7. temperature unit matches spec
SELECT COUNT(*) FROM sensors WHERE name LIKE 'Temp%' AND unit != json_extract((SELECT value FROM evidence_kv WHERE key='sensor_specs'), '$.temp_unit');
-- 8. EXPLAIN uses index on readings
EXPLAIN QUERY PLAN SELECT * FROM readings WHERE sensor_id=1 ORDER BY reading_time;
