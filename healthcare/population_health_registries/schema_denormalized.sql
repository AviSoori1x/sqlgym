PRAGMA foreign_keys=OFF;
CREATE TABLE registry_summary AS
SELECT p.name AS patient_name, r.name AS registry_name,
       m.metric_value, s.score
FROM enrollments e
JOIN patients p ON p.id=e.patient_id
JOIN registries r ON r.id=e.registry_id
LEFT JOIN metrics m ON m.patient_id=p.id
LEFT JOIN risk_scores s ON s.patient_id=p.id;
CREATE INDEX idx_registry_summary_patient ON registry_summary(patient_name);
