# exxon_carbon_tracking

## Overview
This subdomain models carbon accounting and emissions tracking for industrial facilities including activity data collection, emissions calculations, regulatory reporting, and compliance monitoring.

## Entities

### Normalized Schema
- **facilities**: Industrial facilities with operational capacity and regulatory jurisdiction
- **emission_sources**: Equipment and processes that generate emissions
- **emission_factors**: Calculation factors for converting activity to emissions
- **activity_data**: Fuel consumption and production activity measurements
- **emissions_calculations**: Calculated emissions with verification status
- **regulatory_reports**: Annual emissions reports to regulatory agencies
- **compliance_monitoring**: Ongoing compliance tracking and violation management

### Denormalized Schema
- **facility_emissions_summary**: Comprehensive facility-level emissions and trends
- **monthly_emissions_rollup**: Monthly emissions aggregations by source type
- **regulatory_compliance_status**: Compliance tracking and reporting status
- **carbon_intensity_metrics**: Production-normalized emissions intensity tracking

## Key Indexes
- `idx_emission_sources_facility`: Facility emissions source management
- `idx_activity_data_source`: Source activity data tracking
- `idx_emissions_calculations_period`: Time-based emissions analysis
- `idx_regulatory_reports_facility`: Facility reporting compliance
- `idx_compliance_monitoring_facility`: Compliance status tracking

## Efficiency Notes
- JSON pollutant arrays enable multi-pollutant tracking
- Scope 1/2/3 categorization supports GHG Protocol compliance
- Verification workflow ensures data quality and regulatory compliance
- Evidence files define emission factors and calculation methodologies
- Fast/slow pairs demonstrate index usage on facility and time-based queries