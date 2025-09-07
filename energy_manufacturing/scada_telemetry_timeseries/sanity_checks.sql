-- average reading per sensor
SELECT sensor_id, AVG(value) FROM readings GROUP BY sensor_id;

-- join assets
SELECT a.name, COUNT(r.id) FROM readings r JOIN sensors s ON r.sensor_id=s.id JOIN assets a ON s.asset_id=a.id GROUP BY a.id;

-- readings in shift
SELECT COUNT(*) FROM readings WHERE reading_time BETWEEN '2024-01-01' AND '2024-01-02';
