# pricing_promotions_lift

## Entities
- products
- price_books
- promos
- receipts

## Distinctiveness
Analyzes effect of promotions on sales lift across product categories.

## Indexes
- `price_books(product_id)`
- `promos(product_id, start_date)`
- `receipts(product_id, sale_date)`

## Expected Row Counts
- products: 1k
- receipts: 200k

## Efficiency Notes
Indexes support receipt lookups by product and date.
