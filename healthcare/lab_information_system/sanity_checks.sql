-- orders per patient
SELECT patient_id, COUNT(*) FROM lab_orders GROUP BY patient_id;
