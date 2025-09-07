PRAGMA foreign_keys=OFF;
CREATE TABLE receipt_promos AS
SELECT r.id AS receipt_id, p.name AS product_name, r.sale_date, r.price_paid,
       r.promo_code, pr.discount
FROM receipts r
JOIN products p ON r.product_id=p.id
LEFT JOIN promos pr ON r.promo_code=pr.promo_code;
