-- Sanity checks for onboarding customer training domain

-- 1. All enrollments reference valid customers
SELECT COUNT(*) FROM enrollments e LEFT JOIN customers c ON e.customer_id = c.id WHERE c.id IS NULL;

-- 2. All enrollments reference valid programs
SELECT COUNT(*) FROM enrollments e LEFT JOIN training_programs tp ON e.program_id = tp.id WHERE tp.id IS NULL;

-- 3. All modules reference valid programs
SELECT COUNT(*) FROM modules m LEFT JOIN training_programs tp ON m.program_id = tp.id WHERE tp.id IS NULL;

-- 4. All module progress references valid enrollments
SELECT COUNT(*) FROM module_progress mp LEFT JOIN enrollments e ON mp.enrollment_id = e.id WHERE e.id IS NULL;

-- 5. All module progress references valid modules
SELECT COUNT(*) FROM module_progress mp LEFT JOIN modules m ON mp.module_id = m.id WHERE m.id IS NULL;

-- 6. Company size enum validation
SELECT COUNT(*) FROM customers WHERE company_size NOT IN ('SMALL', 'MEDIUM', 'LARGE', 'ENTERPRISE');

-- 7. Onboarding tier enum validation
SELECT COUNT(*) FROM customers WHERE onboarding_tier NOT IN ('SELF_SERVICE', 'STANDARD', 'PREMIUM', 'WHITE_GLOVE');

-- 8. Program type enum validation
SELECT COUNT(*) FROM training_programs WHERE program_type NOT IN ('ONBOARDING', 'FEATURE', 'CERTIFICATION', 'REFRESHER');

-- 9. Delivery method enum validation
SELECT COUNT(*) FROM training_programs WHERE delivery_method NOT IN ('SELF_PACED', 'INSTRUCTOR_LED', 'WEBINAR', 'ON_SITE');

-- 10. Difficulty level enum validation
SELECT COUNT(*) FROM training_programs WHERE difficulty_level NOT IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED');

-- 11. Enrollment status enum validation
SELECT COUNT(*) FROM enrollments WHERE status NOT IN ('ENROLLED', 'IN_PROGRESS', 'COMPLETED', 'DROPPED', 'EXPIRED');

-- 12. Module content type enum validation
SELECT COUNT(*) FROM modules WHERE content_type NOT IN ('VIDEO', 'DOCUMENT', 'QUIZ', 'EXERCISE', 'LIVE_SESSION');

-- 13. Progress percentage range validation
SELECT COUNT(*) FROM enrollments WHERE progress_percentage < 0 OR progress_percentage > 100;

-- 14. Module score range validation
SELECT COUNT(*) FROM module_progress WHERE score IS NOT NULL AND (score < 0 OR score > 100);

-- 15. Passing score range validation
SELECT COUNT(*) FROM modules WHERE passing_score IS NOT NULL AND (passing_score < 0 OR passing_score > 100);

-- 16. Unique enrollment per customer-program pair
SELECT customer_id, program_id, COUNT(*) FROM enrollments GROUP BY customer_id, program_id HAVING COUNT(*) > 1;

-- 17. Unique module progress per enrollment-module pair
SELECT enrollment_id, module_id, COUNT(*) FROM module_progress GROUP BY enrollment_id, module_id HAVING COUNT(*) > 1;

-- 18. Started enrollments should have started_at
SELECT COUNT(*) FROM enrollments WHERE status IN ('IN_PROGRESS', 'COMPLETED') AND started_at IS NULL;

-- 19. Completed enrollments should have completed_at
SELECT COUNT(*) FROM enrollments WHERE status = 'COMPLETED' AND completed_at IS NULL;

-- 20. Completed enrollments should have 100% progress
SELECT COUNT(*) FROM enrollments WHERE status = 'COMPLETED' AND progress_percentage != 100;

-- 21. Module progress must be for enrolled programs
SELECT COUNT(*) FROM module_progress mp 
JOIN enrollments e ON mp.enrollment_id = e.id
JOIN modules m ON mp.module_id = m.id
WHERE m.program_id != e.program_id;

-- 22. Prerequisites should be valid JSON
SELECT COUNT(*) FROM training_programs WHERE prerequisites IS NOT NULL AND json_valid(prerequisites) = 0;

-- 23. EXPLAIN - Verify index usage for customer enrollment lookup
EXPLAIN QUERY PLAN SELECT * FROM enrollments WHERE customer_id = 100;

-- 24. EXPLAIN - Verify index usage for date range queries
EXPLAIN QUERY PLAN SELECT * FROM enrollments WHERE enrolled_at >= '2024-01-01' AND enrolled_at < '2024-02-01';

-- 25. EXPLAIN - Verify index usage for program type filtering
EXPLAIN QUERY PLAN SELECT * FROM training_programs WHERE program_type = 'CERTIFICATION';