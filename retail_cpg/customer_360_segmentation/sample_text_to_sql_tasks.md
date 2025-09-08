# Sample Tasks for amazon_customer_insights

## Task 1: Customer Lifetime Value Analysis
**User**: What's the average customer lifetime value by acquisition channel?
**Assistant**: I'll analyze CLV by acquisition channel.
```sql
SELECT 
    c.acquisition_channel,
    COUNT(DISTINCT c.id) as customer_count,
    AVG(total_spent) as avg_lifetime_value,
    AVG(transaction_count) as avg_transactions,
    AVG(total_spent / transaction_count) as avg_order_value
FROM customers c
JOIN (
    SELECT 
        customer_id,
        SUM(total_amount - discount_amount) as total_spent,
        COUNT(*) as transaction_count
    FROM transactions
    GROUP BY customer_id
) t ON c.id = t.customer_id
GROUP BY c.acquisition_channel
ORDER BY avg_lifetime_value DESC;
```

**User**: Which channels bring the highest value customers?
**Assistant**: Finding top-performing acquisition channels:
```sql
SELECT 
    c.acquisition_channel,
    COUNT(DISTINCT CASE WHEN t.total_spent >= 1000 THEN c.id END) as high_value_customers,
    COUNT(DISTINCT c.id) as total_customers,
    COUNT(DISTINCT CASE WHEN t.total_spent >= 1000 THEN c.id END) * 100.0 / COUNT(DISTINCT c.id) as high_value_rate,
    AVG(t.total_spent) as avg_clv
FROM customers c
LEFT JOIN (
    SELECT customer_id, SUM(total_amount - discount_amount) as total_spent
    FROM transactions GROUP BY customer_id
) t ON c.id = t.customer_id
GROUP BY c.acquisition_channel
ORDER BY high_value_rate DESC;
```

## Task 2: Segment Performance
**User**: How are our customer segments performing?
**Assistant**: Analyzing segment metrics:
```sql
SELECT 
    cs.name as segment_name,
    cs.segment_type,
    COUNT(DISTINCT csa.customer_id) as active_customers,
    AVG(t.total_spent) as avg_segment_value,
    AVG(t.transaction_count) as avg_transactions_per_customer
FROM customer_segments cs
JOIN customer_segment_assignments csa ON cs.id = csa.segment_id
LEFT JOIN (
    SELECT 
        customer_id,
        SUM(total_amount - discount_amount) as total_spent,
        COUNT(*) as transaction_count
    FROM transactions
    GROUP BY customer_id
) t ON csa.customer_id = t.customer_id
WHERE csa.expires_date > DATE('now')
GROUP BY cs.id
ORDER BY avg_segment_value DESC;
```

## Task 3: Efficiency Pair - Customer Profile Lookup
**User**: Show complete profile for customer100@example.com
**Assistant**: Fast query uses email unique constraint:
```sql fast
SELECT 
    c.*,
    COUNT(DISTINCT t.id) as total_transactions,
    SUM(t.total_amount - t.discount_amount) as lifetime_value,
    MAX(t.transaction_date) as last_purchase,
    GROUP_CONCAT(DISTINCT cs.name) as segments
FROM customers c
LEFT JOIN transactions t ON c.id = t.customer_id
LEFT JOIN customer_segment_assignments csa ON c.id = csa.customer_id AND csa.expires_date > DATE('now')
LEFT JOIN customer_segments cs ON csa.segment_id = cs.id
WHERE c.email = 'customer100@example.com'
GROUP BY c.id;
```
```sql slow
SELECT 
    c.*,
    COUNT(DISTINCT t.id) as total_transactions,
    SUM(t.total_amount - t.discount_amount) as lifetime_value,
    MAX(t.transaction_date) as last_purchase,
    GROUP_CONCAT(DISTINCT cs.name) as segments
FROM customers c
LEFT JOIN transactions t ON c.id = t.customer_id
LEFT JOIN customer_segment_assignments csa ON c.id = csa.customer_id AND csa.expires_date > DATE('now')
LEFT JOIN customer_segments cs ON csa.segment_id = cs.id
WHERE LOWER(c.email) LIKE '%customer100%'
GROUP BY c.id;
```

## Task 4: Evidence - Segment Criteria
**User**: What are the criteria for the High Value segment?
**Assistant**: Checking segment definition:
```sql
SELECT 
    name,
    segment_type,
    criteria_json,
    priority
FROM customer_segments
WHERE name = 'High Value';
```

## Task 5: Customer Journey Analysis
**User**: How do customers interact with us over time?
**Assistant**: Analyzing interaction patterns:
```sql
SELECT 
    interaction_type,
    channel,
    COUNT(*) as interaction_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(COUNT(*)) OVER () as avg_interactions
FROM customer_interactions
WHERE interaction_date >= DATE('now', '-30 days')
GROUP BY interaction_type, channel
ORDER BY interaction_count DESC;
```

**User**: What's the typical customer journey flow?
**Assistant**: Journey sequence analysis:
```sql
WITH journey_steps AS (
    SELECT 
        customer_id,
        interaction_type,
        channel,
        interaction_date,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY interaction_date) as step_number
    FROM customer_interactions
    WHERE interaction_date >= DATE('now', '-90 days')
)
SELECT 
    step_number,
    interaction_type,
    channel,
    COUNT(*) as occurrence_count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY step_number) as percentage
FROM journey_steps
WHERE step_number <= 5
GROUP BY step_number, interaction_type, channel
ORDER BY step_number, occurrence_count DESC;
```

## Task 6: Churn Risk Analysis
**User**: Which customers are at risk of churning?
**Assistant**: Identifying churn risk:
```sql
SELECT 
    c.email,
    c.acquisition_channel,
    MAX(t.transaction_date) as last_purchase,
    julianday('now') - julianday(MAX(t.transaction_date)) as days_since_last_purchase,
    COUNT(t.id) as total_transactions,
    SUM(t.total_amount - t.discount_amount) as lifetime_value,
    CASE 
        WHEN julianday('now') - julianday(MAX(t.transaction_date)) > 180 THEN 'HIGH'
        WHEN julianday('now') - julianday(MAX(t.transaction_date)) > 90 THEN 'MEDIUM'
        ELSE 'LOW'
    END as churn_risk
FROM customers c
LEFT JOIN transactions t ON c.id = t.customer_id
WHERE c.status = 'ACTIVE'
GROUP BY c.id
HAVING last_purchase IS NOT NULL
ORDER BY days_since_last_purchase DESC
LIMIT 20;
```

## Task 7: Efficiency Pair - Active Customers Today
**User**: Show customers who interacted today
**Assistant**: Fast uses date index:
```sql fast
SELECT DISTINCT
    c.email,
    c.first_name,
    c.last_name,
    COUNT(DISTINCT ci.id) as interactions_today
FROM customers c
JOIN customer_interactions ci ON c.id = ci.customer_id
WHERE DATE(ci.interaction_date) = DATE('now')
GROUP BY c.id
ORDER BY interactions_today DESC;
```
```sql slow
SELECT DISTINCT
    c.email,
    c.first_name,
    c.last_name,
    COUNT(DISTINCT ci.id) as interactions_today
FROM customers c
JOIN customer_interactions ci ON c.id = ci.customer_id
WHERE substr(ci.interaction_date, 1, 10) = DATE('now')
GROUP BY c.id
ORDER BY interactions_today DESC;
```

## Task 8: Preference Analysis
**User**: What are the most popular customer preferences?
**Assistant**: Analyzing preference patterns:
```sql
SELECT 
    preference_type,
    preference_value,
    COUNT(*) as customer_count,
    AVG(confidence_score) as avg_confidence,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY preference_type) as percentage
FROM customer_preferences
GROUP BY preference_type, preference_value
ORDER BY preference_type, customer_count DESC;
```

## Task 9: Cohort Analysis
**User**: How do customer cohorts perform over time?
**Assistant**: Monthly cohort analysis:
```sql
WITH cohorts AS (
    SELECT 
        strftime('%Y-%m', registration_date) as cohort_month,
        id as customer_id,
        registration_date
    FROM customers
),
cohort_data AS (
    SELECT 
        c.cohort_month,
        COUNT(DISTINCT c.customer_id) as cohort_size,
        COUNT(DISTINCT CASE 
            WHEN t.transaction_date <= DATE(c.registration_date, '+30 days') 
            THEN c.customer_id 
        END) as month_1_active,
        COUNT(DISTINCT CASE 
            WHEN t.transaction_date <= DATE(c.registration_date, '+90 days') 
            THEN c.customer_id 
        END) as month_3_active,
        SUM(t.total_amount - t.discount_amount) as total_revenue
    FROM cohorts c
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.cohort_month
)
SELECT 
    cohort_month,
    cohort_size,
    month_1_active,
    month_3_active,
    month_1_active * 100.0 / cohort_size as month_1_retention,
    month_3_active * 100.0 / cohort_size as month_3_retention,
    total_revenue / cohort_size as revenue_per_customer
FROM cohort_data
ORDER BY cohort_month DESC;
```

## Task 10: Cross-Channel Behavior
**User**: How do customers use different channels?
**Assistant**: Channel usage analysis:
```sql
SELECT 
    c.id,
    c.email,
    COUNT(DISTINCT t.channel) as channels_used,
    GROUP_CONCAT(DISTINCT t.channel) as channel_mix,
    COUNT(t.id) as total_transactions,
    SUM(t.total_amount - t.discount_amount) as total_spent
FROM customers c
JOIN transactions t ON c.id = t.customer_id
GROUP BY c.id
HAVING channels_used >= 2
ORDER BY channels_used DESC, total_spent DESC
LIMIT 20;
```

## Task 11: Efficiency Pair - Segment Members
**User**: List all customers in the Champions segment
**Assistant**: Fast uses segment name:
```sql fast
SELECT 
    c.email,
    c.first_name,
    c.last_name,
    csa.assigned_date,
    csa.confidence_score
FROM customer_segment_assignments csa
JOIN customer_segments cs ON csa.segment_id = cs.id
JOIN customers c ON csa.customer_id = c.id
WHERE cs.name = 'Champions'
  AND csa.expires_date > DATE('now')
ORDER BY csa.confidence_score DESC;
```
```sql slow
SELECT 
    c.email,
    c.first_name,
    c.last_name,
    csa.assigned_date,
    csa.confidence_score
FROM customer_segment_assignments csa
JOIN customer_segments cs ON csa.segment_id = cs.id
JOIN customers c ON csa.customer_id = c.id
WHERE UPPER(cs.name) LIKE '%CHAMPION%'
  AND csa.expires_date > DATE('now')
ORDER BY csa.confidence_score DESC;
```

## Task 12: Evidence - Segmentation Rules
**User**: What are the business rules for customer segmentation?
**Assistant**: Checking segmentation criteria:
```sql
SELECT json_extract(value, '$.segmentation_rules') as rules
FROM evidence_kv 
WHERE key = 'customer_segmentation_config';
```

## Task 13: Transaction Patterns
**User**: What are the seasonal transaction patterns?
**Assistant**: Seasonal analysis:
```sql
SELECT 
    strftime('%m', transaction_date) as month,
    strftime('%Y', transaction_date) as year,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT customer_id) as active_customers,
    SUM(total_amount - discount_amount) as total_revenue,
    AVG(total_amount - discount_amount) as avg_transaction_value
FROM transactions
GROUP BY strftime('%Y-%m', transaction_date)
ORDER BY year, month;
```

## Task 14: Customer Engagement Score
**User**: Calculate engagement scores for customers
**Assistant**: Engagement scoring:
```sql
WITH engagement_metrics AS (
    SELECT 
        c.id as customer_id,
        COUNT(DISTINCT t.id) as transaction_count,
        COUNT(DISTINCT ci.id) as interaction_count,
        julianday('now') - julianday(MAX(t.transaction_date)) as days_since_last_transaction,
        julianday('now') - julianday(c.registration_date) as customer_age_days
    FROM customers c
    LEFT JOIN transactions t ON c.id = t.customer_id
    LEFT JOIN customer_interactions ci ON c.id = ci.customer_id
    WHERE c.status = 'ACTIVE'
    GROUP BY c.id
)
SELECT 
    customer_id,
    transaction_count,
    interaction_count,
    days_since_last_transaction,
    CASE 
        WHEN transaction_count >= 10 AND days_since_last_transaction <= 30 THEN 'HIGH'
        WHEN transaction_count >= 5 AND days_since_last_transaction <= 60 THEN 'MEDIUM'
        WHEN transaction_count >= 1 AND days_since_last_transaction <= 120 THEN 'LOW'
        ELSE 'INACTIVE'
    END as engagement_level,
    (transaction_count * 0.4 + 
     LEAST(interaction_count / 10.0, 1.0) * 0.3 + 
     CASE WHEN days_since_last_transaction <= 30 THEN 0.3 ELSE 0 END) as engagement_score
FROM engagement_metrics
ORDER BY engagement_score DESC
LIMIT 25;
```

## Task 15: Multi-Segment Analysis
**User**: Which customers belong to multiple segments?
**Assistant**: Multi-segment customer analysis:
```sql
SELECT 
    c.email,
    c.first_name,
    c.last_name,
    COUNT(DISTINCT csa.segment_id) as segment_count,
    GROUP_CONCAT(cs.name) as segments,
    AVG(csa.confidence_score) as avg_confidence
FROM customers c
JOIN customer_segment_assignments csa ON c.id = csa.customer_id
JOIN customer_segments cs ON csa.segment_id = cs.id
WHERE csa.expires_date > DATE('now')
GROUP BY c.id
HAVING segment_count > 1
ORDER BY segment_count DESC, avg_confidence DESC;
```