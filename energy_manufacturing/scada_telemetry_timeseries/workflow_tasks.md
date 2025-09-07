# Workflow for scada_telemetry_timeseries

```sql
-- step: hourly_avg
CREATE TEMP TABLE hr AS
SELECT sensor_id, substr(reading_time,1,13) AS hour, AVG(value) AS avg_val FROM readings GROUP BY sensor_id, hour;

-- step: join_assets
-- depends: hourly_avg
SELECT a.name, h.hour, h.avg_val FROM hr h JOIN sensors s ON h.sensor_id=s.id JOIN assets a ON s.asset_id=a.id;
```
