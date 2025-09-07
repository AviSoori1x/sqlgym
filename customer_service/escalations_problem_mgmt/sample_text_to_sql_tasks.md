# Sample Tasks for escalations_problem_mgmt

## Task 1: Current Escalation Rate
**User**: What's our overall escalation rate?
**Assistant**: I'll calculate the percentage of issues that get escalated.
```sql
SELECT 
    COUNT(DISTINCT e.issue_id) * 100.0 / COUNT(DISTINCT i.id) as escalation_rate,
    COUNT(DISTINCT i.id) as total_issues,
    COUNT(DISTINCT e.issue_id) as escalated_issues
FROM issues i
LEFT JOIN escalations e ON i.id = e.issue_id;
```

**User**: Which departments have the highest escalation rates?
**Assistant**: Breaking down by department:
```sql
SELECT 
    a.department,
    COUNT(DISTINCT i.id) as total_issues,
    COUNT(DISTINCT e.issue_id) as escalated,
    COUNT(DISTINCT e.issue_id) * 100.0 / COUNT(DISTINCT i.id) as escalation_rate
FROM issues i
JOIN agents a ON i.created_by_agent_id = a.id
LEFT JOIN escalations e ON i.id = e.issue_id
GROUP BY a.department
ORDER BY escalation_rate DESC;
```

## Task 2: SLA Performance
**User**: How many critical issues breached SLA?
**Assistant**: Checking critical issues resolved after 4-hour SLA:
```sql
SELECT 
    COUNT(*) as total_critical,
    COUNT(CASE 
        WHEN resolved_at IS NULL OR 
             (julianday(resolved_at) - julianday(created_at)) * 24 > 4 
        THEN 1 
    END) as sla_breaches,
    COUNT(CASE 
        WHEN resolved_at IS NULL OR 
             (julianday(resolved_at) - julianday(created_at)) * 24 > 4 
        THEN 1 
    END) * 100.0 / COUNT(*) as breach_rate
FROM issues
WHERE severity = 'CRITICAL';
```

## Task 3: Efficiency Pair - Issue Lookup by Date
**User**: Show all high severity issues from last week
**Assistant**: Fast query uses date and severity indexes:
```sql fast
SELECT 
    id,
    customer_id,
    category,
    severity,
    status,
    created_at
FROM issues
WHERE created_at >= DATE('now', '-7 days') 
    AND severity IN ('HIGH', 'CRITICAL')
ORDER BY created_at DESC;
```
```sql slow
SELECT 
    id,
    customer_id,
    category,
    severity,
    status,
    created_at
FROM issues
WHERE substr(created_at, 1, 10) >= DATE('now', '-7 days')
    AND (severity = 'HIGH' OR severity = 'CRITICAL')
ORDER BY created_at DESC;
```

## Task 4: Evidence - Escalation Matrix
**User**: What are the escalation rules for high-value customers?
**Assistant**: Checking escalation policy:
```sql
SELECT json_extract(value, '$.high_value_customer_rules') as rules
FROM evidence_kv 
WHERE key = 'escalation_matrix';
```

## Task 5: Agent Performance Analysis
**User**: Which L1 agents escalate the most?
**Assistant**: Analyzing L1 escalation patterns:
```sql
SELECT 
    a.name,
    COUNT(DISTINCT i.id) as issues_handled,
    COUNT(DISTINCT e.issue_id) as issues_escalated,
    COUNT(DISTINCT e.issue_id) * 100.0 / COUNT(DISTINCT i.id) as escalation_rate
FROM agents a
JOIN issues i ON a.id = i.created_by_agent_id
LEFT JOIN escalations e ON i.id = e.issue_id AND e.from_agent_id = a.id
WHERE a.skill_level = 'L1'
GROUP BY a.id, a.name
HAVING COUNT(DISTINCT i.id) >= 10
ORDER BY escalation_rate DESC
LIMIT 10;
```

## Task 6: Problem Record Impact
**User**: What problems affected the most customers?
**Assistant**: Finding high-impact problems:
```sql
SELECT 
    pr.id,
    pr.problem_statement,
    i.category,
    pr.affected_customers,
    pr.status,
    pr.created_at
FROM problem_records pr
JOIN issues i ON pr.root_issue_id = i.id
ORDER BY pr.affected_customers DESC
LIMIT 10;
```

**User**: Show resolution timeline for these problems
**Assistant**: Analyzing problem resolution times:
```sql
SELECT 
    pr.id,
    pr.problem_statement,
    pr.status,
    CASE 
        WHEN pr.closed_at IS NOT NULL THEN
            CAST((julianday(pr.closed_at) - julianday(pr.created_at)) AS INTEGER)
        ELSE
            CAST((julianday('now') - julianday(pr.created_at)) AS INTEGER)
    END as days_open,
    pr.affected_customers
FROM problem_records pr
ORDER BY pr.affected_customers DESC
LIMIT 10;
```

## Task 7: Efficiency Pair - Customer Issue History
**User**: Show all issues for customer 'Customer_100'
**Assistant**: Fast uses customer index:
```sql fast
SELECT 
    i.id,
    i.category,
    i.severity,
    i.status,
    i.created_at,
    COUNT(e.id) as escalation_count
FROM issues i
JOIN customers c ON i.customer_id = c.id
LEFT JOIN escalations e ON i.id = e.issue_id
WHERE c.name = 'Customer_100'
GROUP BY i.id
ORDER BY i.created_at DESC;
```
```sql slow
SELECT 
    i.id,
    i.category,
    i.severity,
    i.status,
    i.created_at,
    COUNT(e.id) as escalation_count
FROM issues i
JOIN customers c ON i.customer_id = c.id
LEFT JOIN escalations e ON i.id = e.issue_id
WHERE LOWER(c.name) LIKE '%customer_100%'
GROUP BY i.id
ORDER BY i.created_at DESC;
```

## Task 8: Escalation Path Analysis
**User**: Show me the typical escalation paths
**Assistant**: Analyzing escalation patterns:
```sql
SELECT 
    a1.skill_level as from_level,
    a2.skill_level as to_level,
    e.escalation_reason,
    COUNT(*) as count
FROM escalations e
JOIN agents a1 ON e.from_agent_id = a1.id
JOIN agents a2 ON e.to_agent_id = a2.id
GROUP BY a1.skill_level, a2.skill_level, e.escalation_reason
ORDER BY count DESC;
```

## Task 9: High-Value Customer Service
**User**: How are we serving platinum customers?
**Assistant**: Analyzing platinum tier metrics:
```sql
SELECT 
    COUNT(*) as total_issues,
    AVG(CASE 
        WHEN resolved_at IS NOT NULL THEN
            (julianday(resolved_at) - julianday(created_at)) * 24
    END) as avg_resolution_hours,
    COUNT(CASE WHEN status = 'RESOLVED' THEN 1 END) * 100.0 / COUNT(*) as resolution_rate,
    COUNT(DISTINCT e.issue_id) * 100.0 / COUNT(*) as escalation_rate
FROM issues i
JOIN customers c ON i.customer_id = c.id
LEFT JOIN escalations e ON i.id = e.issue_id
WHERE c.tier = 'PLATINUM';
```

**User**: Compare resolution times across tiers
**Assistant**: Tier comparison:
```sql
SELECT 
    c.tier,
    COUNT(*) as issues,
    AVG(CASE 
        WHEN i.resolved_at IS NOT NULL THEN
            (julianday(i.resolved_at) - julianday(i.created_at)) * 24
    END) as avg_hours,
    MIN(CASE 
        WHEN i.resolved_at IS NOT NULL THEN
            (julianday(i.resolved_at) - julianday(i.created_at)) * 24
    END) as fastest_hours
FROM issues i
JOIN customers c ON i.customer_id = c.id
WHERE i.resolved_at IS NOT NULL
GROUP BY c.tier
ORDER BY c.tier;
```

## Task 10: Category Analysis
**User**: Which issue categories take longest to resolve?
**Assistant**: Resolution time by category:
```sql
SELECT 
    category,
    COUNT(*) as total_issues,
    AVG(CASE 
        WHEN resolved_at IS NOT NULL THEN
            (julianday(resolved_at) - julianday(created_at)) * 24
    END) as avg_resolution_hours,
    COUNT(CASE WHEN resolved_at IS NULL THEN 1 END) as unresolved
FROM issues
GROUP BY category
ORDER BY avg_resolution_hours DESC;
```

## Task 11: Efficiency Pair - Active Critical Issues
**User**: Show all open critical issues
**Assistant**: Fast uses severity and status indexes:
```sql fast
SELECT 
    i.id,
    c.name as customer,
    c.tier,
    i.category,
    i.created_at,
    (julianday('now') - julianday(i.created_at)) * 24 as hours_open
FROM issues i
JOIN customers c ON i.customer_id = c.id
WHERE i.severity = 'CRITICAL' AND i.status IN ('OPEN', 'IN_PROGRESS', 'ESCALATED')
ORDER BY i.created_at;
```
```sql slow
SELECT 
    i.id,
    c.name as customer,
    c.tier,
    i.category,
    i.created_at,
    (julianday('now') - julianday(i.created_at)) * 24 as hours_open
FROM issues i
JOIN customers c ON i.customer_id = c.id
WHERE UPPER(i.severity) = 'CRITICAL' AND i.status NOT IN ('RESOLVED', 'CLOSED')
ORDER BY i.created_at;
```

## Task 12: Evidence - Resolution Targets
**User**: What are the resolution time targets by severity?
**Assistant**: Checking SLA policy:
```sql
SELECT 
    json_extract(value, '$.resolution_targets.CRITICAL') as critical_hours,
    json_extract(value, '$.resolution_targets.HIGH') as high_hours,
    json_extract(value, '$.resolution_targets.MEDIUM') as medium_hours,
    json_extract(value, '$.resolution_targets.LOW') as low_hours
FROM evidence_kv 
WHERE key = 'sla_policy';
```

## Task 13: Multi-Escalation Issues
**User**: Which issues got escalated multiple times?
**Assistant**: Finding complex issues:
```sql
SELECT 
    i.id,
    i.category,
    i.severity,
    c.tier as customer_tier,
    COUNT(e.id) as escalation_count,
    GROUP_CONCAT(a.name || ' (' || a.skill_level || ')', ' -> ') as escalation_chain
FROM issues i
JOIN customers c ON i.customer_id = c.id
JOIN escalations e ON i.id = e.issue_id
JOIN agents a ON e.to_agent_id = a.id
GROUP BY i.id
HAVING COUNT(e.id) >= 2
ORDER BY COUNT(e.id) DESC;
```

## Task 14: Department Workload
**User**: How's the workload distributed across departments?
**Assistant**: Department analysis:
```sql
SELECT 
    a.department,
    COUNT(DISTINCT i.id) as issues_created,
    COUNT(DISTINCT e_in.issue_id) as issues_received,
    COUNT(DISTINCT CASE WHEN i.status = 'RESOLVED' THEN i.id END) as resolved,
    AVG(i.impact_score) as avg_impact
FROM agents a
LEFT JOIN issues i ON a.id = i.created_by_agent_id
LEFT JOIN escalations e_in ON a.id = e_in.to_agent_id
GROUP BY a.department
ORDER BY issues_created + issues_received DESC;
```

## Task 15: Trend Analysis
**User**: Show daily issue volume trend
**Assistant**: Daily issue metrics:
```sql
WITH daily_stats AS (
    SELECT 
        DATE(created_at) as date,
        COUNT(*) as new_issues,
        COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END) as critical_issues,
        COUNT(CASE WHEN resolved_at IS NOT NULL 
                   AND DATE(resolved_at) = DATE(created_at) THEN 1 END) as same_day_resolutions
    FROM issues
    WHERE created_at >= DATE('now', '-14 days')
    GROUP BY DATE(created_at)
)
SELECT 
    date,
    new_issues,
    critical_issues,
    same_day_resolutions,
    same_day_resolutions * 100.0 / new_issues as same_day_rate
FROM daily_stats
ORDER BY date DESC;
```

**User**: What's the escalation trend?
**Assistant**: Escalation trend analysis:
```sql
SELECT 
    DATE(e.escalated_at) as date,
    COUNT(*) as escalations,
    COUNT(DISTINCT e.issue_id) as unique_issues,
    COUNT(CASE WHEN e.escalation_reason = 'SLA_BREACH' THEN 1 END) as sla_escalations
FROM escalations e
WHERE e.escalated_at >= DATE('now', '-14 days')
GROUP BY DATE(e.escalated_at)
ORDER BY date DESC;
```