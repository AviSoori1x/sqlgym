-- Sanity checks for ecommerce funnel A/B testing domain

-- 1. All variants reference valid experiments
SELECT COUNT(*) FROM variants v LEFT JOIN experiments e ON v.experiment_id = e.id WHERE e.id IS NULL;

-- 2. All user sessions with experiment_id reference valid experiments
SELECT COUNT(*) FROM user_sessions us LEFT JOIN experiments e ON us.experiment_id = e.id WHERE us.experiment_id IS NOT NULL AND e.id IS NULL;

-- 3. All user sessions with variant_id reference valid variants
SELECT COUNT(*) FROM user_sessions us LEFT JOIN variants v ON us.variant_id = v.id WHERE us.variant_id IS NOT NULL AND v.id IS NULL;

-- 4. All funnel events reference valid user sessions
SELECT COUNT(*) FROM funnel_events fe LEFT JOIN user_sessions us ON fe.session_id = us.session_id WHERE us.session_id IS NULL;

-- 5. All funnel events reference valid funnel steps
SELECT COUNT(*) FROM funnel_events fe LEFT JOIN funnel_steps fs ON fe.funnel_step_id = fs.id WHERE fs.id IS NULL;

-- 6. Experiment type enum validation
SELECT COUNT(*) FROM experiments WHERE experiment_type NOT IN ('A_B', 'MULTIVARIATE', 'SPLIT_URL', 'FUNNEL');

-- 7. Experiment status enum validation
SELECT COUNT(*) FROM experiments WHERE status NOT IN ('DRAFT', 'RUNNING', 'PAUSED', 'COMPLETED', 'CANCELLED');

-- 8. Variant type enum validation
SELECT COUNT(*) FROM variants WHERE variant_type NOT IN ('CONTROL', 'TREATMENT');

-- 9. Funnel step type enum validation
SELECT COUNT(*) FROM funnel_steps WHERE step_type NOT IN ('LANDING', 'CATEGORY', 'PRODUCT', 'CART', 'CHECKOUT', 'CONFIRMATION');

-- 10. User session device type enum validation
SELECT COUNT(*) FROM user_sessions WHERE device_type NOT IN ('DESKTOP', 'MOBILE', 'TABLET');

-- 11. Traffic source enum validation
SELECT COUNT(*) FROM user_sessions WHERE traffic_source NOT IN ('ORGANIC', 'PAID', 'DIRECT', 'REFERRAL', 'EMAIL', 'SOCIAL');

-- 12. Event type enum validation
SELECT COUNT(*) FROM funnel_events WHERE event_type NOT IN ('PAGE_VIEW', 'CLICK', 'FORM_SUBMIT', 'ADD_TO_CART', 'PURCHASE');

-- 13. Conversion goal type enum validation
SELECT COUNT(*) FROM conversion_goals WHERE goal_type NOT IN ('REVENUE', 'CONVERSION_RATE', 'ENGAGEMENT', 'RETENTION');

-- 14. Traffic allocation range validation
SELECT COUNT(*) FROM experiments WHERE traffic_allocation < 0 OR traffic_allocation > 1;

-- 15. Traffic split range validation
SELECT COUNT(*) FROM variants WHERE traffic_split < 0 OR traffic_split > 1;

-- 16. Statistical significance range validation
SELECT COUNT(*) FROM experiments WHERE statistical_significance IS NOT NULL AND (statistical_significance < 0 OR statistical_significance > 1);

-- 17. Unique session IDs
SELECT session_id, COUNT(*) FROM user_sessions GROUP BY session_id HAVING COUNT(*) > 1;

-- 18. Unique funnel step names
SELECT name, COUNT(*) FROM funnel_steps GROUP BY name HAVING COUNT(*) > 1;

-- 19. Unique conversion goal names
SELECT name, COUNT(*) FROM conversion_goals GROUP BY name HAVING COUNT(*) > 1;

-- 20. Session end time should be after start time
SELECT COUNT(*) FROM user_sessions WHERE end_timestamp IS NOT NULL AND end_timestamp <= start_timestamp;

-- 21. Experiment end date should be after start date
SELECT COUNT(*) FROM experiments WHERE end_date IS NOT NULL AND end_date <= start_date;

-- 22. Variant configuration should be valid JSON where present
SELECT COUNT(*) FROM variants WHERE configuration IS NOT NULL AND json_valid(configuration) = 0;

-- 23. Event data should be valid JSON where present
SELECT COUNT(*) FROM funnel_events WHERE event_data IS NOT NULL AND json_valid(event_data) = 0;

-- 24. EXPLAIN - Verify index usage for experiment session lookup
EXPLAIN QUERY PLAN SELECT * FROM user_sessions WHERE experiment_id = 1;

-- 25. EXPLAIN - Verify index usage for funnel event timestamp queries
EXPLAIN QUERY PLAN SELECT * FROM funnel_events WHERE timestamp >= '2024-01-01' AND timestamp < '2024-02-01';