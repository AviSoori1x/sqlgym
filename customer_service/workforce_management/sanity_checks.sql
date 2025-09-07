-- Sanity checks for workforce management domain

-- 1. All agent skills reference valid agents
SELECT COUNT(*) FROM agent_skills ask LEFT JOIN agents a ON ask.agent_id = a.id WHERE a.id IS NULL;

-- 2. All agent skills reference valid skills
SELECT COUNT(*) FROM agent_skills ask LEFT JOIN skills s ON ask.skill_id = s.id WHERE s.id IS NULL;

-- 3. All schedules reference valid agents
SELECT COUNT(*) FROM schedules s LEFT JOIN agents a ON s.agent_id = a.id WHERE a.id IS NULL;

-- 4. All schedules reference valid shifts
SELECT COUNT(*) FROM schedules s LEFT JOIN shifts sh ON s.shift_id = sh.id WHERE sh.id IS NULL;

-- 5. All time off requests reference valid agents
SELECT COUNT(*) FROM time_off_requests tor LEFT JOIN agents a ON tor.agent_id = a.id WHERE a.id IS NULL;

-- 6. Agent department enum validation
SELECT COUNT(*) FROM agents WHERE department NOT IN ('SALES', 'SUPPORT', 'TECHNICAL', 'BILLING', 'RETENTION');

-- 7. Agent skill level enum validation
SELECT COUNT(*) FROM agents WHERE skill_level NOT IN ('JUNIOR', 'MID', 'SENIOR', 'LEAD', 'MANAGER');

-- 8. Employment type enum validation
SELECT COUNT(*) FROM agents WHERE employment_type NOT IN ('FULL_TIME', 'PART_TIME', 'CONTRACT');

-- 9. Agent status enum validation
SELECT COUNT(*) FROM agents WHERE status NOT IN ('ACTIVE', 'ON_LEAVE', 'TRAINING', 'TERMINATED');

-- 10. Skill category enum validation
SELECT COUNT(*) FROM skills WHERE category NOT IN ('LANGUAGE', 'TECHNICAL', 'PRODUCT', 'SOFT_SKILL');

-- 11. Shift type enum validation
SELECT COUNT(*) FROM shifts WHERE shift_type NOT IN ('MORNING', 'AFTERNOON', 'EVENING', 'NIGHT', 'FLEXIBLE');

-- 12. Schedule status enum validation
SELECT COUNT(*) FROM schedules WHERE status NOT IN ('SCHEDULED', 'CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'ABSENT', 'LATE');

-- 13. Time off request type enum validation
SELECT COUNT(*) FROM time_off_requests WHERE request_type NOT IN ('VACATION', 'SICK', 'PERSONAL', 'BEREAVEMENT', 'JURY_DUTY');

-- 14. Time off status enum validation
SELECT COUNT(*) FROM time_off_requests WHERE status NOT IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED');

-- 15. Proficiency level range validation
SELECT COUNT(*) FROM agent_skills WHERE proficiency_level < 1 OR proficiency_level > 5;

-- 16. Unique agent-skill pairs
SELECT agent_id, skill_id, COUNT(*) FROM agent_skills GROUP BY agent_id, skill_id HAVING COUNT(*) > 1;

-- 17. Unique agent-shift assignments
SELECT agent_id, shift_id, COUNT(*) FROM schedules GROUP BY agent_id, shift_id HAVING COUNT(*) > 1;

-- 18. Check-in/out logic - check-out should be after check-in
SELECT COUNT(*) FROM schedules WHERE check_out_time IS NOT NULL AND check_in_time IS NOT NULL AND check_out_time <= check_in_time;

-- 19. Completed shifts should have check-in/out times
SELECT COUNT(*) FROM schedules WHERE status = 'COMPLETED' AND (check_in_time IS NULL OR check_out_time IS NULL);

-- 20. Certification dates should be before expiry dates
SELECT COUNT(*) FROM agent_skills WHERE certified_date IS NOT NULL AND expiry_date IS NOT NULL AND certified_date >= expiry_date;

-- 21. Time off end date should be after start date
SELECT COUNT(*) FROM time_off_requests WHERE end_date < start_date;

-- 22. Only certified skills should have expiry dates
SELECT COUNT(*) FROM agent_skills WHERE certified_date IS NULL AND expiry_date IS NOT NULL;

-- 23. EXPLAIN - Verify index usage for agent schedule lookup
EXPLAIN QUERY PLAN SELECT * FROM schedules WHERE agent_id = 100;

-- 24. EXPLAIN - Verify index usage for shift date queries
EXPLAIN QUERY PLAN SELECT * FROM shifts WHERE shift_date = '2024-01-15';

-- 25. EXPLAIN - Verify index usage for time off date range
EXPLAIN QUERY PLAN SELECT * FROM time_off_requests WHERE start_date <= '2024-01-31' AND end_date >= '2024-01-01';