-- revenue by product
SELECT product_id, SUM(price_paid) FROM receipts GROUP BY product_id;

-- promo usage counts
SELECT promo_code, COUNT(*) FROM receipts WHERE promo_code IS NOT NULL GROUP BY promo_code;

-- average discount
SELECT AVG(discount) FROM promos;
