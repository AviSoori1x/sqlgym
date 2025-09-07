# Sample Tasks for revenue_cycle_billing_denials

## Task 1: denial policy
**User**: Why might a claim be denied?
**Assistant**: Read denial policies evidence.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='denial_policies'), '$');
```

## Task 2: payment lookup
**User**: Payments for bill 1.
**Assistant**: Fast uses index.
```sql fast
SELECT * FROM payments WHERE bill_id=1;
```
```sql slow
SELECT * FROM payments WHERE CAST(bill_id AS TEXT)='1';
```
