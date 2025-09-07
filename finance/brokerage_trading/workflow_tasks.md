# Workflow Tasks

## Task: intraday volume
```sql
-- step: base
CREATE TEMP TABLE base AS
SELECT instrument_id, trade_time, quantity FROM trades;
```
```sql
-- step: agg
-- depends: base
CREATE TEMP TABLE agg AS
SELECT instrument_id, SUM(quantity) q FROM base GROUP BY instrument_id;
```
```sql
-- step: final
-- depends: agg
SELECT * FROM agg WHERE q>100;
```

## Task: open order cleanup
```sql
-- step: pending
CREATE TEMP TABLE pending AS
SELECT * FROM orders WHERE status='OPEN';
```
```sql
-- step: cancel
-- depends: pending
UPDATE orders SET status='CANCELLED' WHERE id IN (SELECT id FROM pending);
```
```sql
-- step: verify
-- depends: cancel
SELECT COUNT(*) FROM orders WHERE status='OPEN';
```

