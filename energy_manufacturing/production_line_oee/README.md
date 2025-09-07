# production_line_oee

## Entities
- lines
- line_runs
- downtime_events
- ncrs

## Distinctiveness
Computes Overall Equipment Effectiveness from run data.

## Indexes
- `line_runs(line_id, run_date)`
- `downtime_events(line_run_id)`
- `ncrs(line_run_id)`

## Expected Row Counts
- line_runs: 10k
- downtime_events: 30k

## Efficiency Notes
Indexes enable OEE aggregation by line and date.
