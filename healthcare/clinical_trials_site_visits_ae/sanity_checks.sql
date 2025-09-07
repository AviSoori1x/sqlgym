-- visits per trial
SELECT trial_id, COUNT(*) FROM site_visits GROUP BY trial_id;
