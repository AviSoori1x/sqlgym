# Workflow Tasks

## Task: credit_risk_assessment
```sql
-- step: high_risk_customers
CREATE TEMP TABLE high_risk_customers AS
SELECT 
    c.customer_id,
    c.credit_score,
    COUNT(DISTINCT l.id) as active_loans,
    SUM(l.current_balance) as total_exposure,
    MAX(l.delinquency_days) as max_delinquency
FROM customers c
JOIN loans l ON c.id = l.customer_id
WHERE l.status = 'ACTIVE'
GROUP BY c.id
HAVING c.credit_score < 650 OR max_delinquency > 30;
```
```sql
-- step: payment_history
-- depends: high_risk_customers
CREATE TEMP TABLE payment_history AS
SELECT 
    hrc.customer_id,
    COUNT(lp.id) as payment_count,
    COUNT(CASE WHEN lp.days_late > 0 THEN 1 END) as late_payments,
    AVG(lp.payment_amount) as avg_payment_amount
FROM high_risk_customers hrc
JOIN loans l ON hrc.customer_id = l.customer_id
LEFT JOIN loan_payments lp ON l.id = lp.loan_id
WHERE lp.payment_date >= DATE('now', '-12 months')
GROUP BY hrc.customer_id;
```
```sql
-- step: risk_scoring
-- depends: high_risk_customers, payment_history
CREATE TEMP TABLE risk_scoring AS
SELECT 
    hrc.customer_id,
    hrc.credit_score,
    hrc.total_exposure,
    ph.late_payments * 100.0 / NULLIF(ph.payment_count, 0) as late_payment_rate,
    CASE 
        WHEN hrc.credit_score < 580 THEN 'VERY_HIGH'
        WHEN hrc.max_delinquency > 60 THEN 'HIGH'
        WHEN ph.late_payments * 100.0 / NULLIF(ph.payment_count, 0) > 10 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_category
FROM high_risk_customers hrc
LEFT JOIN payment_history ph ON hrc.customer_id = ph.customer_id;
```
```sql
-- step: risk_summary
-- depends: risk_scoring
SELECT 
    risk_category,
    COUNT(*) as customer_count,
    SUM(total_exposure) as total_portfolio_exposure,
    AVG(credit_score) as avg_credit_score,
    AVG(late_payment_rate) as avg_late_payment_rate
FROM risk_scoring
GROUP BY risk_category
ORDER BY 
    CASE risk_category 
        WHEN 'VERY_HIGH' THEN 1 
        WHEN 'HIGH' THEN 2 
        WHEN 'MEDIUM' THEN 3 
        ELSE 4 
    END;
```

## Task: cash_pool_optimization
```sql
-- step: client_cash_flows
CREATE TEMP TABLE client_cash_flows AS
SELECT 
    a.client_id,
    DATE(t.transaction_date) as transaction_date,
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as daily_inflows,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as daily_outflows,
    SUM(t.amount) as net_daily_flow
FROM accounts a
JOIN transactions t ON a.id = t.account_id
WHERE t.transaction_date >= DATE('now', '-90 days')
GROUP BY a.client_id, DATE(t.transaction_date);
```
```sql
-- step: volatility_analysis
-- depends: client_cash_flows
CREATE TEMP TABLE volatility_analysis AS
SELECT 
    client_id,
    AVG(ABS(net_daily_flow)) as avg_daily_volatility,
    STDDEV(net_daily_flow) as flow_volatility,
    MIN(net_daily_flow) as worst_daily_outflow,
    MAX(net_daily_flow) as best_daily_inflow
FROM client_cash_flows
GROUP BY client_id;
```
```sql
-- step: pooling_recommendations
-- depends: volatility_analysis
CREATE TEMP TABLE pooling_recommendations AS
SELECT 
    cc.client_code,
    cc.company_name,
    va.avg_daily_volatility,
    COUNT(DISTINCT a.id) as total_accounts,
    SUM(a.current_balance) as total_balance,
    CASE 
        WHEN va.avg_daily_volatility > 1000000 AND total_accounts >= 3 THEN 'ZERO_BALANCE_POOL'
        WHEN va.avg_daily_volatility > 500000 THEN 'TARGET_BALANCE_POOL'
        WHEN total_accounts >= 5 THEN 'THRESHOLD_SWEEP_POOL'
        ELSE 'NO_POOLING_NEEDED'
    END as recommended_structure
FROM volatility_analysis va
JOIN corporate_clients cc ON va.client_id = cc.id
JOIN accounts a ON cc.id = a.client_id AND a.status = 'ACTIVE'
GROUP BY cc.id;
```
```sql
-- step: optimization_summary
-- depends: pooling_recommendations
SELECT 
    recommended_structure,
    COUNT(*) as eligible_clients,
    SUM(total_balance) as aggregate_balance,
    AVG(avg_daily_volatility) as avg_client_volatility,
    SUM(total_balance) * 0.02 / 365 * 30 as estimated_monthly_savings
FROM pooling_recommendations
WHERE recommended_structure != 'NO_POOLING_NEEDED'
GROUP BY recommended_structure
ORDER BY estimated_monthly_savings DESC;
```

## Task: mortgage_portfolio_health
```sql
-- step: loan_performance_metrics
CREATE TEMP TABLE loan_performance_metrics AS
SELECT 
    ml.loan_type,
    strftime('%Y-%m', ml.origination_date) as vintage_month,
    COUNT(*) as loans_count,
    SUM(ml.original_amount) as original_balance,
    SUM(ml.current_balance) as current_balance,
    AVG(ml.interest_rate) as avg_interest_rate,
    COUNT(CASE WHEN ml.status = 'DEFAULT' THEN 1 END) as default_count
FROM mortgage_loans ml
WHERE ml.origination_date >= DATE('now', '-36 months')
GROUP BY ml.loan_type, strftime('%Y-%m', ml.origination_date);
```
```sql
-- step: delinquency_analysis
-- depends: loan_performance_metrics
CREATE TEMP TABLE delinquency_analysis AS
SELECT 
    ml.loan_type,
    COUNT(*) as active_loans,
    COUNT(CASE WHEN mp.days_late > 30 THEN 1 END) as delinq_30_plus,
    COUNT(CASE WHEN mp.days_late > 60 THEN 1 END) as delinq_60_plus,
    COUNT(CASE WHEN mp.days_late > 90 THEN 1 END) as delinq_90_plus
FROM mortgage_loans ml
LEFT JOIN (
    SELECT loan_id, MAX(days_late) as days_late 
    FROM mortgage_payments 
    WHERE payment_date >= DATE('now', '-30 days')
    GROUP BY loan_id
) mp ON ml.id = mp.loan_id
WHERE ml.status = 'ACTIVE'
GROUP BY ml.loan_type;
```
```sql
-- step: escrow_health_check
-- depends: loan_performance_metrics
CREATE TEMP TABLE escrow_health_check AS
SELECT 
    COUNT(*) as total_escrow_accounts,
    COUNT(CASE WHEN shortage_amount > 0 THEN 1 END) as accounts_with_shortage,
    SUM(shortage_amount) as total_shortage_amount,
    COUNT(CASE WHEN last_analysis_date < DATE('now', '-365 days') THEN 1 END) as overdue_analyses
FROM escrow_accounts ea
JOIN mortgage_loans ml ON ea.loan_id = ml.id
WHERE ml.status = 'ACTIVE';
```
```sql
-- step: portfolio_health_summary
-- depends: loan_performance_metrics, delinquency_analysis, escrow_health_check
SELECT 
    'Loan Performance' as metric_category,
    lpm.loan_type as subcategory,
    lpm.loans_count as metric_value,
    lpm.default_count * 100.0 / lpm.loans_count as performance_rate,
    'Default Rate %' as metric_description
FROM loan_performance_metrics lpm
WHERE lpm.vintage_month >= DATE('now', '-12 months')
UNION ALL
SELECT 
    'Delinquency Status' as metric_category,
    da.loan_type as subcategory,
    da.delinq_30_plus as metric_value,
    da.delinq_30_plus * 100.0 / da.active_loans as performance_rate,
    '30+ Day Delinquency Rate %' as metric_description
FROM delinquency_analysis da
UNION ALL
SELECT 
    'Escrow Management' as metric_category,
    'All Loans' as subcategory,
    ehc.accounts_with_shortage as metric_value,
    ehc.accounts_with_shortage * 100.0 / ehc.total_escrow_accounts as performance_rate,
    'Escrow Shortage Rate %' as metric_description
FROM escrow_health_check ehc;
```