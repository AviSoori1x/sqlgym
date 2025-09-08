# Sample Tasks for cdc_health_registries

## Task 1: enrollment rule
**User**: What is the registry enrollment policy?
**Assistant**: Reference registry rules.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='registry_rules'), '$');
```

## Task 2: metric lookup
**User**: Metrics for patient 1.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM metrics WHERE patient_id=1;
```
```sql slow
SELECT * FROM metrics WHERE CAST(patient_id AS TEXT)='1';
```
