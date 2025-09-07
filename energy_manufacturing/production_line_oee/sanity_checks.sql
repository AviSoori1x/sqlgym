-- OEE calculation
SELECT id, (good_units*1.0/total_units) AS quality FROM line_runs;

-- downtime totals
SELECT line_run_id, SUM(minutes) FROM downtime_events GROUP BY line_run_id;

-- defects per run
SELECT line_run_id, SUM(defect_count) FROM ncrs GROUP BY line_run_id;
