PRAGMA foreign_keys=OFF;
CREATE TABLE oee_daily AS
SELECT lr.id AS run_id, l.name AS line_name, lr.run_date,
       lr.planned_minutes, lr.good_units, lr.total_units,
       de.minutes AS downtime_minutes, n.defect_count
FROM line_runs lr
JOIN lines l ON lr.line_id=l.id
LEFT JOIN (
    SELECT line_run_id, SUM(minutes) AS minutes FROM downtime_events GROUP BY line_run_id
) de ON lr.id=de.line_run_id
LEFT JOIN (
    SELECT line_run_id, SUM(defect_count) AS defect_count FROM ncrs GROUP BY line_run_id
) n ON lr.id=n.line_run_id;
