# Sample Tasks for pos_sales_returns

## Task 1: store revenue on a day
**User**: What's store 1's revenue on 2024-01-02?
**Assistant**: Sum item price*qty for orders that day.
**User**: exclude cancelled orders.
**Assistant**: Filter status!='CANCELLED'.
```sql
SELECT SUM(oi.quantity*p.price_cents) FROM orders o
JOIN order_items oi ON o.id=oi.order_id
JOIN products p ON oi.product_id=p.id
WHERE o.store_id=1 AND substr(o.ordered_at,1,10)='2024-01-02'
  AND o.status!='CANCELLED';
```

## Task 2: evidence promo policy returns window
**User**: According to promo_policy.json, returns after 30 days are rejected. List late returns.
**Assistant**: Join orders and returns and compare dates.
```sql
SELECT r.id FROM returns r
JOIN order_items oi ON r.order_item_id=oi.id
JOIN orders o ON oi.order_id=o.id
WHERE julianday(r.returned_at)-julianday(o.ordered_at)>30;
```

## Task 3: fast vs slow top products
**User**: Which products sold the most units in the last 30 days?
**Assistant**: Fast query narrows orders by date before join.
**User**: also show slow version.
```sql fast
SELECT p.name, SUM(oi.quantity) q
FROM orders o
JOIN order_items oi ON o.id=oi.order_id
JOIN products p ON oi.product_id=p.id
WHERE o.ordered_at>='2024-01-01'
GROUP BY p.id ORDER BY q DESC LIMIT 5;
```
```sql slow
SELECT p.name, SUM(oi.quantity) q
FROM order_items oi
JOIN products p ON oi.product_id=p.id
JOIN orders o ON o.id=oi.order_id
GROUP BY p.id ORDER BY q DESC LIMIT 5;
```

## Task 4: evidence promo stackable flag
**User**: promo_policy.json says stackable_promos is false. Find orders with more than one promo code.
**Assistant**: Assuming orders table has promo_code column? actually none; report none.
```sql
SELECT COUNT(*) FROM orders WHERE instr(promo_code, ',')>0;
```

## Task 5: return rate by store
**User**: Which store has highest return rate?
**Assistant**: Compute returns/items per store.
**User**: only consider DEFECT reason.
**Assistant**: Filter returns.reason='DEFECT'.
```sql
WITH items AS (
  SELECT o.store_id, COUNT(*) c FROM orders o
  JOIN order_items oi ON o.id=oi.order_id GROUP BY o.store_id
), r AS (
  SELECT o.store_id, COUNT(*) rc FROM returns r
  JOIN order_items oi ON r.order_item_id=oi.id
  JOIN orders o ON oi.order_id=o.id
  WHERE r.reason='DEFECT' GROUP BY o.store_id
)
SELECT items.store_id, rc*1.0/c FROM items LEFT JOIN r USING(store_id) ORDER BY rc*1.0/c DESC LIMIT 1;
```

## Task 6: evidence promo types
**User**: What promo types are listed in promo_policy.json?
**Assistant**: The file enumerates types; select them via json_each.
```sql
SELECT value FROM json_each(readfile('evidence/promo_policy.json'), '$.promo_types');
```

## Task 7: efficiency pair on date filtering
**User**: Show orders for store 3 on 2024-01-01.
**Assistant**: Fast query uses index store/date; slow uses substr.
```sql fast
SELECT * FROM orders WHERE store_id=3 AND ordered_at BETWEEN '2024-01-01' AND '2024-01-01T23:59:59';
```
```sql slow
SELECT * FROM orders WHERE substr(ordered_at,1,10)='2024-01-01' AND store_id=3;
```

## Task 8: evidence returns_window_days
**User**: promo_policy.json says returns_window_days=30. Count returns within window for store 2.
**Assistant**: Compare dates <=30 days.
```sql
SELECT COUNT(*) FROM returns r
JOIN order_items oi ON r.order_item_id=oi.id
JOIN orders o ON oi.order_id=o.id
WHERE o.store_id=2 AND julianday(r.returned_at)-julianday(o.ordered_at)<=30;
```

## Task 9: product catalog lookup
**User**: Find SKU00010 details.
**Assistant**: Direct lookup via unique index.
```sql
SELECT * FROM products WHERE sku='SKU00010';
```

## Task 10: fast vs slow revenue aggregation
**User**: What's total revenue per store?
**Assistant**: Fast query pre-aggregates by store; slow cross-joins.
```sql fast
SELECT o.store_id, SUM(oi.quantity*p.price_cents)
FROM orders o JOIN order_items oi ON o.id=oi.order_id
JOIN products p ON oi.product_id=p.id
GROUP BY o.store_id;
```
```sql slow
SELECT s.id, SUM(oi.quantity*p.price_cents)
FROM stores s, orders o, order_items oi, products p
WHERE s.id=o.store_id AND o.id=oi.order_id AND oi.product_id=p.id
GROUP BY s.id;
```

## Task 11: evidence stackable false reminder
**User**: Can promos be stacked per policy?
**Assistant**: promo_policy.json says stackable_promos=false so answer is no.
**User**: show orders with any promo codes.
```sql
SELECT id, promo_code FROM orders WHERE promo_code IS NOT NULL;
```

## Task 12: store without returns
**User**: List stores with no returns.
**Assistant**: Left join orders->items->returns and filter.
```sql
SELECT s.id FROM stores s
LEFT JOIN orders o ON s.id=o.store_id
LEFT JOIN order_items oi ON o.id=oi.order_id
LEFT JOIN returns r ON r.order_item_id=oi.id
GROUP BY s.id HAVING COUNT(r.id)=0;
```

## Task 13: evidence promo types usage
**User**: Which orders used promo type 'BOGO' as defined in promo_policy.json?
**Assistant**: assuming promo_code encodes type; search for 'BOGO'.
```sql
SELECT id FROM orders WHERE promo_code LIKE '%BOGO%';
```

## Task 14: monthly sales trend
**User**: Give total revenue per day for January.
**Assistant**: group by date.
```sql
SELECT substr(ordered_at,1,10) d, SUM(oi.quantity*p.price_cents)
FROM orders o JOIN order_items oi ON o.id=oi.order_id
JOIN products p ON oi.product_id=p.id
WHERE ordered_at LIKE '2024-01%'
GROUP BY d ORDER BY d;
```

## Task 15: late return reasons
**User**: For returns after 30 days, what are the reasons?
**Assistant**: Use promo_policy window and group reasons.
```sql
SELECT reason, COUNT(*) FROM returns r
JOIN order_items oi ON r.order_item_id=oi.id
JOIN orders o ON oi.order_id=o.id
WHERE julianday(r.returned_at)-julianday(o.ordered_at)>30
GROUP BY reason;
```
