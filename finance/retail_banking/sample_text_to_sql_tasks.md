# Sample Tasks for retail_banking

## Task 1: customer account list
**User**: List accounts for customer 1.
**Assistant**: Filter accounts by customer_id.
```sql
SELECT account_number FROM accounts WHERE customer_id=1;
```

## Task 2: evidence wire fee
**User**: What is the wire transfer fee per fee_schedule.json?
**Assistant**: Pull value from evidence_kv then show.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='fee_schedule'), '$.wire_fee_cents');
```

## Task 3: efficiency-sensitive transaction search
**User**: Find posted transactions for account 2 on 2024-01-03.
**Assistant**: Fast query uses indexed date; show slow too.
```sql fast
SELECT * FROM transactions WHERE account_id=2 AND txn_date='2024-01-03' AND status='POSTED';
```
```sql slow
SELECT * FROM transactions WHERE account_id=2 AND substr(txn_date,1,10)='2024-01-03' AND status='POSTED';
```

## Task 4: evidence branch hours
**User**: When are branches open?
**Assistant**: Read branch_hours.md via evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='branch_hours'), '$');
```

## Task 5: high risk customers
**User**: Show customers with HIGH risk rating.
**Assistant**: Simple filter.
```sql
SELECT name FROM customers WHERE risk_rating='HIGH';
```

## Task 6: deposit totals
**User**: Total deposited (positive amounts) for account 3.
**Assistant**: Sum positive amounts.
```sql
SELECT SUM(amount_cents) FROM transactions WHERE account_id=3 AND amount_cents>0;
```

## Task 7: efficiency pair monthly sums
**User**: Sum transactions for January by account.
**Assistant**: Fast uses range; slow uses strftime.
```sql fast
SELECT account_id, SUM(amount_cents) FROM transactions
WHERE txn_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY account_id;
```
```sql slow
SELECT account_id, SUM(amount_cents) FROM transactions
WHERE strftime('%m', txn_date)='01'
GROUP BY account_id;
```

## Task 8: evidence ATM fee
**User**: According to fee_schedule.json, what's the ATM withdrawal fee?
**Assistant**: query evidence_kv.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='fee_schedule'), '$.atm_withdrawal_fee_cents');
```

## Task 9: account opened after date
**User**: Accounts opened after 2024-01-03?
**Assistant**: Compare opened_at.
```sql
SELECT account_number FROM accounts WHERE opened_at>'2024-01-03';
```

## Task 10: branch customer count
**User**: How many customers per branch?
**Assistant**: join accounts and branches.
```sql
SELECT b.name, COUNT(DISTINCT a.customer_id)
FROM branches b JOIN accounts a ON b.id=a.branch_id
GROUP BY b.id;
```

## Task 11: evidence hours text
**User**: Return raw branch hours text.
**Assistant**: Use json_extract with '$'.
```sql
SELECT json_extract((SELECT value FROM evidence_kv WHERE key='branch_hours'), '$');
```

## Task 12: accounts without transactions
**User**: List accounts with no transactions.
**Assistant**: Left join and filter nulls.
```sql
SELECT a.account_number FROM accounts a LEFT JOIN transactions t ON a.id=t.account_id
GROUP BY a.id HAVING COUNT(t.id)=0;
```

## Task 13: efficiency pair status filter
**User**: Count POSTED transactions for account 1.
**Assistant**: Fast uses status index.
```sql fast
SELECT COUNT(*) FROM transactions WHERE account_id=1 AND status='POSTED';
```
```sql slow
SELECT COUNT(*) FROM transactions WHERE account_id=1 AND status LIKE 'POSTED';
```

## Task 14: evidence fee comparison
**User**: Does wire fee exceed ATM fee?
**Assistant**: Compare values from JSON.
```sql
SELECT json_extract(v.value,'$.wire_fee_cents')>json_extract(v.value,'$.atm_withdrawal_fee_cents')
FROM evidence_kv v WHERE v.key='fee_schedule';
```

## Task 15: daily balance for account
**User**: What's total amount on 2024-01-02 for account 2?
**Assistant**: Sum that day's amounts.
```sql
SELECT SUM(amount_cents) FROM transactions WHERE account_id=2 AND txn_date='2024-01-02';
```
