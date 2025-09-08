# Sample Tasks for shopify_returns

## Task 1: Return Rate Overview
**User**: What's our overall return rate?
**Assistant**: I'll calculate the return rate based on delivered orders.
```sql
SELECT 
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT r.id) as total_returns,
    COUNT(DISTINCT r.id) * 100.0 / COUNT(DISTINCT o.id) as return_rate
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN rma_requests r ON oi.id = r.order_item_id
WHERE o.status = 'DELIVERED';
```

**User**: Which product categories have the highest return rates?
**Assistant**: Breaking down by category:
```sql
SELECT 
    p.category,
    COUNT(DISTINCT oi.id) as items_sold,
    COUNT(DISTINCT r.id) as items_returned,
    COUNT(DISTINCT r.id) * 100.0 / COUNT(DISTINCT oi.id) as return_rate
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
LEFT JOIN rma_requests r ON oi.id = r.order_item_id
WHERE o.status = 'DELIVERED'
GROUP BY p.category
ORDER BY return_rate DESC;
```

## Task 2: RMA Processing Time
**User**: How long does it take to process returns?
**Assistant**: Analyzing processing times by status:
```sql
SELECT 
    r.status,
    COUNT(*) as count,
    AVG(julianday('now') - julianday(r.request_date)) as avg_days_in_status,
    MIN(julianday('now') - julianday(r.request_date)) as min_days,
    MAX(julianday('now') - julianday(r.request_date)) as max_days
FROM rma_requests r
GROUP BY r.status
ORDER BY avg_days_in_status DESC;
```

## Task 3: Efficiency Pair - Customer Return History
**User**: Show all returns for customer100@example.com
**Assistant**: Fast query uses email unique constraint:
```sql fast
SELECT 
    r.id as rma_id,
    p.name as product,
    r.request_date,
    r.reason,
    r.status,
    i.recommendation
FROM rma_requests r
JOIN customers c ON r.customer_id = c.id
JOIN order_items oi ON r.order_item_id = oi.id
JOIN products p ON oi.product_id = p.id
LEFT JOIN rma_inspections i ON r.id = i.rma_id
WHERE c.email = 'customer100@example.com'
ORDER BY r.request_date DESC;
```
```sql slow
SELECT 
    r.id as rma_id,
    p.name as product,
    r.request_date,
    r.reason,
    r.status,
    i.recommendation
FROM rma_requests r
JOIN customers c ON r.customer_id = c.id
JOIN order_items oi ON r.order_item_id = oi.id
JOIN products p ON oi.product_id = p.id
LEFT JOIN rma_inspections i ON r.id = i.rma_id
WHERE LOWER(c.email) LIKE '%customer100%'
ORDER BY r.request_date DESC;
```

## Task 4: Evidence - Return Policy Check
**User**: What's our return window for different categories?
**Assistant**: Checking return policy:
```sql
SELECT json_extract(value, '$.return_windows') as category_policies
FROM evidence_kv 
WHERE key = 'return_policy';
```

## Task 5: Return Reason Analysis
**User**: What are the most common return reasons?
**Assistant**: Analyzing return reasons:
```sql
SELECT 
    reason,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage,
    AVG(julianday(request_date) - julianday(o.order_date)) as avg_days_to_return
FROM rma_requests r
JOIN order_items oi ON r.order_item_id = oi.id
JOIN orders o ON oi.order_id = o.id
GROUP BY reason
ORDER BY count DESC;
```

**User**: Which reasons have the highest rejection rate?
**Assistant**: Analyzing rejection by reason:
```sql
SELECT 
    reason,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'REJECTED' THEN 1 END) as rejected,
    COUNT(CASE WHEN status = 'REJECTED' THEN 1 END) * 100.0 / COUNT(*) as rejection_rate
FROM rma_requests
GROUP BY reason
HAVING COUNT(*) >= 10
ORDER BY rejection_rate DESC;
```

## Task 6: Inspection Outcomes
**User**: What percentage of inspections recommend full refund?
**Assistant**: Analyzing inspection recommendations:
```sql
SELECT 
    recommendation,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage,
    AVG(deduction_percentage) as avg_deduction
FROM rma_inspections
GROUP BY recommendation
ORDER BY count DESC;
```

## Task 7: Efficiency Pair - Pending RMAs
**User**: Show all pending RMA requests
**Assistant**: Fast uses status index:
```sql fast
SELECT 
    r.id,
    c.email,
    p.name as product,
    r.request_date,
    julianday('now') - julianday(r.request_date) as days_pending
FROM rma_requests r
JOIN customers c ON r.customer_id = c.id
JOIN order_items oi ON r.order_item_id = oi.id
JOIN products p ON oi.product_id = p.id
WHERE r.status = 'PENDING'
ORDER BY r.request_date;
```
```sql slow
SELECT 
    r.id,
    c.email,
    p.name as product,
    r.request_date,
    julianday('now') - julianday(r.request_date) as days_pending
FROM rma_requests r
JOIN customers c ON r.customer_id = c.id
JOIN order_items oi ON r.order_item_id = oi.id
JOIN products p ON oi.product_id = p.id
WHERE UPPER(r.status) = 'PENDING'
ORDER BY r.request_date;
```

## Task 8: High-Value Returns
**User**: Show returns over $500
**Assistant**: Finding high-value returns:
```sql
SELECT 
    r.id as rma_id,
    c.email,
    c.loyalty_tier,
    p.name as product,
    oi.unit_price * oi.quantity - oi.discount_amount as order_value,
    r.status,
    i.recommendation
FROM rma_requests r
JOIN customers c ON r.customer_id = c.id
JOIN order_items oi ON r.order_item_id = oi.id
JOIN products p ON oi.product_id = p.id
LEFT JOIN rma_inspections i ON r.id = i.rma_id
WHERE oi.unit_price * oi.quantity - oi.discount_amount > 500
ORDER BY order_value DESC;
```

## Task 9: Warranty Analysis
**User**: How many returns are within warranty?
**Assistant**: Analyzing warranty returns:
```sql
SELECT 
    COUNT(*) as total_returns,
    COUNT(CASE 
        WHEN julianday(r.request_date) - julianday(o.order_date) <= p.warranty_days 
        THEN 1 
    END) as warranty_returns,
    COUNT(CASE 
        WHEN julianday(r.request_date) - julianday(o.order_date) <= p.warranty_days 
        THEN 1 
    END) * 100.0 / COUNT(*) as warranty_percentage
FROM rma_requests r
JOIN order_items oi ON r.order_item_id = oi.id
JOIN orders o ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id;
```

**User**: Which categories have most out-of-warranty returns?
**Assistant**: Category breakdown:
```sql
SELECT 
    p.category,
    COUNT(*) as total_returns,
    COUNT(CASE 
        WHEN julianday(r.request_date) - julianday(o.order_date) > p.warranty_days 
        THEN 1 
    END) as out_of_warranty,
    AVG(p.warranty_days) as avg_warranty_days
FROM rma_requests r
JOIN order_items oi ON r.order_item_id = oi.id
JOIN orders o ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
GROUP BY p.category
ORDER BY out_of_warranty DESC;
```

## Task 10: Customer Tier Analysis
**User**: How do return patterns vary by loyalty tier?
**Assistant**: Analyzing by customer tier:
```sql
SELECT 
    c.loyalty_tier,
    COUNT(DISTINCT c.id) as customers,
    COUNT(DISTINCT r.id) as total_returns,
    COUNT(DISTINCT r.id) * 1.0 / COUNT(DISTINCT c.id) as returns_per_customer,
    AVG(oi.unit_price * oi.quantity - oi.discount_amount) as avg_return_value
FROM customers c
LEFT JOIN rma_requests r ON c.id = r.customer_id
LEFT JOIN order_items oi ON r.order_item_id = oi.id
GROUP BY c.loyalty_tier
ORDER BY c.loyalty_tier;
```

## Task 11: Efficiency Pair - Product Return Search
**User**: Find all returns for product SKU 'ELE-0001'
**Assistant**: Fast uses SKU unique constraint:
```sql fast
SELECT 
    r.id,
    c.email,
    r.request_date,
    r.reason,
    r.status
FROM rma_requests r
JOIN order_items oi ON r.order_item_id = oi.id
JOIN products p ON oi.product_id = p.id
JOIN customers c ON r.customer_id = c.id
WHERE p.sku = 'ELE-0001'
ORDER BY r.request_date DESC;
```
```sql slow
SELECT 
    r.id,
    c.email,
    r.request_date,
    r.reason,
    r.status
FROM rma_requests r
JOIN order_items oi ON r.order_item_id = oi.id
JOIN products p ON oi.product_id = p.id
JOIN customers c ON r.customer_id = c.id
WHERE p.sku LIKE '%ELE-0001%'
ORDER BY r.request_date DESC;
```

## Task 12: Evidence - Restocking Fees
**User**: What are the restocking fee policies?
**Assistant**: Checking restocking fee rules:
```sql
SELECT 
    json_extract(value, '$.restocking_fees') as fee_structure
FROM evidence_kv 
WHERE key = 'return_policy';
```

## Task 13: Seasonal Return Patterns
**User**: Do returns increase after holidays?
**Assistant**: Analyzing seasonal patterns:
```sql
WITH monthly_stats AS (
    SELECT 
        strftime('%Y-%m', r.request_date) as month,
        COUNT(*) as returns,
        COUNT(CASE WHEN r.reason = 'CHANGED_MIND' THEN 1 END) as changed_mind,
        COUNT(CASE WHEN r.reason = 'WRONG_ITEM' THEN 1 END) as wrong_item
    FROM rma_requests r
    GROUP BY strftime('%Y-%m', r.request_date)
)
SELECT 
    month,
    returns,
    changed_mind,
    wrong_item,
    LAG(returns) OVER (ORDER BY month) as prev_month_returns,
    returns - LAG(returns) OVER (ORDER BY month) as month_over_month_change
FROM monthly_stats
ORDER BY month DESC
LIMIT 12;
```

## Task 14: Return Method Preferences
**User**: What return methods do customers prefer?
**Assistant**: Analyzing return method usage:
```sql
SELECT 
    return_method,
    COUNT(*) as usage_count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM rma_requests
WHERE return_method IS NOT NULL
GROUP BY return_method
ORDER BY usage_count DESC;
```

**User**: Does this vary by customer tier?
**Assistant**: Return method by tier:
```sql
SELECT 
    c.loyalty_tier,
    r.return_method,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY c.loyalty_tier) as tier_percentage
FROM rma_requests r
JOIN customers c ON r.customer_id = c.id
WHERE r.return_method IS NOT NULL
GROUP BY c.loyalty_tier, r.return_method
ORDER BY c.loyalty_tier, count DESC;
```

## Task 15: Quality Score by Product
**User**: Which products have the best quality scores based on returns?
**Assistant**: Calculating quality scores:
```sql
WITH product_stats AS (
    SELECT 
        p.sku,
        p.name,
        p.category,
        COUNT(DISTINCT oi.id) as units_sold,
        COUNT(DISTINCT r.id) as units_returned,
        COUNT(DISTINCT CASE WHEN r.reason = 'DEFECTIVE' THEN r.id END) as defective_returns
    FROM products p
    JOIN order_items oi ON p.id = oi.product_id
    JOIN orders o ON oi.order_id = o.id
    LEFT JOIN rma_requests r ON oi.id = r.order_item_id
    WHERE o.status = 'DELIVERED'
    GROUP BY p.id
    HAVING units_sold >= 20
)
SELECT 
    sku,
    name,
    category,
    units_sold,
    units_returned,
    units_returned * 100.0 / units_sold as return_rate,
    defective_returns * 100.0 / units_sold as defect_rate,
    CASE 
        WHEN units_returned * 1.0 / units_sold < 0.02 THEN 10
        WHEN units_returned * 1.0 / units_sold < 0.05 THEN 8
        WHEN units_returned * 1.0 / units_sold < 0.10 THEN 6
        WHEN units_returned * 1.0 / units_sold < 0.20 THEN 4
        ELSE 2
    END as quality_score
FROM product_stats
ORDER BY quality_score DESC, units_sold DESC
LIMIT 20;
```