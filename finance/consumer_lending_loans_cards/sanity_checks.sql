-- Sanity checks for consumer lending loans and cards domain

-- REFERENTIAL INTEGRITY CHECKS
-- 1. All loan applications reference valid customers
SELECT COUNT(*) FROM loan_applications la LEFT JOIN customers c ON la.customer_id = c.id WHERE c.id IS NULL;

-- 2. All loan applications reference valid loan products
SELECT COUNT(*) FROM loan_applications la LEFT JOIN loan_products lp ON la.product_id = lp.id WHERE lp.id IS NULL;

-- 3. All loans reference valid loan applications
SELECT COUNT(*) FROM loans l LEFT JOIN loan_applications la ON l.application_id = la.id WHERE la.id IS NULL;

-- 4. All loans reference valid customers
SELECT COUNT(*) FROM loans l LEFT JOIN customers c ON l.customer_id = c.id WHERE c.id IS NULL;

-- 5. All loans reference valid loan products
SELECT COUNT(*) FROM loans l LEFT JOIN loan_products lp ON l.loan_product_id = lp.id WHERE lp.id IS NULL;

-- 6. All loan payments reference valid loans
SELECT COUNT(*) FROM loan_payments lp LEFT JOIN loans l ON lp.loan_id = l.id WHERE l.id IS NULL;

-- 7. All credit cards reference valid loans
SELECT COUNT(*) FROM credit_cards cc LEFT JOIN loans l ON cc.loan_id = l.id WHERE l.id IS NULL;

-- 8. All card transactions reference valid credit cards
SELECT COUNT(*) FROM card_transactions ct LEFT JOIN credit_cards cc ON ct.card_id = cc.id WHERE cc.id IS NULL;

-- ENUM VALIDATION CHECKS
-- 9. Employment status enum validation
SELECT COUNT(*) FROM customers WHERE employment_status NOT IN ('EMPLOYED', 'SELF_EMPLOYED', 'UNEMPLOYED', 'RETIRED', 'STUDENT');

-- 10. Product type enum validation
SELECT COUNT(*) FROM loan_products WHERE product_type NOT IN ('PERSONAL_LOAN', 'AUTO_LOAN', 'CREDIT_CARD', 'STUDENT_LOAN');

-- 11. Application status enum validation
SELECT COUNT(*) FROM loan_applications WHERE status NOT IN ('PENDING', 'APPROVED', 'REJECTED', 'WITHDRAWN', 'BOOKED');

-- 12. Loan status enum validation
SELECT COUNT(*) FROM loans WHERE status NOT IN ('ACTIVE', 'PAID_OFF', 'DEFAULT', 'CHARGED_OFF');

-- 13. Payment method enum validation
SELECT COUNT(*) FROM loan_payments WHERE payment_method NOT IN ('AUTO_DEBIT', 'BANK_TRANSFER', 'CHECK', 'ONLINE_PORTAL');

-- 14. Card type enum validation
SELECT COUNT(*) FROM credit_cards WHERE card_type NOT IN ('REWARDS', 'CASHBACK', 'LOW_APR', 'TRAVEL', 'SECURED');

-- 15. Card status enum validation
SELECT COUNT(*) FROM credit_cards WHERE status NOT IN ('ACTIVE', 'INACTIVE', 'LOST_STOLEN', 'CLOSED');

-- 16. Transaction type enum validation
SELECT COUNT(*) FROM card_transactions WHERE transaction_type NOT IN ('PURCHASE', 'CASH_ADVANCE', 'BALANCE_TRANSFER', 'FEE', 'PAYMENT', 'RETURN');

-- DATA QUALITY CHECKS
-- 17. Credit score range validation
SELECT COUNT(*) FROM customers WHERE credit_score < 300 OR credit_score > 850;

-- 18. Unique customer IDs
SELECT customer_id, COUNT(*) FROM customers GROUP BY customer_id HAVING COUNT(*) > 1;

-- 19. Unique card numbers
SELECT card_number, COUNT(*) FROM credit_cards GROUP BY card_number HAVING COUNT(*) > 1;

-- 20. Loan maturity date should be after origination date
SELECT COUNT(*) FROM loans WHERE maturity_date <= origination_date;

-- 21. Application decision date should be after application date
SELECT COUNT(*) FROM loan_applications WHERE decision_date IS NOT NULL AND decision_date <= application_date;

-- 22. Payment date should be after loan origination
SELECT COUNT(*) FROM loan_payments lp JOIN loans l ON lp.loan_id = l.id WHERE lp.payment_date < l.origination_date;

-- BUSINESS LOGIC VALIDATION
-- 23. Approved applications should have approved amount and interest rate
SELECT COUNT(*) FROM loan_applications WHERE status = 'APPROVED' AND (approved_amount IS NULL OR interest_rate IS NULL);

-- 24. Rejected applications should not have approved amount
SELECT COUNT(*) FROM loan_applications WHERE status = 'REJECTED' AND approved_amount IS NOT NULL;

-- 25. Principal and interest components should sum to payment amount
SELECT COUNT(*) FROM loan_payments WHERE ABS(payment_amount - (principal_component + interest_component + late_fees)) > 0.01;

-- 26. Credit card cash limit should not exceed credit limit
SELECT COUNT(*) FROM credit_cards WHERE cash_limit > credit_limit;

-- 27. JSON validation for loan product ranges
SELECT COUNT(*) FROM loan_products WHERE json_valid(interest_rate_range) = 0 OR json_valid(term_months_range) = 0;

-- PERFORMANCE INDEX VERIFICATION
-- 28. EXPLAIN - Verify index usage for customer credit score queries
EXPLAIN QUERY PLAN SELECT * FROM customers WHERE credit_score >= 700;

-- 29. EXPLAIN - Verify index usage for loan application status filtering
EXPLAIN QUERY PLAN SELECT * FROM loan_applications WHERE status = 'PENDING';

-- 30. EXPLAIN - Verify index usage for loan customer lookup
EXPLAIN QUERY PLAN SELECT * FROM loans WHERE customer_id = 100;
