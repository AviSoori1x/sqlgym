# Workflow for production_line_oee

```sql
-- step: availability
CREATE TEMP TABLE avail AS
SELECT id, planned_minutes - IFNULL((SELECT SUM(minutes) FROM downtime_events de WHERE de.line_run_id=lr.id),0) AS avail_min
FROM line_runs lr;

-- step: oee_calc
-- depends: availability
SELECT a.id, a.avail_min, lr.good_units, lr.total_units
FROM avail a JOIN line_runs lr ON a.id=lr.id;
```
