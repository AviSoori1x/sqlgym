# Sample Tasks for siemens_scada_historian

## Task 1: reading count
**User**: How many readings does sensor 1 have?
**Assistant**: Count readings for sensor 1.
```sql
SELECT COUNT(*) FROM readings WHERE sensor_id=1;
```

## Task 2: evidence temperature unit
**User**: What unit should temperature sensors use per specs?
**Assistant**: Query sensor_specs in evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='sensor_specs'), '$.temp_unit');
```

## Task 3: efficiency timestamp filter
**User**: Readings for sensor 2 on 2024-01-02.
**Assistant**: Fast uses equality; slow uses substr.
```sql fast
SELECT value FROM readings WHERE sensor_id=2 AND reading_time='2024-01-02T00:00';
```
```sql slow
SELECT value FROM readings WHERE sensor_id=2 AND substr(reading_time,1,16)='2024-01-02T00:00';
```

## Task 4: evidence pressure max
**User**: What is max allowed pressure?
**Assistant**: Fetch from sensor_specs.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='sensor_specs'), '$.pressure_max');
```

## Task 5: sensors per site
**User**: How many sensors in each site?
**Assistant**: Group sensors by site.
```sql
SELECT site_id, COUNT(*) FROM sensors GROUP BY site_id;
```
