# amazon_customer_insights

## Overview
This subdomain models comprehensive customer profiling, behavioral segmentation, and personalization capabilities for retail analytics.

## Entities

### Normalized Schema
- **customers**: Core customer demographics and registration details
- **customer_segments**: Segmentation definitions with JSON criteria
- **customer_segment_assignments**: Dynamic segment membership with confidence scoring
- **transactions**: Purchase history across multiple channels
- **customer_interactions**: Multi-touchpoint engagement tracking
- **customer_preferences**: Explicit and inferred preference management

### Denormalized Schema
- **customer_360_profile**: Comprehensive customer view with calculated metrics
- **segment_performance**: Monthly segment performance and retention analysis
- **channel_attribution**: Multi-touch attribution and conversion tracking
- **behavioral_cohorts**: Acquisition cohort analysis with retention metrics

## Key Indexes
- `idx_customers_email`: Fast customer lookup by email
- `idx_segment_assignments_customer`: Customer segment queries
- `idx_transactions_customer`: Customer purchase history
- `idx_interactions_customer_date`: Engagement timeline analysis
- `idx_preferences_customer`: Preference-based personalization

## Efficiency Notes
- JSON criteria allow flexible segment definitions without schema changes
- Confidence scoring enables probabilistic segment assignments
- Multi-channel transaction tracking supports omnichannel analysis
- Evidence files define segmentation rules and personalization strategies
- Fast/slow pairs demonstrate unique constraint usage vs pattern matching