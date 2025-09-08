# salesforce_field_ops

## Overview
This subdomain models field service operations including technician dispatch, appointment scheduling, and route optimization for on-site customer service.

## Entities

### Normalized Schema
- **customers**: Service locations with geographic coordinates and service levels
- **technicians**: Field technicians with skills, certifications, and home base locations
- **service_requests**: Customer requests with type, priority, and time preferences
- **appointments**: Scheduled visits linking technicians to service requests
- **dispatch_events**: Event log tracking appointment lifecycle

### Denormalized Schema
- **daily_technician_schedule**: Daily utilization and route metrics per technician
- **service_metrics**: Service performance aggregated by date and type
- **geographic_demand**: Spatial demand analysis for capacity planning
- **technician_performance**: Monthly technician KPIs and skill utilization

## Key Indexes
- `idx_customers_location`: Spatial queries for nearby customers
- `idx_service_requests_date`: Date-based filtering for scheduling
- `idx_appointments_technician`: Technician schedule lookups
- `idx_appointments_date`: Daily dispatch views
- `idx_technicians_status`: Available technician filtering

## Efficiency Notes
- Geographic calculations use Haversine formula for distance
- Skills stored as JSON arrays for flexible matching
- Time windows enable customer preference scheduling
- Evidence files define SLAs and skill requirements
- Fast/slow pairs demonstrate spatial and temporal index usage