# morgan_stanley_wealth

## Overview
This subdomain models wealth management operations including client portfolios, securities trading, performance attribution, and investment advisory services.

## Entities

### Normalized Schema
- **clients**: High-net-worth client profiles with risk tolerance and investment objectives
- **portfolios**: Investment portfolios with asset allocation targets and benchmarks
- **securities**: Investment universe including stocks, bonds, ETFs, and alternatives
- **positions**: Current portfolio holdings with cost basis and market values
- **trades**: Transaction history with settlement details and performance impact
- **performance_attribution**: Portfolio performance analysis vs benchmarks

### Denormalized Schema
- **client_portfolio_summary**: Consolidated client wealth and allocation metrics
- **daily_portfolio_performance**: Daily portfolio returns and risk metrics
- **security_performance_analysis**: Individual security contribution analysis
- **advisor_performance_summary**: Advisor-level client and portfolio performance

## Key Indexes
- `idx_portfolios_client`: Client portfolio relationship queries
- `idx_trades_portfolio`: Portfolio transaction history
- `idx_positions_portfolio`: Current portfolio composition
- `idx_securities_asset_class`: Asset class allocation analysis
- `idx_clients_advisor`: Advisor client management

## Efficiency Notes
- JSON target allocations enable flexible investment policy management
- Position snapshots support historical performance analysis
- Performance attribution tracks asset allocation vs security selection effects
- Evidence files define investment policies and rebalancing rules
- Fast/slow pairs demonstrate index usage on client codes vs pattern matching