# Sample Tasks for humana_care_mgmt

## Task 1: follow-up policy
**User**: What is the follow-up rule?
**Assistant**: Consult guidelines via evidence.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='guidelines'), '$');
```

## Task 2: intervention search
**User**: Interventions for member 1.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM interventions WHERE enrollment_id=1;
```
```sql slow
SELECT * FROM interventions WHERE CAST(enrollment_id AS TEXT)='1';
```
