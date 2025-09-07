# Sample Tasks for workforce_management

## Task 1: Current Staffing Levels
**User**: How many agents are working today?
**Assistant**: I'll check today's staffing levels.
```sql
SELECT 
    sh.shift_type,
    COUNT(DISTINCT s.agent_id) as scheduled_agents,
    sh.required_agents,
    COUNT(DISTINCT CASE WHEN s.status IN ('CHECKED_IN', 'COMPLETED') THEN s.agent_id END) as present_agents
FROM shifts sh
LEFT JOIN schedules s ON sh.id = s.shift_id
WHERE sh.shift_date = DATE('now')
GROUP BY sh.shift_type, sh.required_agents;
```

**User**: Which departments are understaffed?
**Assistant**: Checking department coverage:
```sql
SELECT 
    a.department,
    COUNT(DISTINCT CASE WHEN s.status IN ('SCHEDULED', 'CONFIRMED') THEN a.id END) as available_agents,
    COUNT(DISTINCT CASE WHEN s.status = 'ABSENT' THEN a.id END) as absent_agents,
    COUNT(DISTINCT a.id) * 0.8 as target_coverage
FROM agents a
LEFT JOIN schedules s ON a.id = s.agent_id
LEFT JOIN shifts sh ON s.shift_id = sh.id AND sh.shift_date = DATE('now')
WHERE a.status = 'ACTIVE'
GROUP BY a.department
HAVING available_agents < target_coverage;
```

## Task 2: Agent Skill Analysis
**User**: Which agents have the most skills?
**Assistant**: Finding multi-skilled agents:
```sql
SELECT 
    a.name,
    a.department,
    a.skill_level,
    COUNT(ask.skill_id) as skill_count,
    AVG(ask.proficiency_level) as avg_proficiency
FROM agents a
JOIN agent_skills ask ON a.id = ask.agent_id
WHERE a.status = 'ACTIVE'
GROUP BY a.id
ORDER BY skill_count DESC, avg_proficiency DESC
LIMIT 10;
```

## Task 3: Efficiency Pair - Agent Schedule Lookup
**User**: Show schedule for employee EMP0001
**Assistant**: Fast query uses employee_id unique constraint:
```sql fast
SELECT 
    sh.shift_date,
    sh.shift_type,
    sh.start_time,
    sh.end_time,
    s.status
FROM schedules s
JOIN agents a ON s.agent_id = a.id
JOIN shifts sh ON s.shift_id = sh.id
WHERE a.employee_id = 'EMP0001'
ORDER BY sh.shift_date DESC;
```
```sql slow
SELECT 
    sh.shift_date,
    sh.shift_type,
    sh.start_time,
    sh.end_time,
    s.status
FROM schedules s
JOIN agents a ON s.agent_id = a.id
JOIN shifts sh ON s.shift_id = sh.id
WHERE a.employee_id LIKE '%0001%'
ORDER BY sh.shift_date DESC;
```

## Task 4: Evidence - Overtime Policy
**User**: What's our overtime policy threshold?
**Assistant**: Checking overtime policy:
```sql
SELECT json_extract(value, '$.overtime_policy') as policy_details
FROM evidence_kv 
WHERE key = 'workforce_policies';
```

## Task 5: Attendance Analysis
**User**: What's the overall attendance rate this month?
**Assistant**: Calculating monthly attendance:
```sql
SELECT 
    COUNT(*) as total_scheduled,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'ABSENT' THEN 1 END) as absent,
    COUNT(CASE WHEN status = 'LATE' THEN 1 END) as late,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*) as attendance_rate
FROM schedules s
JOIN shifts sh ON s.shift_id = sh.id
WHERE sh.shift_date >= DATE('now', 'start of month');
```

**User**: Which agents have poor attendance?
**Assistant**: Finding attendance issues:
```sql
SELECT 
    a.name,
    a.employee_id,
    COUNT(*) as scheduled_shifts,
    COUNT(CASE WHEN s.status = 'ABSENT' THEN 1 END) as absences,
    COUNT(CASE WHEN s.status = 'LATE' THEN 1 END) as late_arrivals,
    COUNT(CASE WHEN s.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(*) as attendance_rate
FROM agents a
JOIN schedules s ON a.id = s.agent_id
GROUP BY a.id
HAVING attendance_rate < 90
ORDER BY attendance_rate ASC;
```

## Task 6: Skill Certification Tracking
**User**: Which certifications are expiring soon?
**Assistant**: Finding expiring certifications:
```sql
SELECT 
    a.name as agent_name,
    s.name as skill_name,
    ask.certified_date,
    ask.expiry_date,
    julianday(ask.expiry_date) - julianday('now') as days_until_expiry
FROM agent_skills ask
JOIN agents a ON ask.agent_id = a.id
JOIN skills s ON ask.skill_id = s.id
WHERE ask.expiry_date IS NOT NULL
  AND julianday(ask.expiry_date) - julianday('now') BETWEEN 0 AND 30
ORDER BY days_until_expiry ASC;
```

## Task 7: Efficiency Pair - Shift Coverage Search
**User**: Show understaffed shifts tomorrow
**Assistant**: Fast uses date index:
```sql fast
SELECT 
    shift_type,
    start_time,
    end_time,
    required_agents,
    COUNT(s.agent_id) as scheduled_agents,
    required_agents - COUNT(s.agent_id) as shortage
FROM shifts sh
LEFT JOIN schedules s ON sh.id = s.shift_id
WHERE sh.shift_date = DATE('now', '+1 day')
GROUP BY sh.id
HAVING shortage > 0
ORDER BY shortage DESC;
```
```sql slow
SELECT 
    shift_type,
    start_time,
    end_time,
    required_agents,
    COUNT(s.agent_id) as scheduled_agents,
    required_agents - COUNT(s.agent_id) as shortage
FROM shifts sh
LEFT JOIN schedules s ON sh.id = s.shift_id
WHERE DATE(sh.shift_date) = DATE('now', '+1 day')
GROUP BY sh.id
HAVING shortage > 0
ORDER BY shortage DESC;
```

## Task 8: Time Off Management
**User**: How many vacation requests are pending?
**Assistant**: Checking pending time off:
```sql
SELECT 
    request_type,
    COUNT(*) as pending_count,
    MIN(start_date) as earliest_start,
    MAX(end_date) as latest_end
FROM time_off_requests
WHERE status = 'PENDING'
GROUP BY request_type
ORDER BY pending_count DESC;
```

**User**: Show vacation conflicts for next week
**Assistant**: Finding scheduling conflicts:
```sql
SELECT 
    a.name,
    a.department,
    tor.start_date,
    tor.end_date,
    COUNT(s.id) as scheduled_shifts_during_leave
FROM time_off_requests tor
JOIN agents a ON tor.agent_id = a.id
LEFT JOIN schedules s ON a.id = s.agent_id
LEFT JOIN shifts sh ON s.shift_id = sh.id
    AND sh.shift_date BETWEEN tor.start_date AND tor.end_date
WHERE tor.status = 'APPROVED'
  AND tor.start_date >= DATE('now')
  AND tor.start_date <= DATE('now', '+7 days')
GROUP BY tor.id
HAVING scheduled_shifts_during_leave > 0;
```

## Task 9: Overtime Analysis
**User**: Which agents have the most overtime this month?
**Assistant**: Analyzing overtime hours:
```sql
SELECT 
    a.name,
    a.department,
    COUNT(s.id) as shifts_worked,
    SUM(s.overtime_minutes) as total_overtime_minutes,
    SUM(s.overtime_minutes) / 60.0 as total_overtime_hours,
    AVG(s.overtime_minutes) as avg_overtime_per_shift
FROM agents a
JOIN schedules s ON a.id = s.agent_id
JOIN shifts sh ON s.shift_id = sh.id
WHERE sh.shift_date >= DATE('now', 'start of month')
  AND s.overtime_minutes > 0
GROUP BY a.id
ORDER BY total_overtime_minutes DESC
LIMIT 10;
```

## Task 10: Department Performance
**User**: Compare attendance rates by department
**Assistant**: Department attendance comparison:
```sql
SELECT 
    a.department,
    COUNT(DISTINCT a.id) as total_agents,
    COUNT(s.id) as total_shifts,
    COUNT(CASE WHEN s.status = 'COMPLETED' THEN 1 END) as completed_shifts,
    COUNT(CASE WHEN s.status = 'ABSENT' THEN 1 END) as absences,
    COUNT(CASE WHEN s.status = 'COMPLETED' THEN 1 END) * 100.0 / COUNT(s.id) as attendance_rate
FROM agents a
LEFT JOIN schedules s ON a.id = s.agent_id
WHERE a.status = 'ACTIVE'
GROUP BY a.department
ORDER BY attendance_rate DESC;
```

## Task 11: Efficiency Pair - Skills by Category
**User**: List all technical skills and their certified agents
**Assistant**: Fast uses category constraint:
```sql fast
SELECT 
    s.name as skill,
    COUNT(DISTINCT ask.agent_id) as certified_agents,
    AVG(ask.proficiency_level) as avg_proficiency
FROM skills s
LEFT JOIN agent_skills ask ON s.id = ask.skill_id
WHERE s.category = 'TECHNICAL'
  AND ask.certified_date IS NOT NULL
GROUP BY s.id
ORDER BY certified_agents DESC;
```
```sql slow
SELECT 
    s.name as skill,
    COUNT(DISTINCT ask.agent_id) as certified_agents,
    AVG(ask.proficiency_level) as avg_proficiency
FROM skills s
LEFT JOIN agent_skills ask ON s.id = ask.skill_id
WHERE UPPER(s.category) LIKE '%TECH%'
  AND ask.certified_date IS NOT NULL
GROUP BY s.id
ORDER BY certified_agents DESC;
```

## Task 12: Evidence - Minimum Staffing Levels
**User**: What are the minimum staffing requirements?
**Assistant**: Checking staffing requirements:
```sql
SELECT 
    json_extract(value, '$.minimum_staffing') as min_requirements
FROM evidence_kv 
WHERE key = 'workforce_policies';
```

## Task 13: Shift Pattern Analysis
**User**: Which shift types have highest absence rates?
**Assistant**: Analyzing absence by shift type:
```sql
SELECT 
    sh.shift_type,
    COUNT(*) as total_scheduled,
    COUNT(CASE WHEN s.status = 'ABSENT' THEN 1 END) as absences,
    COUNT(CASE WHEN s.status = 'LATE' THEN 1 END) as late_arrivals,
    COUNT(CASE WHEN s.status = 'ABSENT' THEN 1 END) * 100.0 / COUNT(*) as absence_rate
FROM shifts sh
JOIN schedules s ON sh.id = s.shift_id
GROUP BY sh.shift_type
ORDER BY absence_rate DESC;
```

## Task 14: Training Status
**User**: How many agents are currently in training?
**Assistant**: Finding training agents:
```sql
SELECT 
    department,
    COUNT(*) as training_agents,
    AVG(julianday('now') - julianday(hire_date)) as avg_days_since_hire
FROM agents
WHERE status = 'TRAINING'
GROUP BY department;
```

**User**: When will they complete training?
**Assistant**: Estimating training completion:
```sql
SELECT 
    name,
    employee_id,
    hire_date,
    julianday('now') - julianday(hire_date) as days_in_training,
    CASE 
        WHEN department IN ('TECHNICAL', 'BILLING') THEN 45
        ELSE 30
    END as expected_training_days,
    DATE(hire_date, '+' || CASE 
        WHEN department IN ('TECHNICAL', 'BILLING') THEN 45
        ELSE 30
    END || ' days') as expected_completion
FROM agents
WHERE status = 'TRAINING'
ORDER BY expected_completion;
```

## Task 15: Workforce Utilization
**User**: What's our overall workforce utilization?
**Assistant**: Calculating utilization metrics:
```sql
WITH utilization_stats AS (
    SELECT 
        DATE(sh.shift_date) as date,
        SUM(sh.required_agents) as total_required,
        COUNT(DISTINCT s.agent_id) as agents_scheduled,
        COUNT(DISTINCT CASE WHEN s.status IN ('COMPLETED', 'LATE') THEN s.agent_id END) as agents_worked,
        SUM(CASE WHEN s.check_out_time IS NOT NULL AND s.check_in_time IS NOT NULL 
            THEN (julianday(s.check_out_time) - julianday(s.check_in_time)) * 24 
            ELSE 8 END) as total_hours_worked
    FROM shifts sh
    LEFT JOIN schedules s ON sh.id = s.shift_id
    WHERE sh.shift_date >= DATE('now', '-7 days')
    GROUP BY DATE(sh.shift_date)
)
SELECT 
    AVG(agents_scheduled * 100.0 / total_required) as avg_schedule_fill_rate,
    AVG(agents_worked * 100.0 / agents_scheduled) as avg_attendance_rate,
    AVG(total_hours_worked) as avg_daily_hours,
    SUM(total_hours_worked) as total_weekly_hours
FROM utilization_stats;
```