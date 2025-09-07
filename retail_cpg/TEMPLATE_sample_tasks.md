# Template: Sample Tasks for Retail CPG Subdomains

## Task 1: Domain Overview Query
**User**: What's the overall performance/status of [DOMAIN_ENTITY]?
**Assistant**: I'll analyze the key metrics for [DOMAIN_ENTITY].
```sql
SELECT 
    -- Key aggregation fields
    main_category,
    COUNT(*) as total_records,
    COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_count,
    AVG(key_metric) as avg_performance,
    SUM(revenue_field) as total_value
FROM main_table
WHERE date_field >= DATE('now', '-30 days')
GROUP BY main_category
ORDER BY total_value DESC;
```

**User**: How does this compare to last month?
**Assistant**: Comparing with previous period:
```sql
WITH current_period AS (
    SELECT 
        main_category,
        COUNT(*) as current_count,
        SUM(revenue_field) as current_revenue
    FROM main_table
    WHERE date_field >= DATE('now', '-30 days')
    GROUP BY main_category
),
previous_period AS (
    SELECT 
        main_category,
        COUNT(*) as previous_count,
        SUM(revenue_field) as previous_revenue
    FROM main_table
    WHERE date_field >= DATE('now', '-60 days') 
      AND date_field < DATE('now', '-30 days')
    GROUP BY main_category
)
SELECT 
    c.main_category,
    c.current_revenue,
    p.previous_revenue,
    (c.current_revenue - p.previous_revenue) * 100.0 / p.previous_revenue as growth_rate
FROM current_period c
LEFT JOIN previous_period p ON c.main_category = p.main_category
ORDER BY growth_rate DESC;
```

## Task 2: Efficiency Pair - Entity Lookup
**User**: Show details for [SPECIFIC_ENTITY]
**Assistant**: Fast query uses primary/unique constraint:
```sql fast
SELECT 
    main_fields.*,
    related_data
FROM main_table main_fields
LEFT JOIN related_table rt ON main_fields.id = rt.foreign_id
WHERE main_fields.unique_identifier = 'SPECIFIC_VALUE'
ORDER BY main_fields.date_field DESC;
```
```sql slow
SELECT 
    main_fields.*,
    related_data
FROM main_table main_fields
LEFT JOIN related_table rt ON main_fields.id = rt.foreign_id
WHERE LOWER(main_fields.unique_identifier) LIKE '%specific%value%'
ORDER BY main_fields.date_field DESC;
```

## Task 3: Evidence-Based Query
**User**: What are the [DOMAIN_SPECIFIC] rules/policies?
**Assistant**: Checking domain configuration:
```sql
SELECT json_extract(value, '$.key_rules') as domain_rules
FROM evidence_kv 
WHERE key = 'domain_configuration';
```

## Task 4: Time-Based Analysis
**User**: Show [DOMAIN_METRIC] trends over time
**Assistant**: Analyzing temporal patterns:
```sql
SELECT 
    DATE(date_field) as date,
    COUNT(*) as daily_count,
    SUM(value_field) as daily_total,
    AVG(performance_metric) as avg_performance
FROM main_table
WHERE date_field >= DATE('now', '-90 days')
GROUP BY DATE(date_field)
ORDER BY date;
```

## Task 5: Efficiency Pair - Status Filtering
**User**: Show all [ENTITIES] with status [SPECIFIC_STATUS]
**Assistant**: Fast uses status index:
```sql fast
SELECT 
    id,
    name,
    status,
    key_metrics
FROM main_table
WHERE status = 'SPECIFIC_STATUS'
ORDER BY date_field DESC;
```
```sql slow
SELECT 
    id,
    name,
    status,
    key_metrics
FROM main_table
WHERE UPPER(status) = 'SPECIFIC_STATUS'
ORDER BY date_field DESC;
```

## Task 6: Cross-Entity Analysis
**User**: How do different [ENTITY_TYPES] perform?
**Assistant**: Comparative analysis:
```sql
SELECT 
    entity_type,
    COUNT(*) as count,
    AVG(performance_metric) as avg_performance,
    MIN(performance_metric) as min_performance,
    MAX(performance_metric) as max_performance,
    STDDEV(performance_metric) as performance_variance
FROM main_table
WHERE status = 'ACTIVE'
GROUP BY entity_type
ORDER BY avg_performance DESC;
```

## Task 7: Top Performers
**User**: Who are the top performing [ENTITIES]?
**Assistant**: Ranking by performance:
```sql
SELECT 
    entity_name,
    entity_category,
    performance_metric,
    RANK() OVER (ORDER BY performance_metric DESC) as performance_rank,
    supporting_metrics
FROM main_table
WHERE status = 'ACTIVE'
  AND date_field >= DATE('now', '-30 days')
ORDER BY performance_metric DESC
LIMIT 20;
```

## Task 8: Efficiency Pair - Date Range Query
**User**: Show activity for last week
**Assistant**: Fast uses date index:
```sql fast
SELECT 
    entity_name,
    activity_type,
    date_field,
    value_metrics
FROM main_table
WHERE date_field >= DATE('now', '-7 days')
ORDER BY date_field DESC;
```
```sql slow
SELECT 
    entity_name,
    activity_type,
    date_field,
    value_metrics
FROM main_table
WHERE substr(date_field, 1, 10) >= DATE('now', '-7 days')
ORDER BY date_field DESC;
```

## TEMPLATE INSTRUCTIONS:

1. **Replace placeholders** with domain-specific terms:
   - [DOMAIN_ENTITY] → customers, products, campaigns, etc.
   - [SPECIFIC_ENTITY] → actual entity names
   - [DOMAIN_METRIC] → conversion rates, sales, performance, etc.
   - main_table → your primary table name
   - Field names → actual column names

2. **Add 7-10 more tasks** specific to your domain:
   - Domain-specific calculations
   - Business logic queries  
   - Segmentation analysis
   - Performance optimization
   - Compliance/audit queries

3. **Include at least 3 fast/slow pairs** demonstrating:
   - Index usage vs table scans
   - Exact matches vs pattern matching
   - Proper date comparisons vs string manipulation

4. **Add 1-2 evidence-based tasks** using:
   - JSON extraction from evidence_kv table
   - Domain policies/configurations
   - Business rules validation

5. **Ensure multi-turn conversations** (2-5 turns per task)

6. **Target 15-20 total tasks** with varied complexity
