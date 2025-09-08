# Sample Tasks for jpmorgan_treasury

## Task 1: Cash Pool Performance Analysis
**User**: How are our cash pooling structures performing?
**Assistant**: I'll analyze cash pool efficiency and utilization.
```sql
SELECT 
    cps.pool_name,
    cc.company_name,
    cps.pool_type,
    cps.sweep_frequency,
    COUNT(DISTINCT pp.account_id) as participant_accounts,
    AVG(se.total_amount_swept) as avg_sweep_amount,
    COUNT(se.id) as sweep_executions_30d
FROM cash_pool_structures cps
JOIN corporate_clients cc ON cps.client_id = cc.id
LEFT JOIN pool_participants pp ON cps.id = pp.pool_id
LEFT JOIN sweep_executions se ON cps.id = se.pool_id 
    AND se.execution_date >= DATE('now', '-30 days')
WHERE cps.is_active = 1
GROUP BY cps.id
ORDER BY avg_sweep_amount DESC;
```

## Task 2: Efficiency Pair - Client Account Lookup
**User**: Show all accounts for client CORP0001
**Assistant**: Fast query uses client_code unique constraint:
```sql fast
SELECT 
    a.account_number,
    at.type_name,
    a.current_balance,
    a.available_balance,
    a.status
FROM accounts a
JOIN corporate_clients cc ON a.client_id = cc.id
JOIN account_types at ON a.account_type_id = at.id
WHERE cc.client_code = 'CORP0001'
ORDER BY a.current_balance DESC;
```
```sql slow
SELECT 
    a.account_number,
    at.type_name,
    a.current_balance,
    a.available_balance,
    a.status
FROM accounts a
JOIN corporate_clients cc ON a.client_id = cc.id
JOIN account_types at ON a.account_type_id = at.id
WHERE cc.client_code LIKE '%0001%'
ORDER BY a.current_balance DESC;
```

## Task 3: Evidence - Cash Management Policy
**User**: What are our cash pooling eligibility requirements?
**Assistant**: Checking cash management policy:
```sql
SELECT json_extract(value, '$.cash_pooling_eligibility') as eligibility_rules
FROM evidence_kv 
WHERE key = 'cash_management_policy';
```

## Task 4: Transaction Volume Analysis
**User**: What's the transaction volume across different account types?
**Assistant**: Analyzing transaction patterns by account type:
```sql
SELECT 
    at.type_name,
    at.category,
    COUNT(DISTINCT a.id) as total_accounts,
    COUNT(t.id) as total_transactions,
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as total_credits,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as total_debits
FROM account_types at
JOIN accounts a ON at.id = a.account_type_id
LEFT JOIN transactions t ON a.id = t.account_id
WHERE t.transaction_date >= DATE('now', '-30 days')
GROUP BY at.id
ORDER BY total_transactions DESC;
```

## Task 5: Efficiency Pair - Recent Transactions
**User**: Show transaction summary for today
**Assistant**: Fast uses transaction date index:
```sql fast
SELECT 
    t.transaction_type,
    COUNT(*) as transaction_count,
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as total_credits,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as total_debits
FROM transactions t
WHERE DATE(t.transaction_date) = DATE('now')
GROUP BY t.transaction_type
ORDER BY transaction_count DESC;
```
```sql slow
SELECT 
    t.transaction_type,
    COUNT(*) as transaction_count,
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as total_credits,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as total_debits
FROM transactions t
WHERE substr(t.transaction_date, 1, 10) = DATE('now')
GROUP BY t.transaction_type
ORDER BY transaction_count DESC;
```

## Task 6: Client Liquidity Analysis
**User**: Which clients have the highest liquidity risk?
**Assistant**: Analyzing client liquidity positions:
```sql
SELECT 
    cc.client_code,
    cc.company_name,
    cc.risk_rating,
    SUM(a.current_balance) as total_cash_position,
    SUM(a.available_balance) as available_liquidity,
    COUNT(a.id) as total_accounts
FROM corporate_clients cc
JOIN accounts a ON cc.id = a.client_id
WHERE a.status = 'ACTIVE'
GROUP BY cc.id
HAVING total_cash_position < 1000000
ORDER BY total_cash_position ASC;
```

## Task 7: Sweep Efficiency Analysis
**User**: How efficient are our sweep operations?
**Assistant**: Analyzing sweep execution performance:
```sql
SELECT 
    cps.sweep_frequency,
    COUNT(DISTINCT cps.id) as active_pools,
    COUNT(se.id) as total_executions,
    COUNT(CASE WHEN se.execution_status = 'COMPLETED' THEN 1 END) as successful_executions,
    AVG(se.total_amount_swept) as avg_sweep_amount
FROM cash_pool_structures cps
LEFT JOIN sweep_executions se ON cps.id = se.pool_id
WHERE cps.is_active = 1
  AND se.execution_date >= DATE('now', '-30 days')
GROUP BY cps.sweep_frequency
ORDER BY avg_sweep_amount DESC;
```
