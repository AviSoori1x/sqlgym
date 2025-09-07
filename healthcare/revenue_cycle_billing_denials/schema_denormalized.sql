PRAGMA foreign_keys=OFF;
CREATE TABLE billing_summary AS
SELECT p.name AS patient_name, b.bill_date, b.total,
       pay.amount AS payment_amount, d.reason
FROM bills b
JOIN patients p ON p.id=b.patient_id
LEFT JOIN payments pay ON pay.bill_id=b.id
LEFT JOIN denials d ON d.bill_id=b.id;
CREATE INDEX idx_billing_summary_patient ON billing_summary(patient_name);
