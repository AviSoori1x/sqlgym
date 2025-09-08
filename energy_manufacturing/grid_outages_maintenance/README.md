# pge_grid_operations

## Overview
PG&E Grid Operations system for tracking electrical grid assets, outage events, maintenance schedules, and restoration activities across the power distribution network.

## Entities
- **grid_assets**: Physical infrastructure (transformers, transmission lines, substations, generators)
- **outage_events**: Planned and unplanned service interruptions with customer impact
- **maintenance_schedules**: Preventive maintenance planning and execution
- **restoration_activities**: Emergency response and service recovery operations
- **crew_assignments**: Field technician dispatch and work coordination

## Key Indexes
- `idx_grid_assets_type`: Asset categorization and inventory management
- `idx_grid_assets_location`: Geographic-based asset queries
- `idx_outage_events_start_time`: Chronological outage analysis and reporting
- `idx_outage_events_asset`: Asset-specific outage history and reliability metrics
- `idx_maintenance_schedules_asset`: Asset maintenance tracking and compliance
- `idx_restoration_activities_outage`: Emergency response coordination

## Efficiency Notes
- **Fast queries**: Use indexed fields (asset_type, location, outage_start_time, affected_asset_id)
- **Slow queries**: Complex geographic calculations, full-text searches on descriptions
- **Optimal patterns**: Time-based outage reports, asset reliability analysis, maintenance scheduling
- **Performance considerations**: Date range queries benefit from proper indexing; geographic queries may require spatial optimization
