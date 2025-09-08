# Sample Tasks for starbucks_rewards

## Task 1: Tier Performance Analysis
**User**: How are our loyalty tiers performing?
**Assistant**: I'll analyze tier-level metrics.
```sql
SELECT 
    t.name as tier_name,
    COUNT(m.id) as member_count,
    AVG(m.lifetime_spend) as avg_lifetime_spend,
    AVG(m.current_points_balance) as avg_points_balance,
    COUNT(r.id) as total_redemptions
FROM tiers t
LEFT JOIN members m ON t.id = m.tier_id AND m.status = 'ACTIVE'
LEFT JOIN redemptions r ON m.id = r.member_id AND r.status = 'PROCESSED'
GROUP BY t.id
ORDER BY t.tier_order;
```

## Task 2: Efficiency Pair - Member Lookup
**User**: Show loyalty details for customer customer_100
**Assistant**: Fast uses customer_id unique constraint:
```sql fast
SELECT 
    m.customer_id,
    t.name as tier,
    m.total_points_earned,
    m.current_points_balance,
    m.lifetime_spend
FROM members m
JOIN tiers t ON m.tier_id = t.id
WHERE m.customer_id = 'customer_100';
```
```sql slow
SELECT 
    m.customer_id,
    t.name as tier,
    m.total_points_earned,
    m.current_points_balance,
    m.lifetime_spend
FROM members m
JOIN tiers t ON m.tier_id = t.id
WHERE m.customer_id LIKE '%100%';
```

## Task 3: Points Economy Analysis
**User**: What's our points liability?
**Assistant**: Analyzing points economy:
```sql
SELECT 
    SUM(m.current_points_balance) as total_outstanding_points,
    SUM(m.current_points_balance) * 0.01 as estimated_liability_dollars,
    COUNT(m.id) as members_with_balance,
    AVG(m.current_points_balance) as avg_balance_per_member
FROM members m
WHERE m.current_points_balance > 0
  AND m.status = 'ACTIVE';
```

## Task 4: Redemption Patterns
**User**: Which rewards are most popular?
**Assistant**: Top reward analysis:
```sql
SELECT 
    rc.name,
    rc.category,
    rc.points_cost,
    COUNT(r.id) as redemption_count,
    SUM(r.points_redeemed) as total_points_used
FROM rewards_catalog rc
LEFT JOIN redemptions r ON rc.id = r.reward_id AND r.status = 'PROCESSED'
WHERE r.redemption_date >= DATE('now', '-90 days')
GROUP BY rc.id
ORDER BY redemption_count DESC
LIMIT 10;
```