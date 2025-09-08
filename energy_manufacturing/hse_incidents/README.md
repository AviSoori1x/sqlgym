# chevron_safety_mgmt

## Overview
Chevron Safety Management system for tracking Health, Safety & Environment (HSE) incidents, investigations, and corrective actions in industrial facilities.

## Entities
- **employees**: Staff members with safety training records
- **incident_types**: Categorized incident classifications with severity levels
- **hse_incidents**: Core incident records with location, timing, and severity
- **investigations**: Formal incident investigations with findings
- **corrective_actions**: Remediation tasks assigned post-incident

## Key Indexes
- `idx_employees_department`: Department-based employee lookups
- `idx_hse_incidents_date`: Time-based incident reporting and analysis
- `idx_hse_incidents_type`: Incident categorization and trending
- `idx_hse_incidents_severity`: Risk assessment and escalation queries
- `idx_investigations_incident`: Investigation tracking per incident
- `idx_corrective_actions_incident`: Action item management per incident

## Efficiency Notes
- **Fast queries**: Use indexed fields (department, incident_date, incident_type_id, severity)
- **Slow queries**: Full-text searches on description, findings, or unindexed filters
- **Optimal patterns**: Date range queries, department rollups, severity trending
- **Performance considerations**: Large text fields (description, findings) benefit from careful WHERE clause ordering
