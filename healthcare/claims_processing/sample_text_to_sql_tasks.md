# Sample Tasks for anthem_claims_system

## Task 1: Claims Processing Performance
**User**: What's our overall claims processing performance this month?
**Assistant**: I'll analyze claims processing metrics for the current month.
```sql
SELECT 
    ip.plan_type,
    COUNT(*) as total_claims,
    COUNT(CASE WHEN mc.status = 'APPROVED' THEN 1 END) as approved_claims,
    COUNT(CASE WHEN mc.status = 'DENIED' THEN 1 END) as denied_claims,
    COUNT(CASE WHEN mc.status = 'PAID' THEN 1 END) as paid_claims,
    AVG(ca.processing_time_hours) as avg_processing_hours,
    SUM(mc.total_charged_amount) as total_charged,
    SUM(cli.paid_amount) as total_paid
FROM medical_claims mc
JOIN insurance_plans ip ON mc.plan_id = ip.id
LEFT JOIN claim_adjudications ca ON mc.id = ca.claim_id
LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
WHERE mc.submission_date >= DATE('now', 'start of month')
GROUP BY ip.plan_type
ORDER BY total_claims DESC;
```

**User**: Which plan types have the highest denial rates?
**Assistant**: Analyzing denial rates by plan type:
```sql
SELECT 
    ip.plan_type,
    COUNT(*) as total_claims,
    COUNT(CASE WHEN mc.status = 'DENIED' THEN 1 END) as denied_claims,
    COUNT(CASE WHEN mc.status = 'DENIED' THEN 1 END) * 100.0 / COUNT(*) as denial_rate,
    AVG(mc.total_charged_amount) as avg_claim_amount
FROM medical_claims mc
JOIN insurance_plans ip ON mc.plan_id = ip.id
WHERE mc.submission_date >= DATE('now', '-90 days')
GROUP BY ip.plan_type
HAVING COUNT(*) >= 100
ORDER BY denial_rate DESC;
```

## Task 2: Provider Analysis
**User**: Which providers have the highest clean claim rates?
**Assistant**: Analyzing provider claim submission quality:
```sql
SELECT 
    p.npi,
    p.provider_name,
    p.specialty,
    COUNT(mc.id) as claims_submitted,
    COUNT(CASE WHEN ca.decision = 'APPROVED' THEN 1 END) as approved_claims,
    COUNT(CASE WHEN ca.decision = 'DENIED' THEN 1 END) as denied_claims,
    COUNT(CASE WHEN ca.decision = 'APPROVED' THEN 1 END) * 100.0 / COUNT(mc.id) as clean_claim_rate,
    SUM(cli.paid_amount) as total_payments_received
FROM providers p
JOIN medical_claims mc ON p.id = mc.provider_id
LEFT JOIN claim_adjudications ca ON mc.id = ca.claim_id
LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
WHERE mc.submission_date >= DATE('now', '-90 days')
GROUP BY p.id
HAVING COUNT(mc.id) >= 20
ORDER BY clean_claim_rate DESC
LIMIT 20;
```

## Task 3: Efficiency Pair - Member Claim History
**User**: Show claim history for member MBR0001000
**Assistant**: Fast query uses member_id unique constraint:
```sql fast
SELECT 
    mc.claim_number,
    mc.service_date,
    p.provider_name,
    mc.claim_type,
    mc.total_charged_amount,
    mc.status,
    SUM(cli.paid_amount) as total_paid
FROM medical_claims mc
JOIN members m ON mc.member_id = m.id
JOIN providers p ON mc.provider_id = p.id
LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
WHERE m.member_id = 'MBR0001000'
GROUP BY mc.id
ORDER BY mc.service_date DESC;
```
```sql slow
SELECT 
    mc.claim_number,
    mc.service_date,
    p.provider_name,
    mc.claim_type,
    mc.total_charged_amount,
    mc.status,
    SUM(cli.paid_amount) as total_paid
FROM medical_claims mc
JOIN members m ON mc.member_id = m.id
JOIN providers p ON mc.provider_id = p.id
LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
WHERE m.member_id LIKE '%001000%'
GROUP BY mc.id
ORDER BY mc.service_date DESC;
```

## Task 4: Evidence - Denial Code Guidelines
**User**: What are the common denial codes and their meanings?
**Assistant**: Checking denial code reference:
```sql
SELECT json_extract(value, '$.denial_codes') as denial_code_guide
FROM evidence_kv 
WHERE key = 'claims_processing_guidelines';
```

## Task 5: Denial Analysis
**User**: What are the most common reasons for claim denials?
**Assistant**: Analyzing denial patterns:
```sql
SELECT 
    cd.denial_category,
    cd.denial_code,
    cd.denial_reason,
    COUNT(*) as denial_count,
    SUM(cd.denial_amount) as total_denied_amount,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claim_denials) as percentage_of_denials,
    COUNT(CASE WHEN cd.is_appealable = 1 THEN 1 END) as appealable_denials
FROM claim_denials cd
WHERE cd.denial_date >= DATE('now', '-90 days')
GROUP BY cd.denial_category, cd.denial_code, cd.denial_reason
ORDER BY denial_count DESC
LIMIT 15;
```

**User**: Which specialties have the highest denial rates?
**Assistant**: Denial rates by provider specialty:
```sql
SELECT 
    p.specialty,
    COUNT(DISTINCT mc.id) as total_claims,
    COUNT(DISTINCT cd.claim_id) as denied_claims,
    COUNT(DISTINCT cd.claim_id) * 100.0 / COUNT(DISTINCT mc.id) as denial_rate,
    SUM(cd.denial_amount) as total_denied_amount,
    AVG(cd.denial_amount) as avg_denial_amount
FROM providers p
JOIN medical_claims mc ON p.id = mc.provider_id
LEFT JOIN claim_denials cd ON mc.id = cd.claim_id
WHERE mc.submission_date >= DATE('now', '-90 days')
GROUP BY p.specialty
HAVING COUNT(DISTINCT mc.id) >= 50
ORDER BY denial_rate DESC;
```

## Task 6: Prior Authorization Analysis
**User**: How effective is our prior authorization process?
**Assistant**: Prior authorization effectiveness analysis:
```sql
SELECT 
    pa.status,
    COUNT(*) as auth_requests,
    AVG(julianday(pa.approval_date) - julianday(pa.requested_date)) as avg_approval_days,
    COUNT(CASE WHEN mc.id IS NOT NULL THEN 1 END) as claims_with_auth,
    COUNT(CASE WHEN mc.status = 'APPROVED' THEN 1 END) as approved_claims_with_auth,
    COUNT(CASE WHEN mc.status = 'APPROVED' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN mc.id IS NOT NULL THEN 1 END), 0) as auth_claim_approval_rate
FROM prior_authorizations pa
LEFT JOIN medical_claims mc ON pa.member_id = mc.member_id 
    AND pa.service_code IN (
        SELECT json_extract(cli.procedure_code, '$') 
        FROM claim_line_items cli 
        WHERE cli.claim_id = mc.id
    )
WHERE pa.requested_date >= DATE('now', '-180 days')
GROUP BY pa.status
ORDER BY auth_requests DESC;
```

## Task 7: Efficiency Pair - High-Value Claims
**User**: Show claims over $10,000 from last month
**Assistant**: Fast uses service date index:
```sql fast
SELECT 
    mc.claim_number,
    m.member_id,
    p.provider_name,
    mc.service_date,
    mc.total_charged_amount,
    mc.status
FROM medical_claims mc
JOIN members m ON mc.member_id = m.id
JOIN providers p ON mc.provider_id = p.id
WHERE mc.total_charged_amount > 10000
  AND mc.service_date >= DATE('now', '-30 days')
ORDER BY mc.total_charged_amount DESC;
```
```sql slow
SELECT 
    mc.claim_number,
    m.member_id,
    p.provider_name,
    mc.service_date,
    mc.total_charged_amount,
    mc.status
FROM medical_claims mc
JOIN members m ON mc.member_id = m.id
JOIN providers p ON mc.provider_id = p.id
WHERE mc.total_charged_amount > 10000
  AND substr(mc.service_date, 1, 7) = strftime('%Y-%m', DATE('now', '-1 month'))
ORDER BY mc.total_charged_amount DESC;
```

## Task 8: Auto-Adjudication Performance
**User**: How well is our auto-adjudication system performing?
**Assistant**: Auto-adjudication analysis:
```sql
SELECT 
    ca.auto_adjudicated,
    COUNT(*) as total_adjudications,
    COUNT(CASE WHEN ca.decision = 'APPROVED' THEN 1 END) as approved_count,
    COUNT(CASE WHEN ca.decision = 'DENIED' THEN 1 END) as denied_count,
    AVG(ca.processing_time_hours) as avg_processing_hours,
    COUNT(CASE WHEN ca.decision = 'APPROVED' THEN 1 END) * 100.0 / COUNT(*) as approval_rate
FROM claim_adjudications ca
WHERE ca.adjudication_date >= DATE('now', '-30 days')
GROUP BY ca.auto_adjudicated
ORDER BY ca.auto_adjudicated DESC;
```

## Task 9: Member Cost Analysis
**User**: What are members paying out-of-pocket by plan type?
**Assistant**: Member cost burden analysis:
```sql
SELECT 
    ip.plan_type,
    COUNT(DISTINCT m.id) as members_with_claims,
    COUNT(mc.id) as total_claims,
    AVG(cli.copay_amount + cli.deductible_amount + cli.coinsurance_amount) as avg_member_cost_per_claim,
    SUM(cli.copay_amount + cli.deductible_amount + cli.coinsurance_amount) as total_member_costs,
    SUM(cli.paid_amount) as total_plan_payments,
    SUM(cli.copay_amount + cli.deductible_amount + cli.coinsurance_amount) / 
        (SUM(cli.paid_amount) + SUM(cli.copay_amount + cli.deductible_amount + cli.coinsurance_amount)) as member_cost_share
FROM medical_claims mc
JOIN members m ON mc.member_id = m.id
JOIN insurance_plans ip ON mc.plan_id = ip.id
LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
WHERE mc.service_date >= DATE('now', '-90 days')
  AND cli.paid_amount > 0
GROUP BY ip.plan_type
ORDER BY avg_member_cost_per_claim DESC;
```

## Task 10: Efficiency Pair - Provider Claims Today
**User**: Show claims submitted by providers today
**Assistant**: Fast uses submission date index:
```sql fast
SELECT 
    p.provider_name,
    p.specialty,
    COUNT(*) as claims_today,
    SUM(mc.total_charged_amount) as total_charges
FROM medical_claims mc
JOIN providers p ON mc.provider_id = p.id
WHERE DATE(mc.submission_date) = DATE('now')
GROUP BY p.id
ORDER BY claims_today DESC;
```
```sql slow
SELECT 
    p.provider_name,
    p.specialty,
    COUNT(*) as claims_today,
    SUM(mc.total_charged_amount) as total_charges
FROM medical_claims mc
JOIN providers p ON mc.provider_id = p.id
WHERE substr(mc.submission_date, 1, 10) = DATE('now')
GROUP BY p.id
ORDER BY claims_today DESC;
```

## Task 11: Procedure Code Analysis
**User**: Which procedure codes generate the most revenue?
**Assistant**: Top revenue-generating procedures:
```sql
SELECT 
    cli.procedure_code,
    COUNT(*) as claim_line_count,
    SUM(cli.charged_amount) as total_charged,
    SUM(cli.paid_amount) as total_paid,
    AVG(cli.paid_amount) as avg_payment_per_service,
    COUNT(DISTINCT mc.provider_id) as providers_billing_code,
    SUM(cli.paid_amount) / SUM(cli.charged_amount) as payment_to_charge_ratio
FROM claim_line_items cli
JOIN medical_claims mc ON cli.claim_id = mc.id
WHERE mc.service_date >= DATE('now', '-90 days')
  AND cli.paid_amount > 0
GROUP BY cli.procedure_code
HAVING COUNT(*) >= 100
ORDER BY total_paid DESC
LIMIT 20;
```

## Task 12: Evidence - Coverage Guidelines
**User**: What are the coverage criteria for specialty procedures?
**Assistant**: Checking coverage policies:
```sql
SELECT json_extract(value, '$.specialty_coverage_criteria') as coverage_rules
FROM evidence_kv 
WHERE key = 'claims_processing_guidelines';
```

## Task 13: Geographic Analysis
**User**: How do claim patterns vary by state?
**Assistant**: Geographic claim distribution:
```sql
WITH state_claims AS (
    SELECT 
        SUBSTR(m.address, -2) as state, -- Simplified state extraction
        COUNT(mc.id) as claim_count,
        SUM(mc.total_charged_amount) as total_charges,
        SUM(cli.paid_amount) as total_payments,
        COUNT(CASE WHEN mc.status = 'DENIED' THEN 1 END) as denied_claims
    FROM medical_claims mc
    JOIN members m ON mc.member_id = m.id
    LEFT JOIN claim_line_items cli ON mc.id = cli.claim_id
    WHERE mc.service_date >= DATE('now', '-90 days')
    GROUP BY state
)
SELECT 
    state,
    claim_count,
    total_charges,
    total_payments,
    denied_claims,
    denied_claims * 100.0 / claim_count as denial_rate,
    total_payments / total_charges as payment_ratio
FROM state_claims
WHERE claim_count >= 50
ORDER BY claim_count DESC;
```

## Task 14: Processing Time Analysis
**User**: How long does it take to process different types of claims?
**Assistant**: Claims processing time analysis:
```sql
SELECT 
    mc.claim_type,
    mc.place_of_service,
    COUNT(ca.id) as processed_claims,
    AVG(ca.processing_time_hours) as avg_processing_hours,
    MIN(ca.processing_time_hours) as fastest_processing,
    MAX(ca.processing_time_hours) as slowest_processing,
    COUNT(CASE WHEN ca.auto_adjudicated = 1 THEN 1 END) as auto_adjudicated,
    COUNT(CASE WHEN ca.auto_adjudicated = 1 THEN 1 END) * 100.0 / COUNT(ca.id) as auto_adj_rate
FROM medical_claims mc
JOIN claim_adjudications ca ON mc.id = ca.claim_id
WHERE ca.adjudication_date >= DATE('now', '-60 days')
GROUP BY mc.claim_type, mc.place_of_service
ORDER BY avg_processing_hours DESC;
```

## Task 15: Appeals and Overturns
**User**: What's our appeal and overturn rate?
**Assistant**: Appeals analysis (using denial data as proxy):
```sql
WITH denial_stats AS (
    SELECT 
        cd.denial_category,
        COUNT(*) as total_denials,
        SUM(cd.denial_amount) as total_denied_amount,
        COUNT(CASE WHEN cd.is_appealable = 1 THEN 1 END) as appealable_denials,
        AVG(julianday(cd.appeal_deadline) - julianday(cd.denial_date)) as avg_appeal_window_days
    FROM claim_denials cd
    WHERE cd.denial_date >= DATE('now', '-180 days')
    GROUP BY cd.denial_category
)
SELECT 
    denial_category,
    total_denials,
    appealable_denials,
    appealable_denials * 100.0 / total_denials as appealable_rate,
    total_denied_amount,
    avg_appeal_window_days,
    appealable_denials * 0.25 as estimated_appeals_filed,  -- Assuming 25% appeal rate
    appealable_denials * 0.25 * 0.30 as estimated_overturns  -- Assuming 30% overturn rate
FROM denial_stats
ORDER BY total_denials DESC;
```
