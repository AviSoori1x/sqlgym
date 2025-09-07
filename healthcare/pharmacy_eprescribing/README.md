# pharmacy_eprescribing

## Entities
- patients
- medications
- pharmacies
- prescriptions
- fills

## Distinctiveness
Captures electronic prescriptions and pharmacy fills.

## Indexes
- `prescriptions(patient_id, written_date)`
- `fills(prescription_id, fill_date)`
- `pharmacies(state)`

## Expected Row Counts
- prescriptions: 5
- fills: 3

## Efficiency Notes
Indexes speed lookup of prescriptions by patient and fill tracking. Denormalized `prescription_summary` simplifies patient-medication reports while duplicating data.
