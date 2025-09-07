# pos_sales_returns

Models point-of-sale orders, itemized sales, and return workflows for a retail chain.
Captures store status, product catalog, order lifecycles and post-sale returns.

## Entities
- **stores** – locations with active/closed lifecycle
- **products** – catalog items
- **orders** – placed at stores with timestamps and statuses
- **order_items** – line items with pricing
- **returns** – item-level returns with reasons and timestamps

## Running
```bash
make build DOMAIN=retail_cpg
make check DOMAIN=retail_cpg
```

Expected rows: ~200 stores, 5k products, 50k orders, 150k items, 5k returns.

## Notable Indexes
- `idx_orders_store_date (store_id, ordered_at)`
- `idx_order_items_product (product_id)`
- `idx_returns_item_date (order_item_id, returned_at)`

## Distinctiveness
- enum statuses for stores, orders, and return reasons
- return policy window driven by evidence/promo_policy.json
- monetary values stored in integer cents; timestamps in ISO-8601

## Efficiency Notes
Indexes support lookups by store/date and product popularity; sample tasks
contrast date-first vs full-scan approaches.

## Denormalized Mart Trade-offs
The `store_daily_sales` mart pre-aggregates revenue and returns for faster reporting
but duplicates figures from orders; late adjustments require recomputation.
