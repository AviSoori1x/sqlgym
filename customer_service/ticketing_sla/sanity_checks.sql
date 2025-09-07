-- 1. tickets reference valid customers
SELECT COUNT(*) FROM tickets t LEFT JOIN customers c ON t.customer_id=c.id WHERE c.id IS NULL;
-- 2. tickets reference valid agents when assigned
SELECT COUNT(*) FROM tickets t LEFT JOIN agents a ON t.agent_id=a.id WHERE t.agent_id IS NOT NULL AND a.id IS NULL;
-- 3. tickets reference valid service levels
SELECT COUNT(*) FROM tickets t LEFT JOIN service_levels s ON t.sl_id=s.id WHERE s.id IS NULL;
-- 4. interactions reference valid tickets
SELECT COUNT(*) FROM interactions i LEFT JOIN tickets t ON i.ticket_id=t.id WHERE t.id IS NULL;
-- 5. interactions reference valid agents
SELECT COUNT(*) FROM interactions i LEFT JOIN agents a ON i.agent_id=a.id WHERE a.id IS NULL;
-- 6. ticket status enum
SELECT COUNT(*) FROM tickets WHERE status NOT IN ('OPEN','PENDING','CLOSED');
-- 7. ticket priority enum
SELECT COUNT(*) FROM tickets WHERE priority NOT IN ('LOW','MED','HIGH');
-- 8. SLA policy alignment with evidence
SELECT COUNT(*) FROM service_levels WHERE (name='GOLD' AND response_hours<>json_extract((SELECT value FROM evidence_kv WHERE key='sla_policy'), '$.gold_response_hours')) OR (name='STANDARD' AND response_hours<>json_extract((SELECT value FROM evidence_kv WHERE key='sla_policy'), '$.standard_response_hours'));
-- 9. ensure response_hours positive
SELECT COUNT(*) FROM service_levels WHERE response_hours<=0;
-- 10. unique agent emails
SELECT email, COUNT(*) FROM agents GROUP BY email HAVING COUNT(*)>1;
-- 11. no orphan tickets without interactions after close
SELECT COUNT(*) FROM tickets t LEFT JOIN interactions i ON t.id=i.ticket_id WHERE t.status='CLOSED' AND i.id IS NULL;
-- 12. EXPLAIN uses status index
EXPLAIN QUERY PLAN SELECT * FROM tickets WHERE status='OPEN';
-- 13. EXPLAIN uses opened index for range
EXPLAIN QUERY PLAN SELECT * FROM tickets WHERE opened_at>'2024-01-01';
