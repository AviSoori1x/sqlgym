# population_health_registries

## Entities
- patients
- registries
- enrollments
- metrics
- risk_scores

## Distinctiveness
Supports population health tracking across disease registries.

## Indexes
- `enrollments(patient_id, registry_id)`
- `metrics(patient_id, metric_date)`
- `risk_scores(patient_id)`

## Expected Row Counts
- enrollments: 5
- metrics: 5
- risk_scores: 5

## Efficiency Notes
Indexes enable quick registry membership and metric lookups. Denormalized `registry_summary` repeats patient names but simplifies cohort reporting.
