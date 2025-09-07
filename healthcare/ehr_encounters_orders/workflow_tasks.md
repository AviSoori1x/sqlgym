# Workflow for ehr_encounters_orders

```sql
-- step: order_counts
CREATE TEMP TABLE oc AS SELECT encounter_id, COUNT(*) cnt FROM orders GROUP BY encounter_id;

-- step: join_results
-- depends: order_counts
SELECT e.id, oc.cnt, COUNT(r.id) AS results
FROM encounters e JOIN oc ON e.id=oc.encounter_id
LEFT JOIN orders o ON e.id=o.encounter_id
LEFT JOIN results r ON o.id=r.order_id
GROUP BY e.id;
```
