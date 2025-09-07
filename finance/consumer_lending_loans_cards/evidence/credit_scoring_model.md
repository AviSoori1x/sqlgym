# Credit Scoring and Risk Assessment Model

## Credit Score Tiers

### Exceptional Credit (800-850)
- **Characteristics**: Excellent payment history, low utilization, long credit history
- **Loan Approval**: 95%+ approval rate
- **Interest Rates**: Best available rates (prime - 1% to prime + 2%)
- **Credit Limits**: High limits with minimal restrictions
- **Special Considerations**: Pre-approved offers, premium products

### Super Prime (740-799)
- **Characteristics**: Strong payment history, moderate utilization
- **Loan Approval**: 85-95% approval rate
- **Interest Rates**: Prime to prime + 4%
- **Credit Limits**: Standard to high limits
- **Special Considerations**: Competitive rates, most products available

### Prime (670-739)
- **Characteristics**: Good payment history, some credit utilization
- **Loan Approval**: 70-85% approval rate
- **Interest Rates**: Prime + 2% to prime + 8%
- **Credit Limits**: Moderate limits with standard terms
- **Special Considerations**: Mainstream lending products

### Near Prime (580-669)
- **Characteristics**: Fair credit, higher utilization or limited history
- **Loan Approval**: 40-70% approval rate
- **Interest Rates**: Prime + 6% to prime + 15%
- **Credit Limits**: Lower limits, additional requirements
- **Special Considerations**: Income verification, co-signer options

### Subprime (300-579)
- **Characteristics**: Poor payment history, high utilization, recent derogatory marks
- **Loan Approval**: 10-40% approval rate
- **Interest Rates**: Prime + 12% to maximum allowed
- **Credit Limits**: Very low limits, secured products only
- **Special Considerations**: Secured cards, alternative data sources

## Risk Assessment Factors

### Primary Factors (70% weight)
- Payment history (35%)
- Credit utilization (30%)
- Length of credit history (15%)
- Credit mix (10%)
- New credit inquiries (10%)

### Secondary Factors (30% weight)
- Income stability and verification
- Debt-to-income ratio
- Employment history
- Bank account history
- Geographic risk factors

## Automated Decision Rules

### Auto-Approval Criteria
- Credit score ≥ 740
- Debt-to-income ratio ≤ 25%
- No derogatory marks in 24 months
- Verified income ≥ $50,000

### Auto-Decline Criteria
- Credit score < 580
- Active bankruptcy
- Debt-to-income ratio > 50%
- Recent charge-offs or foreclosure

### Manual Review Required
- Credit score 580-739 with compensating factors
- High income with limited credit history
- Recent credit events requiring explanation
- Non-standard employment or income sources
