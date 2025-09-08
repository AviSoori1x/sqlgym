# cerner_revenue_cycle

## Entities
- patients
- bills
- bill_items
- payments
- denials

## Distinctiveness
Represents billing lifecycle with payments and denials.

## Indexes
- `bills(patient_id, bill_date)`
- `bill_items(bill_id)`
- `denials(bill_id, denial_date)`

## Expected Row Counts
- bills: 3
- bill_items: 6

## Efficiency Notes
Indexes enable quick aggregation of bill items and denial tracking. Denormalized `billing_summary` eases patient billing reports but repeats names.
