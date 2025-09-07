-- studies per patient
SELECT patient_id, COUNT(*) FROM studies GROUP BY patient_id;
