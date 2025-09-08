# epic_clinical_orders

## Overview
This subdomain models electronic health record workflows including patient encounters, clinical order management, provider productivity, and result tracking.

## Entities

### Normalized Schema
- **patients**: Patient demographics and contact information with insurance details
- **providers**: Healthcare provider profiles with specialties and credentials
- **encounters**: Patient visits with admission/discharge tracking and diagnoses
- **order_types**: Clinical order catalog with categories and turnaround times
- **clinical_orders**: Individual orders with priority and workflow status
- **order_results**: Lab/imaging results with interpretation and values
- **order_tracking**: Order status change audit trail

### Denormalized Schema
- **encounter_summary**: Comprehensive encounter metrics with order completion rates
- **provider_productivity**: Provider-level performance and efficiency metrics
- **order_workflow_metrics**: Order type performance and turnaround analysis
- **department_utilization**: Department capacity and workload distribution

## Key Indexes
- `idx_encounters_patient`: Patient encounter history
- `idx_clinical_orders_encounter`: Encounter order management
- `idx_clinical_orders_datetime`: Time-based order analysis
- `idx_order_results_order`: Order-result relationship tracking
- `idx_providers_specialty`: Specialty-based provider queries

## Efficiency Notes
- JSON diagnosis codes enable flexible ICD-10 coding
- Order tracking provides complete audit trail for workflow analysis
- Priority levels support STAT order workflow optimization
- Evidence files define clinical protocols and order guidelines
- Fast/slow pairs demonstrate index usage on patient/provider identifiers