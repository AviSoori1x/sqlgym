# Workflow Tasks

## Task: sensor rolling avg
```sql
-- step: raw
CREATE TEMP TABLE raw AS
SELECT sensor_id, reading_time, value FROM readings;
```
```sql
-- step: roll
-- depends: raw
CREATE TEMP TABLE roll AS
SELECT sensor_id, AVG(value) OVER (PARTITION BY sensor_id ORDER BY reading_time ROWS 4 PRECEDING) avg_v
FROM raw;
```
```sql
-- step: final
-- depends: roll
SELECT * FROM roll WHERE avg_v>50;
```

## Task: downtime summary
```sql
-- step: base
CREATE TEMP TABLE base AS
SELECT line_id, start_time, end_time FROM downtime_events;
```
```sql
-- step: duration
-- depends: base
SELECT line_id, (julianday(end_time)-julianday(start_time))*24 AS hours FROM base;
```

## Task: sensor daily avg
```sql
-- step: raw
CREATE TEMP TABLE raw AS
SELECT sensor_id, reading_time, value FROM readings;
```
```sql
-- step: day
-- depends: raw
CREATE TEMP TABLE day AS
SELECT sensor_id, substr(reading_time,1,10) AS day, value FROM raw;
```
```sql
-- step: agg
-- depends: day
SELECT sensor_id, day, AVG(value) avg_v FROM day GROUP BY sensor_id, day;
```

