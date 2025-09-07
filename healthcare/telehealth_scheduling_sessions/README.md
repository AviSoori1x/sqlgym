# telehealth_scheduling_sessions

## Entities
- providers
- patients
- appointments
- sessions
- feedback

## Distinctiveness
Tracks telehealth appointments and session feedback.

## Indexes
- `appointments(provider_id, appt_time)`
- `sessions(appointment_id)`
- `feedback(session_id)`

## Expected Row Counts
- appointments: 5
- sessions: 3

## Efficiency Notes
Indexes support querying schedules and related session data. Denormalized `telehealth_summary` streamlines provider reports with some duplication.
