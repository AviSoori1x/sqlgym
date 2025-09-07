# ehr_encounters_orders

## Entities
- patients
- encounters
- orders
- results

## Distinctiveness
Models clinical orders and lab results with encounter context.

## Indexes
- `encounters(patient_id, encounter_date)`
- `orders(encounter_id, order_time)`
- `results(order_id, result_time)`

## Expected Row Counts
- encounters: 5k
- orders: 20k

## Efficiency Notes
Indexes help link orders to results within SLA windows.
