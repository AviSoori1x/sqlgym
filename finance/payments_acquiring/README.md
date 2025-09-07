# payments_acquiring

This subdomain models card-present and card-not-present payments processing. It captures
merchant onboarding, terminal deployment, transaction authorization, settlement batching
and downstream chargeback lifecycles.

## Entities
- **merchants** – onboarding state, MCC, and KYC tier
- **terminals** – devices assigned to merchants
- **card_transactions** – individual auths and refunds with settlement linkage
- **settlement_batches** – daily cutover batches per merchant
- **chargebacks** – disputes flowing through retrieval→arbitration→final

## Running
```bash
make build DOMAIN=finance
make check DOMAIN=finance
```

Expected rows after population: ~5k merchants, 7k terminals, 200k transactions,
600 batches, and a small chargeback tail.

## Notable Indexes
- `idx_card_transactions_merchant_ts (merchant_id, txn_ts)`
- `idx_card_transactions_batch_merchant (settlement_batch_id, merchant_id)`
- `idx_settlement_batches_merchant_date (merchant_id, cutover_utc_date)`

## Distinctiveness
- enums for KYC tier, txn type, auth status, batch status and chargeback stage
- settlement cutovers follow business days and support chargeback reversals
- currency stored in integer cents to avoid float drift

## Efficiency Notes
Queries filtering by merchant and time leverage the composite indexes above.
The sample tasks highlight slow full scans versus indexed access paths.
