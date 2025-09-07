# care_management_utilization

## Entities
- members
- care_programs
- enrollments
- interventions
- outcomes

## Distinctiveness
Tracks care program participation and outcomes for members.

## Indexes
- `enrollments(member_id, program_id)`
- `interventions(enrollment_id, intervention_date)`
- `outcomes(intervention_id)`

## Expected Row Counts
- members: 5
- enrollments: 10
- interventions: 10

## Efficiency Notes
Indexes speed member-program lookups and intervention timelines. Denormalized `care_summary` trades storage for simpler reporting.
