# Sample Tasks for crypto_exchange_custody

## Task 1: BTC deposits by client
**User**: How many satoshis of BTC has client 1 deposited?
**Assistant**: Join wallets and transfers filtering on asset and direction.
```sql
SELECT SUM(ct.amount_sats) FROM custody_transfers ct
JOIN wallets w ON ct.wallet_id=w.id
WHERE w.client_id=1 AND w.asset_symbol='BTC' AND ct.direction='DEPOSIT';
```

## Task 2: evidence audit frequency
**User**: What audit frequency in days is mandated?
**Assistant**: Use json_extract on cold_storage_policy.json.
```sql
SELECT json_extract(value, '$.audit_frequency_days') FROM evidence_kv
WHERE key='cold_storage_policy';
```

## Task 3: fast vs slow wallet day lookup
**User**: Show transfers for wallet 10 on 2024-02-05.
**Assistant**: Fast query predicates on wallet_id and timestamp range; slow uses substr.
```sql fast
SELECT * FROM custody_transfers
WHERE wallet_id=10 AND transfer_ts BETWEEN '2024-02-05' AND '2024-02-05T23:59:59';
```
```sql slow
SELECT * FROM custody_transfers
WHERE substr(transfer_ts,1,10)='2024-02-05' AND wallet_id=10;
```

## Task 4: evidence threshold breach
**User**: Using cold_storage_policy.json, list wallets with BTC deposits exceeding the cold storage threshold.
**Assistant**: Compare total deposits against json threshold.
```sql
WITH thresh AS (
  SELECT json_extract(value, '$.asset_thresholds.BTC') t FROM evidence_kv WHERE key='cold_storage_policy'
)
SELECT w.id FROM wallets w
JOIN custody_transfers ct ON ct.wallet_id=w.id AND ct.direction='DEPOSIT'
JOIN thresh
WHERE w.asset_symbol='BTC'
GROUP BY w.id HAVING SUM(ct.amount_sats)>thresh.t;
```

## Task 5: fast vs slow tx hash lookup
**User**: Find transfer with hash tx00000000000000000000000000000000000000000000000000000000000003e8.
**Assistant**: Fast uses equality on indexed column; slow scans with LIKE.
```sql fast
SELECT * FROM custody_transfers WHERE tx_hash='tx00000000000000000000000000000000000000000000000000000000000003e8';
```
```sql slow
SELECT * FROM custody_transfers WHERE tx_hash LIKE '%03e8';
```

## Task 6: fast vs slow batch move lookup
**User**: Retrieve moves for batch B0001.
**Assistant**: Fast joins on batch_id; slow filters by batch_code after join.
```sql fast
SELECT m.* FROM cold_storage_moves m JOIN cold_storage_batches b ON m.batch_id=b.id
WHERE b.batch_code='B0001';
```
```sql slow
SELECT m.* FROM cold_storage_moves m JOIN cold_storage_batches b ON m.batch_id=b.id
WHERE substr(b.batch_code,1,4)='B0001';
```
