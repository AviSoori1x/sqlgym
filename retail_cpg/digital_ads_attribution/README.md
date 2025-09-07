# digital_ads_attribution

## Overview
This subdomain models digital advertising campaigns, multi-touch attribution, and cross-platform performance tracking for comprehensive marketing analytics.

## Entities

### Normalized Schema
- **campaigns**: Campaign definitions with platform, objectives, and budgets
- **ad_groups**: Targeting and bidding strategy groupings within campaigns
- **ads**: Individual creative assets with headlines, CTAs, and landing pages
- **touchpoints**: User interaction events across all platforms and campaigns
- **conversions**: Goal completions with attribution window configuration
- **attribution_models**: Configurable attribution methodologies and parameters

### Denormalized Schema
- **campaign_performance**: Daily campaign metrics with calculated KPIs
- **attribution_analysis**: Per-conversion attribution across multiple models
- **user_journey_summary**: Complete customer journey aggregations
- **cross_platform_attribution**: Multi-platform interaction analysis

## Key Indexes
- `idx_campaigns_platform`: Platform-specific campaign queries
- `idx_touchpoints_user`: User journey reconstruction
- `idx_touchpoints_timestamp`: Time-based performance analysis
- `idx_conversions_user`: User conversion tracking
- `idx_touchpoints_campaign`: Campaign touchpoint analysis

## Efficiency Notes
- Multi-platform touchpoint tracking enables cross-channel attribution
- Flexible attribution models support different business objectives
- JSON targeting criteria allow complex audience definitions
- Evidence files define optimization rules and attribution methodologies
- Fast/slow pairs demonstrate index usage on exact matches vs pattern searches