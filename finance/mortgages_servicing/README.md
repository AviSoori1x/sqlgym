# wells_fargo_home_loans

## Overview
This subdomain models mortgage loan servicing operations including payment processing, escrow management, delinquency tracking, and portfolio performance analysis.

## Entities

### Normalized Schema
- **borrowers**: Mortgage borrower profiles with contact and employment information
- **properties**: Real estate property details with appraisal values
- **mortgage_loans**: Loan accounts with terms, balances, and status tracking
- **escrow_accounts**: Property tax and insurance escrow management
- **mortgage_payments**: Payment history with principal/interest/escrow breakdown
- **escrow_disbursements**: Tax and insurance payment tracking
- **delinquency_tracking**: Collections workflow and status management

### Denormalized Schema
- **loan_servicing_summary**: Comprehensive loan status with payment metrics
- **portfolio_performance_daily**: Daily portfolio health and delinquency rates
- **escrow_analysis_summary**: Escrow balance projections and shortage analysis
- **delinquency_roll_rates**: Monthly delinquency transition and cure rate analysis

## Key Indexes
- `idx_mortgage_loans_borrower`: Borrower loan portfolio queries
- `idx_mortgage_payments_loan`: Payment history reconstruction
- `idx_mortgage_payments_date`: Time-based payment analysis
- `idx_delinquency_tracking_stage`: Collections workflow management
- `idx_properties_location`: Geographic risk analysis

## Efficiency Notes
- One-to-one relationships between loans and escrow accounts for active mortgages
- Payment component breakdown enables detailed cash flow analysis
- Delinquency staging supports automated collections workflows
- Evidence files define servicing policies and escrow management rules
- Fast/slow pairs demonstrate index usage on unique identifiers vs pattern searches