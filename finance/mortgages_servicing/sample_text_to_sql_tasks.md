# Sample Tasks for wells_fargo_home_loans

## Task 1: Portfolio Delinquency Analysis
**User**: What's our current delinquency rate?
**Assistant**: Analyzing portfolio delinquency status.
```sql
SELECT 
    ml.loan_type,
    COUNT(*) as total_loans,
    COUNT(CASE WHEN mp.days_late > 30 THEN 1 END) as delinquent_30_plus,
    COUNT(CASE WHEN mp.days_late > 60 THEN 1 END) as delinquent_60_plus,
    COUNT(CASE WHEN mp.days_late > 30 THEN 1 END) * 100.0 / COUNT(*) as delinquency_rate
FROM mortgage_loans ml
LEFT JOIN (
    SELECT loan_id, MAX(days_late) as days_late 
    FROM mortgage_payments 
    GROUP BY loan_id
) mp ON ml.id = mp.loan_id
WHERE ml.status = 'ACTIVE'
GROUP BY ml.loan_type;
```

## Task 2: Efficiency Pair - Borrower Lookup
**User**: Show loan details for borrower BOR000001
**Assistant**: Fast uses borrower_id unique constraint:
```sql fast
SELECT 
    ml.loan_number,
    ml.loan_type,
    ml.original_amount,
    ml.current_balance,
    ml.interest_rate,
    ml.status
FROM mortgage_loans ml
JOIN borrowers b ON ml.borrower_id = b.id
WHERE b.borrower_id = 'BOR000001';
```
```sql slow
SELECT 
    ml.loan_number,
    ml.loan_type,
    ml.original_amount,
    ml.current_balance,
    ml.interest_rate,
    ml.status
FROM mortgage_loans ml
JOIN borrowers b ON ml.borrower_id = b.id
WHERE b.borrower_id LIKE '%000001%';
```

## Task 3: Evidence - Payment Processing Rules
**User**: What are our payment processing policies?
**Assistant**: Checking payment policies:
```sql
SELECT json_extract(value, '$.payment_processing') as payment_rules
FROM evidence_kv 
WHERE key = 'servicing_policies';
```

## Task 4: Escrow Analysis
**User**: Which loans have escrow shortages?
**Assistant**: Finding escrow shortages:
```sql
SELECT 
    ml.loan_number,
    b.first_name || ' ' || b.last_name as borrower,
    ea.current_balance,
    ea.annual_tax_amount + ea.annual_insurance_amount as annual_disbursements,
    ea.shortage_amount,
    ea.last_analysis_date
FROM escrow_accounts ea
JOIN mortgage_loans ml ON ea.loan_id = ml.id
JOIN borrowers b ON ml.borrower_id = b.id
WHERE ea.shortage_amount > 0
ORDER BY ea.shortage_amount DESC;
```

## Task 5: Efficiency Pair - Recent Payments
**User**: Show payments from last week
**Assistant**: Fast uses payment date index:
```sql fast
SELECT 
    ml.loan_number,
    mp.payment_date,
    mp.actual_payment_amount,
    mp.days_late
FROM mortgage_payments mp
JOIN mortgage_loans ml ON mp.loan_id = ml.id
WHERE mp.payment_date >= DATE('now', '-7 days')
ORDER BY mp.payment_date DESC;
```
```sql slow
SELECT 
    ml.loan_number,
    mp.payment_date,
    mp.actual_payment_amount,
    mp.days_late
FROM mortgage_payments mp
JOIN mortgage_loans ml ON mp.loan_id = ml.id
WHERE substr(mp.payment_date, 1, 10) >= DATE('now', '-7 days')
ORDER BY mp.payment_date DESC;
```