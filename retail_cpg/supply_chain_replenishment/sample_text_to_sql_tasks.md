# Sample Tasks for supply_chain_replenishment

## Task 1: pending orders
**User**: Show pending orders for store 1.
**Assistant**: Filter orders by store and status.
```sql
SELECT * FROM replen_orders WHERE store_id=1 AND status='PENDING';
```

## Task 2: evidence policy
**User**: How is reorder point calculated?
**Assistant**: Read reorder_policy.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='reorder_policy'), '$');
```

## Task 3: efficiency stock lookup
**User**: Stock for store 2 sku 5 on 2024-01-10.
**Assistant**: Fast uses composite index.
```sql fast
SELECT on_hand FROM store_sku_stock WHERE store_id=2 AND sku_id=5 AND date='2024-01-10';
```
```sql slow
SELECT on_hand FROM store_sku_stock WHERE store_id=2 AND sku_id=5 AND substr(date,1,10)='2024-01-10';
```
