# shopify_conversion_lab

## Overview
This subdomain models ecommerce conversion funnels, A/B testing experiments, and statistical analysis of user behavior optimization.

## Entities

### Normalized Schema
- **experiments**: A/B test definitions with hypotheses and success metrics
- **variants**: Test variations with traffic allocation and configuration
- **funnel_steps**: Conversion funnel stage definitions and requirements
- **user_sessions**: User session tracking with experiment assignments
- **funnel_events**: Individual user interactions within funnel steps
- **conversion_goals**: Success metrics and measurement definitions

### Denormalized Schema
- **experiment_results**: Daily A/B test performance with statistical significance
- **funnel_analysis**: Step-by-step conversion rates and drop-off analysis
- **cohort_funnel_performance**: Cohort-based funnel completion tracking
- **ab_test_summary**: Experiment summaries with lift calculations and winners

## Key Indexes
- `idx_experiments_status`: Active experiment filtering
- `idx_user_sessions_experiment`: Experiment participant analysis
- `idx_funnel_events_session`: Session journey reconstruction
- `idx_funnel_events_timestamp`: Time-based funnel analysis
- `idx_user_sessions_timestamp`: Session timing queries

## Efficiency Notes
- JSON configuration enables flexible variant definitions
- Statistical significance tracking for reliable test conclusions
- Multi-step funnel tracking with drop-off point identification
- Cohort analysis supports segmented conversion optimization
- Fast/slow pairs demonstrate index usage on experiment lookups