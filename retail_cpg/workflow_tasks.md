# Workflow Tasks

## Task: customer_journey_optimization
```sql
-- step: high_value_segments
CREATE TEMP TABLE high_value_segments AS
SELECT 
    customer_id,
    segment_names,
    customer_lifetime_value,
    churn_risk_score
FROM customer_360_profile 
WHERE customer_lifetime_value > 1000;
```
```sql
-- step: campaign_performance
-- depends: high_value_segments
CREATE TEMP TABLE campaign_performance AS
SELECT 
    c.platform,
    c.name as campaign_name,
    SUM(t.cost) as total_spend,
    COUNT(DISTINCT conv.user_id) as conversions,
    SUM(conv.conversion_value) as revenue
FROM campaigns c
JOIN touchpoints t ON c.id = t.campaign_id
LEFT JOIN conversions conv ON t.user_id = conv.user_id
WHERE EXISTS (
    SELECT 1 FROM high_value_segments hvs 
    WHERE hvs.customer_id = SUBSTR(t.user_id, 6)
)
GROUP BY c.id;
```
```sql
-- step: funnel_conversion_rates
-- depends: high_value_segments
CREATE TEMP TABLE funnel_conversion_rates AS
SELECT 
    fs.step_order,
    fs.name as step_name,
    COUNT(DISTINCT fe.session_id) as sessions_entered,
    COUNT(DISTINCT CASE WHEN us.converted = 1 THEN fe.session_id END) as conversions
FROM funnel_steps fs
LEFT JOIN funnel_events fe ON fs.id = fe.funnel_step_id
LEFT JOIN user_sessions us ON fe.session_id = us.session_id
GROUP BY fs.id
ORDER BY fs.step_order;
```
```sql
-- step: optimization_recommendations
-- depends: campaign_performance, funnel_conversion_rates
SELECT 
    'Campaign Optimization' as recommendation_type,
    cp.campaign_name,
    cp.total_spend,
    cp.revenue,
    cp.revenue / NULLIF(cp.total_spend, 0) as roas,
    CASE 
        WHEN cp.revenue / NULLIF(cp.total_spend, 0) > 3 THEN 'Increase Budget'
        WHEN cp.revenue / NULLIF(cp.total_spend, 0) < 1.5 THEN 'Optimize or Pause'
        ELSE 'Monitor Performance'
    END as action_recommended
FROM campaign_performance cp
UNION ALL
SELECT 
    'Funnel Optimization' as recommendation_type,
    fcr.step_name,
    fcr.sessions_entered,
    fcr.conversions,
    fcr.conversions * 100.0 / NULLIF(fcr.sessions_entered, 0) as conversion_rate,
    CASE 
        WHEN fcr.conversions * 100.0 / NULLIF(fcr.sessions_entered, 0) < 50 THEN 'Optimize Step'
        ELSE 'Step Performing Well'
    END as action_recommended
FROM funnel_conversion_rates fcr;
```

## Task: loyalty_program_analysis
```sql
-- step: tier_performance
CREATE TEMP TABLE tier_performance AS
SELECT 
    t.name as tier_name,
    COUNT(DISTINCT m.id) as member_count,
    AVG(m.lifetime_spend) as avg_lifetime_spend,
    SUM(pt.points_amount) as total_points_issued
FROM tiers t
LEFT JOIN members m ON t.id = m.tier_id
LEFT JOIN point_transactions pt ON m.id = pt.member_id AND pt.transaction_type = 'EARN'
WHERE m.status = 'ACTIVE'
GROUP BY t.id;
```
```sql
-- step: redemption_patterns
-- depends: tier_performance
CREATE TEMP TABLE redemption_patterns AS
SELECT 
    rc.category,
    COUNT(r.id) as redemption_count,
    SUM(r.points_redeemed) as total_points_redeemed,
    AVG(rc.monetary_value) as avg_reward_value
FROM redemptions r
JOIN rewards_catalog rc ON r.reward_id = rc.id
WHERE r.status = 'PROCESSED'
  AND r.redemption_date >= DATE('now', '-90 days')
GROUP BY rc.category;
```
```sql
-- step: member_engagement
-- depends: tier_performance
CREATE TEMP TABLE member_engagement AS
SELECT 
    m.tier_id,
    COUNT(DISTINCT m.id) as total_members,
    COUNT(DISTINCT CASE WHEN pt.transaction_date >= DATE('now', '-30 days') THEN m.id END) as active_members,
    COUNT(DISTINCT r.member_id) as redemption_members
FROM members m
LEFT JOIN point_transactions pt ON m.id = pt.member_id
LEFT JOIN redemptions r ON m.id = r.member_id AND r.redemption_date >= DATE('now', '-90 days')
GROUP BY m.tier_id;
```
```sql
-- step: loyalty_insights
-- depends: tier_performance, redemption_patterns, member_engagement
SELECT 
    'Tier Analysis' as insight_type,
    tp.tier_name as category,
    tp.member_count as metric_value,
    tp.avg_lifetime_spend as secondary_metric,
    me.active_members * 100.0 / me.total_members as engagement_rate
FROM tier_performance tp
JOIN member_engagement me ON tp.tier_name = (
    SELECT name FROM tiers WHERE id = me.tier_id
)
UNION ALL
SELECT 
    'Redemption Analysis' as insight_type,
    rp.category,
    rp.redemption_count as metric_value,
    rp.avg_reward_value as secondary_metric,
    NULL as engagement_rate
FROM redemption_patterns rp
ORDER BY metric_value DESC;
```

## Task: marketplace_compliance_monitoring
```sql
-- step: violation_trends
CREATE TEMP TABLE violation_trends AS
SELECT 
    DATE(pv.violation_date) as violation_date,
    cp.policy_type,
    cp.severity_level,
    COUNT(*) as violation_count,
    COUNT(DISTINCT pv.seller_id) as affected_sellers
FROM policy_violations pv
JOIN compliance_policies cp ON pv.policy_id = cp.id
WHERE pv.violation_date >= DATE('now', '-30 days')
GROUP BY DATE(pv.violation_date), cp.policy_type, cp.severity_level;
```
```sql
-- step: seller_risk_assessment
-- depends: violation_trends
CREATE TEMP TABLE seller_risk_assessment AS
SELECT 
    s.id as seller_id,
    s.seller_name,
    s.performance_rating,
    COUNT(pv.id) as total_violations,
    COUNT(CASE WHEN cp.severity_level = 'CRITICAL' THEN 1 END) as critical_violations,
    MAX(al.risk_score) as latest_risk_score,
    COUNT(ea.id) as enforcement_actions
FROM sellers s
LEFT JOIN policy_violations pv ON s.id = pv.seller_id
LEFT JOIN compliance_policies cp ON pv.policy_id = cp.id
LEFT JOIN audit_logs al ON s.id = al.seller_id
LEFT JOIN enforcement_actions ea ON s.id = ea.seller_id
WHERE s.verification_status = 'VERIFIED'
GROUP BY s.id;
```
```sql
-- step: performance_correlation
-- depends: seller_risk_assessment
CREATE TEMP TABLE performance_correlation AS
SELECT 
    sra.seller_id,
    sra.performance_rating,
    sra.total_violations,
    AVG(sm.cancellation_rate) as avg_cancellation_rate,
    AVG(sm.return_rate) as avg_return_rate,
    AVG(sm.customer_satisfaction) as avg_satisfaction
FROM seller_risk_assessment sra
LEFT JOIN seller_metrics sm ON sra.seller_id = sm.seller_id
WHERE sm.metric_date >= DATE('now', '-30 days')
GROUP BY sra.seller_id;
```
```sql
-- step: compliance_action_plan
-- depends: violation_trends, seller_risk_assessment, performance_correlation
SELECT 
    'High Risk Sellers' as category,
    COUNT(*) as seller_count,
    'Immediate Review Required' as recommended_action
FROM seller_risk_assessment
WHERE critical_violations > 0 OR latest_risk_score > 70
UNION ALL
SELECT 
    'Policy Violations Trending Up' as category,
    COUNT(DISTINCT policy_type) as metric_count,
    'Policy Communication Campaign' as recommended_action
FROM violation_trends
WHERE violation_count > 5
UNION ALL
SELECT 
    'Performance Correlation' as category,
    COUNT(*) as affected_sellers,
    'Performance Improvement Program' as recommended_action
FROM performance_correlation
WHERE avg_satisfaction < 3.5 AND total_violations > 2;
```

## Task: merchandising_optimization
```sql
-- step: category_performance
CREATE TEMP TABLE category_performance AS
SELECT 
    pc.category_name,
    COUNT(DISTINCT pp.product_id) as products_placed,
    SUM(sp.units_sold) as total_units_sold,
    SUM(sp.revenue) as total_revenue,
    AVG(sp.revenue / NULLIF(sp.units_sold, 0)) as avg_unit_price
FROM product_categories pc
JOIN products p ON pc.id = p.category_id
JOIN product_placements pp ON p.id = pp.product_id
JOIN sales_performance sp ON p.id = sp.product_id
WHERE sp.date >= DATE('now', '-30 days')
  AND pc.category_level = 3
GROUP BY pc.id;
```
```sql
-- step: placement_effectiveness
-- depends: category_performance
CREATE TEMP TABLE placement_effectiveness AS
SELECT 
    pp.eye_level,
    pp.end_cap,
    COUNT(DISTINCT pp.product_id) as products,
    AVG(sp.units_sold) as avg_units_sold,
    SUM(sp.revenue) as total_revenue
FROM product_placements pp
JOIN sales_performance sp ON pp.product_id = sp.product_id
WHERE sp.date >= DATE('now', '-30 days')
GROUP BY pp.eye_level, pp.end_cap;
```
```sql
-- step: velocity_analysis
-- depends: category_performance
CREATE TEMP TABLE velocity_analysis AS
SELECT 
    p.velocity_rank,
    COUNT(DISTINCT p.id) as product_count,
    AVG(pp.facings_count) as avg_facings,
    SUM(sp.units_sold) as total_units_sold,
    SUM(sp.units_sold) / SUM(pp.facings_count) as units_per_facing
FROM products p
JOIN product_placements pp ON p.id = pp.product_id
JOIN sales_performance sp ON p.id = sp.product_id
WHERE sp.date >= DATE('now', '-30 days')
GROUP BY p.velocity_rank;
```
```sql
-- step: optimization_opportunities
-- depends: category_performance, placement_effectiveness, velocity_analysis
SELECT 
    'Category Optimization' as opportunity_type,
    cp.category_name as item,
    cp.total_revenue as current_performance,
    'Increase high-performing category space' as recommendation
FROM category_performance cp
WHERE cp.total_revenue > (SELECT AVG(total_revenue) * 1.2 FROM category_performance)
UNION ALL
SELECT 
    'Placement Optimization' as opportunity_type,
    CASE 
        WHEN pe.eye_level = 1 AND pe.end_cap = 1 THEN 'Eye Level + End Cap'
        WHEN pe.eye_level = 1 THEN 'Eye Level Only'
        WHEN pe.end_cap = 1 THEN 'End Cap Only'
        ELSE 'Standard Placement'
    END as item,
    pe.avg_units_sold as current_performance,
    'Optimize product placement strategy' as recommendation
FROM placement_effectiveness pe
ORDER BY current_performance DESC
LIMIT 5;
```