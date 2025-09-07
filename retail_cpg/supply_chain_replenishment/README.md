# supply_chain_replenishment

## Entities
- stores
- skus
- store_sku_stock
- replen_orders
- lead_times

## Distinctiveness
Models stock levels and replenishment orders to maintain inventory.

## Indexes
- `store_sku_stock(store_id, sku_id, date)`
- `replen_orders(store_id, sku_id, order_date)`

## Expected Row Counts
- store_sku_stock: 300k
- replen_orders: 50k

## Efficiency Notes
Indexes support fast lookups for reorder analysis.
