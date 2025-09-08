# amazon_seller_central

## Overview
This subdomain models marketplace seller management including compliance monitoring, policy enforcement, performance tracking, and audit workflows.

## Entities

### Normalized Schema
- **sellers**: Marketplace seller profiles with verification and performance metrics
- **compliance_policies**: Policy definitions with severity levels and enforcement rules
- **policy_violations**: Violation tracking with evidence and resolution status
- **seller_metrics**: Daily seller performance metrics and KPIs
- **audit_logs**: Seller audit activities with risk assessments
- **enforcement_actions**: Policy enforcement actions and penalties

### Denormalized Schema
- **seller_compliance_summary**: Comprehensive seller compliance and risk profiles
- **daily_compliance_metrics**: Daily violation and resolution tracking
- **policy_violation_trends**: Policy-level violation patterns and trends
- **seller_performance_metrics**: Monthly seller performance aggregations

## Key Indexes
- `idx_sellers_verification`: Seller verification status management
- `idx_policy_violations_seller`: Seller violation history
- `idx_seller_metrics_seller_date`: Performance timeline analysis
- `idx_audit_logs_seller`: Audit trail reconstruction

## Efficiency Notes
- JSON violation evidence enables flexible documentation
- Auto-enforcement flags support automated policy monitoring
- Risk scoring combines violations with performance metrics
- Evidence files define compliance policies and audit procedures
- Fast/slow pairs demonstrate index usage on seller identifiers