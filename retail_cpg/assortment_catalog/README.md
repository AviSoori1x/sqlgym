# assortment_catalog

Captures product assortment, categories, suppliers and attributes for a retail catalog.

## Entities
- categories – unique catalog categories
- suppliers – product suppliers with active/inactive lifecycle
- products – SKU-level items linked to category and supplier
- product_attributes – flexible attribute key/value

## Indexes
- `idx_products_category (category_id)`
- `idx_products_supplier (supplier_id)`
- `idx_attr_product (product_id)`

## Scale
~3 categories, 3 suppliers, 9 products, 18 attributes.

## Efficiency Notes
Indexes support filtering by category and supplier. Sample tasks show indexed lookups vs scans on computed fields.

## Denormalized Mart Trade-offs
The `product_catalog` mart duplicates category and supplier names for quick analytics but introduces redundancy; updates require rebuilding the mart.
