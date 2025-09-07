# Sample Tasks for ehr_encounters_orders

## Task 1: open orders
**User**: List placed orders for encounter 3.
**Assistant**: Filter orders by encounter and status.
```sql
SELECT id FROM orders WHERE encounter_id=3 AND status='PLACED';
```

## Task 2: evidence lab codes
**User**: Where are lab code hints?
**Assistant**: Read lab_codes.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='lab_codes'), '$');
```

## Task 3: efficiency result lookup
**User**: Results for order 10 after 2024-01-01.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM results WHERE order_id=10 AND result_time>'2024-01-01';
```
```sql slow
SELECT * FROM results WHERE order_id=10 AND substr(result_time,1,10)>'2024-01-01';
```
