# Sample Tasks for ehr_encounters_orders

## Task 1: evidence lab codes
**User**: Where are lab code hints?
**Assistant**: Read lab_codes.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='lab_codes'), '$');
```

## Task 2: efficiency result lookup
**User**: Results for order 10 after 2024-01-01.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM results WHERE order_id=10 AND result_time>'2024-01-01';
```
```sql slow
SELECT * FROM results WHERE order_id=10 AND substr(result_time,1,10)>'2024-01-01';
```
