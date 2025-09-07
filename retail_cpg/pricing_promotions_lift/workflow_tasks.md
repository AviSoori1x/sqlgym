# Workflow for pricing_promotions_lift

```sql
-- step: promo_sales
CREATE TEMP TABLE promo_sales AS
SELECT product_id, SUM(price_paid) AS rev FROM receipts WHERE promo_code IS NOT NULL GROUP BY product_id;

-- step: total_sales
CREATE TEMP TABLE total_sales AS
SELECT product_id, SUM(price_paid) AS rev FROM receipts GROUP BY product_id;

-- step: lift_calc
-- depends: promo_sales, total_sales
SELECT t.product_id, p.rev AS promo_rev, t.rev AS total_rev
FROM total_sales t LEFT JOIN promo_sales p ON t.product_id=p.product_id;
```
