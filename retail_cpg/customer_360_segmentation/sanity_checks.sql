-- Sanity checks for customer 360 segmentation domain

-- 1. All customer segment assignments reference valid customers
SELECT COUNT(*) FROM customer_segment_assignments csa LEFT JOIN customers c ON csa.customer_id = c.id WHERE c.id IS NULL;

-- 2. All customer segment assignments reference valid segments
SELECT COUNT(*) FROM customer_segment_assignments csa LEFT JOIN customer_segments cs ON csa.segment_id = cs.id WHERE cs.id IS NULL;

-- 3. All transactions reference valid customers
SELECT COUNT(*) FROM transactions t LEFT JOIN customers c ON t.customer_id = c.id WHERE c.id IS NULL;

-- 4. All customer interactions reference valid customers
SELECT COUNT(*) FROM customer_interactions ci LEFT JOIN customers c ON ci.customer_id = c.id WHERE c.id IS NULL;

-- 5. All customer preferences reference valid customers
SELECT COUNT(*) FROM customer_preferences cp LEFT JOIN customers c ON cp.customer_id = c.id WHERE c.id IS NULL;

-- 6. Customer gender enum validation
SELECT COUNT(*) FROM customers WHERE gender IS NOT NULL AND gender NOT IN ('M', 'F', 'OTHER', 'PREFER_NOT_SAY');

-- 7. Acquisition channel enum validation
SELECT COUNT(*) FROM customers WHERE acquisition_channel NOT IN ('ORGANIC', 'PAID_SEARCH', 'SOCIAL', 'EMAIL', 'REFERRAL', 'DIRECT');

-- 8. Customer status enum validation
SELECT COUNT(*) FROM customers WHERE status NOT IN ('ACTIVE', 'INACTIVE', 'CHURNED', 'SUSPENDED');

-- 9. Segment type enum validation
SELECT COUNT(*) FROM customer_segments WHERE segment_type NOT IN ('DEMOGRAPHIC', 'BEHAVIORAL', 'VALUE', 'LIFECYCLE');

-- 10. Transaction channel enum validation
SELECT COUNT(*) FROM transactions WHERE channel NOT IN ('STORE', 'ONLINE', 'MOBILE_APP', 'PHONE', 'CATALOG');

-- 11. Payment method enum validation
SELECT COUNT(*) FROM transactions WHERE payment_method NOT IN ('CASH', 'CREDIT', 'DEBIT', 'DIGITAL_WALLET', 'GIFT_CARD');

-- 12. Interaction type enum validation
SELECT COUNT(*) FROM customer_interactions WHERE interaction_type NOT IN ('PURCHASE', 'BROWSE', 'SUPPORT', 'REVIEW', 'SOCIAL_SHARE', 'EMAIL_OPEN', 'EMAIL_CLICK');

-- 13. Interaction channel enum validation
SELECT COUNT(*) FROM customer_interactions WHERE channel NOT IN ('WEB', 'MOBILE', 'STORE', 'EMAIL', 'SOCIAL', 'CALL_CENTER');

-- 14. Preference type enum validation
SELECT COUNT(*) FROM customer_preferences WHERE preference_type NOT IN ('CATEGORY', 'BRAND', 'COMMUNICATION', 'DELIVERY');

-- 15. Confidence score range validation
SELECT COUNT(*) FROM customer_segment_assignments WHERE confidence_score IS NOT NULL AND (confidence_score < 0 OR confidence_score > 1);

-- 16. Preference confidence score range validation
SELECT COUNT(*) FROM customer_preferences WHERE confidence_score IS NOT NULL AND (confidence_score < 0 OR confidence_score > 1);

-- 17. Segment priority range validation
SELECT COUNT(*) FROM customer_segments WHERE priority < 1 OR priority > 10;

-- 18. Unique email addresses
SELECT email, COUNT(*) FROM customers GROUP BY email HAVING COUNT(*) > 1;

-- 19. Unique customer-segment assignments
SELECT customer_id, segment_id, COUNT(*) FROM customer_segment_assignments GROUP BY customer_id, segment_id HAVING COUNT(*) > 1;

-- 20. Unique customer preference combinations
SELECT customer_id, preference_type, preference_value, COUNT(*) FROM customer_preferences GROUP BY customer_id, preference_type, preference_value HAVING COUNT(*) > 1;

-- 21. Segment criteria should be valid JSON
SELECT COUNT(*) FROM customer_segments WHERE json_valid(criteria_json) = 0;

-- 22. Interaction values should be valid JSON where present
SELECT COUNT(*) FROM customer_interactions WHERE interaction_value IS NOT NULL AND json_valid(interaction_value) = 0;

-- 23. Assignment expires date should be after assigned date
SELECT COUNT(*) FROM customer_segment_assignments WHERE expires_date IS NOT NULL AND expires_date <= assigned_date;

-- 24. EXPLAIN - Verify index usage for customer email lookup
EXPLAIN QUERY PLAN SELECT * FROM customers WHERE email = 'customer100@example.com';

-- 25. EXPLAIN - Verify index usage for transaction date range queries
EXPLAIN QUERY PLAN SELECT * FROM transactions WHERE transaction_date >= '2024-01-01' AND transaction_date < '2024-02-01';