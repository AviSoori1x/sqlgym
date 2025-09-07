-- 1 count categories
SELECT COUNT(*) FROM categories;
-- 2 unique suppliers
SELECT COUNT(DISTINCT name) FROM suppliers;
-- 3 products per category
SELECT category_id, COUNT(*) FROM products GROUP BY category_id;
-- 4 products joined to suppliers
SELECT COUNT(*) FROM products p JOIN suppliers s ON p.supplier_id=s.id;
-- 5 attribute count
SELECT COUNT(*) FROM product_attributes;
-- 6 active products
SELECT COUNT(*) FROM products WHERE status='ACTIVE';
-- 7 negative price check (expect 0)
SELECT COUNT(*) FROM products WHERE price_cents<=0;
-- 8 products lacking attributes
SELECT COUNT(*) FROM products p LEFT JOIN product_attributes a ON p.id=a.product_id GROUP BY p.id HAVING COUNT(a.id)=0;
-- 9 supplier status counts
SELECT status, COUNT(*) FROM suppliers GROUP BY status;
--10 average price per category
SELECT category_id, AVG(price_cents) FROM products GROUP BY category_id;
