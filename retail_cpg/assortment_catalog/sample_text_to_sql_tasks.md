# Sample Tasks for assortment_catalog

## Task 1: list beverages
**User**: Show SKUs for products in the Beverages category.
**Assistant**: Join products to categories and filter by name.
```sql
SELECT p.sku FROM products p JOIN categories c ON p.category_id=c.id WHERE c.name='Beverages';
```

## Task 2: evidence policy
**User**: Can inactive suppliers add new items?
**Assistant**: Read catalog_policy.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='catalog_policy'), '$');
```

## Task 3: fast vs slow supplier lookup
**User**: List active products from supplier 1; include slow alt.
**Assistant**: Fast query filters by supplier_id using index; slow uses function on supplier name.
```sql fast
SELECT id, name FROM products WHERE supplier_id=1 AND status='ACTIVE';
```
```sql slow
SELECT p.id, p.name FROM products p JOIN suppliers s ON p.supplier_id=s.id WHERE lower(s.name)='acme co' AND p.status='ACTIVE';
```
