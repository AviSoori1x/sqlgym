# Sample Tasks for pricing_promotions_lift

## Task 1: promo receipts
**User**: List receipts that used promo XYZ.
**Assistant**: Filter receipts by promo code.
```sql
SELECT * FROM receipts WHERE promo_code='XYZ';
```

## Task 2: evidence policy
**User**: How are discounts applied?
**Assistant**: Read promo_policy.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='promo_policy'), '$');
```

## Task 3: efficiency receipt lookup
**User**: Receipts for product 10 on 2024-01-05.
**Assistant**: Fast query uses index; slow uses function.
```sql fast
SELECT price_paid FROM receipts WHERE product_id=10 AND sale_date='2024-01-05';
```
```sql slow
SELECT price_paid FROM receipts WHERE product_id=10 AND substr(sale_date,1,10)='2024-01-05';
```
