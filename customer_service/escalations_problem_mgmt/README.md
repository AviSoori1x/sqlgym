# servicenow_incidents

## Overview
This subdomain models issue escalation hierarchies, problem management workflows, and resolution tracking across support tiers.

## Entities

### Normalized Schema
- **customers**: Customer records with service tiers and account values
- **agents**: Support agents with skill levels (L1-L3, Manager, Director) and departments
- **issues**: Support issues with categories, severity, and impact scoring
- **escalations**: Escalation records tracking handoffs between agents
- **problem_records**: Root cause analysis for systemic issues affecting multiple customers

### Denormalized Schema
- **issue_analytics**: Enriched issue data with escalation chains and resolution metrics
- **daily_escalation_metrics**: Daily departmental performance and SLA tracking
- **agent_performance**: Monthly agent metrics including resolution rates
- **problem_impact_summary**: Problem records with revenue impact analysis

## Key Indexes
- `idx_issues_customer`: Fast customer issue lookups
- `idx_issues_status`: Active issue filtering
- `idx_issues_severity`: Priority queue management
- `idx_escalations_issue`: Escalation chain traversal
- `idx_problem_records_status`: Problem tracking

## Efficiency Notes
- Hierarchical escalation paths enforced through skill level validation
- SLA calculations consider severity and customer tier
- Evidence files define escalation matrix and SLA policies
- Fast/slow query pairs demonstrate index usage patterns