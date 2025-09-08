# chase_consumer_banking

## Overview
This subdomain models consumer lending operations including personal loans, auto loans, student loans, and credit cards with comprehensive application workflows, payment tracking, and risk management.

## Entities

### Normalized Schema
- **customers**: Customer demographics with credit scores and income verification
- **loan_products**: Lending product catalog with eligibility criteria and rate ranges
- **loan_applications**: Application workflow with approval/rejection decisions
- **loans**: Active loan accounts with balances and delinquency tracking
- **loan_payments**: Payment history with principal/interest breakdowns
- **credit_cards**: Revolving credit products linked to loan accounts
- **card_transactions**: Credit card purchase and payment transaction history

### Denormalized Schema
- **loan_portfolio_summary**: Comprehensive loan metrics with risk indicators
- **credit_card_portfolio**: Card utilization and performance analytics
- **daily_lending_metrics**: Daily origination and performance tracking
- **customer_risk_profile**: Consolidated customer risk assessment and exposure

## Key Indexes
- `idx_customers_credit_score`: Credit score-based customer segmentation
- `idx_loan_applications_status`: Application workflow management
- `idx_loans_status`: Portfolio status analysis
- `idx_card_transactions_date`: Transaction timeline analysis
- `idx_loan_payments_loan`: Payment history reconstruction

## Efficiency Notes
- JSON rate ranges enable flexible product configuration without schema changes
- Credit cards modeled as specialized revolving loans for unified balance tracking
- Delinquency days calculated for real-time risk assessment
- Evidence files define underwriting policies and credit limit matrices
- Fast/slow pairs demonstrate index usage on unique constraints vs pattern matching