PRAGMA foreign_keys=OFF;
CREATE TABLE order_stock AS
SELECT o.id AS order_id, s.name AS store_name, sk.name AS sku_name,
       o.order_date, o.quantity, o.status, lt.avg_days, st.on_hand
FROM replen_orders o
JOIN stores s ON o.store_id=s.id
JOIN skus sk ON o.sku_id=sk.id
LEFT JOIN lead_times lt ON lt.sku_id=o.sku_id
LEFT JOIN store_sku_stock st ON st.store_id=o.store_id AND st.sku_id=o.sku_id AND st.date=o.order_date;
