-- Sanity checks for returns RMA support domain

-- 1. All orders reference valid customers
SELECT COUNT(*) FROM orders o LEFT JOIN customers c ON o.customer_id = c.id WHERE c.id IS NULL;

-- 2. All order items reference valid orders
SELECT COUNT(*) FROM order_items oi LEFT JOIN orders o ON oi.order_id = o.id WHERE o.id IS NULL;

-- 3. All order items reference valid products
SELECT COUNT(*) FROM order_items oi LEFT JOIN products p ON oi.product_id = p.id WHERE p.id IS NULL;

-- 4. All RMA requests reference valid order items
SELECT COUNT(*) FROM rma_requests r LEFT JOIN order_items oi ON r.order_item_id = oi.id WHERE oi.id IS NULL;

-- 5. All RMA requests reference valid customers
SELECT COUNT(*) FROM rma_requests r LEFT JOIN customers c ON r.customer_id = c.id WHERE c.id IS NULL;

-- 6. All RMA inspections reference valid RMA requests
SELECT COUNT(*) FROM rma_inspections i LEFT JOIN rma_requests r ON i.rma_id = r.id WHERE r.id IS NULL;

-- 7. Customer loyalty tier enum validation
SELECT COUNT(*) FROM customers WHERE loyalty_tier NOT IN ('BASIC', 'SILVER', 'GOLD', 'PLATINUM');

-- 8. Product category enum validation
SELECT COUNT(*) FROM products WHERE category NOT IN ('ELECTRONICS', 'APPAREL', 'HOME', 'SPORTS', 'TOYS', 'BEAUTY');

-- 9. Order status enum validation
SELECT COUNT(*) FROM orders WHERE status NOT IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED');

-- 10. RMA reason enum validation
SELECT COUNT(*) FROM rma_requests WHERE reason NOT IN ('DEFECTIVE', 'WRONG_ITEM', 'NOT_AS_DESCRIBED', 'DAMAGED', 'CHANGED_MIND', 'BETTER_PRICE', 'OTHER');

-- 11. RMA status enum validation
SELECT COUNT(*) FROM rma_requests WHERE status NOT IN ('PENDING', 'APPROVED', 'REJECTED', 'SHIPPED', 'RECEIVED', 'INSPECTED', 'PROCESSED', 'CLOSED');

-- 12. Return method enum validation
SELECT COUNT(*) FROM rma_requests WHERE return_method IS NOT NULL AND return_method NOT IN ('PREPAID_LABEL', 'CUSTOMER_SHIP', 'PICKUP', 'DROP_OFF');

-- 13. Inspection condition enum validation
SELECT COUNT(*) FROM rma_inspections WHERE condition NOT IN ('NEW', 'LIKE_NEW', 'GOOD', 'FAIR', 'POOR', 'DAMAGED');

-- 14. Inspection functionality enum validation
SELECT COUNT(*) FROM rma_inspections WHERE functionality NOT IN ('WORKING', 'PARTIALLY_WORKING', 'NOT_WORKING', 'NOT_TESTED');

-- 15. Inspection recommendation enum validation
SELECT COUNT(*) FROM rma_inspections WHERE recommendation NOT IN ('FULL_REFUND', 'PARTIAL_REFUND', 'EXCHANGE', 'REPAIR', 'REJECT');

-- 16. Quantity must be positive
SELECT COUNT(*) FROM order_items WHERE quantity <= 0;

-- 17. Deduction percentage range validation
SELECT COUNT(*) FROM rma_inspections WHERE deduction_percentage < 0 OR deduction_percentage > 100;

-- 18. One RMA per order item
SELECT order_item_id, COUNT(*) FROM rma_requests GROUP BY order_item_id HAVING COUNT(*) > 1;

-- 19. One inspection per RMA
SELECT rma_id, COUNT(*) FROM rma_inspections GROUP BY rma_id HAVING COUNT(*) > 1;

-- 20. Only delivered orders can have returns
SELECT COUNT(*) FROM rma_requests r 
JOIN order_items oi ON r.order_item_id = oi.id
JOIN orders o ON oi.order_id = o.id
WHERE o.status != 'DELIVERED';

-- 21. Rejected RMAs should not have return method
SELECT COUNT(*) FROM rma_requests WHERE status = 'REJECTED' AND return_method IS NOT NULL;

-- 22. Inspected RMAs should have inspection records
SELECT COUNT(*) FROM rma_requests r 
LEFT JOIN rma_inspections i ON r.id = i.rma_id
WHERE r.status IN ('INSPECTED', 'PROCESSED', 'CLOSED') AND i.id IS NULL;

-- 23. EXPLAIN - Verify index usage for customer order lookup
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 100;

-- 24. EXPLAIN - Verify index usage for date range queries
EXPLAIN QUERY PLAN SELECT * FROM rma_requests WHERE request_date >= '2024-01-01' AND request_date < '2024-02-01';

-- 25. EXPLAIN - Verify index usage for status filtering
EXPLAIN QUERY PLAN SELECT * FROM rma_requests WHERE status = 'PENDING';