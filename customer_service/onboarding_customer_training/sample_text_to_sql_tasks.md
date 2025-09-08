# Sample Tasks for docusign_onboarding

## Task 1: Onboarding Completion Status
**User**: What percentage of customers have completed onboarding?
**Assistant**: I'll check completion of mandatory onboarding programs.
```sql
SELECT 
    COUNT(DISTINCT c.id) as total_customers,
    COUNT(DISTINCT CASE 
        WHEN NOT EXISTS (
            SELECT 1 FROM training_programs tp
            WHERE tp.is_mandatory = 1
            AND NOT EXISTS (
                SELECT 1 FROM enrollments e 
                WHERE e.customer_id = c.id 
                AND e.program_id = tp.id 
                AND e.status = 'COMPLETED'
            )
        ) THEN c.id 
    END) as onboarded_customers,
    COUNT(DISTINCT CASE 
        WHEN NOT EXISTS (
            SELECT 1 FROM training_programs tp
            WHERE tp.is_mandatory = 1
            AND NOT EXISTS (
                SELECT 1 FROM enrollments e 
                WHERE e.customer_id = c.id 
                AND e.program_id = tp.id 
                AND e.status = 'COMPLETED'
            )
        ) THEN c.id 
    END) * 100.0 / COUNT(DISTINCT c.id) as completion_rate
FROM customers c;
```

**User**: How does this vary by onboarding tier?
**Assistant**: Breaking down by tier:
```sql
SELECT 
    c.onboarding_tier,
    COUNT(DISTINCT c.id) as customers,
    COUNT(DISTINCT CASE 
        WHEN NOT EXISTS (
            SELECT 1 FROM training_programs tp
            WHERE tp.is_mandatory = 1
            AND NOT EXISTS (
                SELECT 1 FROM enrollments e 
                WHERE e.customer_id = c.id 
                AND e.program_id = tp.id 
                AND e.status = 'COMPLETED'
            )
        ) THEN c.id 
    END) * 100.0 / COUNT(DISTINCT c.id) as completion_rate
FROM customers c
GROUP BY c.onboarding_tier
ORDER BY completion_rate DESC;
```

## Task 2: Training Program Effectiveness
**User**: Which programs have the highest completion rates?
**Assistant**: Analyzing program completion rates:
```sql
SELECT 
    tp.name,
    tp.program_type,
    tp.delivery_method,
    COUNT(e.id) as total_enrollments,
    COUNT(CASE WHEN e.status = 'COMPLETED' THEN 1 END) as completions,
    COUNT(CASE WHEN e.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(e.id) as completion_rate
FROM training_programs tp
LEFT JOIN enrollments e ON tp.id = e.program_id
GROUP BY tp.id
HAVING COUNT(e.id) >= 10
ORDER BY completion_rate DESC
LIMIT 10;
```

## Task 3: Efficiency Pair - Customer Progress Lookup
**User**: Show training progress for customer100@example.com
**Assistant**: Fast query uses email unique constraint:
```sql fast
SELECT 
    tp.name as program,
    tp.program_type,
    e.status,
    e.progress_percentage,
    e.enrolled_at,
    e.completed_at
FROM enrollments e
JOIN training_programs tp ON e.program_id = tp.id
JOIN customers c ON e.customer_id = c.id
WHERE c.email = 'customer100@example.com'
ORDER BY e.enrolled_at DESC;
```
```sql slow
SELECT 
    tp.name as program,
    tp.program_type,
    e.status,
    e.progress_percentage,
    e.enrolled_at,
    e.completed_at
FROM enrollments e
JOIN training_programs tp ON e.program_id = tp.id
JOIN customers c ON e.customer_id = c.id
WHERE LOWER(c.email) LIKE '%customer100%'
ORDER BY e.enrolled_at DESC;
```

## Task 4: Evidence - Learning Path Requirements
**User**: What's the recommended learning path for new customers?
**Assistant**: Checking learning path policy:
```sql
SELECT json_extract(value, '$.recommended_paths') as learning_paths
FROM evidence_kv 
WHERE key = 'onboarding_paths';
```

## Task 5: Time to Competency Analysis
**User**: How long does it take customers to complete their first program?
**Assistant**: Analyzing time to first completion:
```sql
SELECT 
    c.onboarding_tier,
    AVG(julianday(e.completed_at) - julianday(e.enrolled_at)) as avg_days_to_complete,
    MIN(julianday(e.completed_at) - julianday(e.enrolled_at)) as fastest_completion,
    MAX(julianday(e.completed_at) - julianday(e.enrolled_at)) as slowest_completion
FROM enrollments e
JOIN customers c ON e.customer_id = c.id
WHERE e.completed_at IS NOT NULL
  AND e.id = (
    SELECT MIN(e2.id) 
    FROM enrollments e2 
    WHERE e2.customer_id = e.customer_id 
    AND e2.completed_at IS NOT NULL
  )
GROUP BY c.onboarding_tier;
```

## Task 6: Module Performance Analysis
**User**: Which modules have the lowest pass rates?
**Assistant**: Finding challenging modules:
```sql
SELECT 
    m.name as module_name,
    tp.name as program_name,
    m.content_type,
    m.passing_score,
    COUNT(mp.id) as attempts,
    COUNT(CASE WHEN mp.score >= m.passing_score THEN 1 END) as passes,
    AVG(mp.score) as avg_score,
    COUNT(CASE WHEN mp.score >= m.passing_score THEN 1 END) * 100.0 / COUNT(mp.id) as pass_rate
FROM modules m
JOIN training_programs tp ON m.program_id = tp.id
LEFT JOIN module_progress mp ON m.id = mp.module_id
WHERE m.passing_score IS NOT NULL
GROUP BY m.id
HAVING COUNT(mp.id) >= 20
ORDER BY pass_rate ASC
LIMIT 10;
```

## Task 7: Efficiency Pair - Active Learners Today
**User**: Show customers with training activity today
**Assistant**: Fast uses date index:
```sql fast
SELECT DISTINCT
    c.name,
    c.email,
    c.onboarding_tier,
    COUNT(DISTINCT mp.module_id) as modules_accessed
FROM customers c
JOIN enrollments e ON c.id = e.customer_id
JOIN module_progress mp ON e.id = mp.enrollment_id
WHERE DATE(mp.started_at) = DATE('now')
GROUP BY c.id
ORDER BY modules_accessed DESC;
```
```sql slow
SELECT DISTINCT
    c.name,
    c.email,
    c.onboarding_tier,
    COUNT(DISTINCT mp.module_id) as modules_accessed
FROM customers c
JOIN enrollments e ON c.id = e.customer_id
JOIN module_progress mp ON e.id = mp.enrollment_id
WHERE substr(mp.started_at, 1, 10) = DATE('now')
GROUP BY c.id
ORDER BY modules_accessed DESC;
```

## Task 8: Certification Success Rate
**User**: What's the certification pass rate?
**Assistant**: Analyzing certification completions:
```sql
SELECT 
    tp.name as certification,
    COUNT(e.id) as enrolled,
    COUNT(CASE WHEN e.status = 'COMPLETED' THEN 1 END) as certified,
    COUNT(CASE WHEN e.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(e.id) as pass_rate,
    AVG(CASE WHEN e.completed_at IS NOT NULL 
        THEN julianday(e.completed_at) - julianday(e.enrolled_at) 
    END) as avg_days_to_certify
FROM training_programs tp
JOIN enrollments e ON tp.id = e.program_id
WHERE tp.program_type = 'CERTIFICATION'
GROUP BY tp.id
ORDER BY pass_rate DESC;
```

## Task 9: Dropout Analysis
**User**: When do customers typically drop out?
**Assistant**: Analyzing dropout patterns:
```sql
SELECT 
    tp.program_type,
    tp.difficulty_level,
    AVG(e.progress_percentage) as avg_progress_at_dropout,
    COUNT(*) as dropout_count,
    AVG(julianday(e.started_at) - julianday(e.enrolled_at)) as avg_days_before_start
FROM enrollments e
JOIN training_programs tp ON e.program_id = tp.id
WHERE e.status = 'DROPPED'
GROUP BY tp.program_type, tp.difficulty_level
ORDER BY dropout_count DESC;
```

**User**: Which specific programs have highest dropout?
**Assistant**: Program-specific dropout rates:
```sql
SELECT 
    tp.name,
    tp.duration_hours,
    COUNT(e.id) as total_enrolled,
    COUNT(CASE WHEN e.status = 'DROPPED' THEN 1 END) as dropouts,
    COUNT(CASE WHEN e.status = 'DROPPED' THEN 1 END) * 100.0 / COUNT(e.id) as dropout_rate,
    AVG(CASE WHEN e.status = 'DROPPED' THEN e.progress_percentage END) as avg_progress_at_dropout
FROM training_programs tp
JOIN enrollments e ON tp.id = e.program_id
GROUP BY tp.id
HAVING COUNT(e.id) >= 50
ORDER BY dropout_rate DESC
LIMIT 10;
```

## Task 10: Learning Velocity
**User**: How fast are different customer segments learning?
**Assistant**: Measuring learning velocity by segment:
```sql
SELECT 
    c.company_size,
    c.onboarding_tier,
    COUNT(DISTINCT c.id) as customers,
    AVG(completed_programs) as avg_programs_completed,
    AVG(months_active) as avg_months_active,
    AVG(CAST(completed_programs AS REAL) / months_active) as programs_per_month
FROM (
    SELECT 
        c.id,
        c.company_size,
        c.onboarding_tier,
        COUNT(CASE WHEN e.status = 'COMPLETED' THEN 1 END) as completed_programs,
        (julianday('now') - julianday(MIN(e.enrolled_at))) / 30 as months_active
    FROM customers c
    JOIN enrollments e ON c.id = e.customer_id
    GROUP BY c.id
    HAVING months_active > 0
) c
GROUP BY c.company_size, c.onboarding_tier
ORDER BY programs_per_month DESC;
```

## Task 11: Efficiency Pair - Prerequisites Check
**User**: Show programs that require Getting Started
**Assistant**: Fast uses program ID in prerequisites:
```sql fast
SELECT 
    tp.name,
    tp.program_type,
    tp.difficulty_level,
    tp.prerequisites
FROM training_programs tp
WHERE json_extract(tp.prerequisites, '$[0]') = 1
   OR json_extract(tp.prerequisites, '$[1]') = 1;
```
```sql slow
SELECT 
    tp.name,
    tp.program_type,
    tp.difficulty_level,
    tp.prerequisites
FROM training_programs tp
WHERE tp.prerequisites LIKE '%1%';
```

## Task 12: Evidence - Completion Targets
**User**: What are the onboarding completion targets by tier?
**Assistant**: Checking tier-specific targets:
```sql
SELECT 
    json_extract(value, '$.completion_targets.SELF_SERVICE') as self_service_target,
    json_extract(value, '$.completion_targets.STANDARD') as standard_target,
    json_extract(value, '$.completion_targets.PREMIUM') as premium_target,
    json_extract(value, '$.completion_targets.WHITE_GLOVE') as white_glove_target
FROM evidence_kv 
WHERE key = 'tier_targets';
```

## Task 13: Multi-attempt Analysis
**User**: Which quizzes require multiple attempts?
**Assistant**: Finding challenging assessments:
```sql
SELECT 
    m.name as quiz_name,
    tp.name as program_name,
    AVG(mp.attempts) as avg_attempts,
    MAX(mp.attempts) as max_attempts,
    COUNT(CASE WHEN mp.attempts > 1 THEN 1 END) * 100.0 / COUNT(*) as retry_rate,
    AVG(mp.score) as avg_final_score
FROM modules m
JOIN training_programs tp ON m.program_id = tp.id
JOIN module_progress mp ON m.id = mp.module_id
WHERE m.content_type = 'QUIZ'
  AND mp.completed_at IS NOT NULL
GROUP BY m.id
HAVING COUNT(*) >= 10
ORDER BY avg_attempts DESC;
```

## Task 14: Time Investment Analysis
**User**: How much time are customers spending on training?
**Assistant**: Analyzing time investment:
```sql
SELECT 
    c.onboarding_tier,
    COUNT(DISTINCT c.id) as customers,
    SUM(mp.time_spent_minutes) / 60.0 as total_hours,
    AVG(mp.time_spent_minutes) / 60.0 as avg_hours_per_module,
    SUM(mp.time_spent_minutes) / 60.0 / COUNT(DISTINCT c.id) as avg_hours_per_customer
FROM customers c
JOIN enrollments e ON c.id = e.customer_id
JOIN module_progress mp ON e.id = mp.enrollment_id
WHERE mp.time_spent_minutes IS NOT NULL
GROUP BY c.onboarding_tier
ORDER BY avg_hours_per_customer DESC;
```

## Task 15: Cohort Progress Tracking
**User**: Show this month's onboarding cohort progress
**Assistant**: Current month cohort analysis:
```sql
WITH current_cohort AS (
    SELECT 
        c.id,
        c.name,
        c.onboarding_tier,
        MIN(e.enrolled_at) as cohort_start
    FROM customers c
    JOIN enrollments e ON c.id = e.customer_id
    WHERE DATE(e.enrolled_at) >= DATE('now', 'start of month')
    GROUP BY c.id
)
SELECT 
    cc.onboarding_tier,
    COUNT(DISTINCT cc.id) as cohort_size,
    COUNT(DISTINCT CASE WHEN e.status = 'COMPLETED' THEN cc.id END) as with_completions,
    AVG(e.progress_percentage) as avg_progress,
    COUNT(DISTINCT CASE 
        WHEN tp.is_mandatory = 1 AND e.status = 'COMPLETED' THEN cc.id 
    END) as completed_mandatory
FROM current_cohort cc
LEFT JOIN enrollments e ON cc.id = e.customer_id
LEFT JOIN training_programs tp ON e.program_id = tp.id
GROUP BY cc.onboarding_tier
ORDER BY cohort_size DESC;
```

**User**: Compare to last month's cohort at same point
**Assistant**: Cohort comparison:
```sql
WITH last_month_cohort AS (
    SELECT 
        c.id,
        c.onboarding_tier,
        MIN(e.enrolled_at) as cohort_start
    FROM customers c
    JOIN enrollments e ON c.id = e.customer_id
    WHERE DATE(e.enrolled_at) >= DATE('now', 'start of month', '-1 month')
      AND DATE(e.enrolled_at) < DATE('now', 'start of month')
    GROUP BY c.id
)
SELECT 
    lmc.onboarding_tier,
    COUNT(DISTINCT lmc.id) as last_month_size,
    COUNT(DISTINCT CASE 
        WHEN e.status = 'COMPLETED' 
        AND julianday(e.completed_at) - julianday(lmc.cohort_start) <= julianday('now') - julianday(DATE('now', 'start of month'))
        THEN lmc.id 
    END) * 100.0 / COUNT(DISTINCT lmc.id) as completion_rate_at_same_point
FROM last_month_cohort lmc
LEFT JOIN enrollments e ON lmc.id = e.customer_id
GROUP BY lmc.onboarding_tier;
```