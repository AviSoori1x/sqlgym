# Sample Tasks for treasury_risk

## Task 1: list breaches
**User**: Show high severity breaches.
**Assistant**: Filter breaches by severity.
```sql
SELECT * FROM breaches WHERE severity='HIGH';
```

## Task 2: evidence policy
**User**: Where is the limit policy?
**Assistant**: Read limit_policy.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='limit_policy'), '$');
```

## Task 3: exposure lookup efficiency
**User**: Exposure for desk 1 on 2024-01-02.
**Assistant**: Fast query uses index; slow uses function.
```sql fast
SELECT amount FROM exposures WHERE desk_id=1 AND as_of='2024-01-02';
```
```sql slow
SELECT amount FROM exposures WHERE desk_id=1 AND substr(as_of,1,10)='2024-01-02';
```
