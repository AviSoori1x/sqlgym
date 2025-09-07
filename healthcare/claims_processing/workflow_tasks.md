# Workflow for claims_processing

```sql
-- step: claim_totals
CREATE TEMP TABLE totals AS
SELECT claim_id, SUM(amount) AS total FROM claim_lines GROUP BY claim_id;

-- step: join_claims
-- depends: claim_totals
SELECT c.id, t.total, c.status FROM claims c JOIN totals t ON c.id=t.claim_id;
```
