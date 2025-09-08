# shopify_returns

## Overview
This subdomain models product returns, RMA (Return Merchandise Authorization) workflows, inspection processes, and refund management.

## Entities

### Normalized Schema
- **customers**: Customer records with loyalty tiers and lifetime value
- **products**: Product catalog with categories, pricing, and warranty information
- **orders**: Customer orders with delivery status tracking
- **order_items**: Individual line items within orders
- **rma_requests**: Return authorization requests with reasons and status workflow
- **rma_inspections**: Quality inspection results and refund recommendations

### Denormalized Schema
- **return_analytics**: Comprehensive return details with calculated metrics
- **daily_return_metrics**: Daily aggregated return statistics
- **product_return_analysis**: Product quality scores based on return patterns
- **customer_return_behavior**: Customer-level return patterns and risk scoring

## Key Indexes
- `idx_customers_tier`: Loyalty tier segmentation
- `idx_orders_customer`: Customer order history
- `idx_rma_status`: Active RMA tracking
- `idx_rma_date`: Time-based return analysis
- `idx_products_category`: Category-based return patterns

## Efficiency Notes
- One-to-one relationship enforced between order items and RMA requests
- Inspection results determine refund calculations
- Warranty validation built into return analytics
- Evidence files define return windows and inspection guidelines
- Fast/slow pairs demonstrate unique constraint usage vs pattern matching