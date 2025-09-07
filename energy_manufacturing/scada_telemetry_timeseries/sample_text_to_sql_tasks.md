# Sample Tasks for scada_telemetry_timeseries

## Task 1: temperature readings
**User**: Fetch temperature readings for sensor 1 on 2024-01-01.
**Assistant**: Filter readings.
```sql
SELECT * FROM readings WHERE sensor_id=1 AND reading_time LIKE '2024-01-01%';
```

## Task 2: evidence shift calendar
**User**: What are the shifts?
**Assistant**: Read shift_calendar.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='shift_calendar'), '$');
```

## Task 3: efficiency reading lookup
**User**: Readings for sensor 2 at a timestamp.
**Assistant**: Fast uses index.
```sql fast
SELECT value FROM readings WHERE sensor_id=2 AND reading_time='2024-01-02T00:00:00';
```
```sql slow
SELECT value FROM readings WHERE sensor_id=2 AND substr(reading_time,1,19)='2024-01-02T00:00:00';
```
