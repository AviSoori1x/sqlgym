-- stock summary
SELECT store_id, sku_id, SUM(on_hand) FROM store_sku_stock GROUP BY store_id, sku_id;

-- orders vs stock
SELECT o.id, st.on_hand FROM replen_orders o JOIN store_sku_stock st ON st.store_id=o.store_id AND st.sku_id=o.sku_id AND st.date=o.order_date;

-- lead time lookup
SELECT sku_id, avg_days FROM lead_times;
