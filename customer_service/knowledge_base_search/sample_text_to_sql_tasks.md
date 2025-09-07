# Sample Tasks for knowledge_base_search

## Task 1: views for article
**User**: How many views did article 3 get?
**Assistant**: Count views.
```sql
SELECT COUNT(*) FROM article_views WHERE article_id=3;
```

## Task 2: evidence synonyms
**User**: What synonyms are defined?
**Assistant**: Read synonyms.json via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='synonyms'), '$');
```

## Task 3: efficiency view lookup
**User**: Views for article 2 after a date.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM article_views WHERE article_id=2 AND viewed_at>'2024-01-01';
```
```sql slow
SELECT * FROM article_views WHERE article_id=2 AND substr(viewed_at,1,10)>'2024-01-01';
```
