# claims_processing

## Entities
- patients
- payer_plans
- claims
- claim_lines
- adjudications
- denials

## Distinctiveness
Captures insurance claim lifecycle including adjudication and denials.

## Indexes
- `claims(plan_id, claim_date)`
- `claim_lines(claim_id)`
- `adjudications(claim_line_id)`
- `denials(claim_id, denial_date)`

## Expected Row Counts
- claims: 20k
- claim_lines: 60k

## Efficiency Notes
Indexes speed up claim lookups by plan and date.
