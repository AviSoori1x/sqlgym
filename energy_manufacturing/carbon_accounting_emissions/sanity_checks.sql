-- Sanity checks for carbon accounting emissions domain

-- 1. All emission sources reference valid facilities
SELECT COUNT(*) FROM emission_sources es LEFT JOIN facilities f ON es.facility_id = f.id WHERE f.id IS NULL;

-- 2. All activity data references valid emission sources
SELECT COUNT(*) FROM activity_data ad LEFT JOIN emission_sources es ON ad.source_id = es.id WHERE es.id IS NULL;

-- 3. All emissions calculations reference valid sources
SELECT COUNT(*) FROM emissions_calculations ec LEFT JOIN emission_sources es ON ec.source_id = es.id WHERE es.id IS NULL;

-- 4. All emissions calculations reference valid activity data
SELECT COUNT(*) FROM emissions_calculations ec LEFT JOIN activity_data ad ON ec.activity_data_id = ad.id WHERE ad.id IS NULL;

-- 5. All emissions calculations reference valid emission factors
SELECT COUNT(*) FROM emissions_calculations ec LEFT JOIN emission_factors ef ON ec.factor_id = ef.id WHERE ef.id IS NULL;

-- 6. All regulatory reports reference valid facilities
SELECT COUNT(*) FROM regulatory_reports rr LEFT JOIN facilities f ON rr.facility_id = f.id WHERE f.id IS NULL;

-- 7. All compliance monitoring references valid facilities
SELECT COUNT(*) FROM compliance_monitoring cm LEFT JOIN facilities f ON cm.facility_id = f.id WHERE f.id IS NULL;

-- 8. Facility type enum validation
SELECT COUNT(*) FROM facilities WHERE facility_type NOT IN ('POWER_PLANT', 'MANUFACTURING', 'REFINERY', 'CHEMICAL_PLANT', 'STEEL_MILL', 'CEMENT_PLANT');

-- 9. Facility status enum validation
SELECT COUNT(*) FROM facilities WHERE status NOT IN ('OPERATIONAL', 'MAINTENANCE', 'DECOMMISSIONED');

-- 10. Emission source type enum validation
SELECT COUNT(*) FROM emission_sources WHERE source_type NOT IN ('COMBUSTION', 'PROCESS', 'FUGITIVE', 'INDIRECT');

-- 11. Emission category enum validation
SELECT COUNT(*) FROM emission_sources WHERE emission_category NOT IN ('SCOPE_1', 'SCOPE_2', 'SCOPE_3');

-- 12. Fuel type enum validation
SELECT COUNT(*) FROM emission_sources WHERE fuel_type IS NOT NULL AND fuel_type NOT IN ('NATURAL_GAS', 'COAL', 'OIL', 'BIOMASS', 'ELECTRICITY', 'STEAM');

-- 13. Pollutant enum validation
SELECT COUNT(*) FROM emission_factors WHERE pollutant NOT IN ('CO2', 'CH4', 'N2O', 'NOX', 'SO2', 'PM25', 'VOC');

-- 14. Activity type enum validation
SELECT COUNT(*) FROM activity_data WHERE activity_type NOT IN ('FUEL_CONSUMPTION', 'PRODUCTION_VOLUME', 'ELECTRICITY_USAGE', 'STEAM_CONSUMPTION');

-- 15. Data quality enum validation
SELECT COUNT(*) FROM activity_data WHERE data_quality NOT IN ('MEASURED', 'CALCULATED', 'ESTIMATED', 'DEFAULT');

-- 16. Report type enum validation
SELECT COUNT(*) FROM regulatory_reports WHERE report_type NOT IN ('EPA_GHGRP', 'EU_ETS', 'STATE_INVENTORY', 'VOLUNTARY');

-- 17. Verification status enum validation
SELECT COUNT(*) FROM regulatory_reports WHERE verification_status NOT IN ('DRAFT', 'SUBMITTED', 'VERIFIED', 'APPROVED');

-- 18. Compliance status enum validation
SELECT COUNT(*) FROM compliance_monitoring WHERE compliance_status NOT IN ('COMPLIANT', 'NON_COMPLIANT', 'PENDING_REVIEW');

-- 19. Unique facility codes
SELECT facility_code, COUNT(*) FROM facilities GROUP BY facility_code HAVING COUNT(*) > 1;

-- 20. Unique emission source codes
SELECT source_code, COUNT(*) FROM emission_sources GROUP BY source_code HAVING COUNT(*) > 1;

-- 21. Unique emission factor codes
SELECT factor_code, COUNT(*) FROM emission_factors GROUP BY factor_code HAVING COUNT(*) > 1;

-- 22. Activity amounts should be positive
SELECT COUNT(*) FROM activity_data WHERE activity_amount <= 0;

-- 23. Emission amounts should be non-negative
SELECT COUNT(*) FROM emissions_calculations WHERE emission_amount_kg < 0;

-- 24. Factor values should be positive
SELECT COUNT(*) FROM emission_factors WHERE factor_value <= 0;

-- 25. Verification date should be after calculation date
SELECT COUNT(*) FROM emissions_calculations WHERE verification_date IS NOT NULL AND verification_date < calculated_date;

-- 26. EXPLAIN - Verify index usage for facility emissions lookup
EXPLAIN QUERY PLAN SELECT * FROM emission_sources WHERE facility_id = 1;

-- 27. EXPLAIN - Verify index usage for emissions period queries
EXPLAIN QUERY PLAN SELECT * FROM emissions_calculations WHERE reporting_period = '2024-01';