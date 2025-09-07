# Workflow Tasks

## Task: payout pipeline
```sql
-- step: pending
CREATE TEMP TABLE pending AS
SELECT ct.* FROM card_transactions ct
JOIN settlement_batches sb ON sb.id=ct.settlement_batch_id
WHERE sb.status='CLOSED';
```
```sql
-- step: by_merchant
-- depends: pending
CREATE TEMP TABLE by_merchant AS
SELECT merchant_id, SUM(amount_cents) gross FROM pending GROUP BY merchant_id;
```
```sql
-- step: final
-- depends: by_merchant
SELECT * FROM by_merchant WHERE gross>100000;
```

## Task: chargeback exposure
```sql
-- step: base
CREATE TEMP TABLE base AS
SELECT ct.id, ct.merchant_id, ct.amount_cents FROM card_transactions ct;
```
```sql
-- step: cb
-- depends: base
CREATE TEMP TABLE cb AS
SELECT b.merchant_id, SUM(cb.amount_cents) cb_amt FROM base b
JOIN chargebacks cb ON cb.card_transaction_id=b.id GROUP BY b.merchant_id;
```
```sql
-- step: final
-- depends: cb
SELECT merchant_id, cb_amt FROM cb WHERE cb_amt>10000;
```
