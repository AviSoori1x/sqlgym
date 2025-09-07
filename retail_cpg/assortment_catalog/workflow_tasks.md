# Workflow Tasks

## Task: attribute pivot
```sql
-- step: base
CREATE TEMP TABLE base AS
SELECT p.id, a.attribute, a.value FROM products p
JOIN product_attributes a ON p.id=a.product_id;
```
```sql
-- step: pivot
-- depends: base
CREATE TEMP TABLE pivoted AS
SELECT id,
       MAX(CASE WHEN attribute='color' THEN value END) color,
       MAX(CASE WHEN attribute='size' THEN value END) size
FROM base GROUP BY id;
```
```sql
-- step: final
-- depends: pivot
SELECT * FROM pivoted;
```

## Task: discontinue inactive supplier products
```sql
-- step: find
CREATE TEMP TABLE inactive AS
SELECT p.id FROM products p JOIN suppliers s ON p.supplier_id=s.id WHERE s.status='INACTIVE';
```
```sql
-- step: mark
-- depends: find
UPDATE products SET status='DISCONTINUED' WHERE id IN (SELECT id FROM inactive);
```
```sql
-- step: verify
-- depends: mark
SELECT COUNT(*) FROM products p JOIN suppliers s ON p.supplier_id=s.id WHERE s.status='INACTIVE' AND p.status!='DISCONTINUED';
```
