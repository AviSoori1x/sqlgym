# corporate_banking_cash_mgmt

## Overview
This subdomain models corporate banking cash management operations including cash pooling, sweep accounts, liquidity management, and multi-account corporate relationships.

## Entities

### Normalized Schema
- **corporate_clients**: Corporate customer profiles with risk ratings and KYC status
- **account_types**: Banking product catalog with fee structures and requirements
- **accounts**: Individual bank accounts with balances and hierarchical relationships
- **cash_pool_structures**: Cash pooling configurations with sweep parameters
- **pool_participants**: Account participation in cash pools with priority settings
- **transactions**: All account transactions including sweeps and fees
- **sweep_executions**: Cash pool sweep execution logs with status tracking

### Denormalized Schema
- **client_cash_position**: Comprehensive client liquidity and risk metrics
- **daily_liquidity_metrics**: Daily cash flow and volatility analysis
- **pool_performance_summary**: Cash pool efficiency and cost savings tracking
- **account_utilization_analysis**: Account activity and dormancy monitoring

## Key Indexes
- `idx_accounts_client`: Client account relationship queries
- `idx_transactions_account`: Account transaction history reconstruction
- `idx_transactions_date`: Time-based transaction analysis
- `idx_sweep_executions_pool`: Pool execution tracking
- `idx_corporate_clients_risk`: Risk-based client segmentation

## Efficiency Notes
- JSON fee structures enable flexible pricing without schema changes
- Parent-child account relationships support complex corporate structures
- Sweep execution tracking provides audit trail for cash movements
- Evidence files define cash management policies and pooling eligibility
- Fast/slow pairs demonstrate index usage on unique constraints vs pattern matching