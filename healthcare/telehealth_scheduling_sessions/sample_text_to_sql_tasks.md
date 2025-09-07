# Sample Tasks for telehealth_scheduling_sessions

## Task 1: join policy
**User**: What is the join policy for sessions?
**Assistant**: Use telehealth policy evidence.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='telehealth_policy'), '$');
```

## Task 2: session lookup
**User**: Sessions for appointment 1.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM sessions WHERE appointment_id=1;
```
```sql slow
SELECT * FROM sessions WHERE CAST(appointment_id AS TEXT)='1';
```
