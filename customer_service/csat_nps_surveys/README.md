# csat_nps_surveys

## Overview
This subdomain models customer satisfaction (CSAT), Net Promoter Score (NPS), and Customer Effort Score (CES) surveys across multiple touchpoints and channels.

## Entities

### Normalized Schema
- **customers**: Customer records with segments (Enterprise, SMB, Consumer)
- **touchpoints**: Survey collection points across channels
- **surveys**: Individual survey instances with scores and responses
- **survey_triggers**: Events that initiated surveys
- **follow_ups**: Actions taken for low-scoring surveys

### Denormalized Schema
- **survey_analytics**: Enriched survey data with calculated metrics
- **daily_metrics**: Daily aggregated metrics by survey type
- **segment_scores**: Monthly performance by customer segment
- **touchpoint_performance**: Quarterly touchpoint effectiveness

## Key Indexes
- `idx_surveys_customer`: Fast customer survey lookups
- `idx_surveys_type`: Efficient filtering by survey type
- `idx_surveys_sent`: Date range queries for trend analysis
- `idx_surveys_score`: Score distribution analysis
- `idx_triggers_event`: Event correlation analysis

## Efficiency Notes
- Response rates modeled with realistic log-normal distribution
- Segment-based score biasing reflects real-world patterns
- Evidence files contain best practices and segment targets
- Fast/slow query pairs demonstrate proper index usage vs scans