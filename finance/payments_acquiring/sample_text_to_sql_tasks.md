# Sample Tasks for payments_acquiring

## Task 1: daily volume for a merchant
**User**: What's the total approved volume for merchant M00010 on 2024-01-02?
**Assistant**: Filter card_transactions by merchant and date, approved auths only.
**User**: Include refunds too.
**Assistant**: Sum amounts for both AUTH and REFUND where auth_status='APPROVED'.
```sql
SELECT SUM(amount_cents) FROM card_transactions
WHERE merchant_id=10 AND substr(txn_ts,1,10)='2024-01-02'
  AND auth_status='APPROVED';
```

## Task 2: evidence-driven fee policy
**User**: Using fee_policy.md, what's the net fee for merchant 5's CNP auths on 2024-01-01?
**Assistant**: evidence/fee_policy.md notes CNP adds 10 bps. Compute volume*rate.
**User**: rate baseline is 250 bps per policy.
**Assistant**: Apply 260 bps.
```sql
SELECT SUM(amount_cents)*0.0026 FROM card_transactions
WHERE merchant_id=5 AND substr(txn_ts,1,10)='2024-01-01'
  AND txn_type='AUTH' AND auth_status='APPROVED';
```

## Task 3: fast vs slow top merchants by settled volume
**User**: Who are the top 5 merchants by settled volume?
**Assistant**: Join batches and transactions; fast query uses indexes.
**User**: show me both the fast and a slow version.
**Assistant**: Slow omits indexed predicates causing scans.
```sql fast
SELECT m.name, SUM(ct.amount_cents) AS vol
FROM settlement_batches sb
JOIN card_transactions ct ON sb.id=ct.settlement_batch_id
JOIN merchants m ON m.id=ct.merchant_id
WHERE sb.status='CLOSED'
GROUP BY m.id ORDER BY vol DESC LIMIT 5;
```
```sql slow
SELECT m.name, SUM(ct.amount_cents) AS vol
FROM merchants m
JOIN card_transactions ct ON m.id=ct.merchant_id
LEFT JOIN settlement_batches sb ON sb.id=ct.settlement_batch_id
GROUP BY m.id ORDER BY vol DESC LIMIT 5;
```

## Task 4: chargeback ratio
**User**: What's the chargeback rate for merchant 3 in January?
**Assistant**: Ratio of chargeback amount to gross volume.
**User**: retrieval stage only.
**Assistant**: Filter chargebacks by stage='RETRIEVAL'.
```sql
WITH gross AS (
  SELECT SUM(amount_cents) a FROM card_transactions
  WHERE merchant_id=3 AND txn_ts LIKE '2024-01%'
), cb AS (
  SELECT SUM(cb.amount_cents) b FROM chargebacks cb
  JOIN card_transactions ct ON cb.card_transaction_id=ct.id
  WHERE ct.merchant_id=3 AND cb.stage='RETRIEVAL'
)
SELECT b*1.0/a FROM gross CROSS JOIN cb;
```

## Task 5: evidence business-day cutover
**User**: According to fee_policy.md, batches cut over on business days. How many batches cut over on weekends?
**Assistant**: Count settlement_batches where cutover_utc_date falls on Sat/Sun.
```sql
SELECT COUNT(*) FROM settlement_batches
WHERE strftime('%w', cutover_utc_date) IN ('0','6');
```

## Task 6: terminal activity
**User**: List inactive terminals.
**Assistant**: status='INACTIVE'.
**User**: return merchant names too.
**Assistant**: Join with merchants.
```sql
SELECT t.serial_number, m.name FROM terminals t
JOIN merchants m ON m.id=t.merchant_id
WHERE t.status='INACTIVE';
```

## Task 7: efficiency pair on date filtering
**User**: get transactions for merchant 1 on 2024-01-01.
**Assistant**: Fast query restricts by merchant then date using index.
**User**: show slow alternative.
```sql fast
SELECT * FROM card_transactions
WHERE merchant_id=1 AND txn_ts BETWEEN '2024-01-01' AND '2024-01-01T23:59:59';
```
```sql slow
SELECT * FROM card_transactions
WHERE substr(txn_ts,1,10)='2024-01-01' AND merchant_id=1;
```

## Task 8: evidence MCC default
**User**: Using fee_policy.md, which merchants have the default MCC?
**Assistant**: policy states default MCC is 5999.
```sql
SELECT merchant_code FROM merchants WHERE mcc=5999;
```

## Task 9: batch payout workflow
**User**: Have all batches for merchant 2 been paid?
**Assistant**: Check settlement_batches status.
**User**: show unpaid dates.
```sql
SELECT cutover_utc_date FROM settlement_batches
WHERE merchant_id=2 AND status!='PAID';
```

## Task 10: evidence retrieval stage note
**User**: Which chargebacks are in retrieval stage?
**Assistant**: Filter by stage per fee_policy.md definition.
```sql
SELECT id FROM chargebacks WHERE stage='RETRIEVAL';
```

## Task 11: fast vs slow merchant search
**User**: Find merchant by code M00020.
**Assistant**: Fast uses UNIQUE lookup; slow scans.
```sql fast
SELECT * FROM merchants WHERE merchant_code='M00020';
```
```sql slow
SELECT * FROM merchants WHERE name LIKE '%20%';
```

## Task 12: evidence business-day helper
**User**: Using fee_policy.md, what's the next business day after 2024-01-05?
**Assistant**: Policy lists business-day cutover; next business day is 2024-01-08.
**User**: show batches with that cutover.
```sql
SELECT * FROM settlement_batches WHERE cutover_utc_date='2024-01-08';
```

## Task 13: merchant volume trend
**User**: Give total volume per merchant for January ordered by merchant_code.
**Assistant**: Group by merchant.
**User**: exclude declined auths.
```sql
SELECT m.merchant_code, SUM(ct.amount_cents)
FROM merchants m JOIN card_transactions ct ON m.id=ct.merchant_id
WHERE ct.txn_ts LIKE '2024-01%' AND ct.auth_status!='DECLINED'
GROUP BY m.id ORDER BY m.merchant_code;
```

## Task 14: evidence foreign fees
**User**: Fee policy notes foreign currency markup of 20 bps. What's fee on EUR transactions for merchant 4?
**Assistant**: Apply 20 bps.
```sql
SELECT SUM(amount_cents)*0.0020 FROM card_transactions
WHERE merchant_id=4 AND currency='EUR';
```

## Task 15: terminal coverage check
**User**: Do any merchants lack terminals?
**Assistant**: Left join merchants to terminals and find NULL.
```sql
SELECT m.id FROM merchants m LEFT JOIN terminals t ON m.id=t.merchant_id
GROUP BY m.id HAVING COUNT(t.id)=0;
```
