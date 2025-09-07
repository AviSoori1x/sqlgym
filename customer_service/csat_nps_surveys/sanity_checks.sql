-- Sanity checks for CSAT/NPS surveys domain

-- 1. All surveys reference valid customers
SELECT COUNT(*) FROM surveys s LEFT JOIN customers c ON s.customer_id = c.id WHERE c.id IS NULL;

-- 2. All surveys reference valid touchpoints
SELECT COUNT(*) FROM surveys s LEFT JOIN touchpoints t ON s.touchpoint_id = t.id WHERE t.id IS NULL;

-- 3. All survey triggers reference valid surveys
SELECT COUNT(*) FROM survey_triggers st LEFT JOIN surveys s ON st.survey_id = s.id WHERE s.id IS NULL;

-- 4. All follow-ups reference valid surveys
SELECT COUNT(*) FROM follow_ups f LEFT JOIN surveys s ON f.survey_id = s.id WHERE s.id IS NULL;

-- 5. Survey type enum validation
SELECT COUNT(*) FROM surveys WHERE survey_type NOT IN ('CSAT', 'NPS', 'CES');

-- 6. Survey status enum validation
SELECT COUNT(*) FROM surveys WHERE status NOT IN ('SENT', 'OPENED', 'COMPLETED', 'EXPIRED');

-- 7. Customer segment enum validation
SELECT COUNT(*) FROM customers WHERE segment NOT IN ('ENTERPRISE', 'SMB', 'CONSUMER');

-- 8. Touchpoint channel enum validation
SELECT COUNT(*) FROM touchpoints WHERE channel NOT IN ('EMAIL', 'SMS', 'IN_APP', 'PHONE', 'WEB');

-- 9. Trigger event enum validation
SELECT COUNT(*) FROM survey_triggers WHERE trigger_event NOT IN ('PURCHASE', 'SUPPORT_CLOSE', 'ONBOARDING', 'RENEWAL', 'CANCELLATION');

-- 10. Follow-up action enum validation
SELECT COUNT(*) FROM follow_ups WHERE action_type NOT IN ('CALLBACK', 'EMAIL', 'DISCOUNT', 'ESCALATION', 'NONE');

-- 11. Score range validation
SELECT COUNT(*) FROM surveys WHERE score IS NOT NULL AND (score < 1 OR score > 10);

-- 12. Completed surveys should have scores
SELECT COUNT(*) FROM surveys WHERE status = 'COMPLETED' AND score IS NULL;

-- 13. Non-completed surveys should not have scores
SELECT COUNT(*) FROM surveys WHERE status != 'COMPLETED' AND score IS NOT NULL;

-- 14. Response time logic - responded_at should be after sent_at
SELECT COUNT(*) FROM surveys WHERE responded_at IS NOT NULL AND responded_at <= sent_at;

-- 15. Follow-up completion logic - completed_at should be after created_at
SELECT COUNT(*) FROM follow_ups WHERE completed_at IS NOT NULL AND completed_at <= created_at;

-- 16. Only one follow-up per survey (UNIQUE constraint check)
SELECT survey_id, COUNT(*) FROM follow_ups GROUP BY survey_id HAVING COUNT(*) > 1;

-- 17. Trigger events should happen before survey sent
SELECT COUNT(*) FROM survey_triggers st JOIN surveys s ON st.survey_id = s.id 
WHERE st.event_timestamp >= s.sent_at;

-- 18. EXPLAIN - Verify index usage for customer survey lookup
EXPLAIN QUERY PLAN SELECT * FROM surveys WHERE customer_id = 100;

-- 19. EXPLAIN - Verify index usage for date range queries
EXPLAIN QUERY PLAN SELECT * FROM surveys WHERE sent_at >= '2024-01-15' AND sent_at < '2024-01-20';

-- 20. EXPLAIN - Verify index usage for score analysis
EXPLAIN QUERY PLAN SELECT AVG(score) FROM surveys WHERE survey_type = 'NPS' AND score IS NOT NULL;