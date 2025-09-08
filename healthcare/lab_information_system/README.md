# labcorp_lis

## Overview
This subdomain models laboratory information system workflows including test ordering, specimen processing, result reporting, and quality control management.

## Entities

### Normalized Schema
- **patients**: Patient demographics with medical record numbers
- **lab_tests**: Laboratory test catalog with reference ranges and critical values
- **lab_orders**: Test orders with clinical indications and priority levels
- **specimens**: Specimen collection and processing tracking
- **lab_results**: Test results with abnormal flags and interpretation
- **quality_controls**: Laboratory quality assurance and control monitoring

### Denormalized Schema
- **lab_analytics**: Comprehensive test metrics with turnaround times
- **daily_lab_metrics**: Daily laboratory volume and performance tracking
- **test_utilization_summary**: Test ordering patterns and appropriateness
- **quality_performance**: Quality control trends and compliance monitoring

## Key Indexes
- `idx_lab_orders_patient`: Patient test history
- `idx_lab_orders_datetime`: Time-based order analysis
- `idx_specimens_order`: Order-specimen tracking
- `idx_lab_results_specimen`: Result reporting workflow
- `idx_quality_controls_test`: QC monitoring by test type

## Efficiency Notes
- Critical value alerting through abnormal flags
- Specimen condition tracking ensures result reliability
- Quality control integration supports laboratory accreditation
- Evidence files define collection protocols and reference ranges
- Fast/slow pairs demonstrate index usage on patient and specimen identifiers