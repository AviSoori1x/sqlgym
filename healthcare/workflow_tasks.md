# Workflow Tasks

## Task: claims denial rate
```sql
-- step: claims
CREATE TEMP TABLE claims AS
SELECT id, status FROM claims;
```
```sql
-- step: denials
-- depends: claims
CREATE TEMP TABLE denials AS
SELECT COUNT(*) c FROM claims WHERE status='DENIED';
```
```sql
-- step: final
-- depends: denials
SELECT c FROM denials;
```

## Task: lab turnaround
```sql
-- step: orders
CREATE TEMP TABLE orders AS
SELECT id, ordered_at FROM lab_orders;
```
```sql
-- step: results
-- depends: orders
SELECT id FROM orders WHERE ordered_at<'2024-01-05';
```

