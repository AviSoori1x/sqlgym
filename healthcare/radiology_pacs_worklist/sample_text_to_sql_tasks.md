# Sample Tasks for ge_healthcare_pacs

## Task 1: sign-off rule
**User**: What is the radiologist sign-off guideline?
**Assistant**: Reference worklist guidelines.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='worklist_guidelines'), '$');
```

## Task 2: assignment lookup
**User**: Assignments for study 1.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM assignments WHERE study_id=1;
```
```sql slow
SELECT * FROM assignments WHERE CAST(study_id AS TEXT)='1';
```
