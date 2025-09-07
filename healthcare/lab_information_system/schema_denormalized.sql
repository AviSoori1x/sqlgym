PRAGMA foreign_keys=OFF;
CREATE TABLE lab_summary AS
SELECT p.name AS patient_name, t.name AS test_name,
       r.result_value, r.result_date
FROM lab_orders o
JOIN patients p ON p.id=o.patient_id
JOIN lab_tests t ON t.id=o.test_id
JOIN specimens s ON s.order_id=o.id
JOIN lab_results r ON r.specimen_id=s.id;
CREATE INDEX idx_lab_summary_patient ON lab_summary(patient_name);
