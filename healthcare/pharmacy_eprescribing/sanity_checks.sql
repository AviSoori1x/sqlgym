-- Sanity checks for pharmacy eprescribing domain

-- 1. All prescriptions reference valid patients
SELECT COUNT(*) FROM prescriptions p LEFT JOIN patients pat ON p.patient_id = pat.id WHERE pat.id IS NULL;

-- 2. All prescriptions reference valid prescribers  
SELECT COUNT(*) FROM prescriptions p LEFT JOIN prescribers pr ON p.prescriber_id = pr.id WHERE pr.id IS NULL;

-- 3. All prescriptions reference valid medications
SELECT COUNT(*) FROM prescriptions p LEFT JOIN medications m ON p.medication_id = m.id WHERE m.id IS NULL;

-- 4. All prescriptions reference valid pharmacies
SELECT COUNT(*) FROM prescriptions p LEFT JOIN pharmacies ph ON p.pharmacy_id = ph.id WHERE ph.id IS NULL;

-- 5. All prescription fills reference valid prescriptions
SELECT COUNT(*) FROM prescription_fills pf LEFT JOIN prescriptions p ON pf.prescription_id = p.id WHERE p.id IS NULL;

-- 6. Patient gender enum validation
SELECT COUNT(*) FROM patients WHERE gender IS NOT NULL AND gender NOT IN ('M', 'F', 'OTHER', 'UNKNOWN');

-- 7. Patient status enum validation
SELECT COUNT(*) FROM patients WHERE status NOT IN ('ACTIVE', 'INACTIVE', 'DECEASED');

-- 8. Prescriber status enum validation
SELECT COUNT(*) FROM prescribers WHERE status NOT IN ('ACTIVE', 'INACTIVE', 'SUSPENDED');

-- 9. Pharmacy type enum validation
SELECT COUNT(*) FROM pharmacies WHERE pharmacy_type NOT IN ('RETAIL', 'HOSPITAL', 'MAIL_ORDER', 'SPECIALTY', 'CLINIC');

-- 10. Dosage form enum validation
SELECT COUNT(*) FROM medications WHERE dosage_form NOT IN ('TABLET', 'CAPSULE', 'LIQUID', 'INJECTION', 'CREAM', 'INHALER');

-- 11. Controlled substance schedule validation
SELECT COUNT(*) FROM medications WHERE controlled_substance_schedule IS NOT NULL AND controlled_substance_schedule NOT IN ('CI', 'CII', 'CIII', 'CIV', 'CV');

-- 12. Transmission method enum validation
SELECT COUNT(*) FROM prescriptions WHERE transmission_method NOT IN ('ELECTRONIC', 'PHONE', 'FAX', 'WRITTEN');

-- 13. Prescription status enum validation
SELECT COUNT(*) FROM prescriptions WHERE status NOT IN ('PENDING', 'TRANSMITTED', 'RECEIVED', 'FILLED', 'CANCELLED', 'EXPIRED');

-- 14. Fill status enum validation
SELECT COUNT(*) FROM prescription_fills WHERE fill_status NOT IN ('PARTIAL', 'COMPLETE', 'CANCELLED');

-- 15. Unique patient IDs
SELECT patient_id, COUNT(*) FROM patients GROUP BY patient_id HAVING COUNT(*) > 1;

-- 16. Unique prescriber NPIs
SELECT npi, COUNT(*) FROM prescribers GROUP BY npi HAVING COUNT(*) > 1;

-- 17. Unique pharmacy NCPDP IDs
SELECT ncpdp_id, COUNT(*) FROM pharmacies GROUP BY ncpdp_id HAVING COUNT(*) > 1;

-- 18. Unique medication NDC codes
SELECT ndc_code, COUNT(*) FROM medications GROUP BY ndc_code HAVING COUNT(*) > 1;

-- 19. Days supply should be positive
SELECT COUNT(*) FROM prescriptions WHERE days_supply <= 0;

-- 20. Quantity prescribed should be positive
SELECT COUNT(*) FROM prescriptions WHERE quantity_prescribed <= 0;

-- 21. EXPLAIN - Verify index usage for patient prescription lookup
EXPLAIN QUERY PLAN SELECT * FROM prescriptions WHERE patient_id = 100;

-- 22. EXPLAIN - Verify index usage for prescription date queries
EXPLAIN QUERY PLAN SELECT * FROM prescriptions WHERE written_date >= '2024-01-01';