-- 1. each order references existing store
SELECT COUNT(*) FROM orders o LEFT JOIN stores s ON o.store_id=s.id WHERE s.id IS NULL;
-- 2. positive order item quantities
SELECT COUNT(*) FROM order_items WHERE quantity<=0;
-- 3. returns link to order items
SELECT COUNT(*) FROM returns r LEFT JOIN order_items oi ON r.order_item_id=oi.id WHERE oi.id IS NULL;
-- 4. store status enum check
SELECT COUNT(*) FROM stores WHERE status NOT IN ('OPEN','CLOSED');
-- 5. order status enum check
SELECT COUNT(*) FROM orders WHERE status NOT IN ('PLACED','SHIPPED','CANCELLED');
-- 6. return reason enum check
SELECT COUNT(*) FROM returns WHERE reason NOT IN ('DEFECT','DISSATISFIED','LATE_RETURN');
-- 7. order items exist for each order
SELECT o.id FROM orders o LEFT JOIN order_items oi ON o.id=oi.order_id GROUP BY o.id HAVING COUNT(oi.id)=0;
-- 8. returns window <=30 days per promo_policy.json
SELECT COUNT(*) FROM returns r JOIN order_items oi ON r.order_item_id=oi.id JOIN orders o ON oi.order_id=o.id WHERE julianday(r.returned_at)-julianday(o.ordered_at)>30;
-- 9. product sku uniqueness
SELECT sku, COUNT(*) c FROM products GROUP BY sku HAVING c>1;
-- 10. EXPLAIN plan uses index for store/date
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE store_id=1 AND ordered_at>'2024-01-01';
