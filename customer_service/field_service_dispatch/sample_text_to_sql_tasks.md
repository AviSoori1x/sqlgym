# Sample Tasks for salesforce_field_ops

## Task 1: Today's Schedule Overview
**User**: How many appointments are scheduled for today?
**Assistant**: I'll check today's appointment schedule.
```sql
SELECT 
    COUNT(*) as total_appointments,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'SCHEDULED' THEN 1 END) as pending
FROM appointments
WHERE scheduled_date = DATE('now');
```

**User**: Which technicians have the most appointments today?
**Assistant**: Finding busiest technicians:
```sql
SELECT 
    t.name,
    COUNT(a.id) as appointment_count,
    MIN(a.scheduled_start_time) as first_appointment,
    MAX(a.scheduled_end_time) as last_appointment
FROM appointments a
JOIN technicians t ON a.technician_id = t.id
WHERE a.scheduled_date = DATE('now')
GROUP BY t.id, t.name
ORDER BY appointment_count DESC
LIMIT 10;
```

## Task 2: Emergency Response Time
**User**: What's our average response time for emergencies?
**Assistant**: Analyzing emergency response times:
```sql
SELECT 
    AVG((julianday(a.scheduled_date) - julianday(sr.created_at)) * 24) as avg_hours_to_schedule,
    MIN((julianday(a.scheduled_date) - julianday(sr.created_at)) * 24) as fastest_response,
    COUNT(*) as total_emergencies
FROM service_requests sr
JOIN appointments a ON sr.id = a.service_request_id
WHERE sr.priority = 'EMERGENCY';
```

## Task 3: Efficiency Pair - Geographic Search
**User**: Find customers within 5km of latitude 37.5, longitude -122.0
**Assistant**: Fast query uses location index:
```sql fast
SELECT 
    id,
    name,
    address,
    latitude,
    longitude,
    service_level
FROM customers
WHERE latitude BETWEEN 37.45 AND 37.55 
  AND longitude BETWEEN -122.05 AND -121.95
ORDER BY latitude, longitude;
```
```sql slow
SELECT 
    id,
    name,
    address,
    latitude,
    longitude,
    service_level
FROM customers
WHERE ABS(latitude - 37.5) < 0.05 
  AND ABS(longitude - (-122.0)) < 0.05
ORDER BY latitude, longitude;
```

## Task 4: Evidence - Service Level Agreements
**User**: What are the response time requirements by priority?
**Assistant**: Checking SLA policy:
```sql
SELECT json_extract(value, '$.response_times') as sla_requirements
FROM evidence_kv 
WHERE key = 'service_sla';
```

## Task 5: Technician Utilization
**User**: Which technicians are underutilized this week?
**Assistant**: Finding available capacity:
```sql
SELECT 
    t.name,
    t.certification_level,
    t.max_daily_jobs * 5 as weekly_capacity,
    COUNT(a.id) as scheduled_jobs,
    (t.max_daily_jobs * 5 - COUNT(a.id)) as available_slots
FROM technicians t
LEFT JOIN appointments a ON t.id = a.technician_id 
    AND a.scheduled_date BETWEEN DATE('now', 'weekday 0', '-6 days') AND DATE('now', 'weekday 0')
WHERE t.status = 'ACTIVE'
GROUP BY t.id
HAVING available_slots > 10
ORDER BY available_slots DESC;
```

## Task 6: Efficiency Pair - Technician Schedule
**User**: Show Tech_10's schedule for tomorrow
**Assistant**: Fast uses technician/date index:
```sql fast
SELECT 
    a.scheduled_start_time,
    a.scheduled_end_time,
    sr.request_type,
    c.name as customer,
    c.address
FROM appointments a
JOIN service_requests sr ON a.service_request_id = sr.id
JOIN customers c ON sr.customer_id = c.id
WHERE a.technician_id = 10 
  AND a.scheduled_date = DATE('now', '+1 day')
ORDER BY a.scheduled_start_time;
```
```sql slow
SELECT 
    a.scheduled_start_time,
    a.scheduled_end_time,
    sr.request_type,
    c.name as customer,
    c.address
FROM appointments a
JOIN service_requests sr ON a.service_request_id = sr.id
JOIN customers c ON sr.customer_id = c.id
JOIN technicians t ON a.technician_id = t.id
WHERE t.name = 'Tech_10'
  AND DATE(a.scheduled_date) = DATE('now', '+1 day')
ORDER BY a.scheduled_start_time;
```

## Task 7: Service Type Analysis
**User**: Which service types take the longest?
**Assistant**: Analyzing service duration by type:
```sql
SELECT 
    sr.request_type,
    COUNT(*) as job_count,
    AVG(sr.estimated_duration_hours) as avg_estimated_hours,
    AVG(CASE 
        WHEN a.actual_end_time IS NOT NULL AND a.actual_start_time IS NOT NULL THEN
            (CAST(substr(a.actual_end_time, 1, 2) AS REAL) - CAST(substr(a.actual_start_time, 1, 2) AS REAL))
    END) as avg_actual_hours
FROM service_requests sr
LEFT JOIN appointments a ON sr.id = a.service_request_id
GROUP BY sr.request_type
ORDER BY avg_actual_hours DESC;
```

## Task 8: VIP Customer Service
**User**: How are we serving VIP customers?
**Assistant**: VIP service metrics:
```sql
SELECT 
    COUNT(*) as vip_requests,
    AVG((julianday(sr.requested_date) - julianday(sr.created_at))) as avg_wait_days,
    COUNT(CASE WHEN sr.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*) as completion_rate,
    COUNT(CASE WHEN sr.priority IN ('HIGH', 'EMERGENCY') THEN 1 END) as high_priority_count
FROM service_requests sr
JOIN customers c ON sr.customer_id = c.id
WHERE c.service_level = 'VIP';
```

## Task 9: Skills Gap Analysis
**User**: Which required skills are we short on?
**Assistant**: Identifying skill shortages:
```sql
WITH required_skills AS (
    SELECT 
        json_extract(value, '$[' || idx || ']') as skill,
        COUNT(*) as demand
    FROM service_requests sr,
         json_each(sr.skills_required) 
    WHERE sr.status = 'PENDING'
    GROUP BY skill
),
available_skills AS (
    SELECT 
        json_extract(value, '$[' || idx || ']') as skill,
        COUNT(DISTINCT t.id) as technicians
    FROM technicians t,
         json_each(t.skill_set)
    WHERE t.status = 'ACTIVE'
    GROUP BY skill
)
SELECT 
    rs.skill,
    rs.demand,
    COALESCE(av.technicians, 0) as available_techs,
    rs.demand - COALESCE(av.technicians, 0) * 5 as shortage_score
FROM required_skills rs
LEFT JOIN available_skills av ON rs.skill = av.skill
ORDER BY shortage_score DESC;
```

## Task 10: Route Optimization Check
**User**: Show technicians with highest travel distances
**Assistant**: High-travel technicians:
```sql
SELECT 
    t.name,
    COUNT(a.id) as jobs,
    SUM(a.travel_distance_km) as total_travel_km,
    AVG(a.travel_distance_km) as avg_travel_km,
    MAX(a.travel_distance_km) as max_single_trip_km
FROM appointments a
JOIN technicians t ON a.technician_id = t.id
WHERE a.scheduled_date >= DATE('now', '-7 days')
GROUP BY t.id
HAVING total_travel_km > 200
ORDER BY total_travel_km DESC;
```

## Task 11: Efficiency Pair - Pending Requests
**User**: Show all pending high-priority requests
**Assistant**: Fast uses status and priority indexes:
```sql fast
SELECT 
    sr.id,
    c.name as customer,
    c.service_level,
    sr.request_type,
    sr.created_at,
    (julianday('now') - julianday(sr.created_at)) * 24 as hours_waiting
FROM service_requests sr
JOIN customers c ON sr.customer_id = c.id
WHERE sr.status = 'PENDING' 
  AND sr.priority IN ('HIGH', 'EMERGENCY')
ORDER BY sr.priority DESC, sr.created_at;
```
```sql slow
SELECT 
    sr.id,
    c.name as customer,
    c.service_level,
    sr.request_type,
    sr.created_at,
    (julianday('now') - julianday(sr.created_at)) * 24 as hours_waiting
FROM service_requests sr
JOIN customers c ON sr.customer_id = c.id
WHERE LOWER(sr.status) = 'pending' 
  AND (UPPER(sr.priority) = 'HIGH' OR UPPER(sr.priority) = 'EMERGENCY')
ORDER BY sr.priority DESC, sr.created_at;
```

## Task 12: Missed Appointments Analysis
**User**: Why are appointments being missed?
**Assistant**: Analyzing missed appointments:
```sql
SELECT 
    de.event_type,
    COUNT(*) as occurrences,
    COUNT(DISTINCT a.id) as affected_appointments
FROM appointments a
JOIN dispatch_events de ON a.id = de.appointment_id
WHERE a.status IN ('MISSED', 'RESCHEDULED')
  AND de.event_type IN ('CUSTOMER_NOT_HOME', 'RESCHEDULED')
GROUP BY de.event_type
ORDER BY occurrences DESC;
```

## Task 13: Evidence - Skill Requirements
**User**: What skills are required for each service type?
**Assistant**: Checking skill matrix:
```sql
SELECT json_extract(value, '$.skill_requirements') as skill_matrix
FROM evidence_kv 
WHERE key = 'service_skills';
```

## Task 14: Time Window Preferences
**User**: What time windows do customers prefer?
**Assistant**: Time window analysis:
```sql
SELECT 
    time_window,
    COUNT(*) as request_count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage,
    COUNT(CASE WHEN c.service_level = 'VIP' THEN 1 END) as vip_requests
FROM service_requests sr
JOIN customers c ON sr.customer_id = c.id
GROUP BY time_window
ORDER BY request_count DESC;
```

## Task 15: Performance Tracking
**User**: Show completion rates by technician level
**Assistant**: Performance by certification:
```sql
SELECT 
    t.certification_level,
    COUNT(a.id) as total_jobs,
    COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(a.id) as completion_rate,
    AVG(a.travel_distance_km) as avg_travel_distance
FROM appointments a
JOIN technicians t ON a.technician_id = t.id
GROUP BY t.certification_level
ORDER BY completion_rate DESC;
```

**User**: Which level handles emergencies best?
**Assistant**: Emergency response by level:
```sql
SELECT 
    t.certification_level,
    COUNT(*) as emergency_jobs,
    AVG((julianday(a.scheduled_date) - julianday(sr.created_at)) * 24) as avg_response_hours,
    COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*) as completion_rate
FROM appointments a
JOIN technicians t ON a.technician_id = t.id
JOIN service_requests sr ON a.service_request_id = sr.id
WHERE sr.priority = 'EMERGENCY'
GROUP BY t.certification_level
ORDER BY avg_response_hours;
```