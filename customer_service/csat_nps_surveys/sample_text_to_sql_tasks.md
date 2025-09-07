# Sample Tasks for csat_nps_surveys

## Task 1: Overall NPS Score Calculation
**User**: What's our current NPS score?
**Assistant**: I'll calculate the Net Promoter Score.
```sql
SELECT 
    (COUNT(CASE WHEN score >= 9 THEN 1 END) - COUNT(CASE WHEN score <= 6 THEN 1 END)) * 100.0 / COUNT(*) as nps_score
FROM surveys
WHERE survey_type = 'NPS' AND score IS NOT NULL;
```

**User**: Break it down by segment
**Assistant**: NPS by customer segment:
```sql
SELECT 
    c.segment,
    (COUNT(CASE WHEN s.score >= 9 THEN 1 END) - COUNT(CASE WHEN s.score <= 6 THEN 1 END)) * 100.0 / COUNT(*) as nps_score
FROM surveys s
JOIN customers c ON s.customer_id = c.id
WHERE s.survey_type = 'NPS' AND s.score IS NOT NULL
GROUP BY c.segment;
```

## Task 2: CSAT Satisfaction Rate
**User**: What's our CSAT satisfaction rate?
**Assistant**: Calculating satisfaction rate (score 8+):
```sql
SELECT 
    COUNT(CASE WHEN score >= 8 THEN 1 END) * 100.0 / COUNT(*) as satisfaction_rate
FROM surveys
WHERE survey_type = 'CSAT' AND score IS NOT NULL;
```

## Task 3: Efficiency Pair - Response Rate by Date
**User**: Show survey response rates for last week
**Assistant**: Fast query uses date index:
```sql fast
SELECT 
    DATE(sent_at) as survey_date,
    COUNT(*) as total_sent,
    COUNT(CASE WHEN responded_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as response_rate
FROM surveys
WHERE sent_at >= DATE('now', '-7 days')
GROUP BY DATE(sent_at);
```
```sql slow
SELECT 
    substr(sent_at, 1, 10) as survey_date,
    COUNT(*) as total_sent,
    COUNT(CASE WHEN responded_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as response_rate
FROM surveys
WHERE sent_at LIKE '%2024-01%'
GROUP BY substr(sent_at, 1, 10);
```

## Task 4: Evidence - Survey Best Practices
**User**: What are the response time targets?
**Assistant**: Checking evidence:
```sql
SELECT json_extract(value, '$.response_time_targets') as targets
FROM evidence_kv 
WHERE key = 'survey_best_practices';
```

## Task 5: Follow-up Analysis
**User**: How many low scores get follow-ups?
**Assistant**: Analyzing follow-up rates:
```sql
SELECT 
    s.score,
    COUNT(*) as total_surveys,
    COUNT(f.id) as with_followup,
    COUNT(f.id) * 100.0 / COUNT(*) as followup_rate
FROM surveys s
LEFT JOIN follow_ups f ON s.id = f.survey_id
WHERE s.score <= 6
GROUP BY s.score;
```

## Task 6: Efficiency Pair - Customer History
**User**: Show surveys for customer100@example.com
**Assistant**: Fast uses unique email:
```sql fast
SELECT s.id, s.survey_type, s.score, s.sent_at
FROM surveys s
JOIN customers c ON s.customer_id = c.id
WHERE c.email = 'customer100@example.com';
```
```sql slow
SELECT s.id, s.survey_type, s.score, s.sent_at
FROM surveys s
JOIN customers c ON s.customer_id = c.id
WHERE LOWER(c.email) LIKE '%customer100%';
```

## Task 7: Trigger Event Analysis
**User**: Which events lead to best scores?
**Assistant**: Analyzing by trigger:
```sql
SELECT 
    st.trigger_event,
    AVG(s.score) as avg_score,
    COUNT(*) as count
FROM survey_triggers st
JOIN surveys s ON st.survey_id = s.id
WHERE s.score IS NOT NULL
GROUP BY st.trigger_event
ORDER BY avg_score DESC;
```

## Task 8: Channel Performance
**User**: Compare response rates by channel
**Assistant**: Channel analysis:
```sql
SELECT 
    t.channel,
    COUNT(*) as total,
    COUNT(CASE WHEN s.responded_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as response_rate
FROM surveys s
JOIN touchpoints t ON s.touchpoint_id = t.id
GROUP BY t.channel;
```

## Task 9: Monthly NPS Trend
**User**: Show NPS trend by month
**Assistant**: Monthly NPS calculation:
```sql
SELECT 
    strftime('%Y-%m', sent_at) as month,
    (COUNT(CASE WHEN score >= 9 THEN 1 END) - COUNT(CASE WHEN score <= 6 THEN 1 END)) * 100.0 / COUNT(*) as nps
FROM surveys
WHERE survey_type = 'NPS' AND score IS NOT NULL
GROUP BY month
ORDER BY month;
```

## Task 10: Negative Comment Search
**User**: Find surveys with complaints
**Assistant**: Searching negative feedback:
```sql
SELECT s.id, c.email, s.score, s.comment
FROM surveys s
JOIN customers c ON s.customer_id = c.id
WHERE s.comment LIKE '%disappoint%' OR s.comment LIKE '%poor%'
LIMIT 10;
```

## Task 11: Efficiency Pair - Score Distribution
**User**: Show NPS score distribution
**Assistant**: Fast uses score index:
```sql fast
SELECT score, COUNT(*) as count
FROM surveys
WHERE survey_type = 'NPS' AND score IS NOT NULL
GROUP BY score
ORDER BY score;
```
```sql slow
SELECT CAST(score AS TEXT) as score_text, COUNT(*) as count
FROM surveys
WHERE survey_type = 'NPS' AND score IS NOT NULL
GROUP BY CAST(score AS TEXT)
ORDER BY CAST(score_text AS INTEGER);
```

## Task 12: Survey Fatigue
**User**: Who's getting too many surveys?
**Assistant**: Finding over-surveyed customers:
```sql
SELECT 
    c.email,
    COUNT(*) as surveys_last_30_days
FROM customers c
JOIN surveys s ON c.id = s.customer_id
WHERE s.sent_at >= DATE('now', '-30 days')
GROUP BY c.email
HAVING COUNT(*) >= 3
ORDER BY COUNT(*) DESC;
```

## Task 13: CES Analysis
**User**: What's the average effort score?
**Assistant**: Analyzing effort scores:
```sql
SELECT 
    AVG(score) as avg_effort,
    COUNT(CASE WHEN score <= 3 THEN 1 END) * 100.0 / COUNT(*) as low_effort_pct
FROM surveys
WHERE survey_type = 'CES' AND score IS NOT NULL;
```

## Task 14: Touchpoint Performance
**User**: Which touchpoints have lowest satisfaction?
**Assistant**: Finding problem touchpoints:
```sql
SELECT 
    t.name,
    AVG(s.score) as avg_score,
    COUNT(*) as responses
FROM surveys s
JOIN touchpoints t ON s.touchpoint_id = t.id
WHERE s.survey_type = 'CSAT' AND s.score IS NOT NULL
GROUP BY t.name
HAVING COUNT(*) >= 10
ORDER BY avg_score ASC
LIMIT 5;
```

## Task 15: Multi-Survey Type Summary
**User**: Give me overview of all survey types
**Assistant**: Comprehensive metrics:
```sql
SELECT 
    survey_type,
    COUNT(*) as total_sent,
    COUNT(CASE WHEN responded_at IS NOT NULL THEN 1 END) as responses,
    AVG(score) as avg_score,
    COUNT(CASE WHEN responded_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as response_rate
FROM surveys
GROUP BY survey_type
ORDER BY survey_type;
```

**User**: Which type has best response rate?
**Assistant**: Comparing response rates:
```sql
SELECT 
    survey_type,
    COUNT(CASE WHEN responded_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as response_rate
FROM surveys
GROUP BY survey_type
ORDER BY response_rate DESC;
```
