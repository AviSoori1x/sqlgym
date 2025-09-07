# lab_information_system

## Entities
- patients
- lab_tests
- lab_orders
- specimens
- lab_results

## Distinctiveness
Tracks lab orders from request to result.

## Indexes
- `lab_orders(patient_id, ordered_at)`
- `specimens(order_id)`
- `lab_results(specimen_id, result_date)`

## Expected Row Counts
- lab_orders: 5
- lab_results: 5

## Efficiency Notes
Indexes help locate orders by patient and join results quickly. Denormalized `lab_summary` eases reporting but duplicates patient and test names.
