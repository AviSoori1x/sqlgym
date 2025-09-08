# Workflow Tasks

## Task: claims denial rate
```sql
-- step: claims
CREATE TEMP TABLE claims AS
SELECT id, status FROM claims;
```
```sql
-- step: denials
-- depends: claims
CREATE TEMP TABLE denials AS
SELECT COUNT(*) c FROM claims WHERE status='DENIED';
```
```sql
-- step: final
-- depends: denials
SELECT c FROM denials;
```

## Task: comprehensive_patient_care_analysis
```sql
-- step: patient_encounters
CREATE TEMP TABLE patient_encounters AS
SELECT 
    p.patient_id,
    COUNT(DISTINCT e.id) as total_encounters,
    COUNT(DISTINCT co.id) as total_orders,
    COUNT(DISTINCT mc.id) as total_claims,
    MAX(e.encounter_date) as last_encounter_date
FROM patients p
LEFT JOIN encounters e ON p.id = e.patient_id
LEFT JOIN clinical_orders co ON e.id = co.encounter_id
LEFT JOIN medical_claims mc ON p.id = mc.member_id
WHERE p.status = 'ACTIVE'
GROUP BY p.id;
```
```sql
-- step: medication_adherence
-- depends: patient_encounters
CREATE TEMP TABLE medication_adherence AS
SELECT 
    pe.patient_id,
    COUNT(DISTINCT pr.id) as total_prescriptions,
    COUNT(DISTINCT pf.prescription_id) as filled_prescriptions,
    COUNT(DISTINCT pf.prescription_id) * 100.0 / NULLIF(COUNT(DISTINCT pr.id), 0) as fill_rate
FROM patient_encounters pe
LEFT JOIN prescriptions pr ON pe.patient_id = CAST(SUBSTR(pr.patient_id, 4) AS INTEGER)
LEFT JOIN prescription_fills pf ON pr.id = pf.prescription_id
GROUP BY pe.patient_id;
```
```sql
-- step: lab_results_analysis
-- depends: patient_encounters
CREATE TEMP TABLE lab_results_analysis AS
SELECT 
    pe.patient_id,
    COUNT(DISTINCT lo.id) as lab_orders_count,
    COUNT(DISTINCT lr.id) as lab_results_count,
    COUNT(DISTINCT CASE WHEN lr.abnormal_flag IN ('CRITICAL_HIGH', 'CRITICAL_LOW') THEN lr.id END) as critical_results,
    AVG((julianday(lr.result_datetime) - julianday(lo.order_datetime)) * 24) as avg_turnaround_hours
FROM patient_encounters pe
LEFT JOIN lab_orders lo ON pe.patient_id = CAST(SUBSTR(lo.patient_id, 4) AS INTEGER)
LEFT JOIN specimens s ON lo.id = s.order_id
LEFT JOIN lab_results lr ON s.id = lr.specimen_id
GROUP BY pe.patient_id;
```
```sql
-- step: comprehensive_care_summary
-- depends: patient_encounters, medication_adherence, lab_results_analysis
SELECT 
    pe.patient_id,
    pe.total_encounters,
    pe.total_orders,
    pe.total_claims,
    ma.fill_rate as medication_adherence_rate,
    lra.critical_results,
    lra.avg_turnaround_hours,
    CASE 
        WHEN pe.total_encounters >= 4 AND ma.fill_rate >= 80 AND lra.critical_results = 0 THEN 'Well Managed'
        WHEN pe.total_encounters >= 2 AND ma.fill_rate >= 60 THEN 'Adequately Managed'
        WHEN lra.critical_results > 0 OR ma.fill_rate < 50 THEN 'High Risk'
        ELSE 'Needs Assessment'
    END as care_quality_category
FROM patient_encounters pe
LEFT JOIN medication_adherence ma ON pe.patient_id = ma.patient_id
LEFT JOIN lab_results_analysis lra ON pe.patient_id = lra.patient_id
WHERE pe.total_encounters > 0
ORDER BY care_quality_category, pe.total_encounters DESC;
```

## Task: clinical_quality_metrics
```sql
-- step: provider_performance
CREATE TEMP TABLE provider_performance AS
SELECT 
    pr.provider_id,
    pr.specialty,
    COUNT(DISTINCT e.id) as encounters,
    COUNT(DISTINCT co.id) as orders_placed,
    COUNT(DISTINCT CASE WHEN co.priority = 'STAT' THEN co.id END) as stat_orders,
    AVG(CASE 
        WHEN co.completed_datetime IS NOT NULL 
        THEN (julianday(co.completed_datetime) - julianday(co.order_datetime)) * 24 
    END) as avg_order_completion_hours
FROM providers pr
LEFT JOIN encounters e ON pr.id = e.provider_id
LEFT JOIN clinical_orders co ON e.id = co.encounter_id
WHERE pr.status = 'ACTIVE'
  AND e.encounter_date >= DATE('now', '-90 days')
GROUP BY pr.id;
```
```sql
-- step: medication_safety_check
-- depends: provider_performance
CREATE TEMP TABLE medication_safety_check AS
SELECT 
    pr.specialty,
    COUNT(DISTINCT di.id) as drug_interactions_detected,
    COUNT(DISTINCT p.id) as controlled_substance_prescriptions,
    COUNT(DISTINCT CASE WHEN m.controlled_substance_schedule IS NOT NULL THEN p.id END) as controlled_rx_count
FROM providers prov
LEFT JOIN prescriptions p ON prov.id = CAST(SUBSTR(p.prescriber_id, 5) AS INTEGER)
LEFT JOIN medications m ON p.medication_id = m.id
LEFT JOIN drug_interactions di ON p.patient_id = di.patient_id
WHERE prov.specialty IN ('Internal Medicine', 'Family Medicine', 'Psychiatry')
GROUP BY prov.specialty;
```
```sql
-- step: quality_indicators
-- depends: provider_performance, medication_safety_check
CREATE TEMP TABLE quality_indicators AS
SELECT 
    'Provider Performance' as metric_category,
    pp.specialty,
    AVG(pp.avg_order_completion_hours) as avg_metric,
    'Hours' as metric_unit,
    CASE WHEN AVG(pp.avg_order_completion_hours) < 4 THEN 'Excellent' ELSE 'Needs Improvement' END as quality_rating
FROM provider_performance pp
GROUP BY pp.specialty
UNION ALL
SELECT 
    'Medication Safety' as metric_category,
    msc.specialty,
    msc.drug_interactions_detected as avg_metric,
    'Interactions Detected' as metric_unit,
    CASE WHEN msc.drug_interactions_detected < 10 THEN 'Good' ELSE 'Review Needed' END as quality_rating
FROM medication_safety_check msc;
```
```sql
-- step: quality_dashboard
-- depends: quality_indicators
SELECT 
    metric_category,
    COUNT(*) as metrics_tracked,
    AVG(avg_metric) as overall_average,
    COUNT(CASE WHEN quality_rating IN ('Excellent', 'Good') THEN 1 END) as passing_metrics,
    COUNT(CASE WHEN quality_rating IN ('Excellent', 'Good') THEN 1 END) * 100.0 / COUNT(*) as quality_percentage
FROM quality_indicators
GROUP BY metric_category
ORDER BY quality_percentage DESC;
```

## Task: population_health_outcomes
```sql
-- step: registry_enrollment_base
CREATE TEMP TABLE registry_enrollment_base AS
SELECT 
    dr.registry_name,
    dr.disease_category,
    COUNT(DISTINCT re.patient_id) as enrolled_patients,
    AVG(CASE WHEN re.risk_stratification = 'HIGH' THEN 1.0 ELSE 0.0 END) as high_risk_percentage
FROM disease_registries dr
LEFT JOIN registry_enrollments re ON dr.id = re.registry_id
WHERE re.status = 'ACTIVE'
GROUP BY dr.id;
```
```sql
-- step: health_measures_tracking
-- depends: registry_enrollment_base
CREATE TEMP TABLE health_measures_tracking AS
SELECT 
    reb.registry_name,
    COUNT(DISTINCT hm.id) as total_measures,
    COUNT(DISTINCT CASE WHEN hm.is_goal_met = 1 THEN hm.id END) as goals_met,
    COUNT(DISTINCT CASE WHEN hm.is_goal_met = 1 THEN hm.id END) * 100.0 / COUNT(DISTINCT hm.id) as goal_achievement_rate,
    COUNT(DISTINCT i.id) as interventions_delivered
FROM registry_enrollment_base reb
LEFT JOIN registry_enrollments re ON reb.registry_name = (SELECT registry_name FROM disease_registries WHERE id = re.registry_id)
LEFT JOIN health_measures hm ON re.id = hm.enrollment_id
LEFT JOIN interventions i ON re.patient_id = i.patient_id
WHERE hm.measure_date >= DATE('now', '-90 days')
GROUP BY reb.registry_name;
```
```sql
-- step: outcome_effectiveness
-- depends: health_measures_tracking
CREATE TEMP TABLE outcome_effectiveness AS
SELECT 
    hmt.registry_name,
    hmt.goal_achievement_rate,
    hmt.interventions_delivered,
    hmt.interventions_delivered * 1.0 / NULLIF(enrolled_patients, 0) as interventions_per_patient,
    CASE 
        WHEN hmt.goal_achievement_rate >= 80 THEN 'High Performing'
        WHEN hmt.goal_achievement_rate >= 60 THEN 'Meeting Targets'
        ELSE 'Needs Improvement'
    END as performance_category
FROM health_measures_tracking hmt
JOIN registry_enrollment_base reb ON hmt.registry_name = reb.registry_name;
```
```sql
-- step: population_health_summary
-- depends: outcome_effectiveness
SELECT 
    performance_category,
    COUNT(*) as registry_count,
    AVG(goal_achievement_rate) as avg_goal_achievement,
    SUM(interventions_delivered) as total_interventions,
    AVG(interventions_per_patient) as avg_interventions_per_patient
FROM outcome_effectiveness
GROUP BY performance_category
ORDER BY avg_goal_achievement DESC;
```