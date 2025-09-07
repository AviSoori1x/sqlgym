# treasury_risk

## Entities
- desks
- limits
- exposures
- scenarios
- breaches

## Distinctiveness
Tracks exposure to risk limits across trading desks with scenario analysis.

## Indexes
- `exposures(as_of, desk_id)`
- `breaches(limit_id, breached_on)`

## Expected Row Counts
- desks: 10
- exposures: 100k

## Efficiency Notes
Composite indexes accelerate exposure lookups by desk and date.
