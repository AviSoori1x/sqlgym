# Workflow for supply_chain_replenishment

```sql
-- step: latest_stock
CREATE TEMP TABLE latest AS
SELECT store_id, sku_id, MAX(date) AS max_date FROM store_sku_stock GROUP BY store_id, sku_id;

-- step: stock_join
-- depends: latest_stock
SELECT s.store_id, s.sku_id, st.on_hand FROM latest s
JOIN store_sku_stock st ON st.store_id=s.store_id AND st.sku_id=s.sku_id AND st.date=s.max_date;
```
