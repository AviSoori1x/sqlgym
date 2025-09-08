# asset_mgmt_fund_accounting

## Overview
Asset Management & Fund Accounting system for tracking investment funds, securities holdings, investor subscriptions, and portfolio valuations across multiple currencies and regions.

## Entities
- **funds**: Investment vehicles with domicile and status tracking
- **investors**: Retail and institutional clients with risk profiles
- **securities**: Financial instruments (equity, bonds, cash) with currency designation
- **holdings**: Fund positions in specific securities with quantities and dates
- **subscriptions**: Investor capital commitments and subscription details
- **valuations**: Time-series pricing and NAV calculations

## Key Indexes
- `idx_funds_status`: Active fund filtering and reporting
- `idx_securities_type`: Asset class analysis and allocation
- `idx_holdings_fund`: Portfolio composition and performance
- `idx_holdings_date`: Historical position tracking and rebalancing
- `idx_subscriptions_investor`: Client relationship management
- `idx_valuations_security_date`: Price history and performance attribution

## Efficiency Notes
- **Fast queries**: Use indexed fields (fund status, security type, position dates)
- **Slow queries**: Complex cross-currency calculations, unindexed text searches
- **Optimal patterns**: Portfolio snapshots by date, asset allocation analysis, performance attribution
- **Performance considerations**: Date-based queries benefit from compound indexes; currency conversions may require careful caching strategies
