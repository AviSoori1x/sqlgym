# Workflow Tasks

## Task: promo lift
```sql
-- step: period
CREATE TEMP TABLE period AS
SELECT substr(ordered_at,1,10) d, SUM(oi.quantity*p.price_cents) rev
FROM orders o JOIN order_items oi ON o.id=oi.order_id
JOIN products p ON oi.product_id=p.id
WHERE ordered_at BETWEEN '2024-01-01' AND '2024-01-07'
GROUP BY d;
```
```sql
-- step: baseline
-- depends: period
CREATE TEMP TABLE baseline AS
SELECT d, AVG(rev) OVER () avg_rev FROM period;
```
```sql
-- step: final
-- depends: baseline
SELECT d, rev-avg_rev AS lift FROM period JOIN baseline USING(d);
```

## Task: return diagnostics
```sql
-- step: recent
CREATE TEMP TABLE recent AS
SELECT r.id, r.reason, r.returned_at, o.store_id
FROM returns r JOIN order_items oi ON r.order_item_id=oi.id
JOIN orders o ON oi.order_id=o.id
WHERE r.returned_at LIKE '2024-01%';
```
```sql
-- step: by_store
-- depends: recent
CREATE TEMP TABLE by_store AS
SELECT store_id, COUNT(*) c FROM recent GROUP BY store_id;
```
```sql
-- step: final
-- depends: by_store
SELECT * FROM by_store WHERE c>5;
```
