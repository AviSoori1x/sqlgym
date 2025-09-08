# walmart_merchandising

## Overview
This subdomain models retail merchandising operations including planogram management, shelf optimization, product placement analysis, and sales performance tracking.

## Entities

### Normalized Schema
- **stores**: Retail store profiles with formats and operational details
- **product_categories**: Hierarchical category structure with space allocations
- **products**: Product catalog with velocity rankings and package dimensions
- **planograms**: Shelf layout plans with facing allocations and approval workflow
- **product_placements**: Individual product positioning within planograms
- **sales_performance**: Daily product sales data by store location

### Denormalized Schema
- **planogram_performance**: Planogram-level sales efficiency and space utilization
- **product_placement_analysis**: Product placement effectiveness across stores
- **store_category_performance**: Category-level space and sales performance

## Key Indexes
- `idx_planograms_store`: Store planogram management
- `idx_product_placements_planogram`: Planogram composition queries
- `idx_sales_performance_store_date`: Store performance timeline
- `idx_products_velocity`: Velocity-based product analysis

## Efficiency Notes
- JSON package dimensions enable flexible space calculations
- Velocity rankings support data-driven placement decisions
- Eye-level and end-cap flags track premium placement effectiveness
- Evidence files define planogram standards and space allocation rules
- Fast/slow pairs demonstrate index usage on store and product lookups