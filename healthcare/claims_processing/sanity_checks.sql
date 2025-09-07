-- Sanity checks for claims processing domain

-- REFERENTIAL INTEGRITY CHECKS
-- 1. All medical claims reference valid members
SELECT COUNT(*) FROM medical_claims mc LEFT JOIN members m ON mc.member_id = m.id WHERE m.id IS NULL;

-- 2. All medical claims reference valid insurance plans
SELECT COUNT(*) FROM medical_claims mc LEFT JOIN insurance_plans ip ON mc.plan_id = ip.id WHERE ip.id IS NULL;

-- 3. All medical claims reference valid providers
SELECT COUNT(*) FROM medical_claims mc LEFT JOIN providers p ON mc.provider_id = p.id WHERE p.id IS NULL;

-- 4. All claim line items reference valid claims
SELECT COUNT(*) FROM claim_line_items cli LEFT JOIN medical_claims mc ON cli.claim_id = mc.id WHERE mc.id IS NULL;

-- 5. All claim adjudications reference valid claims
SELECT COUNT(*) FROM claim_adjudications ca LEFT JOIN medical_claims mc ON ca.claim_id = mc.id WHERE mc.id IS NULL;

-- 6. All claim denials reference valid claims
SELECT COUNT(*) FROM claim_denials cd LEFT JOIN medical_claims mc ON cd.claim_id = mc.id WHERE mc.id IS NULL;

-- 7. All prior authorizations reference valid members
SELECT COUNT(*) FROM prior_authorizations pa LEFT JOIN members m ON pa.member_id = m.id WHERE m.id IS NULL;

-- 8. All prior authorizations reference valid providers
SELECT COUNT(*) FROM prior_authorizations pa LEFT JOIN providers p ON pa.provider_id = p.id WHERE p.id IS NULL;

-- ENUM VALIDATION CHECKS
-- 9. Member gender enum validation
SELECT COUNT(*) FROM members WHERE gender IS NOT NULL AND gender NOT IN ('M', 'F', 'OTHER', 'UNKNOWN');

-- 10. Member status enum validation
SELECT COUNT(*) FROM members WHERE status NOT IN ('ACTIVE', 'INACTIVE', 'TERMINATED', 'SUSPENDED');

-- 11. Plan type enum validation
SELECT COUNT(*) FROM insurance_plans WHERE plan_type NOT IN ('HMO', 'PPO', 'EPO', 'POS', 'HDHP', 'MEDICARE', 'MEDICAID');

-- 12. Coverage level enum validation
SELECT COUNT(*) FROM insurance_plans WHERE coverage_level NOT IN ('INDIVIDUAL', 'FAMILY', 'EMPLOYEE_PLUS_ONE', 'EMPLOYEE_PLUS_FAMILY');

-- 13. Provider type enum validation
SELECT COUNT(*) FROM providers WHERE provider_type NOT IN ('PHYSICIAN', 'HOSPITAL', 'CLINIC', 'LABORATORY', 'PHARMACY', 'DME_SUPPLIER');

-- 14. Network status enum validation
SELECT COUNT(*) FROM providers WHERE network_status NOT IN ('IN_NETWORK', 'OUT_OF_NETWORK', 'CONTRACTED', 'NON_CONTRACTED');

-- 15. Claim type enum validation
SELECT COUNT(*) FROM medical_claims WHERE claim_type NOT IN ('PROFESSIONAL', 'INSTITUTIONAL', 'DENTAL', 'VISION', 'PHARMACY');

-- 16. Place of service enum validation
SELECT COUNT(*) FROM medical_claims WHERE place_of_service NOT IN ('OFFICE', 'HOSPITAL_INPATIENT', 'HOSPITAL_OUTPATIENT', 'EMERGENCY_ROOM', 'HOME', 'NURSING_HOME');

-- 17. Claim status enum validation
SELECT COUNT(*) FROM medical_claims WHERE status NOT IN ('SUBMITTED', 'PENDING', 'APPROVED', 'DENIED', 'PAID', 'APPEALED');

-- 18. Processing priority enum validation
SELECT COUNT(*) FROM medical_claims WHERE processing_priority NOT IN ('ROUTINE', 'URGENT', 'EXPEDITED');

-- 19. Adjudication decision enum validation
SELECT COUNT(*) FROM claim_adjudications WHERE decision NOT IN ('APPROVED', 'DENIED', 'PARTIAL_APPROVAL', 'PENDED');

-- 20. Denial category enum validation
SELECT COUNT(*) FROM claim_denials WHERE denial_category NOT IN ('COVERAGE', 'CODING', 'AUTHORIZATION', 'DUPLICATE', 'TIMELY_FILING', 'PROVIDER_ELIGIBILITY');

-- 21. Prior authorization status enum validation
SELECT COUNT(*) FROM prior_authorizations WHERE status NOT IN ('PENDING', 'APPROVED', 'DENIED', 'EXPIRED');

-- DATA QUALITY CHECKS
-- 22. Unique member IDs
SELECT member_id, COUNT(*) FROM members GROUP BY member_id HAVING COUNT(*) > 1;

-- 23. Unique claim numbers
SELECT claim_number, COUNT(*) FROM medical_claims GROUP BY claim_number HAVING COUNT(*) > 1;

-- 24. Unique provider NPIs
SELECT npi, COUNT(*) FROM providers GROUP BY npi HAVING COUNT(*) > 1;

-- 25. Unique authorization numbers
SELECT authorization_number, COUNT(*) FROM prior_authorizations GROUP BY authorization_number HAVING COUNT(*) > 1;

-- 26. Service date should be before or equal to submission date
SELECT COUNT(*) FROM medical_claims WHERE service_date > submission_date;

-- 27. Adjudication date should be after submission date
SELECT COUNT(*) FROM claim_adjudications ca 
JOIN medical_claims mc ON ca.claim_id = mc.id 
WHERE ca.adjudication_date < mc.submission_date;

-- BUSINESS LOGIC VALIDATION
-- 28. Diagnosis codes should be valid JSON
SELECT COUNT(*) FROM medical_claims WHERE json_valid(diagnosis_codes) = 0;

-- 29. Reason codes should be valid JSON where present
SELECT COUNT(*) FROM claim_adjudications WHERE reason_codes IS NOT NULL AND json_valid(reason_codes) = 0;

-- 30. Approved claims should have positive paid amounts
SELECT COUNT(*) FROM claim_adjudications ca
JOIN claim_line_items cli ON ca.claim_id = cli.claim_id
WHERE ca.decision = 'APPROVED' AND cli.paid_amount <= 0;

-- 31. Denied claims should have zero paid amounts
SELECT COUNT(*) FROM claim_adjudications ca
JOIN claim_line_items cli ON ca.claim_id = cli.claim_id
WHERE ca.decision = 'DENIED' AND cli.paid_amount > 0;

-- 32. Line item amounts should sum correctly
SELECT COUNT(*) FROM claim_line_items 
WHERE ABS(charged_amount - (COALESCE(allowed_amount, 0) + COALESCE(denied_amount, 0))) > 0.01;

-- PERFORMANCE INDEX VERIFICATION
-- 33. EXPLAIN - Verify index usage for member claim lookup
EXPLAIN QUERY PLAN SELECT * FROM medical_claims WHERE member_id = 100;

-- 34. EXPLAIN - Verify index usage for service date range queries
EXPLAIN QUERY PLAN SELECT * FROM medical_claims WHERE service_date >= '2024-01-01' AND service_date < '2024-02-01';

-- 35. EXPLAIN - Verify index usage for provider NPI lookup
EXPLAIN QUERY PLAN SELECT * FROM providers WHERE npi = '1000000001';