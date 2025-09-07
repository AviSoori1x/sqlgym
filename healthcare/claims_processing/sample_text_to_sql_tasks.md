# Sample Tasks for claims_processing

## Task 1: evidence coding
**User**: Where are coding guidelines?
**Assistant**: Read coding_guidelines.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='coding_guidelines'), '$');
```

## Task 2: efficiency claim lookup
**User**: Claims for patient 2 on 2024-02-01.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM claims WHERE patient_id=2 AND claim_date='2024-02-01';
```
```sql slow
SELECT * FROM claims WHERE patient_id=2 AND substr(claim_date,1,10)='2024-02-01';
```
