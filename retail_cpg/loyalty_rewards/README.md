# starbucks_rewards

## Overview
This subdomain models loyalty program operations including member tiers, points earning/redemption, rewards catalog, and tier progression management.

## Entities

### Normalized Schema
- **members**: Loyalty program members with tier assignments and point balances
- **tiers**: Tier definitions with spend thresholds and benefit structures
- **point_transactions**: All point earning, redemption, and adjustment activities
- **rewards_catalog**: Available rewards with point costs and restrictions
- **redemptions**: Reward redemption transactions and fulfillment tracking
- **tier_movements**: Member tier progression history and upgrade tracking

### Denormalized Schema
- **member_analytics**: Comprehensive member engagement and value metrics
- **tier_performance**: Monthly tier-level performance and retention analysis
- **reward_popularity**: Reward redemption patterns and member preferences
- **points_economy_summary**: Daily points liability and breakage tracking

## Key Indexes
- `idx_members_tier`: Tier-based member segmentation
- `idx_point_transactions_member`: Member transaction history
- `idx_redemptions_member`: Member redemption tracking
- `idx_tier_movements_member`: Tier progression analysis

## Efficiency Notes
- JSON tier benefits enable flexible program configuration
- Point transaction types support comprehensive earning/redemption tracking
- Tier movement history enables progression analysis
- Evidence files define tier qualification rules and reward policies
- Fast/slow pairs demonstrate index usage on unique member identifiers