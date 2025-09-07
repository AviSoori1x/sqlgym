# claims_processing

## Overview
This subdomain models healthcare insurance claims processing including member enrollment, provider networks, claim adjudication, denial management, and prior authorization workflows.

## Entities

### Normalized Schema
- **members**: Health plan members with demographics and enrollment status
- **insurance_plans**: Health plan products with coverage levels and cost-sharing
- **providers**: Healthcare provider network with specialties and contract status
- **medical_claims**: Claim submissions with service details and processing status
- **claim_line_items**: Individual services within claims with payment breakdowns
- **claim_adjudications**: Adjudication decisions with processing metrics
- **claim_denials**: Denial tracking with appeal deadlines and reason codes
- **prior_authorizations**: Pre-service authorization workflow management

### Denormalized Schema
- **claims_analytics**: Comprehensive claim details with calculated metrics
- **daily_claims_metrics**: Daily processing volume and performance tracking
- **provider_performance**: Provider-level claim quality and payment metrics
- **denial_analysis**: Denial pattern analysis with appeal tracking

## Key Indexes
- `idx_medical_claims_member`: Member claim history queries
- `idx_medical_claims_service_date`: Time-based claims analysis
- `idx_providers_npi`: Provider network management
- `idx_claim_line_items_claim`: Claim detail reconstruction
- `idx_claim_denials_claim`: Denial workflow tracking

## Efficiency Notes
- JSON diagnosis and procedure codes enable flexible medical coding
- Auto-adjudication tracking supports process optimization
- Prior authorization integration prevents unnecessary denials
- Evidence files define coverage policies and denial code references
- Fast/slow pairs demonstrate index usage on unique identifiers vs pattern searches