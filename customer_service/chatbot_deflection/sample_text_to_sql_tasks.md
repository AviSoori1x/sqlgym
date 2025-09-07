# Sample Tasks for chatbot_deflection

## Task 1: Basic Deflection Rate
**User**: What's our chatbot deflection rate?
**Assistant**: I'll calculate the percentage of conversations successfully resolved by the bot without escalation.
```sql
SELECT 
    COUNT(CASE WHEN status = 'RESOLVED' THEN 1 END) * 100.0 / COUNT(*) as deflection_rate
FROM conversations c
LEFT JOIN escalations e ON c.id = e.conversation_id
WHERE e.id IS NULL;
```

**User**: Break that down by channel
**Assistant**: I'll show the deflection rate for each communication channel.
```sql
SELECT 
    channel,
    COUNT(CASE WHEN status = 'RESOLVED' THEN 1 END) * 100.0 / COUNT(*) as deflection_rate,
    COUNT(*) as total_conversations
FROM conversations c
LEFT JOIN escalations e ON c.id = e.conversation_id
WHERE e.id IS NULL
GROUP BY channel
ORDER BY deflection_rate DESC;
```

## Task 2: Intent Analysis with Confidence
**User**: Which intents have the lowest bot confidence?
**Assistant**: I'll find intents where the bot has low confidence scores on average.
```sql
SELECT 
    ic.name as intent,
    AVG(m.confidence_score) as avg_confidence,
    COUNT(DISTINCT m.conversation_id) as conversation_count
FROM messages m
JOIN intent_categories ic ON m.intent_id = ic.id
WHERE m.sender_type = 'BOT'
GROUP BY ic.name
HAVING AVG(m.confidence_score) < 0.8
ORDER BY avg_confidence ASC;
```

**User**: Show me conversations for the lowest confidence intent
**Assistant**: I'll get conversations for the intent with the lowest average confidence.
```sql
WITH lowest_intent AS (
    SELECT ic.id, ic.name
    FROM messages m
    JOIN intent_categories ic ON m.intent_id = ic.id
    WHERE m.sender_type = 'BOT'
    GROUP BY ic.id, ic.name
    ORDER BY AVG(m.confidence_score) ASC
    LIMIT 1
)
SELECT 
    c.id,
    c.started_at,
    c.status,
    li.name as intent
FROM conversations c
JOIN lowest_intent li ON c.primary_intent_id = li.id
LIMIT 10;
```

## Task 3: Efficiency Pair - Escalation Lookup
**User**: Show me all escalations from yesterday
**Assistant**: I'll find escalations from yesterday. The fast query uses the index on escalated_at.
```sql fast
SELECT 
    e.id,
    e.conversation_id,
    e.reason,
    e.escalated_at
FROM escalations e
WHERE DATE(e.escalated_at) = DATE('now', '-1 day')
ORDER BY e.escalated_at;
```
```sql slow
SELECT 
    e.id,
    e.conversation_id,
    e.reason,
    e.escalated_at
FROM escalations e
WHERE substr(e.escalated_at, 1, 10) = DATE('now', '-1 day')
ORDER BY e.escalated_at;
```

## Task 4: Evidence - Deflection Policy Check
**User**: What's our target deflection rate according to policy?
**Assistant**: I'll check the deflection policy from our evidence files.
```sql
SELECT json_extract(value, '$.target_deflection_rate') as target_rate
FROM evidence_kv 
WHERE key = 'deflection_policy';
```

**User**: Compare actual vs target by channel
**Assistant**: I'll compare our actual deflection rates against the policy target.
```sql
WITH actual_rates AS (
    SELECT 
        channel,
        COUNT(CASE WHEN status = 'RESOLVED' AND e.id IS NULL THEN 1 END) * 100.0 / COUNT(*) as actual_rate
    FROM conversations c
    LEFT JOIN escalations e ON c.id = e.conversation_id
    GROUP BY channel
),
target AS (
    SELECT json_extract(value, '$.target_deflection_rate') as target_rate
    FROM evidence_kv 
    WHERE key = 'deflection_policy'
)
SELECT 
    ar.channel,
    ar.actual_rate,
    t.target_rate,
    ar.actual_rate - t.target_rate as variance
FROM actual_rates ar
CROSS JOIN target t
ORDER BY variance DESC;
```

## Task 5: Customer Satisfaction Analysis
**User**: What's the average satisfaction score for deflected vs escalated conversations?
**Assistant**: I'll compare satisfaction between bot-resolved and agent-resolved conversations.
```sql
SELECT 
    CASE 
        WHEN e.id IS NULL THEN 'Bot Deflected'
        ELSE 'Agent Handled'
    END as resolution_type,
    AVG(c.satisfaction_score) as avg_satisfaction,
    COUNT(*) as total_conversations,
    COUNT(c.satisfaction_score) as rated_conversations
FROM conversations c
LEFT JOIN escalations e ON c.id = e.conversation_id
WHERE c.status IN ('RESOLVED', 'ESCALATED')
GROUP BY resolution_type;
```

**User**: Which intents have the worst satisfaction when deflected?
**Assistant**: I'll find intents with poor satisfaction scores for bot-resolved conversations.
```sql
SELECT 
    ic.name as intent,
    AVG(c.satisfaction_score) as avg_satisfaction,
    COUNT(*) as conversation_count
FROM conversations c
JOIN intent_categories ic ON c.primary_intent_id = ic.id
LEFT JOIN escalations e ON c.id = e.conversation_id
WHERE c.status = 'RESOLVED' 
    AND e.id IS NULL 
    AND c.satisfaction_score IS NOT NULL
GROUP BY ic.name
HAVING COUNT(*) >= 5
ORDER BY avg_satisfaction ASC
LIMIT 10;
```

## Task 6: Efficiency Pair - Message Volume by Hour
**User**: Show message volume by hour for today
**Assistant**: I'll calculate message counts by hour. The fast query extracts hour efficiently.
```sql fast
SELECT 
    strftime('%H', sent_at) as hour,
    COUNT(*) as message_count
FROM messages
WHERE DATE(sent_at) = DATE('now')
GROUP BY hour
ORDER BY hour;
```
```sql slow
SELECT 
    substr(sent_at, 12, 2) as hour,
    COUNT(*) as message_count
FROM messages
WHERE sent_at LIKE DATE('now') || '%'
GROUP BY hour
ORDER BY hour;
```

## Task 7: Complex Escalation Analysis
**User**: What are the main reasons for escalation?
**Assistant**: I'll analyze escalation reasons and their frequency.
```sql
SELECT 
    reason,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM escalations
GROUP BY reason
ORDER BY count DESC;
```

**User**: Which intents escalate most due to low confidence?
**Assistant**: I'll find intents that frequently escalate because of low bot confidence.
```sql
SELECT 
    ic.name as intent,
    COUNT(*) as low_confidence_escalations,
    COUNT(*) * 100.0 / total.cnt as escalation_rate
FROM escalations e
JOIN conversations c ON e.conversation_id = c.id
JOIN intent_categories ic ON c.primary_intent_id = ic.id
CROSS JOIN (SELECT COUNT(*) as cnt FROM escalations WHERE reason = 'LOW_CONFIDENCE') total
WHERE e.reason = 'LOW_CONFIDENCE'
GROUP BY ic.name, total.cnt
HAVING COUNT(*) >= 3
ORDER BY escalation_rate DESC;
```

**User**: What's the average confidence for those high-escalation intents?
**Assistant**: I'll check the average confidence scores for intents that frequently escalate.
```sql
WITH high_escalation_intents AS (
    SELECT c.primary_intent_id
    FROM escalations e
    JOIN conversations c ON e.conversation_id = c.id
    WHERE e.reason = 'LOW_CONFIDENCE'
    GROUP BY c.primary_intent_id
    HAVING COUNT(*) >= 3
)
SELECT 
    ic.name as intent,
    AVG(m.confidence_score) as avg_confidence,
    MIN(m.confidence_score) as min_confidence,
    MAX(m.confidence_score) as max_confidence
FROM messages m
JOIN intent_categories ic ON m.intent_id = ic.id
WHERE m.sender_type = 'BOT'
    AND m.intent_id IN (SELECT primary_intent_id FROM high_escalation_intents)
GROUP BY ic.name
ORDER BY avg_confidence ASC;
```

## Task 8: Efficiency Pair - Customer History
**User**: Find all conversations for customer email 'customer100@example.com'
**Assistant**: I'll retrieve conversation history for this customer. Fast query uses the unique email constraint.
```sql fast
SELECT 
    c.id,
    c.channel,
    c.started_at,
    c.status,
    ic.name as intent
FROM conversations c
JOIN customers cu ON c.customer_id = cu.id
LEFT JOIN intent_categories ic ON c.primary_intent_id = ic.id
WHERE cu.email = 'customer100@example.com'
ORDER BY c.started_at DESC;
```
```sql slow
SELECT 
    c.id,
    c.channel,
    c.started_at,
    c.status,
    ic.name as intent
FROM conversations c
JOIN customers cu ON c.customer_id = cu.id
LEFT JOIN intent_categories ic ON c.primary_intent_id = ic.id
WHERE cu.email LIKE '%customer100@example.com%'
ORDER BY c.started_at DESC;
```

## Task 9: Response Time Analysis
**User**: What's the average time to escalation?
**Assistant**: I'll calculate how long conversations run before escalation occurs.
```sql
SELECT 
    AVG(CAST((julianday(e.escalated_at) - julianday(c.started_at)) * 1440 AS INTEGER)) as avg_minutes_to_escalation,
    MIN(CAST((julianday(e.escalated_at) - julianday(c.started_at)) * 1440 AS INTEGER)) as min_minutes,
    MAX(CAST((julianday(e.escalated_at) - julianday(c.started_at)) * 1440 AS INTEGER)) as max_minutes
FROM escalations e
JOIN conversations c ON e.conversation_id = c.id;
```

**User**: Break that down by escalation reason
**Assistant**: I'll show average escalation time for each reason.
```sql
SELECT 
    e.reason,
    COUNT(*) as count,
    AVG(CAST((julianday(e.escalated_at) - julianday(c.started_at)) * 1440 AS INTEGER)) as avg_minutes,
    STDDEV(CAST((julianday(e.escalated_at) - julianday(c.started_at)) * 1440 AS INTEGER)) as stddev_minutes
FROM escalations e
JOIN conversations c ON e.conversation_id = c.id
GROUP BY e.reason
ORDER BY avg_minutes DESC;
```

## Task 10: Agent Performance Post-Escalation
**User**: How quickly do agents resolve escalated conversations?
**Assistant**: I'll analyze agent resolution times after escalation.
```sql
SELECT 
    AVG(CAST((julianday(e.resolved_at) - julianday(e.escalated_at)) * 1440 AS INTEGER)) as avg_resolution_minutes,
    COUNT(*) as resolved_count,
    COUNT(CASE WHEN e.resolved_at IS NULL THEN 1 END) as unresolved_count
FROM escalations e
WHERE e.agent_id IS NOT NULL;
```

**User**: Which agents are fastest at resolution?
**Assistant**: I'll rank agents by their average resolution speed.
```sql
SELECT 
    e.agent_id,
    COUNT(*) as escalations_handled,
    AVG(CASE 
        WHEN e.resolved_at IS NOT NULL 
        THEN CAST((julianday(e.resolved_at) - julianday(e.escalated_at)) * 1440 AS INTEGER)
        ELSE NULL 
    END) as avg_resolution_minutes,
    COUNT(CASE WHEN e.resolved_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) as resolution_rate
FROM escalations e
WHERE e.agent_id IS NOT NULL
GROUP BY e.agent_id
HAVING COUNT(*) >= 5
ORDER BY avg_resolution_minutes ASC
LIMIT 10;
```

## Task 11: Evidence - Intent Priority Alignment
**User**: Which high-priority intents are we handling well?
**Assistant**: I'll check performance on high-priority intents as defined in our system.
```sql
SELECT 
    ic.name as intent,
    ic.priority,
    COUNT(*) as total_conversations,
    COUNT(CASE WHEN c.status = 'RESOLVED' AND e.id IS NULL THEN 1 END) * 100.0 / COUNT(*) as deflection_rate,
    AVG(c.satisfaction_score) as avg_satisfaction
FROM intent_categories ic
JOIN conversations c ON c.primary_intent_id = ic.id
LEFT JOIN escalations e ON c.id = e.conversation_id
WHERE ic.priority = 'HIGH'
GROUP BY ic.name, ic.priority
ORDER BY deflection_rate DESC;
```

## Task 12: Conversation Flow Analysis
**User**: What's the average number of messages per conversation?
**Assistant**: I'll calculate message statistics across all conversations.
```sql
SELECT 
    AVG(msg_count) as avg_messages,
    MIN(msg_count) as min_messages,
    MAX(msg_count) as max_messages,
    STDDEV(msg_count) as stddev_messages
FROM (
    SELECT COUNT(*) as msg_count
    FROM messages
    GROUP BY conversation_id
) msg_stats;
```

**User**: How does message count correlate with escalation?
**Assistant**: I'll compare message counts between escalated and non-escalated conversations.
```sql
SELECT 
    CASE WHEN e.id IS NOT NULL THEN 'Escalated' ELSE 'Deflected' END as outcome,
    AVG(msg_count) as avg_messages,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY msg_count) as median_messages
FROM (
    SELECT 
        c.id,
        COUNT(m.id) as msg_count
    FROM conversations c
    JOIN messages m ON c.id = m.conversation_id
    WHERE c.status IN ('RESOLVED', 'ESCALATED')
    GROUP BY c.id
) conv_msgs
JOIN conversations c ON conv_msgs.id = c.id
LEFT JOIN escalations e ON c.id = e.conversation_id
GROUP BY outcome;
```

## Task 13: Channel Performance
**User**: Which channel has the best deflection rate?
**Assistant**: I'll analyze deflection performance across different channels.
```sql
SELECT 
    channel,
    COUNT(*) as total_conversations,
    COUNT(CASE WHEN status = 'RESOLVED' AND e.id IS NULL THEN 1 END) as deflected,
    COUNT(CASE WHEN status = 'ESCALATED' THEN 1 END) as escalated,
    COUNT(CASE WHEN status = 'ABANDONED' THEN 1 END) as abandoned,
    ROUND(COUNT(CASE WHEN status = 'RESOLVED' AND e.id IS NULL THEN 1 END) * 100.0 / COUNT(*), 2) as deflection_rate
FROM conversations c
LEFT JOIN escalations e ON c.id = e.conversation_id
GROUP BY channel
ORDER BY deflection_rate DESC;
```

## Task 14: Peak Hours Analysis
**User**: When do we get the most conversations?
**Assistant**: I'll identify peak hours for customer conversations.
```sql
SELECT 
    strftime('%H', started_at) as hour,
    COUNT(*) as conversation_count,
    COUNT(CASE WHEN status = 'ESCALATED' THEN 1 END) as escalations,
    ROUND(COUNT(CASE WHEN status = 'ESCALATED' THEN 1 END) * 100.0 / COUNT(*), 2) as escalation_rate
FROM conversations
GROUP BY hour
ORDER BY conversation_count DESC;
```

## Task 15: Customer Retention Impact
**User**: Do customers with escalated conversations come back?
**Assistant**: I'll analyze repeat conversation patterns after escalations.
```sql
WITH customer_escalations AS (
    SELECT DISTINCT 
        c.customer_id,
        MIN(c.started_at) as first_escalation_date
    FROM conversations c
    JOIN escalations e ON c.id = e.conversation_id
    GROUP BY c.customer_id
)
SELECT 
    COUNT(DISTINCT ce.customer_id) as customers_with_escalations,
    COUNT(DISTINCT CASE 
        WHEN c2.id IS NOT NULL THEN ce.customer_id 
    END) as customers_returned,
    ROUND(COUNT(DISTINCT CASE 
        WHEN c2.id IS NOT NULL THEN ce.customer_id 
    END) * 100.0 / COUNT(DISTINCT ce.customer_id), 2) as return_rate
FROM customer_escalations ce
LEFT JOIN conversations c2 ON ce.customer_id = c2.customer_id
    AND c2.started_at > ce.first_escalation_date;
```
