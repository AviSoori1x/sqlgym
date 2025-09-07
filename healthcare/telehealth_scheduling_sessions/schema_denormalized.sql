PRAGMA foreign_keys=OFF;
CREATE TABLE telehealth_summary AS
SELECT pr.name AS provider_name, pa.name AS patient_name,
       a.appt_time, s.status, f.rating
FROM appointments a
JOIN providers pr ON pr.id=a.provider_id
JOIN patients pa ON pa.id=a.patient_id
LEFT JOIN sessions s ON s.appointment_id=a.id
LEFT JOIN feedback f ON f.session_id=s.id;
CREATE INDEX idx_telehealth_summary_provider ON telehealth_summary(provider_name);
