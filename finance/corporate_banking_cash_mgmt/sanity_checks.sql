-- Sanity checks for corporate banking cash management domain

-- REFERENTIAL INTEGRITY CHECKS
-- 1. All accounts reference valid corporate clients
SELECT COUNT(*) FROM accounts a LEFT JOIN corporate_clients cc ON a.client_id = cc.id WHERE cc.id IS NULL;

-- 2. All accounts reference valid account types
SELECT COUNT(*) FROM accounts a LEFT JOIN account_types at ON a.account_type_id = at.id WHERE at.id IS NULL;

-- 3. All cash pool structures reference valid clients
SELECT COUNT(*) FROM cash_pool_structures cps LEFT JOIN corporate_clients cc ON cps.client_id = cc.id WHERE cc.id IS NULL;

-- 4. All cash pool structures reference valid master accounts
SELECT COUNT(*) FROM cash_pool_structures cps LEFT JOIN accounts a ON cps.master_account_id = a.id WHERE a.id IS NULL;

-- 5. All pool participants reference valid pools
SELECT COUNT(*) FROM pool_participants pp LEFT JOIN cash_pool_structures cps ON pp.pool_id = cps.id WHERE cps.id IS NULL;

-- 6. All pool participants reference valid accounts
SELECT COUNT(*) FROM pool_participants pp LEFT JOIN accounts a ON pp.account_id = a.id WHERE a.id IS NULL;

-- 7. All transactions reference valid accounts
SELECT COUNT(*) FROM transactions t LEFT JOIN accounts a ON t.account_id = a.id WHERE a.id IS NULL;

-- 8. All sweep executions reference valid pools
SELECT COUNT(*) FROM sweep_executions se LEFT JOIN cash_pool_structures cps ON se.pool_id = cps.id WHERE cps.id IS NULL;

-- ENUM VALIDATION CHECKS
-- 9. Corporate client risk rating enum validation
SELECT COUNT(*) FROM corporate_clients WHERE risk_rating NOT IN ('LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH');

-- 10. Corporate client KYC status enum validation
SELECT COUNT(*) FROM corporate_clients WHERE kyc_status NOT IN ('PENDING', 'APPROVED', 'EXPIRED', 'REJECTED');

-- 11. Account type category enum validation
SELECT COUNT(*) FROM account_types WHERE category NOT IN ('CHECKING', 'SAVINGS', 'MONEY_MARKET', 'CD', 'SWEEP', 'CONCENTRATION');

-- 12. Account status enum validation
SELECT COUNT(*) FROM accounts WHERE status NOT IN ('ACTIVE', 'DORMANT', 'FROZEN', 'CLOSED');

-- 13. Pool type enum validation
SELECT COUNT(*) FROM cash_pool_structures WHERE pool_type NOT IN ('ZERO_BALANCE', 'TARGET_BALANCE', 'THRESHOLD_SWEEP');

-- 14. Sweep frequency enum validation
SELECT COUNT(*) FROM cash_pool_structures WHERE sweep_frequency NOT IN ('DAILY', 'WEEKLY', 'MONTHLY', 'ON_DEMAND');

-- 15. Participation type enum validation
SELECT COUNT(*) FROM pool_participants WHERE participation_type NOT IN ('CONTRIBUTOR', 'BENEFICIARY', 'BOTH');

-- 16. Transaction type enum validation
SELECT COUNT(*) FROM transactions WHERE transaction_type NOT IN ('CREDIT', 'DEBIT', 'SWEEP_IN', 'SWEEP_OUT', 'INTEREST', 'FEE');

-- 17. Sweep execution status enum validation
SELECT COUNT(*) FROM sweep_executions WHERE execution_status NOT IN ('COMPLETED', 'FAILED', 'PARTIAL');

-- DATA QUALITY CHECKS
-- 18. Unique client codes
SELECT client_code, COUNT(*) FROM corporate_clients GROUP BY client_code HAVING COUNT(*) > 1;

-- 19. Unique account numbers
SELECT account_number, COUNT(*) FROM accounts GROUP BY account_number HAVING COUNT(*) > 1;

-- 20. Available balance should not exceed current balance
SELECT COUNT(*) FROM accounts WHERE available_balance > current_balance;

-- 21. Value date should be on or after transaction date
SELECT COUNT(*) FROM transactions WHERE value_date < DATE(transaction_date);

-- 22. Pool participants should not reference master account
SELECT COUNT(*) FROM pool_participants pp 
JOIN cash_pool_structures cps ON pp.pool_id = cps.id 
WHERE pp.account_id = cps.master_account_id;

-- BUSINESS LOGIC VALIDATION
-- 23. Target balance pools should have target_balance > 0
SELECT COUNT(*) FROM cash_pool_structures WHERE pool_type = 'TARGET_BALANCE' AND (target_balance IS NULL OR target_balance <= 0);

-- 24. Threshold sweep pools should have threshold_amount > 0
SELECT COUNT(*) FROM cash_pool_structures WHERE pool_type = 'THRESHOLD_SWEEP' AND (threshold_amount IS NULL OR threshold_amount <= 0);

-- 25. Parent account relationships should not create cycles
WITH RECURSIVE account_hierarchy AS (
    SELECT id, parent_account_id, 1 as level FROM accounts WHERE parent_account_id IS NOT NULL
    UNION ALL
    SELECT a.id, a.parent_account_id, ah.level + 1 
    FROM accounts a 
    JOIN account_hierarchy ah ON a.parent_account_id = ah.id
    WHERE ah.level < 10
)
SELECT COUNT(*) FROM account_hierarchy WHERE id = parent_account_id;

-- 26. Fee structure should be valid JSON where present
SELECT COUNT(*) FROM account_types WHERE fee_structure IS NOT NULL AND json_valid(fee_structure) = 0;

-- 27. Execution details should be valid JSON where present
SELECT COUNT(*) FROM sweep_executions WHERE execution_details IS NOT NULL AND json_valid(execution_details) = 0;

-- 28. Unique pool-account participation
SELECT pool_id, account_id, COUNT(*) FROM pool_participants GROUP BY pool_id, account_id HAVING COUNT(*) > 1;

-- PERFORMANCE INDEX VERIFICATION
-- 29. EXPLAIN - Verify index usage for client account lookup
EXPLAIN QUERY PLAN SELECT * FROM accounts WHERE client_id = 100;

-- 30. EXPLAIN - Verify index usage for transaction date range queries
EXPLAIN QUERY PLAN SELECT * FROM transactions WHERE transaction_date >= '2024-01-01' AND transaction_date < '2024-02-01';