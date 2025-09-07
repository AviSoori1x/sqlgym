-- Sanity checks for chatbot deflection domain

-- 1. All conversations reference valid customers
SELECT COUNT(*) FROM conversations c LEFT JOIN customers cu ON c.customer_id = cu.id WHERE cu.id IS NULL;

-- 2. All messages reference valid conversations
SELECT COUNT(*) FROM messages m LEFT JOIN conversations c ON m.conversation_id = c.id WHERE c.id IS NULL;

-- 3. All escalations reference valid conversations
SELECT COUNT(*) FROM escalations e LEFT JOIN conversations c ON e.conversation_id = c.id WHERE c.id IS NULL;

-- 4. Intent references are valid when present
SELECT COUNT(*) FROM conversations c LEFT JOIN intent_categories ic ON c.primary_intent_id = ic.id 
WHERE c.primary_intent_id IS NOT NULL AND ic.id IS NULL;

-- 5. Message intent references are valid when present
SELECT COUNT(*) FROM messages m LEFT JOIN intent_categories ic ON m.intent_id = ic.id 
WHERE m.intent_id IS NOT NULL AND ic.id IS NULL;

-- 6. Status enum validation
SELECT COUNT(*) FROM conversations WHERE status NOT IN ('ACTIVE', 'RESOLVED', 'ESCALATED', 'ABANDONED');

-- 7. Channel enum validation
SELECT COUNT(*) FROM conversations WHERE channel NOT IN ('WEB', 'MOBILE', 'SMS', 'VOICE');

-- 8. Sender type enum validation
SELECT COUNT(*) FROM messages WHERE sender_type NOT IN ('CUSTOMER', 'BOT', 'AGENT');

-- 9. Escalation reason enum validation
SELECT COUNT(*) FROM escalations WHERE reason NOT IN ('LOW_CONFIDENCE', 'CUSTOMER_REQUEST', 'COMPLEX_ISSUE', 'SENTIMENT_NEGATIVE');

-- 10. Confidence scores are in valid range
SELECT COUNT(*) FROM messages WHERE confidence_score IS NOT NULL AND (confidence_score < 0 OR confidence_score > 1);

-- 11. Satisfaction scores are in valid range
SELECT COUNT(*) FROM conversations WHERE satisfaction_score IS NOT NULL AND (satisfaction_score < 1 OR satisfaction_score > 5);

-- 12. Conversations have at least one message
SELECT COUNT(*) FROM conversations c LEFT JOIN messages m ON c.id = m.conversation_id 
GROUP BY c.id HAVING COUNT(m.id) = 0;

-- 13. Escalated conversations should have escalation records
SELECT COUNT(*) FROM conversations c LEFT JOIN escalations e ON c.id = e.conversation_id 
WHERE c.status = 'ESCALATED' AND e.id IS NULL;

-- 14. Non-escalated conversations should not have escalation records
SELECT COUNT(*) FROM conversations c JOIN escalations e ON c.id = e.conversation_id 
WHERE c.status != 'ESCALATED';

-- 15. Messages are chronologically ordered within conversations
SELECT COUNT(*) FROM messages m1 JOIN messages m2 ON m1.conversation_id = m2.conversation_id 
WHERE m1.id < m2.id AND m1.sent_at > m2.sent_at;

-- 16. Ended conversations have end time after start time
SELECT COUNT(*) FROM conversations WHERE ended_at IS NOT NULL AND ended_at <= started_at;

-- 17. Bot messages should have confidence scores
SELECT COUNT(*) FROM messages WHERE sender_type = 'BOT' AND confidence_score IS NULL;

-- 18. Customer messages should not have confidence scores
SELECT COUNT(*) FROM messages WHERE sender_type = 'CUSTOMER' AND confidence_score IS NOT NULL;

-- 19. EXPLAIN - Verify index usage for conversation status queries
EXPLAIN QUERY PLAN SELECT * FROM conversations WHERE status = 'ESCALATED';

-- 20. EXPLAIN - Verify index usage for date range queries
EXPLAIN QUERY PLAN SELECT * FROM conversations WHERE started_at >= '2024-01-15' AND started_at < '2024-01-20';
