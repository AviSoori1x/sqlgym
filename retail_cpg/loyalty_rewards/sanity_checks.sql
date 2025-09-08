-- Sanity checks for loyalty rewards domain

-- 1. All members reference valid tiers
SELECT COUNT(*) FROM members m LEFT JOIN tiers t ON m.tier_id = t.id WHERE t.id IS NULL;

-- 2. All point transactions reference valid members
SELECT COUNT(*) FROM point_transactions pt LEFT JOIN members m ON pt.member_id = m.id WHERE m.id IS NULL;

-- 3. All redemptions reference valid members
SELECT COUNT(*) FROM redemptions r LEFT JOIN members m ON r.member_id = m.id WHERE m.id IS NULL;

-- 4. All redemptions reference valid rewards
SELECT COUNT(*) FROM redemptions r LEFT JOIN rewards_catalog rc ON r.reward_id = rc.id WHERE rc.id IS NULL;

-- 5. All tier movements reference valid members
SELECT COUNT(*) FROM tier_movements tm LEFT JOIN members m ON tm.member_id = m.id WHERE m.id IS NULL;

-- 6. Member status enum validation
SELECT COUNT(*) FROM members WHERE status NOT IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'CHURNED');

-- 7. Transaction type enum validation
SELECT COUNT(*) FROM point_transactions WHERE transaction_type NOT IN ('EARN', 'REDEEM', 'EXPIRE', 'ADJUSTMENT');

-- 8. Reward category enum validation
SELECT COUNT(*) FROM rewards_catalog WHERE category NOT IN ('DISCOUNT', 'FREE_PRODUCT', 'FREE_SHIPPING', 'EXPERIENCE', 'CASHBACK');

-- 9. Redemption status enum validation
SELECT COUNT(*) FROM redemptions WHERE status NOT IN ('PENDING', 'PROCESSED', 'CANCELLED', 'EXPIRED');

-- 10. Tier movement reason enum validation
SELECT COUNT(*) FROM tier_movements WHERE reason NOT IN ('SPEND_THRESHOLD', 'POINTS_THRESHOLD', 'MANUAL_UPGRADE', 'ANNUAL_RESET', 'DOWNGRADE');

-- 11. Unique customer IDs
SELECT customer_id, COUNT(*) FROM members GROUP BY customer_id HAVING COUNT(*) > 1;

-- 12. Points balance should not be negative
SELECT COUNT(*) FROM members WHERE current_points_balance < 0;

-- 13. Tier order should be unique
SELECT tier_order, COUNT(*) FROM tiers GROUP BY tier_order HAVING COUNT(*) > 1;

-- 14. Point multiplier should be positive
SELECT COUNT(*) FROM tiers WHERE point_multiplier <= 0;

-- 15. Reward points cost should be positive
SELECT COUNT(*) FROM rewards_catalog WHERE points_cost <= 0;

-- 16. EXPLAIN - Verify index usage for member tier queries
EXPLAIN QUERY PLAN SELECT * FROM members WHERE tier_id = 1;

-- 17. EXPLAIN - Verify index usage for transaction date queries
EXPLAIN QUERY PLAN SELECT * FROM point_transactions WHERE transaction_date >= '2024-01-01';