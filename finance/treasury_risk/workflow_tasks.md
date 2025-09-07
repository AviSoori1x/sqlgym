# Workflow for treasury_risk

```sql
-- step: agg_exposure
CREATE TEMP TABLE agg AS
SELECT desk_id, SUM(amount) AS exposure_amt FROM exposures GROUP BY desk_id;

-- step: join_limits
-- depends: agg_exposure
SELECT a.desk_id, a.exposure_amt, l.amount AS limit_amt
FROM agg a JOIN limits l ON a.desk_id=l.desk_id;
```
