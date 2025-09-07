# radiology_pacs_worklist

## Entities
- patients
- radiologists
- studies
- images
- assignments

## Distinctiveness
Manages imaging studies and radiologist assignments.

## Indexes
- `studies(patient_id, study_date)`
- `images(study_id)`
- `assignments(study_id, radiologist_id)`

## Expected Row Counts
- studies: 5
- assignments: 5

## Efficiency Notes
Indexes support rapid filtering of studies and assignments. Denormalized `worklist_summary` speeds dashboard queries at cost of redundancy.
