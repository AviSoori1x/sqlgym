# crypto_exchange_custody

Entities capture exchange clients and wallet activity:
- `clients` with risk tiers
- `wallets` per client and asset (HOT/COLD)
- `custody_transfers` for deposits and withdrawals
- `cold_storage_batches` grouping periodic vault moves
- `cold_storage_moves` linking wallets to batches

Indexes created after bulk load:
- `wallets(client_id, asset_symbol)`
- `custody_transfers(wallet_id, transfer_ts)`
- `custody_transfers(tx_hash)`
- `cold_storage_moves(batch_id, wallet_id)`

The denormalized mart `wallet_daily_balances` accelerates day-grain reporting at the
cost of transaction detail.
