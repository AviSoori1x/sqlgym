# Workflow Tasks

## Task: conversation quality rollup
```sql
-- step: base
CREATE TEMP TABLE base AS
SELECT conversation_id, AVG(score) s FROM qa_scores GROUP BY conversation_id;
```
```sql
-- step: flag
-- depends: base
CREATE TEMP TABLE flag AS
SELECT conversation_id FROM base WHERE s<0.8;
```
```sql
-- step: final
-- depends: flag
SELECT COUNT(*) FROM flag;
```

## Task: ticket aging
```sql
-- step: open
CREATE TEMP TABLE open AS
SELECT id, opened_at FROM tickets WHERE status='OPEN';
```
```sql
-- step: aged
-- depends: open
SELECT id FROM open WHERE opened_at<'2024-01-05';
```

## Task: customer_journey_analysis
```sql
-- step: recent_interactions
CREATE TEMP TABLE recent_interactions AS
SELECT 
    c.customer_id,
    c.conversation_start,
    c.channel,
    c.resolved,
    e.escalation_reason
FROM conversations c
LEFT JOIN escalations e ON c.id = e.conversation_id
WHERE c.conversation_start >= DATE('now', '-30 days');
```
```sql
-- step: training_progress
-- depends: recent_interactions
CREATE TEMP TABLE training_progress AS
SELECT 
    ri.customer_id,
    COUNT(DISTINCT e.program_id) as programs_enrolled,
    COUNT(DISTINCT CASE WHEN e.status = 'COMPLETED' THEN e.program_id END) as programs_completed
FROM recent_interactions ri
JOIN enrollments e ON ri.customer_id = e.customer_id
GROUP BY ri.customer_id;
```
```sql
-- step: satisfaction_scores
-- depends: training_progress
CREATE TEMP TABLE satisfaction_scores AS
SELECT 
    tp.customer_id,
    AVG(sr.response_value) as avg_satisfaction,
    tp.programs_completed
FROM training_progress tp
JOIN survey_responses sr ON tp.customer_id = sr.customer_id
WHERE sr.question_id IN (SELECT id FROM survey_questions WHERE question_type = 'RATING')
GROUP BY tp.customer_id;
```
```sql
-- step: journey_summary
-- depends: satisfaction_scores
SELECT 
    COUNT(DISTINCT customer_id) as total_customers,
    AVG(avg_satisfaction) as overall_satisfaction,
    AVG(programs_completed) as avg_programs_completed,
    COUNT(CASE WHEN avg_satisfaction >= 4 AND programs_completed >= 2 THEN 1 END) as successful_journeys
FROM satisfaction_scores;
```

## Task: workforce_optimization
```sql
-- step: skill_gaps
CREATE TEMP TABLE skill_gaps AS
SELECT 
    s.name as skill_name,
    s.category,
    COUNT(DISTINCT ask.agent_id) as current_agents,
    20 as required_agents,
    20 - COUNT(DISTINCT ask.agent_id) as gap
FROM skills s
LEFT JOIN agent_skills ask ON s.id = ask.skill_id AND ask.proficiency_level >= 3
WHERE s.requires_certification = 1
GROUP BY s.id
HAVING gap > 0;
```
```sql
-- step: shift_coverage
-- depends: skill_gaps
CREATE TEMP TABLE shift_coverage AS
SELECT 
    sh.shift_date,
    sh.shift_type,
    sh.required_agents,
    COUNT(DISTINCT sc.agent_id) as scheduled,
    sh.required_agents - COUNT(DISTINCT sc.agent_id) as shortage
FROM shifts sh
LEFT JOIN schedules sc ON sh.id = sc.shift_id
WHERE sh.shift_date >= DATE('now')
  AND sh.shift_date < DATE('now', '+7 days')
GROUP BY sh.id;
```
```sql
-- step: available_agents
-- depends: shift_coverage
CREATE TEMP TABLE available_agents AS
SELECT 
    a.id,
    a.name,
    a.skill_level,
    COUNT(DISTINCT ask.skill_id) as skill_count
FROM agents a
LEFT JOIN agent_skills ask ON a.id = ask.agent_id
WHERE a.status = 'ACTIVE'
  AND a.id NOT IN (
    SELECT agent_id FROM time_off_requests 
    WHERE status = 'APPROVED' 
    AND DATE('now') BETWEEN start_date AND end_date
  )
GROUP BY a.id;
```
```sql
-- step: optimization_report
-- depends: available_agents, skill_gaps, shift_coverage
SELECT 
    (SELECT COUNT(*) FROM skill_gaps) as critical_skill_gaps,
    (SELECT SUM(shortage) FROM shift_coverage WHERE shortage > 0) as total_shift_shortage,
    (SELECT COUNT(*) FROM available_agents) as available_agent_pool,
    (SELECT AVG(skill_count) FROM available_agents) as avg_skills_per_agent;
```

## Task: return_fraud_detection
```sql
-- step: high_return_customers
CREATE TEMP TABLE high_return_customers AS
SELECT 
    c.id as customer_id,
    c.email,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT r.id) as total_returns,
    COUNT(DISTINCT r.id) * 1.0 / COUNT(DISTINCT o.id) as return_rate
FROM customers c
JOIN orders o ON c.id = o.customer_id
LEFT JOIN rma_requests r ON c.id = r.customer_id
WHERE o.status = 'DELIVERED'
GROUP BY c.id
HAVING return_rate > 0.3 AND total_orders >= 5;
```
```sql
-- step: return_patterns
-- depends: high_return_customers
CREATE TEMP TABLE return_patterns AS
SELECT 
    hrc.customer_id,
    hrc.return_rate,
    COUNT(DISTINCT CASE WHEN r.reason = 'NOT_AS_DESCRIBED' THEN r.id END) as not_as_described,
    COUNT(DISTINCT CASE WHEN r.reason = 'CHANGED_MIND' THEN r.id END) as changed_mind,
    AVG(julianday(r.request_date) - julianday(o.order_date)) as avg_days_to_return
FROM high_return_customers hrc
JOIN rma_requests r ON hrc.customer_id = r.customer_id
JOIN order_items oi ON r.order_item_id = oi.id
JOIN orders o ON oi.order_id = o.id
GROUP BY hrc.customer_id;
```
```sql
-- step: product_correlation
-- depends: return_patterns
CREATE TEMP TABLE product_correlation AS
SELECT 
    rp.customer_id,
    p.category,
    COUNT(DISTINCT r.id) as category_returns
FROM return_patterns rp
JOIN rma_requests r ON rp.customer_id = r.customer_id
JOIN order_items oi ON r.order_item_id = oi.id
JOIN products p ON oi.product_id = p.id
GROUP BY rp.customer_id, p.category;
```
```sql
-- step: fraud_risk_summary
-- depends: product_correlation, return_patterns
SELECT 
    COUNT(DISTINCT rp.customer_id) as suspicious_customers,
    AVG(rp.return_rate) as avg_return_rate,
    MAX(rp.return_rate) as max_return_rate,
    COUNT(DISTINCT CASE WHEN pc.category_returns > 5 THEN pc.customer_id END) as serial_returners,
    AVG(rp.avg_days_to_return) as avg_return_timing
FROM return_patterns rp
LEFT JOIN product_correlation pc ON rp.customer_id = pc.customer_id;
```