PRAGMA foreign_keys=OFF;
CREATE TABLE prescription_summary AS
SELECT p.name AS patient_name, m.name AS medication_name,
       r.written_date, f.fill_date, f.status, ph.state
FROM prescriptions r
JOIN patients p ON p.id=r.patient_id
JOIN medications m ON m.id=r.medication_id
JOIN pharmacies ph ON ph.id=r.pharmacy_id
LEFT JOIN fills f ON f.prescription_id=r.id;
CREATE INDEX idx_prescription_summary_patient ON prescription_summary(patient_name);
