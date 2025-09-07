# Sample Tasks for consumer_lending_loans_cards

## Task 1: Portfolio Risk Analysis
**User**: What's the current risk profile of our loan portfolio?
**Assistant**: I'll analyze the risk distribution across our lending portfolio.
```sql
SELECT 
    lp.product_type,
    COUNT(*) as total_loans,
    SUM(l.current_balance) as total_outstanding,
    AVG(c.credit_score) as avg_credit_score,
    COUNT(CASE WHEN l.delinquency_days > 30 THEN 1 END) as delinquent_loans,
    COUNT(CASE WHEN l.delinquency_days > 30 THEN 1 END) * 100.0 / COUNT(*) as delinquency_rate
FROM loans l
JOIN customers c ON l.customer_id = c.id
JOIN loan_products lp ON l.loan_product_id = lp.id
WHERE l.status = 'ACTIVE'
GROUP BY lp.product_type
ORDER BY delinquency_rate DESC;
```

**User**: Which credit score bands have the highest default rates?
**Assistant**: Breaking down default rates by credit score segments:
```sql
SELECT 
    CASE 
        WHEN c.credit_score < 580 THEN 'Subprime (300-579)'
        WHEN c.credit_score < 670 THEN 'Near Prime (580-669)'
        WHEN c.credit_score < 740 THEN 'Prime (670-739)'
        WHEN c.credit_score < 800 THEN 'Super Prime (740-799)'
        ELSE 'Exceptional (800+)'
    END as credit_tier,
    COUNT(*) as total_loans,
    COUNT(CASE WHEN l.status = 'DEFAULT' THEN 1 END) as defaults,
    COUNT(CASE WHEN l.status = 'DEFAULT' THEN 1 END) * 100.0 / COUNT(*) as default_rate,
    AVG(l.current_balance) as avg_balance
FROM loans l
JOIN customers c ON l.customer_id = c.id
GROUP BY credit_tier
ORDER BY default_rate DESC;
```

## Task 2: Credit Card Utilization Analysis
**User**: How are our credit card customers utilizing their credit limits?
**Assistant**: Analyzing credit card utilization patterns:
```sql
SELECT 
    cc.card_type,
    COUNT(*) as total_cards,
    AVG(cc.credit_limit) as avg_limit,
    AVG(l.current_balance) as avg_balance,
    AVG(l.current_balance / cc.credit_limit) as avg_utilization_rate,
    COUNT(CASE WHEN l.current_balance / cc.credit_limit > 0.8 THEN 1 END) as high_utilization_cards
FROM credit_cards cc
JOIN loans l ON cc.loan_id = l.id
WHERE cc.status = 'ACTIVE'
GROUP BY cc.card_type
ORDER BY avg_utilization_rate DESC;
```

## Task 3: Efficiency Pair - Customer Loan History
**User**: Show all loans for customer CUST00100
**Assistant**: Fast query uses customer_id unique constraint:
```sql fast
SELECT 
    l.id as loan_id,
    lp.product_name,
    l.principal_amount,
    l.interest_rate,
    l.origination_date,
    l.status,
    l.current_balance
FROM loans l
JOIN customers c ON l.customer_id = c.id
JOIN loan_products lp ON l.loan_product_id = lp.id
WHERE c.customer_id = 'CUST00100'
ORDER BY l.origination_date DESC;
```
```sql slow
SELECT 
    l.id as loan_id,
    lp.product_name,
    l.principal_amount,
    l.interest_rate,
    l.origination_date,
    l.status,
    l.current_balance
FROM loans l
JOIN customers c ON l.customer_id = c.id
JOIN loan_products lp ON l.loan_product_id = lp.id
WHERE c.customer_id LIKE '%00100%'
ORDER BY l.origination_date DESC;
```

## Task 4: Evidence - Underwriting Guidelines
**User**: What are our current underwriting guidelines for personal loans?
**Assistant**: Checking underwriting policy:
```sql
SELECT json_extract(value, '$.personal_loan_guidelines') as guidelines
FROM evidence_kv 
WHERE key = 'underwriting_policy';
```

## Task 5: Application Approval Analysis
**User**: What's our approval rate by product type this month?
**Assistant**: Analyzing recent application performance:
```sql
SELECT 
    lp.product_type,
    COUNT(*) as total_applications,
    COUNT(CASE WHEN la.status = 'APPROVED' THEN 1 END) as approved,
    COUNT(CASE WHEN la.status = 'REJECTED' THEN 1 END) as rejected,
    COUNT(CASE WHEN la.status = 'APPROVED' THEN 1 END) * 100.0 / COUNT(*) as approval_rate,
    AVG(la.requested_amount) as avg_requested_amount
FROM loan_applications la
JOIN loan_products lp ON la.product_id = lp.id
WHERE la.application_date >= DATE('now', 'start of month')
GROUP BY lp.product_type
ORDER BY approval_rate DESC;
```

## Task 6: Efficiency Pair - High Credit Score Customers
**User**: Show customers with credit scores above 750
**Assistant**: Fast uses credit score index:
```sql fast
SELECT 
    customer_id,
    first_name,
    last_name,
    credit_score,
    income,
    employment_status
FROM customers
WHERE credit_score > 750
ORDER BY credit_score DESC;
```
```sql slow
SELECT 
    customer_id,
    first_name,
    last_name,
    credit_score,
    income,
    employment_status
FROM customers
WHERE CAST(credit_score AS TEXT) > '750'
ORDER BY credit_score DESC;
```

## Task 7: Card Transaction Analysis
**User**: What are the spending patterns on our credit cards?
**Assistant**: Analyzing card transaction patterns:
```sql
SELECT 
    ct.merchant_category,
    COUNT(*) as transaction_count,
    SUM(ct.transaction_amount) as total_volume,
    AVG(ct.transaction_amount) as avg_transaction_size,
    COUNT(DISTINCT ct.card_id) as unique_cards
FROM card_transactions ct
WHERE ct.transaction_type = 'PURCHASE'
  AND ct.transaction_date >= DATE('now', '-30 days')
GROUP BY ct.merchant_category
ORDER BY total_volume DESC;
```

## Task 8: Efficiency Pair - Recent Transactions
**User**: Show card transactions from the last 7 days
**Assistant**: Fast uses transaction date index:
```sql fast
SELECT 
    ct.transaction_date,
    cc.card_number,
    ct.merchant_name,
    ct.transaction_amount,
    ct.transaction_type
FROM card_transactions ct
JOIN credit_cards cc ON ct.card_id = cc.id
WHERE ct.transaction_date >= DATE('now', '-7 days')
ORDER BY ct.transaction_date DESC;
```
```sql slow
SELECT 
    ct.transaction_date,
    cc.card_number,
    ct.merchant_name,
    ct.transaction_amount,
    ct.transaction_type
FROM card_transactions ct
JOIN credit_cards cc ON ct.card_id = cc.id
WHERE substr(ct.transaction_date, 1, 10) >= DATE('now', '-7 days')
ORDER BY ct.transaction_date DESC;
```
