PRAGMA foreign_keys=OFF;
CREATE TABLE worklist_summary AS
SELECT p.name AS patient_name, s.study_date, a.assigned_at, r.name AS radiologist_name
FROM studies s
JOIN patients p ON p.id=s.patient_id
LEFT JOIN assignments a ON a.study_id=s.id
LEFT JOIN radiologists r ON r.id=a.radiologist_id;
CREATE INDEX idx_worklist_summary_patient ON worklist_summary(patient_name);
