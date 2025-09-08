# Sample Tasks for pfizer_clinical_trials

## Task 1: reporting rule
**User**: What is the AE reporting timeline?
**Assistant**: Read protocol via evidence.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='protocol'), '$');
```

## Task 2: visit search
**User**: Visits in TrialA.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM site_visits WHERE trial_id=1;
```
```sql slow
SELECT * FROM site_visits WHERE CAST(trial_id AS TEXT)='1';
```
