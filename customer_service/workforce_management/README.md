# kronos_scheduling

## Overview
This subdomain models agent workforce management including scheduling, skills tracking, time-off management, and performance monitoring.

## Entities

### Normalized Schema
- **agents**: Employee records with departments, skill levels, and employment status
- **skills**: Skill catalog with categories and certification requirements
- **agent_skills**: Many-to-many relationship tracking agent proficiencies
- **shifts**: Work shift definitions with staffing requirements
- **schedules**: Agent-shift assignments with attendance tracking
- **time_off_requests**: Vacation, sick leave, and other time-off tracking

### Denormalized Schema
- **agent_performance_summary**: Individual agent metrics and attendance
- **daily_staffing_metrics**: Department-level staffing and utilization
- **shift_coverage_analysis**: Shift fulfillment and skill matching
- **skill_demand_forecast**: Certification tracking and training needs

## Key Indexes
- `idx_agents_department`: Department-based queries
- `idx_schedules_agent_date`: Agent schedule lookups
- `idx_shifts_date`: Daily staffing queries
- `idx_time_off_dates`: Leave conflict detection
- `idx_agent_skills_agent`: Skill profile queries

## Efficiency Notes
- Unique constraints on agent-skill and agent-shift pairs prevent duplicates
- Schedule status tracks full attendance lifecycle
- Certification expiry tracking for compliance
- Evidence files define policies and minimum staffing levels
- Fast/slow pairs demonstrate index usage on unique constraints vs pattern matching