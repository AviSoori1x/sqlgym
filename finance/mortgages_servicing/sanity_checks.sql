-- Sanity checks for mortgage servicing domain

-- 1. All mortgage loans reference valid borrowers
SELECT COUNT(*) FROM mortgage_loans ml LEFT JOIN borrowers b ON ml.borrower_id = b.id WHERE b.id IS NULL;

-- 2. All mortgage loans reference valid properties
SELECT COUNT(*) FROM mortgage_loans ml LEFT JOIN properties p ON ml.property_id = p.id WHERE p.id IS NULL;

-- 3. All escrow accounts reference valid mortgage loans
SELECT COUNT(*) FROM escrow_accounts ea LEFT JOIN mortgage_loans ml ON ea.loan_id = ml.id WHERE ml.id IS NULL;

-- 4. All mortgage payments reference valid loans
SELECT COUNT(*) FROM mortgage_payments mp LEFT JOIN mortgage_loans ml ON mp.loan_id = ml.id WHERE ml.id IS NULL;

-- 5. Employment status enum validation
SELECT COUNT(*) FROM borrowers WHERE employment_status NOT IN ('EMPLOYED', 'SELF_EMPLOYED', 'RETIRED', 'UNEMPLOYED');

-- 6. Property type enum validation
SELECT COUNT(*) FROM properties WHERE property_type NOT IN ('SINGLE_FAMILY', 'CONDO', 'TOWNHOUSE', 'MULTI_FAMILY', 'MANUFACTURED');

-- 7. Loan type enum validation
SELECT COUNT(*) FROM mortgage_loans WHERE loan_type NOT IN ('CONVENTIONAL', 'FHA', 'VA', 'USDA', 'JUMBO');

-- 8. Loan purpose enum validation
SELECT COUNT(*) FROM mortgage_loans WHERE loan_purpose NOT IN ('PURCHASE', 'REFINANCE', 'CASH_OUT_REFINANCE');

-- 9. Loan status enum validation
SELECT COUNT(*) FROM mortgage_loans WHERE status NOT IN ('ACTIVE', 'PAID_OFF', 'DEFAULT', 'FORECLOSURE', 'REO');

-- 10. Payment method enum validation
SELECT COUNT(*) FROM mortgage_payments WHERE payment_method NOT IN ('AUTO_DEBIT', 'ONLINE', 'MAIL', 'PHONE', 'IN_PERSON');

-- 11. Unique borrower IDs
SELECT borrower_id, COUNT(*) FROM borrowers GROUP BY borrower_id HAVING COUNT(*) > 1;

-- 12. Unique SSN hashes
SELECT ssn_hash, COUNT(*) FROM borrowers GROUP BY ssn_hash HAVING COUNT(*) > 1;

-- 13. Unique loan numbers
SELECT loan_number, COUNT(*) FROM mortgage_loans GROUP BY loan_number HAVING COUNT(*) > 1;

-- 14. Maturity date should be after origination
SELECT COUNT(*) FROM mortgage_loans WHERE maturity_date <= origination_date;

-- 15. Current balance should not exceed original amount
SELECT COUNT(*) FROM mortgage_loans WHERE current_balance > original_amount;

-- 16. EXPLAIN - Verify index for borrower lookup
EXPLAIN QUERY PLAN SELECT * FROM mortgage_loans WHERE borrower_id = 100;

-- 17. EXPLAIN - Verify index for payment date queries
EXPLAIN QUERY PLAN SELECT * FROM mortgage_payments WHERE payment_date >= '2024-01-01';