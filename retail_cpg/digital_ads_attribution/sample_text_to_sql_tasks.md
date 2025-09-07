# Sample Tasks for digital_ads_attribution

## Task 1: Campaign Performance Overview
**User**: What's the performance of our Google Ads campaigns this month?
**Assistant**: I'll analyze Google Ads performance metrics.
```sql
SELECT 
    c.name as campaign_name,
    c.objective,
    SUM(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 ELSE 0 END) as impressions,
    SUM(CASE WHEN t.interaction_type = 'CLICK' THEN 1 ELSE 0 END) as clicks,
    SUM(t.cost) as total_spend,
    COUNT(DISTINCT conv.id) as conversions,
    SUM(conv.conversion_value) as revenue
FROM campaigns c
LEFT JOIN touchpoints t ON c.id = t.campaign_id
LEFT JOIN conversions conv ON t.user_id = conv.user_id 
    AND DATE(t.timestamp) <= DATE(conv.conversion_timestamp)
WHERE c.platform = 'GOOGLE_ADS'
  AND DATE(t.timestamp) >= DATE('now', 'start of month')
GROUP BY c.id
ORDER BY total_spend DESC;
```

**User**: Which campaigns have the best ROAS?
**Assistant**: Calculating return on ad spend:
```sql
SELECT 
    c.name,
    c.platform,
    SUM(t.cost) as spend,
    SUM(conv.conversion_value) as revenue,
    CASE 
        WHEN SUM(t.cost) > 0 THEN SUM(conv.conversion_value) / SUM(t.cost)
        ELSE 0 
    END as roas,
    COUNT(DISTINCT conv.id) as conversions
FROM campaigns c
JOIN touchpoints t ON c.id = t.campaign_id
LEFT JOIN conversions conv ON t.user_id = conv.user_id
WHERE t.cost > 0
GROUP BY c.id
HAVING spend > 100
ORDER BY roas DESC
LIMIT 10;
```

## Task 2: Attribution Analysis
**User**: How do different attribution models affect our results?
**Assistant**: Comparing attribution models:
```sql
WITH attribution_comparison AS (
    SELECT 
        c.conversion_type,
        COUNT(*) as total_conversions,
        SUM(c.conversion_value) as total_value,
        -- First touch attribution
        COUNT(CASE WHEN t_first.campaign_id IS NOT NULL THEN 1 END) as first_touch_attributed,
        -- Last touch attribution  
        COUNT(CASE WHEN t_last.campaign_id IS NOT NULL THEN 1 END) as last_touch_attributed
    FROM conversions c
    LEFT JOIN touchpoints t_first ON c.user_id = t_first.user_id 
        AND t_first.timestamp = (
            SELECT MIN(timestamp) FROM touchpoints 
            WHERE user_id = c.user_id AND timestamp <= c.conversion_timestamp
        )
    LEFT JOIN touchpoints t_last ON c.user_id = t_last.user_id
        AND t_last.timestamp = (
            SELECT MAX(timestamp) FROM touchpoints 
            WHERE user_id = c.user_id AND timestamp <= c.conversion_timestamp
        )
    GROUP BY c.conversion_type
)
SELECT 
    conversion_type,
    total_conversions,
    total_value,
    first_touch_attributed,
    last_touch_attributed,
    first_touch_attributed * 100.0 / total_conversions as first_touch_rate,
    last_touch_attributed * 100.0 / total_conversions as last_touch_rate
FROM attribution_comparison;
```

## Task 3: Efficiency Pair - Campaign Lookup
**User**: Show performance for campaign "Campaign_1_GOOGLE_ADS"
**Assistant**: Fast query uses campaign name:
```sql fast
SELECT 
    c.name,
    c.platform,
    c.status,
    COUNT(DISTINCT t.user_id) as unique_users,
    SUM(CASE WHEN t.interaction_type = 'CLICK' THEN 1 ELSE 0 END) as clicks,
    SUM(t.cost) as spend
FROM campaigns c
LEFT JOIN touchpoints t ON c.id = t.campaign_id
WHERE c.name = 'Campaign_1_GOOGLE_ADS'
GROUP BY c.id;
```
```sql slow
SELECT 
    c.name,
    c.platform,
    c.status,
    COUNT(DISTINCT t.user_id) as unique_users,
    SUM(CASE WHEN t.interaction_type = 'CLICK' THEN 1 ELSE 0 END) as clicks,
    SUM(t.cost) as spend
FROM campaigns c
LEFT JOIN touchpoints t ON c.id = t.campaign_id
WHERE LOWER(c.name) LIKE '%campaign_1_google%'
GROUP BY c.id;
```

## Task 4: Evidence - Attribution Model Configuration
**User**: What attribution models are we using?
**Assistant**: Checking active attribution models:
```sql
SELECT 
    name,
    model_type,
    parameters,
    is_active
FROM attribution_models
WHERE is_active = 1;
```

## Task 5: Customer Journey Analysis
**User**: What does a typical customer journey look like?
**Assistant**: Analyzing journey patterns:
```sql
WITH journey_steps AS (
    SELECT 
        t.user_id,
        t.platform,
        t.interaction_type,
        t.timestamp,
        ROW_NUMBER() OVER (PARTITION BY t.user_id ORDER BY t.timestamp) as step_number
    FROM touchpoints t
    WHERE t.user_id IN (
        SELECT user_id FROM conversions 
        WHERE conversion_type = 'PURCHASE'
    )
)
SELECT 
    step_number,
    platform,
    interaction_type,
    COUNT(*) as occurrence_count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY step_number) as percentage
FROM journey_steps
WHERE step_number <= 5
GROUP BY step_number, platform, interaction_type
ORDER BY step_number, occurrence_count DESC;
```

## Task 6: Cross-Platform Performance
**User**: How do different platforms perform together?
**Assistant**: Cross-platform analysis:
```sql
WITH user_platforms AS (
    SELECT 
        t.user_id,
        GROUP_CONCAT(DISTINCT t.platform) as platform_mix,
        COUNT(DISTINCT t.platform) as platform_count,
        MAX(CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END) as converted
    FROM touchpoints t
    LEFT JOIN conversions c ON t.user_id = c.user_id
    GROUP BY t.user_id
)
SELECT 
    platform_count,
    COUNT(*) as users,
    SUM(converted) as conversions,
    SUM(converted) * 100.0 / COUNT(*) as conversion_rate,
    platform_mix
FROM user_platforms
GROUP BY platform_count, platform_mix
ORDER BY conversion_rate DESC;
```

## Task 7: Efficiency Pair - Daily Performance
**User**: Show campaign performance for yesterday
**Assistant**: Fast uses date index:
```sql fast
SELECT 
    c.name,
    c.platform,
    COUNT(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 END) as impressions,
    COUNT(CASE WHEN t.interaction_type = 'CLICK' THEN 1 END) as clicks,
    SUM(t.cost) as spend
FROM campaigns c
JOIN touchpoints t ON c.id = t.campaign_id
WHERE DATE(t.timestamp) = DATE('now', '-1 day')
GROUP BY c.id
ORDER BY spend DESC;
```
```sql slow
SELECT 
    c.name,
    c.platform,
    COUNT(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 END) as impressions,
    COUNT(CASE WHEN t.interaction_type = 'CLICK' THEN 1 END) as clicks,
    SUM(t.cost) as spend
FROM campaigns c
JOIN touchpoints t ON c.id = t.campaign_id
WHERE substr(t.timestamp, 1, 10) = DATE('now', '-1 day')
GROUP BY c.id
ORDER BY spend DESC;
```

## Task 8: Conversion Window Analysis
**User**: How does attribution window affect conversion credit?
**Assistant**: Analyzing attribution windows:
```sql
SELECT 
    c.attribution_window_hours,
    COUNT(*) as conversions,
    AVG(touchpoint_count) as avg_touchpoints,
    AVG(journey_duration_hours) as avg_journey_hours
FROM conversions c
JOIN (
    SELECT 
        conv.id,
        COUNT(t.id) as touchpoint_count,
        (julianday(conv.conversion_timestamp) - julianday(MIN(t.timestamp))) * 24 as journey_duration_hours
    FROM conversions conv
    LEFT JOIN touchpoints t ON conv.user_id = t.user_id 
        AND t.timestamp <= conv.conversion_timestamp
        AND julianday(conv.conversion_timestamp) - julianday(t.timestamp) <= conv.attribution_window_hours / 24.0
    GROUP BY conv.id
) journey ON c.id = journey.id
GROUP BY c.attribution_window_hours
ORDER BY c.attribution_window_hours;
```

## Task 9: Ad Creative Performance
**User**: Which ad creatives are performing best?
**Assistant**: Creative performance analysis:
```sql
SELECT 
    a.creative_id,
    a.ad_type,
    a.headline,
    a.call_to_action,
    COUNT(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 END) as impressions,
    COUNT(CASE WHEN t.interaction_type = 'CLICK' THEN 1 END) as clicks,
    COUNT(CASE WHEN t.interaction_type = 'CLICK' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 END), 0) as ctr,
    COUNT(DISTINCT conv.id) as conversions
FROM ads a
LEFT JOIN touchpoints t ON a.id = t.ad_id
LEFT JOIN conversions conv ON t.user_id = conv.user_id
GROUP BY a.id
HAVING impressions > 1000
ORDER BY ctr DESC
LIMIT 15;
```

## Task 10: Time-Based Performance
**User**: What are our peak performance hours?
**Assistant**: Hourly performance analysis:
```sql
SELECT 
    CAST(strftime('%H', t.timestamp) AS INTEGER) as hour,
    COUNT(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 END) as impressions,
    COUNT(CASE WHEN t.interaction_type = 'CLICK' THEN 1 END) as clicks,
    COUNT(DISTINCT conv.id) as conversions,
    SUM(t.cost) as spend,
    SUM(conv.conversion_value) as revenue
FROM touchpoints t
LEFT JOIN conversions conv ON t.user_id = conv.user_id 
    AND DATE(t.timestamp) = DATE(conv.conversion_timestamp)
GROUP BY hour
ORDER BY hour;
```

## Task 11: Efficiency Pair - User Conversion History
**User**: Show conversion history for user_1234
**Assistant**: Fast uses user_id index:
```sql fast
SELECT 
    c.conversion_timestamp,
    c.conversion_type,
    c.conversion_value,
    c.order_id,
    COUNT(t.id) as prior_touchpoints
FROM conversions c
LEFT JOIN touchpoints t ON c.user_id = t.user_id 
    AND t.timestamp <= c.conversion_timestamp
WHERE c.user_id = 'user_1234'
GROUP BY c.id
ORDER BY c.conversion_timestamp DESC;
```
```sql slow
SELECT 
    c.conversion_timestamp,
    c.conversion_type,
    c.conversion_value,
    c.order_id,
    COUNT(t.id) as prior_touchpoints
FROM conversions c
LEFT JOIN touchpoints t ON c.user_id = t.user_id 
    AND t.timestamp <= c.conversion_timestamp
WHERE c.user_id LIKE '%1234%'
GROUP BY c.id
ORDER BY c.conversion_timestamp DESC;
```

## Task 12: Evidence - Campaign Budget Allocation
**User**: What's our budget allocation strategy?
**Assistant**: Checking budget allocation rules:
```sql
SELECT json_extract(value, '$.budget_allocation') as allocation_strategy
FROM evidence_kv 
WHERE key = 'campaign_optimization_rules';
```

## Task 13: Bid Strategy Performance
**User**: How do different bid strategies perform?
**Assistant**: Bid strategy analysis:
```sql
SELECT 
    ag.bid_strategy,
    COUNT(DISTINCT ag.id) as ad_groups,
    AVG(ag.max_bid) as avg_max_bid,
    SUM(CASE WHEN t.interaction_type = 'CLICK' THEN 1 ELSE 0 END) as total_clicks,
    SUM(t.cost) as total_spend,
    SUM(t.cost) / NULLIF(SUM(CASE WHEN t.interaction_type = 'CLICK' THEN 1 ELSE 0 END), 0) as avg_cpc,
    COUNT(DISTINCT conv.id) as conversions
FROM ad_groups ag
LEFT JOIN ads a ON ag.id = a.ad_group_id
LEFT JOIN touchpoints t ON a.id = t.ad_id
LEFT JOIN conversions conv ON t.user_id = conv.user_id
GROUP BY ag.bid_strategy
ORDER BY conversions DESC;
```

## Task 14: Platform Comparison
**User**: Compare performance across advertising platforms
**Assistant**: Platform performance comparison:
```sql
SELECT 
    c.platform,
    COUNT(DISTINCT c.id) as campaigns,
    SUM(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 ELSE 0 END) as impressions,
    SUM(CASE WHEN t.interaction_type = 'CLICK' THEN 1 ELSE 0 END) as clicks,
    SUM(t.cost) as spend,
    COUNT(DISTINCT conv.id) as conversions,
    SUM(conv.conversion_value) as revenue,
    -- Key metrics
    SUM(CASE WHEN t.interaction_type = 'CLICK' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN t.interaction_type = 'IMPRESSION' THEN 1 ELSE 0 END), 0) as ctr,
    COUNT(DISTINCT conv.id) * 100.0 / 
        NULLIF(SUM(CASE WHEN t.interaction_type = 'CLICK' THEN 1 ELSE 0 END), 0) as conversion_rate,
    SUM(conv.conversion_value) / NULLIF(SUM(t.cost), 0) as roas
FROM campaigns c
LEFT JOIN touchpoints t ON c.id = t.campaign_id
LEFT JOIN conversions conv ON t.user_id = conv.user_id
GROUP BY c.platform
ORDER BY roas DESC;
```

## Task 15: Multi-Touch Attribution
**User**: Show multi-touch attribution for recent conversions
**Assistant**: Multi-touch attribution analysis:
```sql
WITH conversion_journeys AS (
    SELECT 
        c.id as conversion_id,
        c.user_id,
        c.conversion_value,
        t.campaign_id,
        t.platform,
        t.timestamp,
        ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY t.timestamp) as touch_sequence,
        COUNT(*) OVER (PARTITION BY c.id) as total_touches
    FROM conversions c
    JOIN touchpoints t ON c.user_id = t.user_id
    WHERE t.timestamp <= c.conversion_timestamp
      AND julianday(c.conversion_timestamp) - julianday(t.timestamp) <= 7
      AND c.conversion_timestamp >= DATE('now', '-30 days')
)
SELECT 
    conversion_id,
    user_id,
    conversion_value,
    total_touches,
    -- First touch
    MAX(CASE WHEN touch_sequence = 1 THEN platform END) as first_touch_platform,
    -- Last touch  
    MAX(CASE WHEN touch_sequence = total_touches THEN platform END) as last_touch_platform,
    -- Linear attribution value per touch
    conversion_value / total_touches as linear_attribution_per_touch,
    -- Journey summary
    GROUP_CONCAT(platform, ' -> ') as journey_path
FROM conversion_journeys
GROUP BY conversion_id
ORDER BY conversion_value DESC
LIMIT 20;
```