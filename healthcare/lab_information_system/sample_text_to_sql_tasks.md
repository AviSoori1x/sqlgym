# Sample Tasks for lab_information_system

## Task 1: specimen policy
**User**: How soon must specimens be processed?
**Assistant**: Consult protocol evidence.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='collection_protocol'), '$');
```

## Task 2: order lookup
**User**: Orders on Jan 01.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM lab_orders WHERE ordered_at='2024-01-01';
```
```sql slow
SELECT * FROM lab_orders WHERE substr(ordered_at,1,10)='2024-01-01';
```
