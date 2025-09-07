-- 1. every terminal belongs to a valid merchant
SELECT COUNT(*) FROM terminals t LEFT JOIN merchants m ON t.merchant_id=m.id WHERE m.id IS NULL;
-- 2. each merchant has exactly 2 terminals
SELECT merchant_id, COUNT(*) c FROM terminals GROUP BY merchant_id HAVING c<>2;
-- 3. settlement batch uniqueness per merchant/date
SELECT merchant_id, cutover_utc_date, COUNT(*) c FROM settlement_batches GROUP BY 1,2 HAVING c>1;
-- 4. transaction amounts positive
SELECT COUNT(*) FROM card_transactions WHERE amount_cents<=0;
-- 5. card transactions link to existing batch
SELECT COUNT(*) FROM card_transactions ct LEFT JOIN settlement_batches sb ON ct.settlement_batch_id=sb.id WHERE ct.settlement_batch_id IS NOT NULL AND sb.id IS NULL;
-- 6. chargeback not exceeding original amount
SELECT COUNT(*) FROM chargebacks cb JOIN card_transactions ct ON cb.card_transaction_id=ct.id WHERE cb.amount_cents>ct.amount_cents;
-- 7. transaction counts per batch
SELECT settlement_batch_id, COUNT(*) c FROM card_transactions GROUP BY 1 HAVING c=0;
-- 8. merchants present in batches
SELECT COUNT(*) FROM settlement_batches sb LEFT JOIN merchants m ON sb.merchant_id=m.id WHERE m.id IS NULL;
-- 9. sample net settlement equals transactions minus chargebacks
WITH tx AS (
  SELECT merchant_id, SUM(amount_cents) a FROM card_transactions GROUP BY merchant_id
), cb AS (
  SELECT merchant_id, SUM(amount_cents) b FROM chargebacks cb JOIN card_transactions ct ON cb.card_transaction_id=ct.id GROUP BY merchant_id
)
SELECT COUNT(*) FROM tx LEFT JOIN cb USING(merchant_id) WHERE a-COALESCE(b,0)<0;
-- 10. index coverage check: EXPLAIN to ensure index usage
EXPLAIN QUERY PLAN SELECT * FROM card_transactions WHERE merchant_id=1 ORDER BY txn_ts LIMIT 10;
