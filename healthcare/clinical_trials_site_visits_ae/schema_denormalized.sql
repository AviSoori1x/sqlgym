PRAGMA foreign_keys=OFF;
CREATE TABLE visit_events AS
SELECT s.name AS subject_name, t.title AS trial_title,
       v.visit_date, ae.description, ae.severity
FROM site_visits v
JOIN subjects s ON s.id=v.subject_id
JOIN trials t ON t.id=v.trial_id
LEFT JOIN adverse_events ae ON ae.visit_id=v.id;
CREATE INDEX idx_visit_events_subject ON visit_events(subject_name);
