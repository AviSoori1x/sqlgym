# cvs_eprescribe

## Overview
This subdomain models electronic prescribing workflows including medication management, pharmacy networks, drug interaction checking, and prescription fulfillment tracking.

## Entities

### Normalized Schema
- **patients**: Patient profiles with allergy information and insurance details
- **prescribers**: Healthcare providers with DEA numbers and prescribing credentials
- **pharmacies**: Pharmacy network with NCPDP identifiers and location data
- **medications**: Drug catalog with NDC codes, controlled substance scheduling
- **prescriptions**: Electronic prescriptions with transmission and status tracking
- **prescription_fills**: Pharmacy fulfillment records with payment information
- **drug_interactions**: Clinical decision support for medication safety

### Denormalized Schema
- **prescription_analytics**: Comprehensive prescription metrics with adherence tracking
- **pharmacy_performance**: Pharmacy-level fulfillment and service metrics
- **prescriber_patterns**: Prescriber behavior and medication utilization analysis
- **drug_utilization_summary**: Medication usage patterns and safety monitoring

## Key Indexes
- `idx_prescriptions_patient`: Patient medication history
- `idx_prescriptions_written_date`: Time-based prescribing analysis
- `idx_medications_ndc`: Drug lookup and verification
- `idx_drug_interactions_patient`: Patient safety monitoring
- `idx_prescription_fills_prescription`: Fulfillment tracking

## Efficiency Notes
- JSON allergy tracking enables comprehensive safety checking
- NDC codes provide standardized medication identification
- Controlled substance scheduling supports regulatory compliance
- Evidence files define prescribing protocols and safety guidelines
- Fast/slow pairs demonstrate index usage on patient and prescriber identifiers