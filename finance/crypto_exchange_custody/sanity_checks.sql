-- wallets must map to clients
SELECT COUNT(*) FROM wallets w LEFT JOIN clients c ON w.client_id=c.id WHERE c.id IS NULL;
-- transfers must map to wallets
SELECT COUNT(*) FROM custody_transfers ct LEFT JOIN wallets w ON ct.wallet_id=w.id WHERE w.id IS NULL;
-- deposits by asset
SELECT asset_symbol, SUM(amount_sats) FROM custody_transfers ct JOIN wallets w ON ct.wallet_id=w.id WHERE direction='DEPOSIT' GROUP BY asset_symbol;
-- cumulative balance per wallet
SELECT wallet_id, transfer_ts,
       SUM(CASE WHEN direction='DEPOSIT' THEN amount_sats ELSE -amount_sats END)
       OVER(PARTITION BY wallet_id ORDER BY transfer_ts) AS balance
FROM custody_transfers ORDER BY wallet_id, transfer_ts LIMIT 10;
-- cold storage moves reference batches
SELECT COUNT(*) FROM cold_storage_moves m JOIN cold_storage_batches b ON m.batch_id=b.id;
-- risk tier distribution
SELECT risk_tier, COUNT(*) FROM clients GROUP BY risk_tier;
-- daily net flow using CTE
WITH daily AS (
  SELECT substr(transfer_ts,1,10) d,
         SUM(CASE WHEN direction='DEPOSIT' THEN amount_sats ELSE -amount_sats END) net
  FROM custody_transfers GROUP BY d
)
SELECT * FROM daily WHERE net<>0 LIMIT 5;
-- unique tx hashes
SELECT COUNT(tx_hash), COUNT(DISTINCT tx_hash) FROM custody_transfers;
-- average transfer per client
SELECT c.id, AVG(amount_sats) avg_amt FROM custody_transfers ct
JOIN wallets w ON ct.wallet_id=w.id JOIN clients c ON w.client_id=c.id
GROUP BY c.id HAVING avg_amt>0 LIMIT 5;
-- positive cold storage moves
SELECT COUNT(*) FROM cold_storage_moves WHERE amount_sats<=0;
