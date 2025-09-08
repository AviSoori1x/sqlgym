# Sample Tasks for cvs_eprescribe

## Task 1: transmission rule
**User**: When must e-prescriptions be sent?
**Assistant**: Read policy evidence.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='eprescribing_policy'), '$');
```

## Task 2: fill lookup
**User**: Fills for prescription 1.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM fills WHERE prescription_id=1;
```
```sql slow
SELECT * FROM fills WHERE CAST(prescription_id AS TEXT)='1';
```
