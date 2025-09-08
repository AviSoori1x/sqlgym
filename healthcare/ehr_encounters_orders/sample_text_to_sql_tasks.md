# Sample Tasks for epic_clinical_orders

## Task 1: Provider Productivity Analysis
**User**: Which providers see the most patients?
**Assistant**: I'll analyze provider encounter volumes.
```sql
SELECT 
    pr.provider_id,
    pr.first_name || ' ' || pr.last_name as provider_name,
    pr.specialty,
    pr.department,
    COUNT(DISTINCT e.id) as total_encounters,
    COUNT(DISTINCT e.patient_id) as unique_patients,
    AVG(CASE 
        WHEN e.encounter_type = 'INPATIENT' AND e.discharge_date IS NOT NULL 
        THEN (julianday(e.discharge_date) - julianday(e.admission_date)) * 24 
    END) as avg_los_hours
FROM providers pr
JOIN encounters e ON pr.id = e.provider_id
WHERE e.encounter_date >= DATE('now', '-30 days')
  AND pr.status = 'ACTIVE'
GROUP BY pr.id
ORDER BY total_encounters DESC
LIMIT 20;
```

## Task 2: Efficiency Pair - Patient Lookup
**User**: Show encounters for patient PAT0001000
**Assistant**: Fast uses patient_id unique constraint:
```sql fast
SELECT 
    e.encounter_id,
    e.encounter_date,
    e.encounter_type,
    pr.first_name || ' ' || pr.last_name as provider,
    e.chief_complaint,
    e.status
FROM encounters e
JOIN patients p ON e.patient_id = p.id
JOIN providers pr ON e.provider_id = pr.id
WHERE p.patient_id = 'PAT0001000'
ORDER BY e.encounter_date DESC;
```
```sql slow
SELECT 
    e.encounter_id,
    e.encounter_date,
    e.encounter_type,
    pr.first_name || ' ' || pr.last_name as provider,
    e.chief_complaint,
    e.status
FROM encounters e
JOIN patients p ON e.patient_id = p.id
JOIN providers pr ON e.provider_id = pr.id
WHERE p.patient_id LIKE '%001000%'
ORDER BY e.encounter_date DESC;
```

## Task 3: Order Turnaround Analysis
**User**: What's the average turnaround time for STAT orders?
**Assistant**: Analyzing STAT order performance:
```sql
SELECT 
    ot.order_type_name,
    ot.category,
    COUNT(co.id) as stat_orders,
    AVG((julianday(co.completed_datetime) - julianday(co.order_datetime)) * 24) as avg_turnaround_hours,
    ot.typical_turnaround_hours as target_hours,
    COUNT(CASE 
        WHEN (julianday(co.completed_datetime) - julianday(co.order_datetime)) * 24 <= ot.typical_turnaround_hours 
        THEN 1 
    END) * 100.0 / COUNT(co.id) as on_time_percentage
FROM clinical_orders co
JOIN order_types ot ON co.order_type_id = ot.id
WHERE co.priority = 'STAT'
  AND co.completed_datetime IS NOT NULL
  AND co.order_datetime >= DATE('now', '-30 days')
GROUP BY ot.id
ORDER BY avg_turnaround_hours ASC;
```

## Task 4: Evidence - Clinical Protocols
**User**: What are the ordering guidelines for laboratory tests?
**Assistant**: Checking clinical protocols:
```sql
SELECT json_extract(value, '$.laboratory_protocols') as lab_guidelines
FROM evidence_kv 
WHERE key = 'clinical_protocols';
```

## Task 5: Efficiency Pair - Orders by Date
**User**: Show all orders placed today
**Assistant**: Fast uses order datetime index:
```sql fast
SELECT 
    co.order_id,
    p.patient_id,
    ot.order_type_name,
    co.priority,
    co.status
FROM clinical_orders co
JOIN encounters e ON co.encounter_id = e.id
JOIN patients p ON e.patient_id = p.id
JOIN order_types ot ON co.order_type_id = ot.id
WHERE DATE(co.order_datetime) = DATE('now')
ORDER BY co.order_datetime DESC;
```
```sql slow
SELECT 
    co.order_id,
    p.patient_id,
    ot.order_type_name,
    co.priority,
    co.status
FROM clinical_orders co
JOIN encounters e ON co.encounter_id = e.id
JOIN patients p ON e.patient_id = p.id
JOIN order_types ot ON co.order_type_id = ot.id
WHERE substr(co.order_datetime, 1, 10) = DATE('now')
ORDER BY co.order_datetime DESC;
```