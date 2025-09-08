-- Sanity checks for EHR encounters and orders domain

-- 1. All encounters reference valid patients
SELECT COUNT(*) FROM encounters e LEFT JOIN patients p ON e.patient_id = p.id WHERE p.id IS NULL;

-- 2. All encounters reference valid providers
SELECT COUNT(*) FROM encounters e LEFT JOIN providers pr ON e.provider_id = pr.id WHERE pr.id IS NULL;

-- 3. All clinical orders reference valid encounters
SELECT COUNT(*) FROM clinical_orders co LEFT JOIN encounters e ON co.encounter_id = e.id WHERE e.id IS NULL;

-- 4. All clinical orders reference valid providers
SELECT COUNT(*) FROM clinical_orders co LEFT JOIN providers pr ON co.provider_id = pr.id WHERE pr.id IS NULL;

-- 5. All clinical orders reference valid order types
SELECT COUNT(*) FROM clinical_orders co LEFT JOIN order_types ot ON co.order_type_id = ot.id WHERE ot.id IS NULL;

-- 6. All order results reference valid orders
SELECT COUNT(*) FROM order_results or_r LEFT JOIN clinical_orders co ON or_r.order_id = co.id WHERE co.id IS NULL;

-- 7. All order tracking records reference valid orders
SELECT COUNT(*) FROM order_tracking ot LEFT JOIN clinical_orders co ON ot.order_id = co.id WHERE co.id IS NULL;

-- 8. Patient gender enum validation
SELECT COUNT(*) FROM patients WHERE gender IS NOT NULL AND gender NOT IN ('M', 'F', 'OTHER', 'UNKNOWN');

-- 9. Patient status enum validation
SELECT COUNT(*) FROM patients WHERE status NOT IN ('ACTIVE', 'INACTIVE', 'DECEASED', 'TRANSFERRED');

-- 10. Provider status enum validation
SELECT COUNT(*) FROM providers WHERE status NOT IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'TERMINATED');

-- 11. Encounter type enum validation
SELECT COUNT(*) FROM encounters WHERE encounter_type NOT IN ('INPATIENT', 'OUTPATIENT', 'EMERGENCY', 'OBSERVATION', 'SURGERY');

-- 12. Encounter status enum validation
SELECT COUNT(*) FROM encounters WHERE status NOT IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW');

-- 13. Order category enum validation
SELECT COUNT(*) FROM order_types WHERE category NOT IN ('LABORATORY', 'RADIOLOGY', 'MEDICATION', 'PROCEDURE', 'CONSULT', 'THERAPY');

-- 14. Order priority enum validation
SELECT COUNT(*) FROM clinical_orders WHERE priority NOT IN ('ROUTINE', 'URGENT', 'STAT', 'ASAP');

-- 15. Order status enum validation
SELECT COUNT(*) FROM clinical_orders WHERE status NOT IN ('ORDERED', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'DISCONTINUED');

-- 16. Result type enum validation
SELECT COUNT(*) FROM order_results WHERE result_type NOT IN ('PRELIMINARY', 'FINAL', 'AMENDED', 'CORRECTED');

-- 17. Result status enum validation
SELECT COUNT(*) FROM order_results WHERE result_status NOT IN ('NORMAL', 'ABNORMAL', 'CRITICAL', 'PENDING');

-- 18. Unique patient IDs
SELECT patient_id, COUNT(*) FROM patients GROUP BY patient_id HAVING COUNT(*) > 1;

-- 19. Unique provider NPIs
SELECT npi, COUNT(*) FROM providers GROUP BY npi HAVING COUNT(*) > 1;

-- 20. Unique encounter IDs
SELECT encounter_id, COUNT(*) FROM encounters GROUP BY encounter_id HAVING COUNT(*) > 1;

-- 21. Discharge date should be after admission date for inpatients
SELECT COUNT(*) FROM encounters WHERE encounter_type = 'INPATIENT' AND discharge_date IS NOT NULL AND admission_date IS NOT NULL AND discharge_date <= admission_date;

-- 22. Order datetime should be during or after encounter
SELECT COUNT(*) FROM clinical_orders co JOIN encounters e ON co.encounter_id = e.id WHERE co.order_datetime < e.encounter_date;

-- 23. Result datetime should be after order datetime
SELECT COUNT(*) FROM order_results or_r JOIN clinical_orders co ON or_r.order_id = co.id WHERE or_r.result_datetime < co.order_datetime;

-- 24. Completed orders should have completed datetime
SELECT COUNT(*) FROM clinical_orders WHERE status = 'COMPLETED' AND completed_datetime IS NULL;

-- 25. EXPLAIN - Verify index usage for patient encounter lookup
EXPLAIN QUERY PLAN SELECT * FROM encounters WHERE patient_id = 100;

-- 26. EXPLAIN - Verify index usage for encounter date range queries
EXPLAIN QUERY PLAN SELECT * FROM encounters WHERE encounter_date >= '2024-01-01' AND encounter_date < '2024-02-01';