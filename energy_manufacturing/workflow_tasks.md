# Workflow Tasks

## Task: carbon_emissions_regulatory_compliance
```sql
-- step: facility_emissions_totals
CREATE TEMP TABLE facility_emissions_totals AS
SELECT 
    f.facility_code,
    f.facility_name,
    f.regulatory_jurisdiction,
    SUM(ec.co2_equivalent_kg) / 1000 as annual_co2_tonnes,
    COUNT(DISTINCT es.id) as emission_sources_count
FROM facilities f
JOIN emission_sources es ON f.id = es.facility_id
JOIN emissions_calculations ec ON es.id = ec.source_id
WHERE ec.reporting_period LIKE '2024-%'
GROUP BY f.id;
```
```sql
-- step: regulatory_thresholds_check
-- depends: facility_emissions_totals
CREATE TEMP TABLE regulatory_thresholds_check AS
SELECT 
    fet.facility_code,
    fet.annual_co2_tonnes,
    fet.regulatory_jurisdiction,
    CASE 
        WHEN fet.regulatory_jurisdiction LIKE 'USA_%' AND fet.annual_co2_tonnes >= 25 THEN 'EPA_GHGRP_REQUIRED'
        WHEN fet.regulatory_jurisdiction LIKE 'EU_%' AND fet.annual_co2_tonnes >= 20 THEN 'EU_ETS_REQUIRED'
        WHEN fet.annual_co2_tonnes >= 10 THEN 'STATE_REPORTING_REQUIRED'
        ELSE 'VOLUNTARY_ONLY'
    END as reporting_requirement,
    EXISTS(
        SELECT 1 FROM regulatory_reports rr 
        WHERE rr.facility_id = (SELECT id FROM facilities WHERE facility_code = fet.facility_code)
        AND rr.reporting_year = 2024
    ) as compliance_report_filed
FROM facility_emissions_totals fet;
```
```sql
-- step: compliance_gaps
-- depends: regulatory_thresholds_check
CREATE TEMP TABLE compliance_gaps AS
SELECT 
    rtc.facility_code,
    rtc.reporting_requirement,
    rtc.compliance_report_filed,
    CASE 
        WHEN rtc.reporting_requirement != 'VOLUNTARY_ONLY' AND rtc.compliance_report_filed = 0 THEN 'NON_COMPLIANT'
        WHEN rtc.reporting_requirement != 'VOLUNTARY_ONLY' AND rtc.compliance_report_filed = 1 THEN 'COMPLIANT'
        ELSE 'NOT_APPLICABLE'
    END as compliance_status
FROM regulatory_thresholds_check rtc;
```
```sql
-- step: compliance_summary
-- depends: compliance_gaps
SELECT 
    reporting_requirement,
    COUNT(*) as facilities_count,
    COUNT(CASE WHEN compliance_status = 'COMPLIANT' THEN 1 END) as compliant_facilities,
    COUNT(CASE WHEN compliance_status = 'NON_COMPLIANT' THEN 1 END) as non_compliant_facilities,
    COUNT(CASE WHEN compliance_status = 'COMPLIANT' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(CASE WHEN compliance_status != 'NOT_APPLICABLE' THEN 1 END), 0) as compliance_rate
FROM compliance_gaps
GROUP BY reporting_requirement
ORDER BY facilities_count DESC;
```

## Task: production_efficiency_optimization  
```sql
-- step: line_oee_performance
CREATE TEMP TABLE line_oee_performance AS
SELECT 
    pl.line_code,
    mp.plant_name,
    COUNT(pr.id) as total_runs,
    AVG(oc.oee_percentage) as avg_oee,
    AVG(oc.availability_percentage) as avg_availability,
    AVG(oc.performance_percentage) as avg_performance,
    AVG(oc.quality_percentage) as avg_quality,
    SUM(pr.good_units_produced) as total_good_units
FROM production_lines pl
JOIN manufacturing_plants mp ON pl.plant_id = mp.id
LEFT JOIN production_runs pr ON pl.id = pr.line_id
LEFT JOIN oee_calculations oc ON pr.id = oc.production_run_id
WHERE pr.run_start_time >= DATE('now', '-30 days')
GROUP BY pl.id;
```
```sql
-- step: downtime_root_causes
-- depends: line_oee_performance
CREATE TEMP TABLE downtime_root_causes AS
SELECT 
    lop.line_code,
    de.downtime_category,
    COUNT(de.id) as event_count,
    SUM(de.downtime_minutes) as total_downtime_minutes,
    AVG(de.downtime_minutes) as avg_event_duration
FROM line_oee_performance lop
JOIN production_lines pl ON lop.line_code = pl.line_code
JOIN production_runs pr ON pl.id = pr.line_id
JOIN downtime_events de ON pr.id = de.production_run_id
GROUP BY lop.line_code, de.downtime_category;
```
```sql
-- step: improvement_opportunities
-- depends: line_oee_performance, downtime_root_causes
CREATE TEMP TABLE improvement_opportunities AS
SELECT 
    lop.line_code,
    lop.avg_oee,
    drc.downtime_category,
    drc.total_downtime_minutes,
    CASE 
        WHEN lop.avg_oee < 60 AND drc.downtime_category = 'UNPLANNED_MAINTENANCE' THEN 'Critical: Implement Predictive Maintenance'
        WHEN lop.avg_oee < 70 AND drc.downtime_category = 'SETUP_CHANGEOVER' THEN 'High: Optimize Changeover Process'
        WHEN lop.avg_quality < 95 THEN 'Medium: Improve Quality Control'
        WHEN lop.avg_performance < 85 THEN 'Medium: Optimize Operating Speed'
        ELSE 'Low: Monitor and Maintain'
    END as improvement_priority,
    drc.total_downtime_minutes * 0.75 as estimated_recovery_minutes
FROM line_oee_performance lop
LEFT JOIN downtime_root_causes drc ON lop.line_code = drc.line_code
WHERE lop.avg_oee < 85;  -- Industry benchmark
```
```sql
-- step: optimization_recommendations
-- depends: improvement_opportunities
SELECT 
    improvement_priority,
    COUNT(DISTINCT line_code) as lines_affected,
    SUM(total_downtime_minutes) as total_downtime_impact,
    SUM(estimated_recovery_minutes) as potential_recovery,
    SUM(estimated_recovery_minutes) / 60 as potential_recovery_hours,
    'Implement recommended actions' as next_steps
FROM improvement_opportunities
GROUP BY improvement_priority
ORDER BY 
    CASE improvement_priority 
        WHEN 'Critical: Implement Predictive Maintenance' THEN 1
        WHEN 'High: Optimize Changeover Process' THEN 2
        ELSE 3 
    END;
```

## Task: supplier_performance_analysis
```sql
-- step: supplier_scorecard_base
CREATE TEMP TABLE supplier_scorecard_base AS
SELECT 
    s.supplier_code,
    s.supplier_name,
    s.business_category,
    s.risk_rating,
    COUNT(DISTINCT po.id) as total_pos,
    SUM(po.total_amount) as total_spend,
    AVG(spm.on_time_delivery_rate) as avg_otd_rate,
    AVG(spm.quality_score) as avg_quality_score,
    AVG(spm.overall_score) as avg_overall_score
FROM suppliers s
LEFT JOIN purchase_orders po ON s.id = po.supplier_id
LEFT JOIN supplier_performance_metrics spm ON s.id = spm.supplier_id
WHERE po.order_date >= DATE('now', '-12 months')
GROUP BY s.id;
```
```sql
-- step: performance_categorization
-- depends: supplier_scorecard_base
CREATE TEMP TABLE performance_categorization AS
SELECT 
    ssb.*,
    CASE 
        WHEN ssb.avg_overall_score >= 90 THEN 'STRATEGIC_PARTNER'
        WHEN ssb.avg_overall_score >= 80 THEN 'PREFERRED_SUPPLIER'
        WHEN ssb.avg_overall_score >= 70 THEN 'APPROVED_SUPPLIER'
        WHEN ssb.avg_overall_score >= 60 THEN 'CONDITIONAL_SUPPLIER'
        ELSE 'AT_RISK_SUPPLIER'
    END as performance_category,
    CASE 
        WHEN ssb.total_spend >= 1000000 THEN 'HIGH_SPEND'
        WHEN ssb.total_spend >= 100000 THEN 'MEDIUM_SPEND'
        ELSE 'LOW_SPEND'
    END as spend_category
FROM supplier_scorecard_base ssb;
```
```sql
-- step: strategic_recommendations
-- depends: performance_categorization
SELECT 
    performance_category,
    spend_category,
    COUNT(*) as supplier_count,
    SUM(total_spend) as category_spend,
    AVG(avg_overall_score) as avg_score,
    CASE 
        WHEN performance_category = 'STRATEGIC_PARTNER' THEN 'Expand Partnership'
        WHEN performance_category = 'PREFERRED_SUPPLIER' AND spend_category = 'HIGH_SPEND' THEN 'Develop Strategic Partnership'
        WHEN performance_category = 'AT_RISK_SUPPLIER' THEN 'Improvement Plan or Replace'
        WHEN performance_category = 'CONDITIONAL_SUPPLIER' THEN 'Performance Improvement Required'
        ELSE 'Monitor Performance'
    END as recommended_action
FROM performance_categorization
GROUP BY performance_category, spend_category
ORDER BY category_spend DESC;
```