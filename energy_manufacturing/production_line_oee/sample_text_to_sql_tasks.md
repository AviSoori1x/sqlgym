# Sample Tasks for ford_manufacturing_ops

## Task 1: downtime events
**User**: Show downtime for run 5.
**Assistant**: Filter downtime_events.
```sql
SELECT minutes, reason FROM downtime_events WHERE line_run_id=5;
```

## Task 2: evidence formula
**User**: How is OEE calculated?
**Assistant**: Read oee_formula.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='oee_formula'), '$');
```

## Task 3: efficiency run lookup
**User**: Runs for line 2 on date 2024-01-07.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM line_runs WHERE line_id=2 AND run_date='2024-01-07';
```
```sql slow
SELECT * FROM line_runs WHERE line_id=2 AND substr(run_date,1,10)='2024-01-07';
```
