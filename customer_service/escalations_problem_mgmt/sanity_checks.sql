-- Sanity checks for escalations and problem management domain

-- 1. All issues reference valid customers
SELECT COUNT(*) FROM issues i LEFT JOIN customers c ON i.customer_id = c.id WHERE c.id IS NULL;

-- 2. All issues reference valid creating agents
SELECT COUNT(*) FROM issues i LEFT JOIN agents a ON i.created_by_agent_id = a.id WHERE a.id IS NULL;

-- 3. All escalations reference valid issues
SELECT COUNT(*) FROM escalations e LEFT JOIN issues i ON e.issue_id = i.id WHERE i.id IS NULL;

-- 4. All escalations reference valid from_agents
SELECT COUNT(*) FROM escalations e LEFT JOIN agents a ON e.from_agent_id = a.id WHERE a.id IS NULL;

-- 5. All escalations reference valid to_agents
SELECT COUNT(*) FROM escalations e LEFT JOIN agents a ON e.to_agent_id = a.id WHERE a.id IS NULL;

-- 6. All problem records reference valid root issues
SELECT COUNT(*) FROM problem_records pr LEFT JOIN issues i ON pr.root_issue_id = i.id WHERE i.id IS NULL;

-- 7. Customer tier enum validation
SELECT COUNT(*) FROM customers WHERE tier NOT IN ('BRONZE', 'SILVER', 'GOLD', 'PLATINUM');

-- 8. Agent skill level enum validation
SELECT COUNT(*) FROM agents WHERE skill_level NOT IN ('L1', 'L2', 'L3', 'MANAGER', 'DIRECTOR');

-- 9. Agent department enum validation
SELECT COUNT(*) FROM agents WHERE department NOT IN ('SUPPORT', 'TECHNICAL', 'BILLING', 'SALES');

-- 10. Issue category enum validation
SELECT COUNT(*) FROM issues WHERE category NOT IN ('BUG', 'BILLING', 'ACCESS', 'PERFORMANCE', 'FEATURE_REQUEST', 'COMPLIANCE');

-- 11. Issue severity enum validation
SELECT COUNT(*) FROM issues WHERE severity NOT IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

-- 12. Issue status enum validation
SELECT COUNT(*) FROM issues WHERE status NOT IN ('OPEN', 'IN_PROGRESS', 'ESCALATED', 'RESOLVED', 'CLOSED');

-- 13. Escalation reason enum validation
SELECT COUNT(*) FROM escalations WHERE escalation_reason NOT IN ('EXPERTISE_REQUIRED', 'CUSTOMER_REQUEST', 'SLA_BREACH', 'HIGH_VALUE_CUSTOMER', 'LEGAL_RISK');

-- 14. Problem status enum validation
SELECT COUNT(*) FROM problem_records WHERE status NOT IN ('INVESTIGATING', 'ROOT_CAUSE_FOUND', 'FIX_IN_PROGRESS', 'RESOLVED');

-- 15. Impact score range validation
SELECT COUNT(*) FROM issues WHERE impact_score IS NOT NULL AND (impact_score < 1 OR impact_score > 100);

-- 16. Resolved issues should have resolved_at timestamp
SELECT COUNT(*) FROM issues WHERE status = 'RESOLVED' AND resolved_at IS NULL;

-- 17. Non-resolved issues should not have resolved_at
SELECT COUNT(*) FROM issues WHERE status NOT IN ('RESOLVED', 'CLOSED') AND resolved_at IS NOT NULL;

-- 18. Escalation hierarchy validation (no L1 -> L1, etc.)
SELECT COUNT(*) FROM escalations e 
JOIN agents a1 ON e.from_agent_id = a1.id
JOIN agents a2 ON e.to_agent_id = a2.id
WHERE 
    (a1.skill_level = 'L1' AND a2.skill_level = 'L1') OR
    (a1.skill_level = 'L2' AND a2.skill_level IN ('L1', 'L2')) OR
    (a1.skill_level = 'L3' AND a2.skill_level IN ('L1', 'L2', 'L3')) OR
    (a1.skill_level = 'MANAGER' AND a2.skill_level IN ('L1', 'L2', 'L3', 'MANAGER')) OR
    (a1.skill_level = 'DIRECTOR' AND a2.skill_level = 'DIRECTOR');

-- 19. Updated_at should be >= created_at
SELECT COUNT(*) FROM issues WHERE updated_at < created_at;

-- 20. Problem records should have unique root issues
SELECT root_issue_id, COUNT(*) FROM problem_records GROUP BY root_issue_id HAVING COUNT(*) > 1;

-- 21. Closed problem records should have closed_at
SELECT COUNT(*) FROM problem_records WHERE status = 'RESOLVED' AND closed_at IS NULL;

-- 22. EXPLAIN - Verify index usage for customer issue lookup
EXPLAIN QUERY PLAN SELECT * FROM issues WHERE customer_id = 100;

-- 23. EXPLAIN - Verify index usage for date range queries
EXPLAIN QUERY PLAN SELECT * FROM issues WHERE created_at >= '2024-01-15' AND created_at < '2024-01-20';

-- 24. EXPLAIN - Verify index usage for severity filtering
EXPLAIN QUERY PLAN SELECT * FROM issues WHERE severity = 'CRITICAL' AND status = 'OPEN';