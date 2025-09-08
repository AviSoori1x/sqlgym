# pfizer_clinical_trials

## Entities
- subjects
- trials
- investigators
- site_visits
- adverse_events

## Distinctiveness
Models clinical trial visits and reported adverse events.

## Indexes
- `site_visits(subject_id, trial_id, visit_date)`
- `site_visits(investigator_id)`
- `adverse_events(visit_id)`

## Expected Row Counts
- site_visits: 10
- adverse_events: 5

## Efficiency Notes
Indexes support filtering by subject and investigator. Denormalized `visit_events` simplifies reporting at cost of duplication.
